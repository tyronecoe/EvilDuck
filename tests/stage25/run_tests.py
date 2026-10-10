#!/usr/bin/env python3
"""Offline partition/build/migration tests, including deliberate invalid inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import s3_validation as validation
import s3_migration as migration
import s3_write_plan as plan

assertions = 0
CORE = None
BUILD = None
TMP = None


def check(condition, message):
    global assertions
    assertions += 1
    if not condition:
        raise AssertionError(message)


def rejects(operation, message):
    try:
        operation()
    except (RuntimeError, ValueError, subprocess.SubprocessError):
        check(True, message)
    else:
        check(False, message)


def csv_fixture(text):
    path = TMP / "fixture.csv"
    path.write_text(text)
    return path


def repository_csv():
    return (ROOT / "EvilDuckS3/partitions.csv").read_text()


def stage25_reviewed_partition_layout():
    binary = validation.validate_csv(CORE)
    table = validation.partition_tool(CORE).PartitionTable.from_binary(binary)
    check(len(table) == 6, "Six reviewed partitions")
    check(len(binary) == 3072, "Standard 3 KiB generated table")
    check(max(p.offset + p.size for p in table) == 0x1000000, "Ends at 16 MiB")
    for p, expected in zip(table, validation.LAYOUT):
        check((p.name, p.type, p.subtype, p.offset, p.size) == expected, "Exact reviewed partition")
        check(p.offset % (0x10000 if p.type == 0 else 0x1000) == 0, "Required alignment")


def stage25_overlapping_partitions_rejected():
    path = csv_fixture(repository_csv().replace("0x750000", "0x740000"))
    rejects(lambda: validation.validate_csv(CORE, path), "Overlapping slots must fail")


def stage25_unaligned_application_rejected():
    path = csv_fixture(repository_csv().replace("0x750000", "0x750001"))
    rejects(lambda: validation.validate_csv(CORE, path), "Unaligned app must fail")


def stage25_reviewed_offsets_sizes_flags_enforced():
    original = repository_csv()
    for old, new in (("0x9000", "0xA000"), ("0x5000", "0x4000"),
                     ("0xE000", "0xD000"), ("0x2000", "0x1000"),
                     ("0x740000", "0x730000"), ("0xE90000", "0xE80000"),
                     ("0x160000", "0x150000"), ("0xFF0000", "0xFE0000"),
                     ("0x10000,\n", "0x20000,\n"), ("0x160000,", "0x160000,encrypted")):
        path = csv_fixture(original.replace(old, new))
        rejects(lambda: validation.validate_csv(CORE, path), "Reviewed value drift must fail")


def stage25_core_version_pin_enforced():
    core = TMP / "other-core"
    core.mkdir()
    (core / "platform.txt").write_text("version=3.3.1\n")
    rejects(lambda: validation.partition_tool(core), "Untested core must be rejected")


def make_image(path, size):
    header = bytearray(24)
    header[0:4] = bytes([0xE9, 1, 2, 0x4F])
    struct.pack_into("<H", header, 12, 9)
    with path.open("wb") as output:
        output.write(header)
        output.truncate(size)


def stage25_application_size_boundary():
    image = TMP / "boundary.bin"
    make_image(image, validation.APP_BYTES)
    check(validation.validate_image(image) == 0x740000, "Exactly one slot is accepted")
    make_image(image, validation.APP_BYTES + 1)
    rejects(lambda: validation.validate_image(image), "One byte over slot must fail")
    make_image(image, 23)
    rejects(lambda: validation.validate_image(image), "Truncated header must fail")


def stage25_image_header_configuration_enforced():
    image = TMP / "header.bin"
    for offset, value in ((0, 0), (1, 0), (2, 0), (3, 0x2F), (3, 0x40), (12, 0)):
        make_image(image, 24)
        with image.open("r+b") as output:
            output.seek(offset)
            output.write(bytes([value]))
        rejects(lambda: validation.validate_image(image), "Wrong magic/mode/size/frequency/target must fail")


def stage25_build_configuration_and_app_address_enforced():
    properties = json.loads((BUILD / "s3-build-properties.json").read_text())
    validation.validate_properties(properties)
    check(True, "Actual resolved pinned properties accepted")
    for key in validation.EXPECTED_PROPERTIES:
        bad = dict(properties)
        bad[key] = "unexpected"
        rejects(lambda: validation.validate_properties(bad), "Configuration drift must fail")
    for key in ("tools.esptool_py.upload.pattern_args",
                "recipe.hooks.objcopy.postobjcopy.3.pattern_args"):
        bad = dict(properties)
        bad[key] = bad[key].replace("0x10000", "0x400000")
        rejects(lambda: validation.validate_properties(bad), "Wrong application upload address must fail")


def stage25_generated_16m_build_artifacts():
    report = validation.validate_build(CORE, BUILD)
    check(report["flash_bytes"] == 16 * 1024 * 1024, "Actual build is 16 MiB")
    check(report["application_address"] == 0x10000, "Actual app0 address is standard")
    check(report["application_bytes"] <= 0x740000, "Actual app fits either OTA slot")
    check(report["hardware_verified"] is False, "Build is never proof of physical capacity")


def artifact_fixture(name):
    directory = TMP / name
    directory.mkdir()
    for file in ("s3-build-properties.json", "build.options.json", "partitions.csv",
                 "EvilDuckS3.ino.partitions.bin", "EvilDuckS3.ino.bin",
                 "EvilDuckS3.ino.bootloader.bin", "EvilDuckS3.ino.merged.bin"):
        shutil.copyfile(BUILD / file, directory / file)
    return directory


def stage25_corrupt_partition_binary_rejected():
    directory = artifact_fixture("bad-partition-binary")
    binary = directory / "EvilDuckS3.ino.partitions.bin"
    data = bytearray(binary.read_bytes())
    data[12] ^= 1
    binary.write_bytes(data)
    rejects(lambda: validation.validate_build(CORE, directory), "Partition checksum corruption must fail")


def stage25_merged_image_wrong_address_rejected():
    directory = artifact_fixture("bad-merged-address")
    with (directory / "EvilDuckS3.ino.merged.bin").open("r+b") as output:
        output.seek(0x10000)
        output.write(b"\x00")
    rejects(lambda: validation.validate_build(CORE, directory), "Application absent at standard address must fail")


def stage25_stale_4m_partition_artifact_rejected():
    directory = artifact_fixture("stale-table")
    shutil.copyfile(CORE / "tools/partitions/default.csv", directory / "partitions.csv")
    rejects(lambda: validation.validate_build(CORE, directory), "Stale build CSV must fail")


def stage25_saved_physical_flash_capacity_guard():
    for size in (16, 32):
        check(migration.check_flash_id("Detected flash size: {}MB\n".format(size)) == size * 1024 * 1024,
              "Sufficient recorded capacity accepted")
    for text in ("Detected flash size: 4MB\n", "Detected flash size: 8MB\n",
                 "FlashSize=16M\n", "Detected flash size: Unknown\n",
                 "Detected flash size: 16MB\nDetected flash size: 4MB\n"):
        rejects(lambda: migration.check_flash_id(text), "Insufficient/absent/ambiguous evidence must fail")


def legacy_backup(name):
    directory = TMP / name
    directory.mkdir()
    tool = validation.partition_tool(CORE)
    table = tool.PartitionTable.from_csv("nvs,data,nvs,0x9000,20K,\notadata,data,ota,0xe000,8K,\napp0,app,ota_0,0x10000,1280K,\napp1,app,ota_1,0x150000,1280K,\nspiffs,data,spiffs,0x290000,1472K,\n")
    sector = table.to_binary().ljust(0x1000, b"\xFF")
    partition = directory / "partition-sector.bin"
    partition.write_bytes(sector)
    log = directory / "flash-id.txt"
    log.write_text("esptool.py v4.12.0\nDetected flash size: 16MB\n")
    backup = directory / "backup.bin"
    data_images = {}
    with backup.open("wb") as output:
        output.truncate(validation.FLASH_BYTES)
        output.seek(0x8000)
        output.write(sector)
        for index, name in enumerate(("nvs", "spiffs")):
            part = next(p for p in validation.LEGACY_LAYOUT if p[0] == name)
            data = bytes([index + 1]) * part[4]
            output.seek(part[3])
            output.write(data)
            data_images[name] = data
    return log, backup, partition, data_images


def stage25_offline_source_archives_require_file_migration():
    log, backup, sector, expected = legacy_backup("source-archive")
    output = TMP / "prepared"
    manifest = migration.prepare(CORE, log, backup, sector, output)
    for entry in manifest["images"]:
        name = "spiffs" if entry["file"].startswith("spiffs-") else "nvs"
        data = (output / entry["file"]).read_bytes()
        check(data == expected[name], "Entire source partition archived without truncation")
        check(hashlib.sha256(data).hexdigest() == entry["sha256"], "Archive hash recorded")
        check(entry["destination_offset"] is None and not entry["raw_relocation_allowed"],
              "Source/recovery archives must not be presented as destination writes")
    spiffs = next(p for p in manifest["images"] if p["file"].startswith("spiffs-"))
    check(spiffs["bytes"] == 0x170000 and spiffs["destination_bytes"] == 0x160000,
          "Installed source/destination mismatch explicit")
    check(not manifest["existing_coredump_partition"] and not (output / "coredump.bin").exists(),
          "No old coredump image exists or is fabricated")
    check(not manifest["migration_authorized"], "Preparation never authorizes migration")
    check(manifest["offline_preparation_only"], "Offline preparation clearly labeled")
    check(json.loads((output / "manifest.json").read_text()) == manifest, "Saved manifest matches")


def stage25_offline_preparation_rejects_invalid_backups():
    log, backup, sector, _ = legacy_backup("invalid-backups")
    output = TMP / "must-not-exist"
    log.write_text("Detected flash size: 8MB\n")
    rejects(lambda: migration.prepare(CORE, log, backup, sector, output), "Capacity guard precedes output")
    log.write_text("Detected flash size: 16MB\n")
    with backup.open("r+b") as source:
        source.seek(0x8000 + 1000)
        source.write(b"\x00")
    rejects(lambda: migration.prepare(CORE, log, backup, sector, output), "Mismatched partition backup must fail")
    with backup.open("r+b") as source:
        source.truncate(4 * 1024 * 1024)
    rejects(lambda: migration.prepare(CORE, log, backup, sector, output), "Short flash backup must fail")
    check(not output.exists(), "No output created on any rejected preparation")
    log, backup, sector, _ = legacy_backup("unexpected-legacy-table")
    sector.write_bytes(validation.validate_csv(CORE).ljust(0x1000, b"\xFF"))
    rejects(lambda: migration.prepare(CORE, log, backup, sector, output), "Unexpected installed map must fail")
    check(not output.exists(), "Unexpected legacy map does not create output")


def stage25_offline_preparation_never_overwrites():
    log, backup, sector, _ = legacy_backup("overwrite-check")
    output = TMP / "existing-backup"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("existing user data")
    rejects(lambda: migration.prepare(CORE, log, backup, sector, output), "Existing output must be refused")
    check(marker.read_text() == "existing user data", "Existing backup untouched")


def stage25_build_wrapper_requires_clean_output():
    output = TMP / "nonempty-build"
    output.mkdir()
    (output / "keep.txt").write_text("existing user data")
    result = subprocess.run([sys.executable, str(ROOT / "tools/build_s3.py"),
                             "--build-dir", str(output), "--arduino-cli", "not-a-command"],
                            capture_output=True, text=True)
    check(result.returncode != 0, "Nonempty directory rejected before invoking Arduino")
    check("must be empty" in result.stderr, "Useful clean-build diagnostic")
    check((output / "keep.txt").read_text() == "existing user data", "Existing output not erased")


def stage25_verified_device_map_differs_from_core_default():
    tool = validation.partition_tool(CORE)
    check(len(validation.LEGACY_LAYOUT) == 5, "Actual device has exactly five partitions")
    spiffs = validation.LEGACY_LAYOUT[-1]
    check(spiffs[3:] == (0x290000, 0x170000) and sum(spiffs[3:]) == 0x400000,
          "Actual SPIFFS extends to four MiB, without coredump")
    default = tool.PartitionTable.from_csv((CORE / "tools/partitions/default.csv").read_text())
    rejects(lambda: validation.check_table(default, validation.LEGACY_LAYOUT),
            "Core default must never substitute for actual installed evidence")


def stage25_raw_spiffs_size_mismatch_refused():
    rejects(lambda: migration.check_raw_relocation(0x170000, 0x160000),
            "Old full image is too large; raw relocation/truncation forbidden")
    rejects(lambda: migration.check_raw_relocation(0x150000, 0x160000),
            "Short raw image cannot bypass geometry checks")
    migration.check_raw_relocation(0x160000, 0x160000)
    check(True, "Only exact destination-sized geometry passes size guard")


def stage25_recorded_backup_hash_guards():
    log, backup, sector, _ = legacy_backup("hash-guards")
    output = TMP / "wrong-hash"
    rejects(lambda: migration.prepare(CORE, log, backup, sector, output, "0"*64),
            "Wrong full-flash recorded hash rejected")
    rejects(lambda: migration.prepare(CORE, log, backup, sector, output, None, "0"*64),
            "Wrong partition-sector recorded hash rejected")
    check(not output.exists(), "Hash failures create no output")
    result = migration.prepare(CORE, log, backup, sector, TMP / "correct-hash",
                               migration.sha256_file(backup), migration.sha256_file(sector))
    check(result["full_backup_sha256"] == migration.sha256_file(backup), "Correct synthetic evidence hashes accepted")


def file_fixture(name):
    files = TMP / name
    files.mkdir()
    (files / "script.txt").write_bytes(b"REM harmless fixture\r\nSTRINGLN archive-ok\n")
    (files / "binary.dat").write_bytes(bytes(range(256))*3 + b"\x00\xff")
    (files / "empty").write_bytes(b"")
    (files / ".hidden").write_bytes(b"hidden preserved")
    (files / ".DS_Store").write_bytes(b"do not silently omit")
    (files / "nested").mkdir()
    (files / "nested/file with spaces").write_bytes(b"nested names")
    return files


def stage25_file_level_extract_repack_roundtrip():
    files = file_fixture("file-export")
    old_image = TMP / "old-spiffs-0x170000.bin"
    executable = migration.checked_mkspiffs(MKSPIFFS)
    migration.mk_run(executable, "-c", files, 0x170000, old_image)
    extracted = TMP / "offline-extracted"
    index = migration.extract_files(MKSPIFFS, old_image, extracted)
    check(index == migration.inventory(files), "Old-geometry extraction preserves binary/empty/hidden/nested files")
    result = migration.pack_files(MKSPIFFS, extracted, TMP / "new-spiffs")
    check(result["bytes"] == 0x160000, "Repacked destination image exact smaller size")
    check(result["files"] == index and result["roundtrip_verified"], "Roundtrip verifies all names/content")
    check(not result["migration_authorized"] and not result["on_device_restoration_verified"],
          "Offline verification does not authorize or certify hardware migration")
    image = TMP / "new-spiffs" / result["image"]
    check(image.stat().st_size == 0x160000 and migration.sha256_file(image) == result["image_sha256"],
          "Saved image size and hash match manifest")
    migration.save_inventory(files, TMP / "file-inventory.json")
    migration.verify_files(extracted, json.loads((TMP / "file-inventory.json").read_text()))
    check(True, "Independent file-tree verification succeeds")
    (extracted / "binary.dat").write_bytes(b"changed")
    rejects(lambda: migration.verify_files(extracted, index), "Changed file bytes rejected")
    (extracted / "missing.txt").write_bytes(b"extra")
    rejects(lambda: migration.verify_files(extracted, index), "Changed file set rejected")


def stage25_file_level_empty_filesystem():
    files = TMP / "empty-export"
    files.mkdir()
    result = migration.pack_files(MKSPIFFS, files, TMP / "empty-repack")
    check(result["files"] == {} and result["roundtrip_verified"], "Empty new filesystem roundtrips correctly")


def stage25_file_level_capacity_and_overwrite_guards():
    files = file_fixture("pack-guard-export")
    output = TMP / "pack-existing"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_bytes(b"existing")
    rejects(lambda: migration.pack_files(MKSPIFFS, files, output), "Existing pack output refused")
    check(marker.read_bytes() == b"existing", "Existing output data preserved")
    rejects(lambda: migration.pack_files(MKSPIFFS, files, files / "inside"), "Output inside export tree refused")
    large = TMP / "large-export"
    large.mkdir()
    with (large / "big.bin").open("wb") as f:
        f.truncate(0x160000*3//4 + 1)
    destination = TMP / "too-large"
    rejects(lambda: migration.pack_files(MKSPIFFS, large, destination), "Conservative capacity budget enforced")
    check(not destination.exists(), "Oversized file set creates no destination")
    (files / "link").symlink_to(files / "script.txt")
    rejects(lambda: migration.inventory(files), "Symlink exports refused")
    (files / "link").unlink()
    (files / ("x"*32)).write_bytes(b"bad name")
    rejects(lambda: migration.inventory(files), "Name length must fit target SPIFFS")


def stage25_corrupt_or_wrong_geometry_extraction_refused():
    bad = TMP / "corrupt-spiffs.bin"
    bad.write_bytes(b"bad")
    output = TMP / "corrupt-export"
    rejects(lambda: migration.extract_files(MKSPIFFS, bad, output), "Short/wrong geometry image refused")
    check(not output.exists(), "Rejected source creates no extraction output")
    bad.write_bytes(b"\x02" * 0x170000)
    rejects(lambda: migration.extract_files(MKSPIFFS, bad, output), "Full-sized corrupt filesystem also refused")
    check(not output.exists(), "Corrupt mount does not create extraction output")


def stage25_alternative_layout_maximum_equal_slots():
    def largest(spiffs, coredump):
        sizes = []
        for size in range(0x1000, 0x1000000, 0x1000):
            app1 = (0x10000 + size + 0xFFFF) & ~0xFFFF
            if app1 + size + spiffs + coredump <= 0x1000000:
                sizes.append(size)
        return max(sizes)
    check(largest(0x160000, 0x10000) == 0x740000, "Retained A layout gives maximum equal slots")
    check(largest(0x170000, 0x10000) == 0x730000, "Full old SPIFFS plus coredump reduces both slots by 64 KiB")
    check(largest(0x170000, 0) == 0x740000, "Full old SPIFFS without coredump retains slot sizes")
    csv = "nvs,data,nvs,0x9000,0x5000,\notadata,data,ota,0xe000,0x2000,\napp0,app,ota_0,0x10000,0x730000,\napp1,app,ota_1,0x740000,0x730000,\nspiffs,data,spiffs,0xe70000,0x170000,\ncoredump,data,coredump,0xff0000,0x10000,\n"
    table = validation.partition_tool(CORE).PartitionTable.from_csv(csv)
    table.verify()
    check(max(p.offset+p.size for p in table) == 0x1000000, "Alternative B map validates with final 64 KiB gap before coredump")



def plan_fixture(name):
    log, backup, sector, _ = legacy_backup(name + "-backup")
    archive = TMP / (name + "-archive")
    migration.prepare(CORE, log, backup, sector, archive)
    files = file_fixture(name + "-files")
    repack = TMP / (name + "-repack")
    migration.pack_files(MKSPIFFS, files, repack)
    return archive, repack, migration.sha256_file(backup), migration.sha256_file(sector)


def stage25_review_only_plan_preserves_nvs_and_initializes_both_apps():
    archive, repack, full_hash, sector_hash = plan_fixture("plan-safe")
    before = migration.inventory(archive)
    output = TMP / "review-only-plan"
    result = plan.make_plan(CORE, BUILD, archive, repack, output, full_hash, sector_hash)
    check(result["review_only"] and not result["migration_authorized"] and
          not result["hardware_execution_supported"], "Plan cannot execute or authorize hardware operations")
    check(result["core_version"] == "3.3.0" and not result["psram_enabled"], "Pinned core, PSRAM disabled")
    check(len(result["writes"]) == 7, "Exact seven region writes")
    for entry in result["writes"]:
        check(entry["erase_end_exclusive"] <= 0x9000 or entry["erase_start"] >= 0xE000,
              "Sector-rounded erase excludes NVS")
        check(migration.sha256_file(output / entry["file"]) == entry["sha256"], "Staged bytes match plan")
    check(result["writes"][3]["sha256"] == result["writes"][4]["sha256"] == result["application_sha256"],
          "Same validated Stage 4 image in both slots")
    table = (output / "partitions-sector.bin").read_bytes()
    check(len(table) == 4096 and table[3072:] == b"\xff" * 1024, "Partition sector padded without touching NVS")
    check((output / "coredump-empty.bin").read_bytes() == b"\xff" * 0x10000, "New coredump erased-state initializer")
    check((output / "otadata-app0.bin").read_bytes() == (CORE / "tools/partitions/boot_app0.bin").read_bytes(),
          "Both OTA metadata sectors replaced with pinned initializer")
    check(migration.inventory(archive) == before, "Original source/NVS archives untouched")
    check(json.loads((output / "review-plan.json").read_text()) == result, "Saved review manifest exact")
    rejects(lambda: plan.make_plan(CORE, BUILD, archive, repack, output, full_hash, sector_hash), "No plan overwrite")


def stage25_write_and_erase_region_guards():
    def entries():
        return [{"role": role, "offset": start, "bytes": end-start}
                for role, (start, end) in plan.REGIONS.items()]
    plan.validate_regions(entries())
    check(True, "Exact full reviewed regions valid")
    for role, field, value in (("app1", "offset", 0x150000), ("partitions", "offset", 0x9000),
                               ("partitions", "bytes", 0x1001), ("bootloader", "bytes", 0x8001),
                               ("spiffs", "bytes", 0x170000), ("coredump", "bytes", 0x10001),
                               ("app0", "bytes", 0x740001), ("bootloader", "bytes", 0x1000000),
                               ("otadata", "bytes", 0x1000), ("app0", "offset", 0x10001)):
        invalid = entries()
        next(row for row in invalid if row["role"] == role)[field] = value
        rejects(lambda: plan.validate_regions(invalid), "Wrong offsets/oversize/merged/partial metadata rejected")
    rejects(lambda: plan.validate_regions(entries()[:-1]), "Missing region rejected")
    invalid = entries(); invalid[-1] = invalid[-2].copy()
    rejects(lambda: plan.validate_regions(invalid), "Duplicate/missing role rejected")


def stage25_ota_initializer_selects_app0_deterministically():
    valid = (CORE / "tools/partitions/boot_app0.bin").read_bytes()
    plan.validate_ota_initializer(valid)
    check(True, "Pinned two-sector initializer valid, app0 selected")
    for offset in (0, 24, 28, 0x1000, 0x101C):
        invalid = bytearray(valid); invalid[offset] ^= 1
        rejects(lambda: plan.validate_ota_initializer(invalid), "Changed sequence/state/CRC rejected")
    rejects(lambda: plan.validate_ota_initializer(valid[:4096]), "Incomplete OTA metadata rejected")


def stage25_plan_refuses_unverified_files_and_backup_provenance():
    archive, repack, full_hash, sector_hash = plan_fixture("plan-invalid")
    output = TMP / "must-not-plan"
    rejects(lambda: plan.make_plan(CORE, BUILD, archive, repack, output, "0"*64, sector_hash), "Wrong full backup evidence rejected")
    rejects(lambda: plan.make_plan(CORE, BUILD, archive, repack, output, full_hash, "0"*64), "Wrong sector evidence rejected")
    path = repack / "manifest.json"
    original = json.loads(path.read_text())
    for key, value in (("roundtrip_verified", False), ("bytes", 0x170000),
                       ("image", "spiffs-source-archive.bin"), ("image_sha256", "0"*64),
                       ("block_bytes", 8192), ("page_bytes", 512)):
        modified = original.copy(); modified[key] = value
        path.write_text(json.dumps(modified))
        rejects(lambda: plan.make_plan(CORE, BUILD, archive, repack, output, full_hash, sector_hash), "Unverified/raw/wrong geometry files rejected")
        check(not output.exists(), "Validation failures create no staged output")
    path.write_text(json.dumps(original))
    modified = original.copy(); modified["files"] = {"/too-large": {"bytes": 0x160000, "sha256": "0"*64}}
    path.write_text(json.dumps(modified))
    rejects(lambda: plan.make_plan(CORE, BUILD, archive, repack, output, full_hash, sector_hash), "Capacity overflow rejected")
    check(not output.exists(), "No oversized plan output")


def stage25_mac_old_core_rejected_before_compile():
    core = TMP / "mac-core-2.0.17"
    core.mkdir(); (core / "platform.txt").write_text("version=2.0.17\n")
    rejects(lambda: validation.partition_tool(core), "Mac installed core must not replace pinned 3.3.0")


TESTS = [value for name, value in list(globals().items()) if name.startswith("stage25_")]


def main():
    global CORE, BUILD, TMP, MKSPIFFS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-dir", required=True, type=Path)
    parser.add_argument("--build-dir", required=True, type=Path, help="Actual completed pinned build")
    parser.add_argument("--mkspiffs", type=Path, help="Tested mkspiffs 0.2.3 executable")
    args = parser.parse_args()
    CORE, BUILD = args.core_dir, args.build_dir
    MKSPIFFS = args.mkspiffs or CORE.parents[2] / "tools/mkspiffs/0.2.3/mkspiffs"
    failures = 0
    with tempfile.TemporaryDirectory(prefix="evilduck-stage25-tests-") as directory:
        TMP = Path(directory)
        for test in TESTS:
            before = assertions
            try:
                test()
                print("PASS {} ({} assertions)".format(test.__name__, assertions - before), flush=True)
            except Exception:
                failures += 1
                print("FAIL {}".format(test.__name__), flush=True)
                traceback.print_exc()
    print("Stage 2.5: {} PASS, {} FAIL; {} assertions; no hardware access".format(
        len(TESTS) - failures, failures, assertions), flush=True)
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
