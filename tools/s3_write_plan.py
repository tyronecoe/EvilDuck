#!/usr/bin/env python3
"""Build a REVIEW-ONLY migration region manifest. Never access/write hardware."""
import argparse
import json
from pathlib import Path
import hashlib
import struct
import sys
import zlib

sys.dont_write_bytecode = True
from s3_validation import FLASH_BYTES, validate_build, require
from s3_migration import sha256_file, check_raw_relocation, SPIFFS_DESTINATION_BYTES

SECTOR_BYTES = 0x1000
NVS_START, NVS_END = 0x9000, 0xE000
# Exact permitted regions; there is no generic arbitrary-address writer.
REGIONS = {
    "bootloader": (0, 0x8000),
    "partitions": (0x8000, 0x9000),
    "otadata": (0xE000, 0x10000),
    "app0": (0x10000, 0x750000),
    "app1": (0x750000, 0xE90000),
    "spiffs": (0xE90000, 0xFF0000),
    "coredump": (0xFF0000, 0x1000000),
}


def validate_regions(entries):
    """Validate both written bytes and sectors that esptool would erase."""
    require(len(entries) == len(REGIONS) and {e["role"] for e in entries} == set(REGIONS),
            "Plan requires exactly one of each reviewed region, including both applications")
    erased = []
    for entry in entries:
        start, end = REGIONS[entry["role"]]
        size = entry["bytes"]
        require(type(size) is int and 0 < size <= end - start, "Image exceeds its exact reviewed region")
        require(entry["offset"] == start, "Image offset differs from the reviewed region")
        erase_start = start // SECTOR_BYTES * SECTOR_BYTES
        erase_end = (start + size + SECTOR_BYTES - 1) // SECTOR_BYTES * SECTOR_BYTES
        require(erase_start >= start and erase_end <= end <= FLASH_BYTES, "Erase crosses region boundary")
        require(erase_end <= NVS_START or erase_start >= NVS_END, "Write/erase overlaps preserved NVS")
        if entry["role"] in ("partitions", "otadata", "spiffs", "coredump"):
            require(size == end - start, "Initialization/data image must cover its exact region")
        entry["erase_start"], entry["erase_end_exclusive"] = erase_start, erase_end
        erased.append((erase_start, erase_end))
    erased.sort()
    require(all(a[1] <= b[0] for a, b in zip(erased, erased[1:])), "Write/erase regions overlap")


def validate_ota_initializer(data):
    require(len(data) == 0x2000, "OTA initializer must cover both metadata sectors")
    seq = struct.unpack_from("<I", data, 0)[0]
    state, crc = struct.unpack_from("<II", data, 24)
    require(seq == 1 and state == 0xFFFFFFFF and crc == zlib.crc32(data[:4], 0xFFFFFFFF),
            "Pinned Arduino initializer must select app0 with valid CRC and undefined state")
    require(struct.unpack_from("<I", data, 0x1000)[0] == 0 and
            struct.unpack_from("<I", data, 0x101C)[0] == 0xFFFFFFFF,
            "Pinned Arduino second OTA record must remain invalid, not select app1")


