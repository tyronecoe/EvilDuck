#!/usr/bin/env python3
"""Pinned, offline web/privacy regressions bound to the full new composition.

Only mocked native SDK responses and inert Linux Chromium/DOM requests run.
The historical native test's whole-tree check is adapted for the explicitly
changed compiler and inherited build identity; its SDK, response/resource and
remaining source checks are retained. No historical test or manifest is edited.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PINS = {
    "tests/dashboard_response_safety/test_native.py": "0cfc05c580b430ccea6489a4ad7b4e38fc466331165dd5766e37229688d4b78e",
    "tests/dashboard_response_safety/test_browser.py": "8d0bff34655580c40d8528b187a171b2b4401792c3f9478cfbfcfb8ef7c1d3ea",
    "tests/editor_load_safety/test_browser.py": "a5915a0b2a617f9090eab994e8a50eeeb1863d402cd2194aa9d783e0c5d617ef",
    "tests/dashboard_cleanup/test_browser.py": "3713fa15a9d5ca9fa1bfe1fbfe4fde337af1b662c67c79921efe74aa05ce6166",
}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--results", type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists() and not args.results.exists(), "Use fresh evidence paths"
    assert not args.output.resolve().is_relative_to(ROOT), "Keep evidence outside the repository"
    for name, pin in PINS.items():
        assert sha(ROOT / name) == pin, name
    preparer = ROOT / "tests/previous_command_repeat/prepare_sources.py"
    spec = importlib.util.spec_from_file_location("repeat_complete_web_composition", preparer)
    layer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(layer)
    inventory = layer.verify_final(args.source)
    assert sha(args.source / "caps_trial.h") == "e7076dec55591a3b8513d3715f3ddb0e4e96a4617d96f24b2ed2bd3a152c58b6", "Inherited build identity changed"
    source_hashes = {p.name: sha(p) for p in args.source.iterdir() if p.is_file()}
    args.output.mkdir(parents=True)

    parent = ROOT / "tests/dashboard_response_safety/test_native.py"
    text = parent.read_text()
    before = ('    for row in manifest["after"] + manifest["unchanged"]:\n'
              '        assert digest((args.source/row["file"]).read_bytes()) == row["sha256"], row["file"]\n')
    after = ('    _repeat_verify_source(args.source)\n'
             '    for row in manifest["after"] + manifest["unchanged"]:\n'
             '        if row["file"] not in {"core.cpp", "caps_trial.h"}:\n'
             '            assert digest((args.source/row["file"]).read_bytes()) == row["sha256"], row["file"]\n')
    assert text.count(before) == 1
    adapted = text.replace(before, after)
    native_stdout = io.StringIO()
    original_argv = sys.argv[:]
    native_result = args.output / "static-native.json"
    try:
        sys.argv = [str(parent), "--source", str(args.source), "--output", str(args.output / "static-native"),
                    "--results", str(native_result)]
        with contextlib.redirect_stdout(native_stdout):
            exec(compile(adapted, str(parent), "exec"),
                 {"__name__": "__main__", "__file__": str(parent),
                  "_repeat_verify_source": layer.verify_final})
    finally:
        sys.argv = original_argv
        (args.output / "static-native.stdout.txt").write_text(native_stdout.getvalue())
    native = json.loads(native_result.read_text())
    native["repeat_composition_binding"] = dict(
        source=str(args.source), preparer_sha256=sha(preparer),
        source_manifest_sha256=sha(preparer.parent / "source-manifest.json"),
        full_inventory=inventory, original_test_sha256=PINS[str(parent.relative_to(ROOT))],
        adapted_test_sha256=hashlib.sha256(adapted.encode()).hexdigest(),
        adaptation="Full new composition verification replaces old inventory expectations for core.cpp and caps_trial.h only; all other historical checks retained")
    native_result.write_text(json.dumps(native, indent=2) + "\n")

    commands = [
        ("streamed-browser", [sys.executable, "-B", str(ROOT / "tests/dashboard_response_safety/test_browser.py"),
            "--source", str(args.source), "--native-output", str(args.output / "static-native"),
            "--native-results", str(native_result), "--output", str(args.output / "streamed-browser"),
            "--results", str(args.output / "streamed-browser.json")], args.output / "streamed-browser.json"),
        ("dashboard-browser", [sys.executable, "-B", str(ROOT / "tests/dashboard_cleanup/test_browser.py"),
            "--source", str(args.source / "webfiles.h"), "--output-dir", str(args.output / "dashboard-browser")],
            args.output / "dashboard-browser/results.json"),
        ("editor-browser", [sys.executable, "-B", str(ROOT / "tests/editor_load_safety/test_browser.py"),
            "--source", str(args.source / "webfiles.h"), "--output-dir", str(args.output / "editor-browser")],
            args.output / "editor-browser/results.json"),
    ]
    groups = {"static-native": dict(counts=native["counts"], assertions=native["assertions"],
                                    receipt=str(native_result), receipt_sha256=sha(native_result), exit=0)}
    status = 0
    for label, command, receipt in commands:
        run = subprocess.run(command, capture_output=True, text=True, timeout=360)
        (args.output / (label + ".stdout.txt")).write_text(run.stdout)
        (args.output / (label + ".stderr.txt")).write_text(run.stderr)
        row = dict(command=command, exit=run.returncode, stderr=run.stderr)
        if receipt is not None and receipt.exists():
            data = json.loads(receipt.read_text())
            row.update(counts=data["counts"], assertions=data["assertions"],
                       receipt=str(receipt), receipt_sha256=sha(receipt))
        groups[label] = row
        if run.returncode or row.get("counts", {}).get("FAIL", 0):
            status = 1
    assert layer.verify_final(args.source) == inventory, "Full composition changed during tests"
    assert {p.name: sha(p) for p in args.source.iterdir() if p.is_file()} == source_hashes
    for name, pin in PINS.items():
        assert sha(ROOT / name) == pin, "Historical test changed"
    result = dict(status="PASS" if status == 0 else "FAIL", groups=groups,
                  full_inventory=inventory, source=str(args.source), source_hashes=source_hashes,
                  source_manifest_sha256=sha(preparer.parent / "source-manifest.json"),
                  test_sha256=sha(__file__), historical_test_pins=PINS,
                  native_adaptation_sha256=hashlib.sha256(adapted.encode()).hexdigest(),
                  hardware_access=False, target_build=False, external_requests=False,
                  real_hid=False, owner_credentials_used=False,
                  limitations="Component native/mock-browser checks bound to actual complete composition; not full ESP32 HTTP stack or physical High Sierra/iPhone behavior")
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(status=result["status"], groups=groups), indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
