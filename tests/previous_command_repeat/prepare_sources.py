"""Hash-pinned compiler-only delta after the complete static-response stack.

No target compiler, installer, hardware or network interface. Native fixtures
may apply delta() after their independently verified full parent composition;
overlay()/verify_final() preserve the complete 201-file target inventory.
"""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/previous_command_repeat'
PARENT = ROOT / 'tests/static_response_build_integration/prepare_sources.py'
PARENT_SHA = '0e9e4be1654770c688cd79161b47753b922992f657b9904ac381e5efa5268ef5'
PARENT_MANIFEST_SHA = 'fd5d434764f223fd3925d645ce203c09a4a887d2672ef9b8ae9c877eb90b3d9f'
MANIFEST_SHA = 'd443a622cf62ac87b18e15ecd017e69781dee597074d053effd86418bfeca120'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pin():
    assert digest(HERE / 'source-manifest.json') == MANIFEST_SHA, 'REPEAT_MANIFEST_PIN_MISMATCH'
    value = json.loads((HERE / 'source-manifest.json').read_text())
    assert value['format'] == 'evilduck-previous-command-repeat-source-only-v1'
    assert value['parent_prepare_sha256'] == PARENT_SHA == digest(PARENT), 'REPEAT_PARENT_PIN_MISMATCH'
    assert value['parent_manifest_sha256'] == PARENT_MANIFEST_SHA == digest(PARENT.with_name('source-manifest.json'))
    assert value['patch_sha256'] == digest(HERE / 'application.patch'), 'REPEAT_PATCH_PIN_MISMATCH'
    assert value['source_count'] == 201 and len(value['unchanged']) == 200
    assert len(value['before']) == len(value['after']) == 1
    assert value['before'][0]['file'] == value['after'][0]['file'] == 'core.cpp'
    return value


_initial_pin = pin()
spec = importlib.util.spec_from_file_location('previous_repeat_static_parent', PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load


def inventory(source):
    # The parent rejects symlinks and nonregular filesystem entries.
    return B.B.inventory(source)


def verify_final(source):
    source = pathlib.Path(source)
    value = pin()
    expected = {r['file']: r['sha256'] for r in value['after'] + value['unchanged']}
    assert len(expected) == 201 and inventory(source) == expected, 'REPEAT_FINAL_COMPOSITION_MISMATCH'
    return [dict(file='EvilDuckS3/' + name, size=(source / name).stat().st_size,
                 sha256=expected[name]) for name in sorted(expected)]


def delta(source):
    source = pathlib.Path(source)
    value = pin()
    # Native harnesses have extra generated mocks. Their parent pinning remains
    # authoritative; this delta still accepts only the exact original core.
    for row in value['before']:
        assert (source / row['file']).is_file() and not (source / row['file']).is_symlink()
        assert digest(source / row['file']) == row['sha256'], 'REPEAT_WRONG_PARENT_CORE'
    result = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch',
                             '-p0', '-i', str(HERE / 'application.patch')],
                            cwd=source, capture_output=True, text=True, check=True)
    assert 'fuzz' not in result.stdout.lower() and 'offset' not in result.stdout.lower(), 'REPEAT_PATCH_NOT_EXACT'
    for row in value['after']:
        assert digest(source / row['file']) == row['sha256'], 'REPEAT_FINAL_CORE_MISMATCH'
    return source


def overlay(source):
    pin()
    B.overlay(source)
    B.verify_final(source)
    delta(source)
    verify_final(source)
    return source
