"""Source-only privacy delta over the pinned complete right-modifier H1 tree.

No historical source/preparer is edited. No build, package or upload entry point.
"""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA = "17c5f6d7d640800985a3969d265f8249249eb63ab9e6fd3a6955e319fee33f40"
parent = ROOT / "tests/h1_right_modifiers/prepare_sources.py"
assert hashlib.sha256(parent.read_bytes()).hexdigest() == PARENT_SHA
spec = importlib.util.spec_from_file_location("privacy_fix1_parent", parent)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources = B.prepare, B.native_sources


def delta(source, *, native=False):
    source = pathlib.Path(source)
    pin = json.loads((ROOT / "tests/privacy_fix1/source-manifest.json").read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert pin["parent_prepare_sha256"] == PARENT_SHA
    assert sha(ROOT / "docs/h1-right-modifiers-build.json") == pin["baseline_inventory_sha256"]
    patch = ROOT / "tests/privacy_fix1/application.patch"
    assert sha(patch) == pin["patch_sha256"]
    # Native preparation has explicit historical platform/header substitutions.
    # Validate all target files by default; only the 3 touched files in native mode.
    for row in pin["before"] + ([] if native else pin["unchanged"]):
        assert sha(source / row["file"]) == row["sha256"], row["file"]
    subprocess.run(["patch", "--batch", "--fuzz=0", "-p0", "-i", str(patch)],
                   cwd=source, check=True, capture_output=True)
    for row in pin["after"] + ([] if native else pin["unchanged"]):
        assert sha(source / row["file"]) == row["sha256"], row["file"]
    return source


def overlay(source):
    B.overlay(source)
    return delta(source)
