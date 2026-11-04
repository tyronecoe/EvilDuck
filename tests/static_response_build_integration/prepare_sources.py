"""Default target composition: exact reviewed static streaming repair + identity.

No owner data, installer or hardware interface. All historical layers are pinned.
"""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/static_response_build_integration'
BUILD_ID = 'ROUTEB-STATIC-RESPONSE-REPAIR-v1'
MANIFEST_SHA = 'fd5d434764f223fd3925d645ce203c09a4a887d2672ef9b8ae9c877eb90b3d9f'
PARENT = ROOT / 'tests/dashboard_response_safety/prepare_sources.py'
PARENT_SHA = 'efe6979e6d63238fdb3eb5fa6836e47bf43c350d9bc5f17db3bcd82b1eca44a1'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pin():
    assert digest(HERE / 'source-manifest.json') == MANIFEST_SHA
    value = json.loads((HERE / 'source-manifest.json').read_text())
    assert value['format'] == 'evilduck-static-response-build-integration-v1'
    assert value['build_id'] == BUILD_ID and value['comparison_base'] == 'privacy-fix1'
    assert value['parent_prepare_sha256'] == PARENT_SHA == digest(PARENT)
    for name, key in [('dashboard_response_safety', 'parent_manifest_sha256'),
                      ('editor_build_integration', 'editor_manifest_sha256'),
                      ('editor_load_safety', 'reviewed_editor_manifest_sha256'),
                      ('dashboard_cleanup', 'dashboard_manifest_sha256'),
                      ('privacy_fix1', 'privacy_manifest_sha256')]:
        assert digest(ROOT / 'tests' / name / 'source-manifest.json') == value[key], key
    assert digest(HERE / 'identity.patch') == value['patch_sha256']
    assert digest(ROOT / 'tests/dashboard_response_safety/application.patch') == value['repair_patch_sha256']
    assert len(value['after']) == 3 and len(value['unchanged']) == 198
    return value


_pin = pin()
spec = importlib.util.spec_from_file_location('streaming_repair_reviewed_parent', PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load


def verify_final(source):
    source = pathlib.Path(source)
    value = pin()
    expected = {r['file']: r['sha256'] for r in value['after'] + value['unchanged']}
    actual = B.inventory(source)
    assert len(expected) == 201 and actual == expected, 'STATIC_RESPONSE_OR_EDITOR_OMITTED_OR_CHANGED'
    assert (source / 'caps_trial.h').read_bytes().count(BUILD_ID.encode()) == 1
    return [dict(file='EvilDuckS3/' + n, size=(source / n).stat().st_size, sha256=actual[n]) for n in sorted(actual)]


def delta(source):
    source = pathlib.Path(source)
    B.verify_final(source)
    before = (source / 'caps_trial.h').read_bytes()
    old = b'ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
    assert before.count(old) == 1
    result = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch', '-p0',
                             '-i', str(HERE / 'identity.patch')], cwd=source, capture_output=True,
                            text=True, check=True)
    assert 'offset' not in result.stdout.lower() and 'fuzz' not in result.stdout.lower()
    assert (source / 'caps_trial.h').read_bytes() == before.replace(old, BUILD_ID.encode(), 1)
    verify_final(source)
    return source


def overlay(source):
    B.overlay(source)
    return delta(source)
