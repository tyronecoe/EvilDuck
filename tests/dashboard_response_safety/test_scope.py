#!/usr/bin/env python3
"""Source composition/guard checks only; synthetic copies, no target build."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / "tests/dashboard_response_safety"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["baseline", "source", "output", "results"]:
        parser.add_argument("--" + name, type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists() and not args.results.exists()
    args.output.mkdir(parents=True)
    spec = importlib.util.spec_from_file_location("streaming_source_scope", HERE / "prepare_sources.py")
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    results, assertions = [], 0

    def check(value, message):
        nonlocal assertions
        assertions += 1
        if not value:
            raise AssertionError(message)

    def group(name, callback):
        before = assertions
        try:
            callback()
            results.append(dict(name=name, status="PASS", assertions=assertions-before))
        except Exception as error:
            results.append(dict(name=name, status="FAIL", assertions=assertions-before,
                                diagnostic=type(error).__name__ + ": " + str(error)))

    def rejected(callback, label):
        try:
            callback()
        except (AssertionError, FileNotFoundError):
            check(True, label)
        else:
            check(False, label)

    def scope():
        original, fixed = M.inventory(args.baseline), M.inventory(args.source)
        check(len(original) == len(fixed) == 201, "Composition entry count")
        check([n for n in original if original[n] != fixed[n]] == ["webserver.cpp"], "Unexpected changed files")
        old = (args.baseline / "webserver.cpp").read_text()
        new = (args.source / "webserver.cpp").read_text()
        a, z = "static void handleStatic(", "\nnamespace webserver {"
        check(old.split(a, 1)[0] == new.split(a, 1)[0], "Change before static handler")
        check(old.split(z, 1)[1] == new.split(z, 1)[1], "Change after static handler")
        check(original["webfiles.h"] == fixed["webfiles.h"], "Changed resource content")
        check("Dynamic filesystem responses disabled in Route B candidate" in new, "Lost filesystem refusal")
        check("req->send(SPIFFS, path, getContentType(path));" in new, "Changed legacy branch")
        rows = M.verify_final(args.source)
        check(len(rows) == 201, "Final verification incomplete")

    def fresh_cli():
        destination = args.output / "cli-composed"
        r = subprocess.run([sys.executable, "-B", str(HERE / "prepare_sources.py"),
                            "--from-composed", str(args.baseline), "--output", str(destination)],
                           text=True, capture_output=True)
        check(r.returncode == 0, "CLI failed: " + r.stderr)
        check(M.inventory(destination) == M.inventory(args.source), "Non-reproducible composition")
        check(not r.stderr, "Unexpected CLI stderr")
        r2 = subprocess.run([sys.executable, "-B", str(HERE / "prepare_sources.py"),
                             "--from-composed", str(args.baseline), "--output", str(destination)],
                            text=True, capture_output=True)
        check(r2.returncode != 0, "CLI overwrote old output")

    def missing_fix_and_repeated_patch():
        rejected(lambda: M.verify_final(args.baseline), "Accepted unpatched source as final")
        with tempfile.TemporaryDirectory(dir=args.output) as d:
            copied = pathlib.Path(d) / "source"
            shutil.copytree(args.source, copied)
            before = M.inventory(copied)
            rejected(lambda: M.delta(copied), "Repeated delta accepted")
            check(M.inventory(copied) == before, "Rejected repeat mutated source")

    def wrong_source():
        with tempfile.TemporaryDirectory(dir=args.output) as d:
            copied = pathlib.Path(d) / "source"
            shutil.copytree(args.baseline, copied)
            p = copied / "settings.cpp"
            p.write_bytes(p.read_bytes() + b"\n")
            before = M.inventory(copied)
            rejected(lambda: M.delta(copied), "Accepted changed unrelated settings")
            check(M.inventory(copied) == before, "Wrong-base refusal mutated source")

    def symlink():
        with tempfile.TemporaryDirectory(dir=args.output) as d:
            copied = pathlib.Path(d) / "source"
            shutil.copytree(args.baseline, copied)
            p = copied / "settings.cpp"
            p.unlink()
            p.symlink_to(args.baseline.resolve() / "settings.cpp")
            rejected(lambda: M.delta(copied), "Accepted symlink source")

    def sdk_guards():
        pin = M.pin()
        with tempfile.TemporaryDirectory(dir=args.output) as d:
            sdk = pathlib.Path(d)
            for name in pin["sdk_pins"]:
                p = sdk / name
                p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(M.DEFAULT_SDK_ROOT / name, p)
            check(M.pin(sdk) == pin, "Equivalent exact SDK was refused")
            for name in pin["sdk_pins"]:
                p = sdk / name
                original = p.read_bytes()
                p.write_bytes(original + b"\n")
                rejected(lambda: M.pin(sdk), "Accepted altered SDK: " + name)
                p.unlink()
                rejected(lambda: M.pin(sdk), "Accepted missing SDK: " + name)
                p.write_bytes(original)

    def manifest_guard():
        old_here = M.HERE
        with tempfile.TemporaryDirectory(dir=args.output) as d:
            try:
                M.HERE = pathlib.Path(d)
                data = json.loads((HERE / "source-manifest.json").read_text())
                data["source_count"] = 200
                (M.HERE / "source-manifest.json").write_text(json.dumps(data))
                rejected(M.pin_sources, "Accepted rehashed/edited manifest")
            finally:
                M.HERE = old_here

    for name, callback in [("only_static_handler_and_200_other_sources_unchanged", scope),
                           ("fresh_cli_exact_composition_and_overwrite_refusal", fresh_cli),
                           ("unpatched_final_and_double_apply_refused", missing_fix_and_repeated_patch),
                           ("wrong_source_rejected_before_patch", wrong_source),
                           ("symlink_source_rejected", symlink),
                           ("all_six_SDK_pins_reject_changed_or_missing_inputs", sdk_guards),
                           ("source_manifest_pin_rejects_edit", manifest_guard)]:
        group(name, callback)
    counts = dict(PASS=sum(r["status"] == "PASS" for r in results), FAIL=sum(r["status"] == "FAIL" for r in results))
    receipt = dict(scope="Source-only composition and fail-closed controls", counts=counts,
                   assertions=assertions, results=results,
                   overlay_sha256=hashlib.sha256((HERE / "prepare_sources.py").read_bytes()).hexdigest(),
                   firmware_build=False, hardware=False, owner_data=False, network=False)
    args.results.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return int(counts["FAIL"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
