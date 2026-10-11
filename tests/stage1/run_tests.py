#!/usr/bin/env python3
"""Build/run the actual S3 execution sources against RAM-only hardware mocks."""
import argparse
import pathlib
import subprocess
import tempfile

TESTS = [
    "supported_commands_and_mock_interfaces",
    "script_run_state_isolation",
    "cooperative_delay_and_text_cancellation",
    "repeat_timing_and_control_loop_yield",
    "live_commands_cannot_mutate_running_script",
    "documented_language_gaps",
]
ROOT = pathlib.Path(__file__).resolve().parent
FW = ROOT.parent.parent / "EvilDuckS3"


def compile_target(main, build, name):
    build.mkdir(parents=True, exist_ok=True)
    sources = [main, ROOT / "mocks/host.cpp"] + [FW / f"{module}.cpp" for module in
        ("com", "duckscript", "duck_vars", "duck_keys", "keyboard_locale", "locales", "hid_backend",
         "script_log", "cli", "script_source", "script_parser", "duck_expr", "duck_constants", "script_functions", "script_preprocessor", "duck_random")]
    exe = build / name
    subprocess.run(["g++", "-std=gnu++17", "-g", "-O1", "-Wall", "-Wextra",
        "-pthread", "-DEVILDUCK_HOST_TEST", "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
        "-fno-pie", "-no-pie", f"-I{ROOT / 'mocks'}", f"-I{FW}",
        *map(str, sources), "-o", str(exe)], check=True)
    return exe


def run_suite(exe, tests):
    failed = 0
    for name in tests:
        try:
            result = subprocess.run([str(exe), name], timeout=20)
            failed += result.returncode != 0
        except subprocess.TimeoutExpired:
            print(f"FAIL {name}: 20-second timeout", flush=True)
            failed += 1
    print(f"{len(tests)-failed}/{len(tests)} test processes succeeded; failures={failed}", flush=True)
    return failed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=pathlib.Path)
    args = parser.parse_args()
    build = args.build_dir or pathlib.Path(tempfile.mkdtemp(prefix="evilduck-stage1-"))
    exe = compile_target(ROOT / "test_main.cpp", build, "stage1_tests")
    return bool(run_suite(exe, TESTS))


if __name__ == "__main__":
    raise SystemExit(main())
