"""Default release composition: reviewed editor overlay, then identity only."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD_ID = 'ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
BASE_COMMIT = '805d989c3ac50cb96025862c95916830c59f8ba7'
EDITOR_HEADER_SHA = 'df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445'
PARENT = ROOT / 'tests/editor_load_safety/prepare_sources.py'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pin():
    value = json.loads((ROOT / 'tests/editor_build_integration/source-manifest.json').read_text())
    assert value['format'] == 'evilduck-editor-build-integration-v1' and value['baseline'] == BASE_COMMIT
    assert value['build_id'] == BUILD_ID and value['comparison_base'] == 'privacy-fix1'
    assert value['parent_prepare_sha256'] == digest(PARENT)
    for name, key in [('privacy_fix1', 'privacy_manifest_sha256'), ('dashboard_cleanup', 'dashboard_manifest_sha256'),
                      ('editor_load_safety', 'reviewed_editor_manifest_sha256')]:
        assert digest(ROOT / 'tests' / name / 'source-manifest.json') == value[key], key
    for layer in value['ordered_layers']:
        assert digest(ROOT / layer['patch']) == layer['patch_sha256'], layer['layer']
    assert digest(ROOT / 'tests/editor_build_integration/identity.patch') == value['patch_sha256']
    assert len(value['after']) == 2 and len(value['unchanged']) == 199
    return value


_initial_pin = pin()
spec = importlib.util.spec_from_file_location('editor_build_reviewed_parent', PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load


def verify_final(source):
    source = pathlib.Path(source)
    value = pin()
    rows = value['after'] + value['unchanged']
    expected = {r['file']: r['sha256'] for r in rows}
    actual = {str(p.relative_to(source)): digest(p) for p in source.rglob('*') if p.is_file()}
    if actual.get('webfiles.h') != EDITOR_HEADER_SHA:
        raise AssertionError('EDITOR_SAFETY_OMITTED_OR_CHANGED: final webfiles.h is not the reviewed repaired resource')
    assert len(expected) == len(rows) == 201 and actual == expected, 'FINAL_COMPOSITION_MISMATCH'
    return [dict(file='EvilDuckS3/' + name, size=(source / name).stat().st_size, sha256=actual[name]) for name in sorted(actual)]


def delta(source):
    source = pathlib.Path(source)
    reviewed = json.loads((ROOT / 'tests/editor_load_safety/source-manifest.json').read_text())
    current = {r['file']: r['sha256'] for r in reviewed['after'] + reviewed['unchanged']}
    assert len(current) == 201
    assert all(digest(source / name) == expected for name, expected in current.items())
    before = (source / 'caps_trial.h').read_bytes()
    old, new = b'ROUTEB-DASHBOARD-CLEANUP-v1', BUILD_ID.encode()
    assert before.count(old) == 1
    subprocess.run(['patch', '--batch', '--fuzz=0', '-p0', '-i', str(ROOT / 'tests/editor_build_integration/identity.patch')],
                   cwd=source, capture_output=True, check=True)
    assert (source / 'caps_trial.h').read_bytes() == before.replace(old, new, 1), 'IDENTITY_DELTA_NOT_METADATA_ONLY'
    verify_final(source)
    return source


def overlay(source):
    # Parent explicitly chains H1 -> privacy -> dashboard -> reviewed editor once.
    B.overlay(source)
    return delta(source)