def make_plan(core_dir, build_dir, archive_dir, repack_dir, output,
              expected_backup_sha256, expected_sector_sha256):
    """Stage local files and validate a plan; no device APIs or command execution."""
    core_dir, build_dir, archive_dir, repack_dir, output = map(Path, (core_dir, build_dir, archive_dir, repack_dir, output))
    require(not output.exists(), "Plan output already exists; refusing overwrite")
    build = validate_build(core_dir, build_dir)
    archive = json.loads((archive_dir / "manifest.json").read_text())
    require(archive.get("offline_preparation_only") is True and archive.get("migration_authorized") is False,
            "Expected offline source archive manifest")
    require(archive.get("recorded_flash_capacity_bytes", 0) >= FLASH_BYTES, "Saved evidence must establish at least 16 MiB")
    require(archive.get("full_backup_sha256") == expected_backup_sha256.lower() and
            archive.get("partition_sector_sha256") == expected_sector_sha256.lower(),
            "Source archive does not match recorded backup evidence")
    require(archive.get("existing_coredump_partition") is False, "Actual installed device has no old coredump")
    require(len(archive["images"]) == 2, "Require complete NVS and old SPIFFS archives")
    for entry in archive["images"]:
        name = entry["file"]
        require(name in ("nvs-recovery-backup.bin", "spiffs-source-archive.bin"), "Unexpected source archive")
        source = archive_dir / name
        size = 0x5000 if name.startswith("nvs-") else 0x170000
        require(source.stat().st_size == size and sha256_file(source) == entry["sha256"], "Source archive changed")
    require({e["file"] for e in archive["images"]} == {"nvs-recovery-backup.bin", "spiffs-source-archive.bin"},
            "Require both actual source archives")
    repack = json.loads((repack_dir / "manifest.json").read_text())
    require(repack.get("roundtrip_verified") is True and repack.get("migration_authorized") is False,
            "Require completed offline file-level repack; never an unverified/raw source image")
    require(repack.get("block_bytes") == 4096 and repack.get("page_bytes") == 256 and
            repack.get("offline_preparation_only") is True, "Require verified pinned SPIFFS geometry")
    require(repack.get("image") == "spiffs-new-0x160000.bin" and repack.get("bytes") == SPIFFS_DESTINATION_BYTES,
            "Require new destination-size SPIFFS, not old source image")
    require(sum(row["bytes"] for row in repack["files"].values()) <= SPIFFS_DESTINATION_BYTES * 3 // 4,
            "Restored file contents exceed conservative destination capacity")
    spiffs = repack_dir / repack["image"]
    check_raw_relocation(spiffs.stat().st_size, SPIFFS_DESTINATION_BYTES)
    require(sha256_file(spiffs) == repack["image_sha256"], "Repacked SPIFFS changed since verification")
    require(json.loads((repack_dir / "file-inventory.json").read_text()) == repack["files"],
            "Repacked file inventory differs from verified manifest")
    ota = (core_dir / "tools/partitions/boot_app0.bin").read_bytes()
    validate_ota_initializer(ota)
    payloads = {
        "bootloader": ("bootloader.bin", (build_dir / "EvilDuckS3.ino.bootloader.bin").read_bytes()),
        "partitions": ("partitions-sector.bin", (build_dir / "EvilDuckS3.ino.partitions.bin").read_bytes().ljust(0x1000, b"\xFF")),
        "otadata": ("otadata-app0.bin", ota),
        "app0": ("evilduck-app.bin", (build_dir / "EvilDuckS3.ino.bin").read_bytes()),
        "app1": ("evilduck-app.bin", (build_dir / "EvilDuckS3.ino.bin").read_bytes()),
        "spiffs": (spiffs.name, spiffs.read_bytes()),
        "coredump": ("coredump-empty.bin", b"\xFF" * 0x10000),
    }
    entries = [{"role": role, "file": name, "offset": REGIONS[role][0], "bytes": len(data)}
               for role, (name, data) in payloads.items()]
    validate_regions(entries)  # Finish every geometry/evidence check before output.
    for entry in entries:
        entry["sha256"] = hashlib.sha256(payloads[entry["role"]][1]).hexdigest()
    require(entries[3]["sha256"] == entries[4]["sha256"] == build["application_sha256"], "App slot images differ")
    result = {"review_only": True, "migration_authorized": False, "hardware_execution_supported": False,
              "core_version": "3.3.0", "psram_enabled": False,
              "application_sha256": build["application_sha256"],
              "original_backup_sha256": archive["full_backup_sha256"],
              "original_partition_sector_sha256": archive["partition_sector_sha256"],
              "protected_regions": [{"name": "nvs", "offset": NVS_START, "bytes": NVS_END-NVS_START}],
              "ota_strategy": "Rewrite both sectors with pinned boot_app0 initializer; start app0",
              "applications": "Install same validated build image in both slots; Stage17 preflight and physical validation pending",
              "coredump_strategy": "New partition initialized to erased 0xFF; no old coredump",
              "file_inventory": repack["files"], "on_device_verification_required": True,
              "writes": entries, "stage17_preflight_required": True}
    output.mkdir(parents=True)
    for entry in entries:
        data = payloads[entry["role"]][1]
        (output / entry["file"]).write_bytes(data)

    (output / "review-plan.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("core-dir", "build-dir", "archive-dir", "repack-dir", "output"):
        parser.add_argument("--"+name, required=True, type=Path)
    parser.add_argument("--expected-backup-sha256", required=True)
    parser.add_argument("--expected-sector-sha256", required=True)
    args = parser.parse_args()
    result = make_plan(args.core_dir, args.build_dir, args.archive_dir, args.repack_dir, args.output,
                       args.expected_backup_sha256, args.expected_sector_sha256)
    print(json.dumps(result, indent=2))
    print("REVIEW ONLY: no serial access, commands, flashing or migration authorization.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError) as error:
        sys.exit("FAIL: {}".format(error))
