"""Pinned additive bounded lock-wait layer; historical layers unchanged."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA = '564973d10eedba72e4fc36f44c0c009d2a2dce3a1a6b709a538df8d5fe8324f3'
p = ROOT/'tests/source_text_v2/prepare_sources.py'
assert hashlib.sha256(p.read_bytes()).hexdigest() == PARENT_SHA
s = importlib.util.spec_from_file_location('bounded_lock_timeout_parent_prepare', p)
B = importlib.util.module_from_spec(s); s.loader.exec_module(B)
prepare, native_sources, manifest, frameworks, sha, load = B.prepare, B.native_sources, B.manifest, B.frameworks, B.sha, B.load

def delta(source):
    source = pathlib.Path(source)
    pin = json.loads((ROOT/'tests/lock_wait_timeout/source-manifest.json').read_text())
    patch = ROOT/'tests/lock_wait_timeout/application.patch'
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
