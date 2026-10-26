"""Pinned additive Route B uppercase randomization layer; no installed source is modified."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA = 'f38a2d9fa7d17122aa8c6803cd964fab1ad94525e54664c31166b4f5b9ea690f'
p = ROOT/'tests/randomization_jitter/prepare_sources.py'
assert hashlib.sha256(p.read_bytes()).hexdigest() == PARENT_SHA
s = importlib.util.spec_from_file_location('source_compat_lock_prepare', p)
B = importlib.util.module_from_spec(s); s.loader.exec_module(B)
prepare, native_sources, manifest, frameworks, sha, load = B.prepare, B.native_sources, B.manifest, B.frameworks, B.sha, B.load

def delta(source):
    source = pathlib.Path(source)
    pin = json.loads((ROOT/'tests/text_keyboard/source-manifest.json').read_text())
    patch = ROOT/'tests/text_keyboard/application.patch'
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
