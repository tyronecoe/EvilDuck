"""Local source-only editor overlay over the pinned complete dashboard composition.

No compiler, package, device, upload or network interface. Historical target
builders remain unchanged and do not select this new overlay automatically.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA = '47f8c3d51347d3744f197e84b52017efe8a1d061d28a25f8ff690af138202295'
parent = ROOT / "tests/dashboard_cleanup/prepare_sources.py"
assert hashlib.sha256(parent.read_bytes()).hexdigest() == PARENT_SHA
spec = importlib.util.spec_from_file_location("editor_dashboard_parent", parent)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load


def inventory(source):
    return {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in pathlib.Path(source).rglob("*") if p.is_file()}


def delta(source):
    source = pathlib.Path(source)
    pin = json.loads((ROOT / "tests/editor_load_safety/source-manifest.json").read_text())
    assert pin["format"] == "evilduck-editor-load-safety-source-only-v1"
    assert pin["baseline"] == "805d989c3ac50cb96025862c95916830c59f8ba7"
    assert pin["parent_prepare_sha256"] == PARENT_SHA
    assert pin["parent_manifest_sha256"] == sha(ROOT / "tests/dashboard_cleanup/source-manifest.json")
    assert len(pin["before"]) == len(pin["after"]) == 1 and len(pin["unchanged"]) == 200
    assert pin["before"][0]["file"] == pin["after"][0]["file"] == "webfiles.h"
    expected = {row["file"]: row["sha256"] for row in pin["before"] + pin["unchanged"]}
    assert len(expected) == 201 and inventory(source) == expected, "Wrong complete dashboard base"
    patch = ROOT / "tests/editor_load_safety/application.patch"
    assert sha(patch) == pin["patch_sha256"]
    subprocess.run(["patch", "--batch", "--fuzz=0", "-p0", "-i", str(patch)], cwd=source,
                   check=True, capture_output=True)
    final = {row["file"]: row["sha256"] for row in pin["after"] + pin["unchanged"]}
    assert inventory(source) == final, "Wrong final editor composition"
    return source


def overlay(source):
    B.overlay(source)
    return delta(source)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-composed", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists() and not args.output.resolve().is_relative_to(ROOT)
    pin = json.loads((ROOT / "tests/editor_load_safety/source-manifest.json").read_text())
    expected = {row["file"]: row["sha256"] for row in pin["before"] + pin["unchanged"]}
    assert inventory(args.from_composed) == expected, "Input is not the verified composed public source"
    shutil.copytree(args.from_composed, args.output)
    delta(args.output)
    print("PASS source-only editor overlay: 1 changed, 200 unchanged; no firmware generated")


if __name__ == "__main__":
    main()
