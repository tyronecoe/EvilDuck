"""Pinned additive Route B preprocessing layer; no installed source is modified."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA = 'e4ff80a9e2f422b0337c892563970a1f73572365cbfc3af75c32ba00b84e8d83'
p = ROOT/'tests/lock_feedback/prepare_sources.py'
assert hashlib.sha256(p.read_bytes()).hexdigest() == PARENT_SHA
s = importlib.util.spec_from_file_location('source_compat_lock_prepare', p)
B = importlib.util.module_from_spec(s); s.loader.exec_module(B)
prepare, native_sources, manifest, frameworks, sha, load = B.prepare, B.native_sources, B.manifest, B.frameworks, B.sha, B.load

def delta(source):
    source = pathlib.Path(source)
    pin = json.loads((ROOT/'tests/source_compat/source-manifest.json').read_text())
    patch = ROOT/'tests/source_compat/application.patch'
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
