#!/usr/bin/env python3
"""Portable shared-engine checks only; no macOS APIs or hardware operations."""
import argparse
import json
import os
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    args.build_dir.mkdir(parents=True, exist_ok=False)
    executable = args.build_dir / "engine-tests"
    compiler = os.environ.get("CC", "cc")
    command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               "-g", "-fno-omit-frame-pointer", "-fsanitize=address,undefined",
               "-I" + str(ROOT / "host_tests/led_return/mac_fixed_message"),
               str(ROOT / "host_tests/led_return/mac_fixed_message/engine.c"),
               str(ROOT / "tests/mac_fixed_message/test_engine.c"), "-o", str(executable)]
    subprocess.run(command, check=True)
    environment = dict(os.environ, ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
                       UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
    completed = subprocess.run([str(executable)], env=environment, text=True,
                               capture_output=True, timeout=60)
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    if completed.returncode:
        sys.stdout.write(completed.stdout)
        return completed.returncode
    result = json.loads(completed.stdout)
    result.update(command=command, sanitizers="ASan/UBSan/leak detection",
                  native_apple_compilation="PENDING_OWNER", physical_device="NOT_ACCESSED")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
