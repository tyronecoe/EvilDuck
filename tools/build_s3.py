#!/usr/bin/env python3
"""Clean, pinned 16 MiB S3 compilation only; never discover, upload or flash."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
from s3_validation import (APP_BYTES, CORE_VERSION, FQBN, ROOT, ValidationError,
                           require, validate_build, validate_csv, validate_properties)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arduino-cli", default=os.environ.get("ARDUINO_CLI", "arduino-cli"))
    parser.add_argument("--config-file", type=Path)
    parser.add_argument("--build-dir", type=Path, help="Must be empty; defaults to a temporary directory")
    parser.add_argument("--patched-core-dir", type=Path, required=True, help="Verified disposable Stage16 core; use build_s3_patched.py")
    parser.add_argument("--deployment-safe-start", action="store_true", help="Explicit quiescent first-boot profile; normal behavior otherwise")
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    require(args.jobs > 0, "--jobs must be positive")
    build = (args.build_dir or Path(tempfile.mkdtemp(prefix="evilduck-s3-16m-"))).resolve()
    require(build != ROOT and ROOT not in build.parents,
            "Build output must be outside the repository")
    require(not build.exists() or not any(build.iterdir()),
            "Build directory must be empty; choose a new directory for this clean build")
    build.mkdir(parents=True, exist_ok=True)
    cli = [args.arduino_cli]
    if args.config_file:
        cli += ["--config-file", str(args.config_file)]
    compile_args = ["compile", "--fqbn", FQBN, "--build-path", str(build),
                    "--build-property", "upload.maximum_size={}".format(APP_BYTES),
                    "--jobs", str(args.jobs)]
    # --show-properties computes configuration without port discovery or uploading.
    resolved = subprocess.run(cli + compile_args + ["--show-properties=expanded", str(ROOT / "EvilDuckS3")],
                              check=True, capture_output=True, text=True)
    properties = dict(line.split("=", 1) for line in resolved.stdout.splitlines() if "=" in line)
    core = Path(properties["runtime.platform.path"]).resolve()
    from patched_core import check_sources
    require(core == args.patched_core_dir.resolve(), "CLI selected a different core; refusing unpatched fallback")
    check_sources(core, True)
    extra_flags = "-DEVILDUCK_VERIFIED_HID_ROUTING=1 -DEVILDUCK_VERIFIED_NVS_PRESERVATION=1"
    if args.deployment_safe_start:
        extra_flags += " -DEVILDUCK_DEPLOYMENT_SAFE_START=1"
    compile_args += ["--build-property", "compiler.cpp.extra_flags=" + extra_flags]
    validate_csv(core)  # Also rejects any active core other than 3.3.0.
    validate_properties(properties)
    print("Pinned ESP32 core {}: {}".format(CORE_VERSION, core), flush=True)
    print("FQBN: {}\nBuild output: {}".format(FQBN, build), flush=True)
    print("Compilation only. Hardware capacity remains UNVERIFIED.", flush=True)
    # Keep the actual compiler output and exit status; do not claim success on failure.
    # Arduino --clean can remove build-directory files; retain the log outside
    # that directory until compilation has finished.
    with tempfile.TemporaryFile(mode="w+t") as log:
        process = subprocess.Popen(cli + compile_args + ["--clean", str(ROOT / "EvilDuckS3")],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
        status = process.wait()
        log.seek(0)
        compiler_output = log.read()
    (build / "s3-build.log").write_text(compiler_output)
    require(status == 0, "Arduino compilation failed with exit status {} (see s3-build.log)".format(status))
    (build / "s3-build-properties.json").write_text(json.dumps(properties, indent=2) + "\n")
    check_sources(core, True)
    report = validate_build(core, build)
    program = re.search(r"Sketch uses (\d+) bytes .*Maximum is (\d+) bytes", compiler_output)
    ram = re.search(r"Global variables use (\d+) bytes .*Maximum is (\d+) bytes", compiler_output)
    require(program and ram, "Compiler flash/RAM measurements missing from build output")
    require(int(program[2]) == APP_BYTES, "Compiler maximum differs from the OTA slot size")
    report.update(compiler_program_bytes=int(program[1]), static_ram_bytes=int(ram[1]),
                  compiler_ram_maximum_bytes=int(ram[2]), merged_image_for_migration=False,
                  deployment_safe_start=args.deployment_safe_start, verified_cpp_extra_flags=extra_flags)
    (build / "s3-build-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print("PASS: clean 16 MiB build. Application-only .bin is for OTA AFTER authorized migration.")
    print("Do not upload to an unverified or unmigrated device. Never use the padded merged image for migration.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit("FAIL: {}\n{}".format(error, error.stderr or ""))
    except (RuntimeError, OSError, ValueError, KeyError) as error:
        sys.exit("FAIL: {}".format(error))
