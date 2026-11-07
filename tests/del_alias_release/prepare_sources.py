"""Pinned DEL alias release identity over the complete reviewed composition."""
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
BUILD_ID = 'ROUTEB-DEL-ALIAS-H1-v1'
PARENT = ROOT / 'tests/del_alias/prepare_sources.py'
PARENT_SHA = 'b22f11518d099fb137b242642d116193158549ef6d3e729e71d82deb91c34906'
MANIFEST_SHA = '78fcc150bc4d259db1f1023f218ca5b221129a77f1f0d9fe4c312a057226d610'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pin():
    assert digest(HERE / 'source-manifest.json') == MANIFEST_SHA, 'DEL_RELEASE_MANIFEST_CHANGED'
    value = json.loads((HERE / 'source-manifest.json').read_text())
    assert value['format'] == 'evilduck-del-alias-release-v1'
    assert value['build_id'] == BUILD_ID and value['comparison_base'] == 'privacy-fix1'
    assert value['parent_prepare_sha256'] == PARENT_SHA == digest(PARENT), 'DEL_RELEASE_PARENT_CHANGED'
    assert value['parent_manifest_sha256'] == digest(PARENT.with_name('source-manifest.json'))
    assert value['patch_sha256'] == digest(HERE / 'identity.patch')
    assert value['del_patch_sha256'] == digest(PARENT.with_name('application.patch'))
    assert value['repeat_manifest_sha256'] == digest(ROOT / 'tests/previous_command_repeat_release/source-manifest.json')
    assert value['static_manifest_sha256'] == digest(ROOT / 'tests/static_response_build_integration/source-manifest.json')
    assert value['privacy_manifest_sha256'] == digest(ROOT / 'tests/privacy_fix1/source-manifest.json')
    assert len(value['after']) == len(value['before']) == 5 and len(value['unchanged']) == 196
    assert {r['file'] for r in value['after']} == {'core.cpp', 'shortcut_keys.h', 'webfiles.h', 'webserver.cpp', 'caps_trial.h'}
    assert len(value['cumulative_h1_after']) == 6 and value['source_count'] == 201
    return value


pin()
spec = importlib.util.spec_from_file_location('del_release_complete_source_parent', PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load


def inventory(source):
    return B.inventory(source)


def verify_final(source):
    source = pathlib.Path(source)
    value = pin()
    expected = {r['file']: r['sha256'] for r in value['after'] + value['unchanged']}
    assert len(expected) == 201 and inventory(source) == expected, 'DEL_RELEASE_COMPOSITION_MISSING_OR_CHANGED'
    assert (source / 'caps_trial.h').read_bytes().count(BUILD_ID.encode()) == 1
    return [dict(file='EvilDuckS3/' + n, size=(source / n).stat().st_size,
                 sha256=expected[n]) for n in sorted(expected)]


def delta(source):
    source = pathlib.Path(source)
    pin()
    B.verify_final(source)
    before = (source / 'caps_trial.h').read_bytes()
    result = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch',
                             '-p0', '-i', str(HERE / 'identity.patch')], cwd=source,
                            capture_output=True, text=True, check=True)
    assert 'fuzz' not in result.stdout.lower() and 'offset' not in result.stdout.lower()
    assert (source / 'caps_trial.h').read_bytes() == before.replace(
        b'ROUTEB-PREVIOUS-COMMAND-REPEAT-v1', BUILD_ID.encode(), 1)
    verify_final(source)
    return source


def overlay(source):
    pin()
    B.overlay(source)
    return delta(source)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-composed', type=pathlib.Path, required=True)
    parser.add_argument('--output-dir', type=pathlib.Path, required=True)
    args = parser.parse_args()
    B.verify_final(args.from_composed)
    assert not args.output_dir.exists() and not args.output_dir.is_symlink(), 'OUTPUT_ALREADY_EXISTS'
    for ancestor in (ROOT, args.from_composed):
        assert not args.output_dir.resolve().is_relative_to(ancestor.resolve()), 'OUTPUT_INSIDE_INPUT'
    args.output_dir.mkdir(parents=True)
    destination = args.output_dir / 'EvilDuckS3'
    shutil.copytree(args.from_composed, destination)
    delta(destination)
    rows = verify_final(destination)
    value = dict(status='SOURCE_ONLY_COMPOSED', source=str(destination), source_count=len(rows), sources=rows,
                 selected_preparer='tests/del_alias_release/prepare_sources.py', build_id=BUILD_ID,
                 firmware_built=False, hardware_access=False)
    (args.output_dir / 'composition.json').write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({k: v for k, v in value.items() if k != 'sources'}, indent=2))


if __name__ == '__main__':
    main()
