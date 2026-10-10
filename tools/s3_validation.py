#!/usr/bin/env python3
"""Offline checks for the approved EvilDuck S3 build. No hardware interfaces."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
CORE_VERSION = "3.3.0"
FLASH_BYTES = 0x1000000
APP_BYTES = 0x740000
APP_OFFSET = 0x10000
FQBN = ("esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,"
        "PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,"
        "MSCOnBoot=default,DFUOnBoot=default")
# Numeric types/subtypes match esp_partition.h and gen_esp32part.py.
LAYOUT = (
    ("nvs", 1, 2, 0x9000, 0x5000),
    ("otadata", 1, 0, 0xE000, 0x2000),
    ("app0", 0, 0x10, APP_OFFSET, APP_BYTES),
    ("app1", 0, 0x11, 0x750000, APP_BYTES),
    ("spiffs", 1, 0x82, 0xE90000, 0x160000),
    ("coredump", 1, 3, 0xFF0000, 0x10000),
)
# Actual installed map reported from this device on 2026-10-10, not the core default CSV.
LEGACY_LAYOUT = (
    LAYOUT[0], LAYOUT[1],
    ("app0", 0, 0x10, 0x10000, 0x140000),
    ("app1", 0, 0x11, 0x150000, 0x140000),
    ("spiffs", 1, 0x82, 0x290000, 0x170000),
)
EXPECTED_PROPERTIES = {
    "build.fqbn": FQBN, "build.mcu": "esp32s3", "build.board": "ESP32S3_DEV",
    "build.flash_size": "16MB", "build.flash_mode": "dio", "build.boot": "qio",
    "build.flash_freq": "80m", "build.img_freq": "80m", "build.boot_freq": "80m",
    "build.partitions": "", "build.memory_type": "qio_qspi", "build.defines": "",
    "build.f_cpu": "240000000L", "build.usb_mode": "0", "build.cdc_on_boot": "1",
    "build.msc_on_boot": "0", "build.dfu_on_boot": "0", "build.bootloader_addr": "0x0",
    "upload.maximum_size": str(APP_BYTES),
}


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def partition_tool(core_dir):
    """Use the installed, pinned Espressif tool rather than a second CSV parser."""
    core_dir = Path(core_dir)
    platform = dict(line.split("=", 1) for line in
                    (core_dir / "platform.txt").read_text().splitlines()
                    if "=" in line and not line.startswith("#"))
    require(platform.get("version") == CORE_VERSION,
            "ESP32 core must be {}, found {}".format(CORE_VERSION, platform.get("version")))
    spec = importlib.util.spec_from_file_location(
        "evilduck_partition_tool", core_dir / "tools/gen_esp32part.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.offset_part_table = 0x8000
    return module


def check_table(table, expected=LAYOUT):
    table.verify()  # Espressif's overlap, alignment, name and subtype checks.
    actual = tuple((p.name, p.type, p.subtype, p.offset, p.size) for p in table)
    require(actual == expected, "Partition map differs from the reviewed layout: {}".format(actual))
    require(all(not p.encrypted and not p.readonly for p in table),
            "Unexpected partition flags")
    require(max(p.offset + p.size for p in table) <= FLASH_BYTES,
            "Partition end exceeds 16 MiB")
    return table


def validate_csv(core_dir, path=ROOT / "EvilDuckS3/partitions.csv"):
    tool = partition_tool(core_dir)
    table = check_table(tool.PartitionTable.from_csv(Path(path).read_text()))
    # Exercise binary serialization and its MD5 check as well.
    binary = table.to_binary()
    check_table(tool.PartitionTable.from_binary(binary))
    return binary


def validate_properties(properties):
    for key, value in EXPECTED_PROPERTIES.items():
        require(properties.get(key) == value,
                "{} must be {!r}, found {!r}".format(key, value, properties.get(key)))
    # The standard Arduino recipes must still target the reviewed app0 address.
    for key in ("tools.esptool_py.upload.pattern_args",
                "recipe.hooks.objcopy.postobjcopy.3.pattern_args"):
        recipe = properties.get(key, "")
        require(re.search(r'0x10000\s+"[^"\n]+\.bin"', recipe) is not None,
                "{} does not place the application at 0x10000".format(key))


def validate_image(path, app=True):
    path = Path(path)
    size = path.stat().st_size
    require(24 <= size <= (APP_BYTES if app else 0x8000),
            "{} size {} exceeds its region or is truncated".format(path.name, size))
    with path.open("rb") as source:
        header = source.read(24)
    require(header[0] == 0xE9 and 1 <= header[1] <= 16, "Invalid ESP image header")
    require(header[2] == 2, "Expected DIO image field for Arduino's QIO boot configuration")
    require(header[3] >> 4 == 4, "Image must advertise 16 MiB, not the old 4 MiB")
    require(header[3] & 15 == 15, "Image must advertise 80 MHz flash")
    require(struct.unpack_from("<H", header, 12)[0] == 9, "Image must target ESP32-S3")
    return size


def validate_build(core_dir, build_dir):
    """Cross-check saved properties, generated partitions and merged-image offsets."""
    build_dir = Path(build_dir)
    validate_properties(json.loads((build_dir / "s3-build-properties.json").read_text()))
    options = json.loads((build_dir / "build.options.json").read_text())
    require(options["fqbn"] == FQBN, "Build options do not use the pinned FQBN")
    require("upload.maximum_size={}".format(APP_BYTES) in options["customBuildProperties"],
            "Build options lack the application-slot size override")
    tool = partition_tool(core_dir)
    expected = validate_csv(core_dir)
    generated = validate_csv(core_dir, build_dir / "partitions.csv")
    require(expected == generated, "Build did not use the repository partition table")
    partition_bin = build_dir / "EvilDuckS3.ino.partitions.bin"
    check_table(tool.PartitionTable.from_binary(partition_bin.read_bytes()))
    require(partition_bin.read_bytes() == expected, "Generated partition binary differs")
    app = build_dir / "EvilDuckS3.ino.bin"
    boot = build_dir / "EvilDuckS3.ino.bootloader.bin"
    size = validate_image(app)
    validate_image(boot, app=False)
    merged = build_dir / "EvilDuckS3.ino.merged.bin"
    require(merged.stat().st_size == FLASH_BYTES, "Merged image does not span 16 MiB")
    with merged.open("rb") as source:
        for offset, image in ((0, boot), (0x8000, partition_bin),
                              (0xE000, Path(core_dir) / "tools/partitions/boot_app0.bin"),
                              (APP_OFFSET, app)):
            source.seek(offset)
            require(source.read(image.stat().st_size) == image.read_bytes(),
                    "Merged image mismatch at {}".format(hex(offset)))
    return {"core_version": CORE_VERSION, "fqbn": FQBN,
            "application_address": APP_OFFSET, "flash_bytes": FLASH_BYTES,
            "application_bytes": size, "ota_slot_bytes": APP_BYTES,
            "free_bytes_per_slot": APP_BYTES - size,
            "free_percent_per_slot": 100 * (APP_BYTES - size) / APP_BYTES,
            "application_sha256": hashlib.sha256(app.read_bytes()).hexdigest(),
            "hardware_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-dir", required=True, type=Path)
    parser.add_argument("--build-dir", type=Path,
                        help="Also validate artifacts from tools/build_s3.py")
    args = parser.parse_args()
    validate_csv(args.core_dir)
    if args.build_dir:
        print(json.dumps(validate_build(args.core_dir, args.build_dir), indent=2))
    print("PASS: approved partition layout" + (" and 16 MiB build" if args.build_dir else ""))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError) as error:
        sys.exit("FAIL: {}".format(error))
