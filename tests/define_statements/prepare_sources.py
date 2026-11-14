"""Additive core-only DEFINE statement overlay; no firmware build entry point."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def parent():
    pin = json.loads((HERE/'source-manifest.json').read_text())
    path = ROOT/'tests/admission_diagnostics_release/prepare_sources.py'
    assert sha(path) == pin['parent_prepare_sha256']
    assert sha(path.with_name('source-manifest.json')) == pin['parent_manifest_sha256']
    assert sha(HERE/'application.patch') == pin['patch_sha256']
    spec = importlib.util.spec_from_file_location('define_statements_parent', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, pin

def delta(source):
    source = pathlib.Path(source)
    _, pin = parent()
    assert sha(source/'core.cpp') == pin['before_core_sha256']
    result = subprocess.run(['patch','--batch','--fuzz=0','--no-backup-if-mismatch','-p0','-i',str(HERE/'application.patch')], cwd=source, check=True, capture_output=True, text=True)
    assert 'offset' not in result.stdout and 'fuzz' not in result.stdout
    assert sha(source/'core.cpp') == pin['after_core_sha256']
    return source

def verify_final(source):
    module, pin = parent()
    expected = json.loads((ROOT/'tests/admission_diagnostics_release/source-manifest.json').read_text())
    expected = {r['file']:r['sha256'] for r in expected['after']+expected['unchanged']}
    assert expected['core.cpp'] == pin['before_core_sha256']
    expected['core.cpp'] = pin['after_core_sha256']
    assert len(expected) == pin['source_count'] == 201
    assert module.inventory(source) == expected
    return expected

def overlay(source):
    module, _ = parent()
    module.overlay(source)
    module.verify_final(source)
    delta(source)
    verify_final(source)
    return source
