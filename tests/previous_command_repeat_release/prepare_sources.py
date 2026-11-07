"""Pinned final identity after the complete bounded-REPEAT Route B composition."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
BUILD_ID = 'ROUTEB-PREVIOUS-COMMAND-REPEAT-v1'
PARENT = ROOT / 'tests/previous_command_repeat/prepare_sources.py'
PARENT_SHA = '677c3c950afabd9a7a8ec014416b8fe3660d460b8aab014ef598e2d177053791'
MANIFEST_SHA = '8a65bdff292d6e8a288b795a846fbd57cf135bcb1e54af063f29bef38f9d6f5b'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pin():
    assert digest(HERE / 'source-manifest.json') == MANIFEST_SHA, 'REPEAT_RELEASE_MANIFEST_CHANGED'
    value = json.loads((HERE / 'source-manifest.json').read_text())
    assert value['format'] == 'evilduck-previous-command-repeat-release-v1'
    assert value['build_id'] == BUILD_ID and value['comparison_base'] == 'privacy-fix1'
    assert value['parent_prepare_sha256'] == PARENT_SHA == digest(PARENT), 'REPEAT_RELEASE_PARENT_CHANGED'
    assert value['parent_manifest_sha256'] == digest(PARENT.with_name('source-manifest.json'))
    assert value['patch_sha256'] == digest(HERE / 'identity.patch')
    assert value['repeat_patch_sha256'] == digest(PARENT.with_name('application.patch'))
    assert value['static_manifest_sha256'] == digest(ROOT / 'tests/static_response_build_integration/source-manifest.json')
    assert value['privacy_manifest_sha256'] == digest(ROOT / 'tests/privacy_fix1/source-manifest.json')
    assert len(value['after']) == len(value['before']) == 4 and len(value['unchanged']) == 197
    assert {r['file'] for r in value['after']} == {'core.cpp', 'webfiles.h', 'webserver.cpp', 'caps_trial.h'}
    assert len(value['cumulative_h1_after']) == 5 and value['source_count'] == 201
    return value


pin()
spec = importlib.util.spec_from_file_location('release_complete_previous_repeat_parent', PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load


def inventory(source):
    return B.inventory(source)


def verify_final(source):
    source = pathlib.Path(source)
    value = pin()
    expected = {r['file']: r['sha256'] for r in value['after'] + value['unchanged']}
    assert len(expected) == 201 and inventory(source) == expected, 'REPEAT_RELEASE_COMPOSITION_MISSING_OR_CHANGED'
    assert (source / 'caps_trial.h').read_bytes().count(BUILD_ID.encode()) == 1
    return [dict(file='EvilDuckS3/' + n, size=(source / n).stat().st_size,
                 sha256=expected[n]) for n in sorted(expected)]


def delta(source):
    source = pathlib.Path(source)
    value = pin()
    B.verify_final(source)
    before = (source / 'caps_trial.h').read_bytes()
    result = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch',
                             '-p0', '-i', str(HERE / 'identity.patch')], cwd=source,
                            capture_output=True, text=True, check=True)
    assert 'fuzz' not in result.stdout.lower() and 'offset' not in result.stdout.lower()
    assert (source / 'caps_trial.h').read_bytes() == before.replace(
        b'ROUTEB-STATIC-RESPONSE-REPAIR-v1', BUILD_ID.encode(), 1)
    verify_final(source)
    return source


def overlay(source):
    pin()
    B.overlay(source)
    return delta(source)
