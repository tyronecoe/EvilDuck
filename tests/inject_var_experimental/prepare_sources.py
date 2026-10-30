"""Pinned additive experimental INJECT_VAR H1 layer; historical layers unchanged."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA = '5c20e11456d16936835df2530b3e46768b4a1ac6aa910f8d4e64fd78e7d56127'
p = ROOT/'tests/lock_wait_timeout/prepare_sources.py'
assert hashlib.sha256(p.read_bytes()).hexdigest() == PARENT_SHA
s = importlib.util.spec_from_file_location('experimental_inject_h1_parent_prepare', p)
B = importlib.util.module_from_spec(s); s.loader.exec_module(B)
prepare, native_sources, manifest, frameworks, sha, load = B.prepare, B.native_sources, B.manifest, B.frameworks, B.sha, B.load

def delta(source):
    source = pathlib.Path(source)
    pin = json.loads((ROOT/'tests/inject_var_experimental/source-manifest.json').read_text())
    patch = ROOT/'tests/inject_var_experimental/application.patch'
    assert pin['parent_prepare_sha256'] == PARENT_SHA
    assert sha(patch) == pin['patch_sha256']
    for row in pin['before']:
        assert sha(source/row['file']) == row['sha256'], row['file']
    subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(patch)],cwd=source,check=True,capture_output=True)
    for row in pin['after']:
        assert sha(source/row['file']) == row['sha256'], row['file']
    return source

def overlay(source):
    B.overlay(source)
    return delta(source)
