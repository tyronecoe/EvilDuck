"""Source-only streaming static responses over the exact verified editor build.

No target compiler, package, device, upload or network interface. The normal
historical builder remains unchanged and does not automatically select this fix.
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
HERE = ROOT / 'tests/dashboard_response_safety'
DEFAULT_SDK_ROOT = ROOT.parent
BASE_COMMIT = 'e692435a7c70dbc0d917bbff733c57900cf7d57c'
MANIFEST_SHA = 'd2d4be0a8265a4a198bab2af8afa5d2148f412ce242c3168e0369876f3a447fa'
PARENT_SHA = '51a527fdc0a8f149c5b6c2e8baa414ceb177fdb13fce1e3680581d63c8db6397'
PARENT_MANIFEST_SHA = '0e0e12436952ea3e4e688259623bd76814d506ac59a9a0211617b14cc2d7a898'
PARENT = ROOT / 'tests/editor_build_integration/prepare_sources.py'
PARENT_MANIFEST = ROOT / 'tests/editor_build_integration/source-manifest.json'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def pin_sources():
    manifest_path = HERE / 'source-manifest.json'
    assert digest(manifest_path) == MANIFEST_SHA, 'SOURCE_MANIFEST_PIN_MISMATCH'
    value = json.loads(manifest_path.read_text())
    assert value['format'] == 'evilduck-dashboard-static-response-source-only-v1'
    assert value['baseline'] == BASE_COMMIT
    assert value['parent_prepare_sha256'] == PARENT_SHA == digest(PARENT), 'PARENT_PREPARER_PIN_MISMATCH'
    assert value['parent_manifest_sha256'] == PARENT_MANIFEST_SHA == digest(PARENT_MANIFEST), 'PARENT_MANIFEST_PIN_MISMATCH'
    assert value['patch_sha256'] == digest(HERE / 'application.patch'), 'PATCH_PIN_MISMATCH'
    assert value['source_count'] == 201 and len(value['unchanged']) == 200
    assert len(value['before']) == len(value['after']) == 1
    assert value['before'][0]['file'] == value['after'][0]['file'] == 'webserver.cpp'
    assert len(value['sdk_pins']) == 6
    assert value['portable_url_aliases'] == 12 and value['distinct_literals'] == 9
    assert value['static_send_replacements'] == 11
    return value


def pin(sdk_root=DEFAULT_SDK_ROOT):
    value = pin_sources()
    sdk_root = pathlib.Path(sdk_root)
    for name, expected in value['sdk_pins'].items():
        path = sdk_root / name
        assert path.is_file() and not path.is_symlink(), 'SDK_PIN_MISSING: ' + name
        assert digest(path) == expected, 'SDK_PIN_MISMATCH: ' + name
    return value


_initial_pin = pin_sources()
spec = importlib.util.spec_from_file_location('dashboard_response_editor_parent', PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load


def inventory(source):
    source = pathlib.Path(source)
    assert source.is_dir() and not source.is_symlink(), 'SOURCE_DIRECTORY_INVALID'
    rows = {}
    for path in source.rglob('*'):
        assert not path.is_symlink(), 'SOURCE_SYMLINK_REJECTED: ' + str(path)
        if path.is_file():
            rows[str(path.relative_to(source))] = digest(path)
        else:
            assert path.is_dir(), 'SOURCE_NONREGULAR_ENTRY: ' + str(path)
    return rows


def expected_inventory(value, final):
    rows = value['after' if final else 'before'] + value['unchanged']
    result = {row['file']: row['sha256'] for row in rows}
    assert len(rows) == len(result) == 201, 'SOURCE_INVENTORY_DUPLICATE_OR_MISSING'
    return result


def verify_final(source, sdk_root=DEFAULT_SDK_ROOT):
    source = pathlib.Path(source)
    value = pin(sdk_root)
    actual = inventory(source)
    assert actual == expected_inventory(value, True), 'FINAL_COMPOSITION_MISMATCH'
    return [dict(file='EvilDuckS3/' + name, size=(source / name).stat().st_size,
                 sha256=actual[name]) for name in sorted(actual)]


def delta(source, sdk_root=DEFAULT_SDK_ROOT):
    source = pathlib.Path(source)
    value = pin(sdk_root)
    assert inventory(source) == expected_inventory(value, False), 'WRONG_VERIFIED_EDITOR_BASE'
    B.verify_final(source)
    result = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch',
                             '-p0', '-i', str(HERE / 'application.patch')],
                            cwd=source, capture_output=True, text=True, check=True)
    assert 'fuzz' not in result.stdout.lower() and 'offset' not in result.stdout.lower(), 'PATCH_NOT_EXACT'
    verify_final(source, sdk_root)
    return source


def overlay(source, sdk_root=DEFAULT_SDK_ROOT):
    # Pin before any parent changes. The parent retains its full H1/privacy/
    # dashboard/editor/identity stack and existing dependency/build guard APIs.
    pin(sdk_root)
    B.overlay(source)
    return delta(source, sdk_root)


def contained(path, parent):
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-composed', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    parser.add_argument('--sdk-root', type=pathlib.Path, default=DEFAULT_SDK_ROOT,
                        help='Root containing the exact pinned workspace SDK paths; no fallback')
    args = parser.parse_args()
    value = pin(args.sdk_root)
    assert not args.output.exists() and not args.output.is_symlink(), 'OUTPUT_ALREADY_EXISTS'
    assert not contained(args.output, ROOT), 'OUTPUT_INSIDE_REPOSITORY_REJECTED'
    assert not contained(args.output, args.from_composed), 'OUTPUT_INSIDE_SOURCE_REJECTED'
    assert inventory(args.from_composed) == expected_inventory(value, False), 'WRONG_VERIFIED_EDITOR_BASE'
    B.verify_final(args.from_composed)
    shutil.copytree(args.from_composed, args.output)
    delta(args.output, args.sdk_root)
    print(json.dumps(dict(status='PASS', scope='SOURCE_ONLY', changed=['webserver.cpp'],
                          unchanged=200, source_count=201, sdk_pins_verified=6,
                          output=str(args.output), firmware_built=False,
                          hardware_access=False), indent=2))


if __name__ == '__main__':
    main()
