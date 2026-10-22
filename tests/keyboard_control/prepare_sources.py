"""Exact additive keyboard-control layer on the preserved composed Caps/STOP candidate."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
_manifest = json.loads((ROOT / 'tests/keyboard_control/source-manifest.json').read_text())
_parent = ROOT / 'tests/caps_stop/prepare_sources.py'
assert hashlib.sha256(_parent.read_bytes()).hexdigest() == _manifest['parent_prepare_sha256']
_spec = importlib.util.spec_from_file_location('keyboard_control_parent_prepare', _parent)
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)
prepare = B.prepare
native_sources = B.native_sources
manifest = B.manifest
frameworks = B.frameworks
sha = B.sha
load = B.load


def delta(source):
    source = pathlib.Path(source)
    pin = json.loads((ROOT / 'tests/keyboard_control/source-manifest.json').read_text())
    patch = ROOT / 'tests/keyboard_control/application.patch'
    assert sha(patch) == pin['patch_sha256'], 'keyboard-control patch identity mismatch'
    for row in pin['before']:
        assert sha(source / row['file']) == row['sha256'], row['file']
    subprocess.run(['patch', '--batch', '--fuzz=0', '-p0', '-i', str(patch)],
                   cwd=source, check=True, capture_output=True)
    for row in pin['after']:
        assert sha(source / row['file']) == row['sha256'], row['file']
    return source


def overlay(source):
    B.overlay(source)
    return delta(source)
