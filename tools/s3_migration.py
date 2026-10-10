#!/usr/bin/env python3
"""Prepare migration data OFFLINE from saved evidence; never access hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from s3_validation import (FLASH_BYTES, LAYOUT, LEGACY_LAYOUT,
                           check_table, partition_tool, require, validate_csv)

SPIFFS_SOURCE_BYTES = 0x170000
SPIFFS_DESTINATION_BYTES = 0x160000
BLOCK_BYTES, PAGE_BYTES = 4096, 256
MK_CONFIG = {"SPIFFS_OBJ_NAME_LEN": "32", "SPIFFS_OBJ_META_LEN": "4",
             "SPIFFS_USE_MAGIC": "1", "SPIFFS_USE_MAGIC_LENGTH": "1",
             "SPIFFS_ALIGNED_OBJECT_INDEX_TABLES": "0"}


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(128 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_flash_id(text):
    """Accept saved esptool 4.x/5.x capacity output, never access a serial port."""
    matches = re.findall(r"^\s*Detected flash size:\s*(\d+)\s*(MB|MiB)\s*$", text, re.MULTILINE)
    require(len(matches) == 1, "Expected exactly one 'Detected flash size: ...' line from esptool")
    capacity = int(matches[0][0]) * 1024 * 1024
    require(capacity >= FLASH_BYTES, "Detected physical flash is below 16 MiB; DO NOT migrate")
    return capacity


def check_raw_relocation(source_bytes, destination_bytes):
    require(source_bytes == destination_bytes,
            "Unsafe raw relocation: source 0x{:X} differs from destination 0x{:X}; file-level migration required".format(
                source_bytes, destination_bytes))


def prepare(core_dir, flash_id_log, backup, partition_sector, output,
            expected_backup_sha256=None, expected_sector_sha256=None):
    """Archive installed data. The old SPIFFS image is NOT destination-ready."""
    capacity = check_flash_id(Path(flash_id_log).read_text())
    require(Path(backup).stat().st_size == FLASH_BYTES, "Expected a complete 16 MiB flash backup")
    sector = Path(partition_sector).read_bytes()
    require(len(sector) == 0x1000, "Expected the complete 0x1000-byte partition-table sector")
    tool = partition_tool(core_dir)
    check_table(tool.PartitionTable.from_binary(sector), LEGACY_LAYOUT)
    validate_csv(core_dir)
    output = Path(output)
    require(not output.exists(), "Output already exists; existing backups must not be overwritten")
    backup_hash, sector_hash = sha256_file(backup), hashlib.sha256(sector).hexdigest()
    for actual, expected, label in ((backup_hash, expected_backup_sha256, "Full backup"),
                                     (sector_hash, expected_sector_sha256, "Partition sector")):
        require(expected is None or actual == expected.lower(), label + " SHA-256 does not match recorded evidence")
    images = []
    with Path(backup).open("rb") as source:
        source.seek(0x8000)
        require(source.read(0x1000) == sector, "Partition sector does not match the full backup")
        for name in ("nvs", "spiffs"):
            old = next(p for p in LEGACY_LAYOUT if p[0] == name)
            new = next(p for p in LAYOUT if p[0] == name)
            source.seek(old[3])
            data = source.read(old[4])
            require(len(data) == old[4], "Backup truncated while extracting {}".format(name))
            images.append((name, old, new, data))
    require(sha256_file(backup) == backup_hash, "Backup changed during preparation")
    manifest = {"offline_preparation_only": True, "migration_authorized": False,
                "recorded_flash_capacity_bytes": capacity,
                "partition_sector_sha256": sector_hash, "full_backup_sha256": backup_hash,
                "existing_coredump_partition": False,
                "new_coredump_action": "Initialize new 0x10000 region; no old crash partition exists",
                "spiffs_migration": "file-level restore/repack required; never truncate or raw-relocate source image",
                "images": []}
    output.mkdir(parents=True)
    for name, old, new, data in images:
        filename = "spiffs-source-archive.bin" if name == "spiffs" else "nvs-recovery-backup.bin"
        (output / filename).write_bytes(data)
        manifest["images"].append({"file": filename, "source_offset": old[3],
                                   "source_bytes": old[4], "destination_offset": None,
                                   "proposed_destination_offset": new[3], "destination_bytes": new[4],
                                   "raw_relocation_allowed": False, "bytes": len(data),
                                   "purpose": "source archive only" if name == "spiffs" else "recovery backup; preserve NVS in place",
                                   "sha256": hashlib.sha256(data).hexdigest()})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def inventory(directory):
    """File-level integrity inventory; reject links and unrepresentable names."""
    directory = Path(directory)
    require(directory.is_dir() and not directory.is_symlink(), "Expected an ordinary file-export directory")
    result = {}
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), "File export may not contain symbolic links")
        if path.is_dir():
            continue
        require(path.is_file(), "File export contains a non-regular file")
        name = "/" + path.relative_to(directory).as_posix()
        require(len(name.encode("utf-8")) < 32 and not any(c in name for c in "\x00\r\n\t\\"),
                "SPIFFS name must fit 31 UTF-8 bytes without control/backslash characters: " + name)
        result[name] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    return result


def save_inventory(directory, output):
    output = Path(output)
    require(not output.exists(), "Inventory output already exists; refusing overwrite")
    result = inventory(directory)
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


def verify_files(directory, expected):
    require(inventory(directory) == expected, "Restored file names, sizes or SHA-256 differ from backup inventory")


def checked_mkspiffs(executable):
    executable = str(Path(executable).resolve())
    result = subprocess.run([executable, "--version"], capture_output=True, text=True, check=True, timeout=30)
    require("mkspiffs ver. 0.2.3" in result.stdout, "Require tested mkspiffs 0.2.3")
    for key, value in MK_CONFIG.items():
        require(re.search(r"^\s*" + key + r":\s*" + value + r"\s*$", result.stdout, re.MULTILINE),
                "mkspiffs geometry/configuration differs: " + key)
    return executable


def mk_run(executable, operation, argument, size, image):
    args = [executable, operation]
    if argument is not None:
        args.append(str(argument))
    if operation == "-c":
        args.append("-a")  # Include dotfiles/.DS_Store/.git data; never silently omit exports.
    args += ["-b", str(BLOCK_BYTES), "-p", str(PAGE_BYTES), "-s", str(size), str(image)]
    return subprocess.run(args, capture_output=True, text=True, check=True, timeout=120).stdout


def source_listing(executable, image, size):
    require(Path(image).stat().st_size == size, "Unexpected source SPIFFS archive length")
    expected = {}
    for line in mk_run(executable, "-l", None, size, image).splitlines():
        match = re.fullmatch(r"(\d+)\t(/[^\r\n\t]+)", line)
        require(match is not None, "Unrecognized SPIFFS listing; refuse unchecked unpack")
        length, name = int(match[1]), match[2]
        parts = name[1:].split("/")
        require(all(p and p not in (".", "..") for p in parts) and
                "\\" not in name and len(name.encode("utf-8")) < 32,
                "Unsafe/unrepresentable SPIFFS filename; refuse unpack")
        require(name not in expected, "Duplicate SPIFFS file name")
        expected[name] = length
    return expected


def extract_files(executable, image, output):
    """Optional offline decode; compare with an independent export before trusting."""
    executable = checked_mkspiffs(executable)
    output = Path(output)
    require(not output.exists(), "Extraction output already exists; refusing overwrite")
    expected = source_listing(executable, image, SPIFFS_SOURCE_BYTES)
    with tempfile.TemporaryDirectory(prefix="evilduck-spiffs-extract-") as temporary:
        files = Path(temporary) / "files"
        files.mkdir()
        mk_run(executable, "-u", files, SPIFFS_SOURCE_BYTES, image)
        require({name: row["bytes"] for name, row in inventory(files).items()} == expected,
                "Unpacked file set/lengths differ from source listing")
        shutil.copytree(files, output)
    return inventory(output)


def pack_files(executable, files, output):
    """Create exact destination geometry, then unpack and verify every file."""
    executable = checked_mkspiffs(executable)
    output = Path(output)
    require(not output.exists(), "Pack output already exists; refusing overwrite")
    files = Path(files)
    require(files.resolve() != output.resolve() and files.resolve() not in output.resolve().parents,
            "Pack output must be outside the exported file tree")
    expected = inventory(files)
    require(sum(row["bytes"] for row in expected.values()) <= SPIFFS_DESTINATION_BYTES * 3 // 4,
            "File contents exceed conservative 75% destination capacity budget; review space before migration")
    with tempfile.TemporaryDirectory(prefix="evilduck-spiffs-repack-") as temporary:
        temporary = Path(temporary)
        image = temporary / "spiffs-new-0x160000.bin"
        mk_run(executable, "-c", files, SPIFFS_DESTINATION_BYTES, image)
        require(image.stat().st_size == SPIFFS_DESTINATION_BYTES, "Generated SPIFFS size differs from destination")
        check_raw_relocation(image.stat().st_size, SPIFFS_DESTINATION_BYTES)
        restored = temporary / "roundtrip"
        restored.mkdir()
        mk_run(executable, "-u", restored, SPIFFS_DESTINATION_BYTES, image)
        verify_files(restored, expected)
        verify_files(files, expected)  # Detect exports changing during packing.
        result = {"offline_preparation_only": True, "migration_authorized": False,
                  "image": image.name, "bytes": SPIFFS_DESTINATION_BYTES,
                  "proposed_destination_offset": 0xE90000,
                  "block_bytes": BLOCK_BYTES, "page_bytes": PAGE_BYTES,
                  "image_sha256": sha256_file(image), "files": expected,
                  "roundtrip_verified": True, "on_device_restoration_verified": False}
        output.mkdir(parents=True)
        shutil.copy2(image, output / image.name)
        (output / "file-inventory.json").write_text(json.dumps(expected, indent=2) + "\n")
        (output / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("check-flash-id", help="Check a saved esptool 4.x/5.x log; no serial access")
    verify.add_argument("--log", required=True, type=Path)
    extract = commands.add_parser("prepare", help="Archive installed NVS/SPIFFS from saved backup; not flash-ready")
    extract.add_argument("--core-dir", required=True, type=Path)
    extract.add_argument("--flash-id-log", required=True, type=Path)
    extract.add_argument("--backup", required=True, type=Path)
    extract.add_argument("--partition-sector", required=True, type=Path)
    extract.add_argument("--output", required=True, type=Path)
    extract.add_argument("--expected-backup-sha256")
    extract.add_argument("--expected-sector-sha256")
    unpack = commands.add_parser("extract-files", help="Optional offline SPIFFS decode; never touches device")
    unpack.add_argument("--mkspiffs", required=True, type=Path)
    unpack.add_argument("--image", required=True, type=Path)
    unpack.add_argument("--output", required=True, type=Path)
    pack = commands.add_parser("pack-files", help="Build and roundtrip-verify smaller SPIFFS image offline")
    pack.add_argument("--mkspiffs", required=True, type=Path)
    pack.add_argument("--files", required=True, type=Path)
    pack.add_argument("--output", required=True, type=Path)
    index = commands.add_parser("inventory", help="Hash all files in a local export")
    index.add_argument("--files", required=True, type=Path)
    index.add_argument("--output", required=True, type=Path)
    compare = commands.add_parser("verify-files", help="Verify a separately exported/restored file tree")
    compare.add_argument("--files", required=True, type=Path)
    compare.add_argument("--inventory", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "check-flash-id":
        print("PASS: saved log reports {} MiB; no migration authorization".format(check_flash_id(args.log.read_text()) // 1024 // 1024))
    elif args.command == "prepare":
        print(json.dumps(prepare(args.core_dir, args.flash_id_log, args.backup,
                                 args.partition_sector, args.output,
                                 args.expected_backup_sha256, args.expected_sector_sha256), indent=2))
    elif args.command == "extract-files":
        print(json.dumps(extract_files(args.mkspiffs, args.image, args.output), indent=2))
    elif args.command == "pack-files":
        print(json.dumps(pack_files(args.mkspiffs, args.files, args.output), indent=2))
    elif args.command == "inventory":
        print(json.dumps(save_inventory(args.files, args.output), indent=2))
    else:
        verify_files(args.files, json.loads(args.inventory.read_text()))
        print("PASS: local exported/restored files match inventory; no hardware accessed")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        sys.exit("FAIL: {}".format(error))
