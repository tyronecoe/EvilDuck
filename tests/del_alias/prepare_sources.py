"""Pinned DEL vocabulary delta on the complete reviewed REPEAT composition.

Only core.cpp and shortcut_keys.h change. delta() accepts native fixture trees
with additional mocks; overlay()/verify_final() check every production source.
No hardware, target compiler, installer, automatic payload or network access.
"""
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
PARENT = ROOT / 'tests/previous_command_repeat_release/prepare_sources.py'
PARENT_SHA = '8a65daede7912ec39e7b5976f8c8a93f5b9cdcf55e8e1bcdea44e169bffa7259'
MANIFEST_SHA = '7da4fb08194269a15ded87faa25f878a7170537a63b54153a9d6636d6f5a2af3'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pin():
    assert digest(HERE / 'source-manifest.json') == MANIFEST_SHA, 'DEL_MANIFEST_CHANGED'
    value = json.loads((HERE / 'source-manifest.json').read_text())
    assert value['format'] == 'evilduck-del-alias-source-v1'
    assert value['parent_prepare_sha256'] == PARENT_SHA == digest(PARENT), 'DEL_PARENT_CHANGED'
    assert value['parent_manifest_sha256'] == digest(PARENT.with_name('source-manifest.json'))
    assert value['patch_sha256'] == digest(HERE / 'application.patch'), 'DEL_PATCH_CHANGED'
    assert value['source_count'] == 201 and len(value['unchanged']) == 199
    assert {r['file'] for r in value['before']} == {r['file'] for r in value['after']} == {'core.cpp', 'shortcut_keys.h'}
    return value


pin()
spec = importlib.util.spec_from_file_location('del_alias_reviewed_repeat_parent', PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load


def inventory(source):
    return B.inventory(source)


def verify_final(source):
    source = pathlib.Path(source)
    value = pin()
    expected = {r['file']: r['sha256'] for r in value['after'] + value['unchanged']}
    assert len(expected) == 201 and inventory(source) == expected, 'DEL_FINAL_COMPOSITION_MISMATCH'
    return [dict(file='EvilDuckS3/' + n, size=(source / n).stat().st_size,
                 sha256=expected[n]) for n in sorted(expected)]


def delta(source):
    source = pathlib.Path(source)
    value = pin()
    # A full target identity is checked by overlay(); native parents retain their
    # explicitly documented generated identity and add RAM-only mocks.
    for row in value['before']:
        selected = source / row['file']
        assert selected.is_file() and not selected.is_symlink()
        assert digest(selected) == row['sha256'], 'DEL_WRONG_PARENT_' + row['file']
    result = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch',
                             '-p0', '-i', str(HERE / 'application.patch')],
                            cwd=source, capture_output=True, text=True, check=True)
    assert 'fuzz' not in result.stdout.lower() and 'offset' not in result.stdout.lower(), 'DEL_PATCH_NOT_EXACT'
    for row in value['after']:
        assert digest(source / row['file']) == row['sha256'], 'DEL_WRONG_RESULT_' + row['file']
    return source


def overlay(source):
    pin()
    B.overlay(source)
    B.verify_final(source)
    delta(source)
    verify_final(source)
    return source


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
    proof = dict(status='SOURCE_ONLY_COMPOSED', source=str(destination), source_count=len(rows), sources=rows,
                 selected_preparer='tests/del_alias/prepare_sources.py',
                 selected_manifest_sha256=digest(HERE / 'source-manifest.json'),
                 changed_sources=['core.cpp', 'shortcut_keys.h'], unchanged_sources=199,
                 firmware_built=False, hardware_access=False)
    (args.output_dir / 'composition.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k != 'sources'}, indent=2))


if __name__ == '__main__':
    main()
