"""Pinned dashboard-only layer over the complete Privacy Fix 1 composition."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA = "0bb594377dd1964926dcefbfb2e746251cdd908434bc6eba4eeb6624a2ba1dca"
BUILD_ID = "ROUTEB-DASHBOARD-CLEANUP-v1"
OLD_BUILD_ID = "ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1"
parent = ROOT / "tests/privacy_fix1/prepare_sources.py"
assert hashlib.sha256(parent.read_bytes()).hexdigest() == PARENT_SHA
spec = importlib.util.spec_from_file_location("dashboard_privacy_parent", parent)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources = B.prepare, B.native_sources
sha, frameworks, manifest, load = B.sha, B.frameworks, B.manifest, B.load


def delta(source):
    source = pathlib.Path(source)
    pin = json.loads((ROOT / "tests/dashboard_cleanup/source-manifest.json").read_text())
    assert pin["format"] == "evilduck-dashboard-cleanup-v1"
    assert pin["baseline"] == "70d08e9f789c187c5e27350a66f4d0d52992964b"
    assert pin["parent_prepare_sha256"] == PARENT_SHA
    assert pin["privacy_manifest_sha256"] == sha(ROOT / "tests/privacy_fix1/source-manifest.json")
    assert pin["baseline_inventory_sha256"] == sha(ROOT / "docs/h1-right-modifiers-build.json")
    assert pin["build_id"] == BUILD_ID
    patch = ROOT / "tests/dashboard_cleanup/application.patch"
    assert sha(patch) == pin["patch_sha256"]
    assert len(pin["before"]) == len(pin["after"]) == 2 and len(pin["unchanged"]) == 199
    assert {r["file"] for r in pin["before"]} == {r["file"] for r in pin["after"]} == {"webfiles.h", "caps_trial.h"}
    for row in pin["before"] + pin["unchanged"]:
        assert sha(source / row["file"]) == row["sha256"], row["file"]
    before_caps = (source / "caps_trial.h").read_bytes()
    old, new = OLD_BUILD_ID.encode(), BUILD_ID.encode()
    assert before_caps.count(old) == 1
    subprocess.run(["patch", "--batch", "--fuzz=0", "-p0", "-i", str(patch)],
                   cwd=source, check=True, capture_output=True)
    for row in pin["after"] + pin["unchanged"]:
        assert sha(source / row["file"]) == row["sha256"], row["file"]
    assert (source / "caps_trial.h").read_bytes() == before_caps.replace(old, new, 1), "Build ID header changed beyond identity"
    return source


def overlay(source):
    # Privacy's overlay already composes H1; never invoke H1 separately here.
    B.overlay(source)
    return delta(source)
