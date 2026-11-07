#!/usr/bin/env python3
"""Offline regressions bound to the exact final standalone-REPEAT release tree.

Historical C++ cases, expectations, SDK/resource checks and sanitizer flags are
unchanged. Occurrence-checked adapters advance only the full target manifest and
metadata identity. Native fixtures deliberately keep their historical identities;
the complete target identity is independently checked by the release preparer.
No target compiler, device, installer, payload or external request is used.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/previous_command_repeat_release'
PREPARER = HERE / 'prepare_sources.py'
BUILD_ID = 'ROUTEB-PREVIOUS-COMMAND-REPEAT-v1'
PINS = {
    'tests/previous_command_repeat/run_tests.py':
        '31db6d039a4aa0fb8f70150e0227c5aa4996f0a3d339ca10d775de3250c3dd8d',
    'tests/previous_command_repeat/test_web_regressions.py':
        '9b6ce0a7a30595c5d96484c832725a6d8fc74c67006223ee6c8c25ccc2676ea4',
    'tests/previous_command_repeat/test_main.cpp':
        '80cd858daf73af57612f6bc356a45a537cb5ddf4f0b0e3ca089c128a879e933d',
}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def replacement(text, old, new, changes, count=1):
    assert text.count(old) == count, (old, text.count(old))
    changes.append(dict(before=old, after=new, occurrences=count))
    return text.replace(old, new)


def final_preparer(source):
    for name, expected in PINS.items():
        assert sha(ROOT / name) == expected, name
    spec = importlib.util.spec_from_file_location('repeat_release_regression_source', PREPARER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = module.verify_final(source)
    assert len(rows) == 201
    assert (pathlib.Path(source) / 'caps_trial.h').read_bytes().count(BUILD_ID.encode()) == 1
    return module, rows


def native(source, core, build_dir, output):
    layer, inventory = final_preparer(source)
    parent = ROOT / 'tests/previous_command_repeat/run_tests.py'
    text, changes = parent.read_text(), []
    # Core delta and old/new causal probes continue to use the original pinned
    # core-only preparer. Only complete final-target validation advances here.
    text = replacement(text, 'layer.verify_final(target)', 'FINAL_VERIFY(target)',
                       changes, count=4)
    old = ('text=replace(text,"\'tests/static_response_build_integration/source-manifest.json\'",'
           '"\'tests/previous_command_repeat/source-manifest.json\'")')
    new = ('text=replace(text,"\'tests/static_response_build_integration/source-manifest.json\'",'
           '"\'tests/previous_command_repeat_release/source-manifest.json\'")')
    text = replacement(text, old, new, changes)
    namespace = dict(__name__='repeat_release_native', __file__=str(parent),
                     FINAL_VERIFY=layer.verify_final)
    exec(compile(text, str(parent), 'exec'), namespace)
    argv = sys.argv
    try:
        sys.argv = [str(parent), '--core', str(core), '--build-dir', str(build_dir),
                    '--results', str(output), '--target-composed', str(source)]
        status = namespace['main']()
    finally:
        sys.argv = argv
    record = json.loads(output.read_text())
    assert record['counts'] == dict(PASS=636, FAIL=0), 'Final composed native regression failed'
    assert record['previous_command_repeat'] == dict(PASS=50, FAIL=0, assertions=2739)
    assert record['privacy_fix1'] == dict(PASS=28, FAIL=0, assertions=736)
    assert record['all_existing_composed_regressions'] == dict(PASS=558, FAIL=0, assertions=23901)
    assert record['assertions'] == 27376
    assert record['causal_controls']['counts'] == dict(PASS=2, FAIL=0)
    assert all(not row['stderr'] for row in record['results'])
    assert layer.verify_final(source) == inventory
    record['repeat_release_regression_binding'] = dict(
        wrapper_sha256=sha(__file__), original_runner_sha256=sha(parent),
        adapted_runner_sha256=hashlib.sha256(text.encode()).hexdigest(),
        source_manifest_sha256=sha(HERE / 'source-manifest.json'),
        final_source=str(source), final_build_id=BUILD_ID,
        full_source_inventory=inventory, exact_adaptations=changes,
        native_fixture_identity_policy='Historical mock identities retained; final target is independently full-manifest-bound',
        test_case_or_expectation_changes=False, sanitizer_flag_changes=False,
        target_build=False, hardware_access=False, real_hid=False)
    output.write_text(json.dumps(record, indent=2) + '\n')
    return status


def web(source, work, output):
    layer, inventory = final_preparer(source)
    parent = ROOT / 'tests/previous_command_repeat/test_web_regressions.py'
    text, changes = parent.read_text(), []
    text = replacement(text, 'ROOT / "tests/previous_command_repeat/prepare_sources.py"',
                       'ROOT / "tests/previous_command_repeat_release/prepare_sources.py"', changes)
    caps_sha = sha(source / 'caps_trial.h')
    text = replacement(text,
                       '"e7076dec55591a3b8513d3715f3ddb0e4e96a4617d96f24b2ed2bd3a152c58b6", "Inherited build identity changed"',
                       repr(caps_sha) + ', "Final release build identity changed"', changes)
    namespace = dict(__name__='repeat_release_web', __file__=str(parent))
    exec(compile(text, str(parent), 'exec'), namespace)
    argv = sys.argv
    try:
        sys.argv = [str(parent), '--source', str(source), '--output', str(work),
                    '--results', str(output)]
        status = namespace['main']()
    finally:
        sys.argv = argv
    record = json.loads(output.read_text())
    assert record['status'] == 'PASS'
    assert layer.verify_final(source) == inventory
    record['repeat_release_regression_binding'] = dict(
        wrapper_sha256=sha(__file__), original_runner_sha256=sha(parent),
        adapted_runner_sha256=hashlib.sha256(text.encode()).hexdigest(),
        source_manifest_sha256=sha(HERE / 'source-manifest.json'),
        final_build_id=BUILD_ID, full_source_inventory=inventory,
        exact_adaptations=changes, test_case_or_expectation_changes=False,
        target_build=False, hardware_access=False, real_hid=False)
    output.write_text(json.dumps(record, indent=2) + '\n')
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=pathlib.Path, required=True)
    parser.add_argument('--core', type=pathlib.Path, required=True)
    parser.add_argument('--output-dir', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    parser.add_argument('--mode', choices=['all', 'native', 'web'], default='all')
    args = parser.parse_args()
    assert not args.output_dir.exists() and not args.results.exists(), 'Use fresh evidence paths'
    assert not args.output_dir.resolve().is_relative_to(ROOT), 'Evidence belongs outside the repository'
    _, inventory = final_preparer(args.source)
    args.output_dir.mkdir(parents=True)
    groups, exit_code = {}, 0
    selected = ['native', 'web'] if args.mode == 'all' else [args.mode]
    for mode in selected:
        receipt = args.output_dir / (mode + '.json')
        work = args.output_dir / (mode + '-build')
        command = [sys.executable, '-B', str(pathlib.Path(__file__)),
                   '--child', mode, str(args.source), str(args.core), str(work), str(receipt)]
        run = subprocess.run(command, capture_output=True, text=True, timeout=1200)
        (args.output_dir / (mode + '.stdout.txt')).write_text(run.stdout)
        (args.output_dir / (mode + '.stderr.txt')).write_text(run.stderr)
        row = dict(command=command, exit=run.returncode, stderr=run.stderr)
        if receipt.exists():
            record = json.loads(receipt.read_text())
            row.update(receipt=str(receipt), receipt_sha256=sha(receipt))
            if mode == 'native':
                row.update(counts=record['counts'], assertions=record['assertions'],
                           repeat=record.get('previous_command_repeat'),
                           privacy=record.get('privacy_fix1'),
                           existing=record.get('all_existing_composed_regressions'))
            else:
                row['groups'] = record['groups']
        groups[mode] = row
        if run.returncode:
            exit_code = 1
            break
    for name, expected in PINS.items():
        assert sha(ROOT / name) == expected, 'Historical test changed: ' + name
    result = dict(status='PASS' if exit_code == 0 else 'FAIL', groups=groups,
                  wrapper_sha256=sha(__file__), source=str(args.source), full_inventory=inventory,
                  source_manifest_sha256=sha(HERE / 'source-manifest.json'),
                  historical_pins=PINS, target_build=False, hardware_access=False,
                  real_hid=False, external_requests=False,
                  limitations='Linux native/Chromium mocks do not establish physical High Sierra/iPhone behavior')
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return exit_code


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        mode, source, core, work, receipt = sys.argv[2:]
        if mode == 'native':
            raise SystemExit(native(pathlib.Path(source), pathlib.Path(core), pathlib.Path(work), pathlib.Path(receipt)))
        raise SystemExit(web(pathlib.Path(source), pathlib.Path(work), pathlib.Path(receipt)))
    raise SystemExit(main())
