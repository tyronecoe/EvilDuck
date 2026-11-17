"""Exact merged DEFINE overlay, then one identity literal, over admission201."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
BUILD_ID = 'ROUTEB-DEFINE-STATEMENTS-H1-v1'
OLD_BUILD_ID = 'ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1'
CORE_SHA = 'b9c53bd3632e049e674ea66bf6c110bf22bb51c35f0d46ae75e0f5825d069d99'
MANIFEST_SHA = '63fc26c0397097864e11827cc5767216c0ba2ce0c3f62f1380c12993f3e39200'


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load(ROOT / 'tests/define_statements/prepare_sources.py', 'release_define_overlay')
A, FEATURE = B.parent()
prepare, native_sources, frameworks, manifest = A.prepare, A.native_sources, A.frameworks, A.manifest
inventory = A.inventory


def pin():
    assert sha(HERE / 'source-manifest.json') == MANIFEST_SHA, 'DEFINE release pin changed'
    value = json.loads((HERE / 'source-manifest.json').read_text())
    assert value['format'] == 'evilduck-routeb-define-statements-release-v1'
    assert value['build_id'] == BUILD_ID and value['source_count'] == 201
    assert value['define_prepare_sha256'] == sha(ROOT / 'tests/define_statements/prepare_sources.py')
    assert value['define_manifest_sha256'] == sha(ROOT / 'tests/define_statements/source-manifest.json')
    assert value['admission_release_manifest_sha256'] == sha(ROOT / 'tests/admission_diagnostics_release/source-manifest.json')
    assert value['patch_sha256'] == sha(HERE / 'identity.patch')
    assert FEATURE['after_core_sha256'] == CORE_SHA
    old = {r['file']: r['sha256'] for r in A.pin()['after'] + A.pin()['unchanged']}
    final = {r['file']: r['sha256'] for r in value['after'] + value['unchanged']}
    assert len(final) == len(old) == 201 and set(final) == set(old)
    assert {n for n in old if old[n] != final[n]} == {'core.cpp', 'caps_trial.h'}
    assert final['core.cpp'] == CORE_SHA
    assert value['identity_before_sha256'] == old['caps_trial.h']
    assert value['identity_after_sha256'] == final['caps_trial.h']
    return value


def verify_final(source):
    source = pathlib.Path(source)
    value = pin()
    expected = {r['file']: r['sha256'] for r in value['after'] + value['unchanged']}
    assert inventory(source) == expected, 'DEFINE_RELEASE_COMPOSITION_MISMATCH'
    caps = (source / 'caps_trial.h').read_bytes()
    assert caps.count(BUILD_ID.encode()) == 1 and OLD_BUILD_ID.encode() not in caps
    assert hashlib.sha256(caps.replace(BUILD_ID.encode(), OLD_BUILD_ID.encode(), 1)).hexdigest() == value['identity_before_sha256']
    return [dict(file='EvilDuckS3/' + n, size=(source / n).stat().st_size, sha256=expected[n]) for n in sorted(expected)]


def delta(source):
    source = pathlib.Path(source)
    value = pin()
    B.verify_final(source)
    before = (source / 'caps_trial.h').read_bytes()
    assert sha(source / 'caps_trial.h') == value['identity_before_sha256']
    result = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch', '-p0', '-i', str(HERE / 'identity.patch')], cwd=source, capture_output=True, text=True, check=True)
    assert not any(word in (result.stdout + result.stderr).lower() for word in ['offset', 'fuzz'])
    assert (source / 'caps_trial.h').read_bytes() == before.replace(OLD_BUILD_ID.encode(), BUILD_ID.encode(), 1)
    verify_final(source)
    return source


def overlay(source):
    B.overlay(source)
    return delta(source)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-composed', type=pathlib.Path, required=True)
    parser.add_argument('--output-dir', type=pathlib.Path, required=True)
    args = parser.parse_args()
    A.verify_final(args.from_composed)
    assert not args.output_dir.exists() and not args.output_dir.is_symlink()
    for ancestor in (ROOT, args.from_composed):
        assert not args.output_dir.resolve().is_relative_to(ancestor.resolve())
    args.output_dir.mkdir(parents=True)
    source = args.output_dir / 'EvilDuckS3'
    shutil.copytree(args.from_composed, source)
    B.delta(source)
    delta(source)
    print('PASS exact201 DEFINE composition; no compiler')


pin()
if __name__ == '__main__':
    main()
