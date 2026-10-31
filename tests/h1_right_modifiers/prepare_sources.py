"""Pinned additive named right-modifier layer over the opt-in H1 composition."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA = '0da0dc94b569d4a72c45b72c31d8af71267d594d238a18bb11a9941c8c7e5413'
p = ROOT/'tests/inject_var_experimental/prepare_sources.py'
assert hashlib.sha256(p.read_bytes()).hexdigest() == PARENT_SHA
s = importlib.util.spec_from_file_location('right_modifiers_h1_parent_prepare', p)
B = importlib.util.module_from_spec(s); s.loader.exec_module(B)
prepare, native_sources, manifest, frameworks, sha, load = B.prepare, B.native_sources, B.manifest, B.frameworks, B.sha, B.load

def delta(source):
    source = pathlib.Path(source)
    pin = json.loads((ROOT/'tests/h1_right_modifiers/source-manifest.json').read_text())
    patch = ROOT/'tests/h1_right_modifiers/application.patch'
    assert pin['parent_prepare_sha256'] == PARENT_SHA
    assert sha(patch) == pin['patch_sha256']
    for row in pin['before'] + pin['unchanged']:
        assert sha(source/row['file']) == row['sha256'], row['file']
    subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(patch)],cwd=source,check=True,capture_output=True)
    for row in pin['after'] + pin['unchanged']:
        assert sha(source/row['file']) == row['sha256'], row['file']
    return source

def overlay(source):
    B.overlay(source)
    return delta(source)
