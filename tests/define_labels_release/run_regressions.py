#!/usr/bin/env python3
"""Fresh native regressions over the exact DEFINE-label composition.

The preserved RAM-only native snapshots supply unchanged case bodies, fixtures,
compiler flags and sanitizer options. Only the reviewed DEFINE source delta and
disposable output paths change. Unchanged web resources reuse their hash-bound
completed checks explicitly; they are not relabelled as newly executed tests.
No target compiler, owner data, real HID, hardware or network interface is used.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
BUILD_ID = 'ROUTEB-DEFINE-LABELS-H1-v1'
PARENTS = {
    'native': ('/workspace/scratch/del-alias-release/regressions-v1/native.json',
               '3693d9b12140686e7973520bc7e69f1f0607d7f630dfac14f4264d494137e345'),
    'del': ('/workspace/scratch/del-alias/focused-v2.json',
            'bee4546913c336387d62143288020897b85784acdb57b58f6c79eb8713eecd02'),
    'web': ('/workspace/scratch/del-alias-release/regressions-v1/web.json',
            'cb18c4b40d52f11c6e6f9bd4159561ad6372c48fcac4c6d4ee83edf2e253f2eb'),
}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parent_record(label):
    file, expected = PARENTS[label]
    assert sha(file) == expected, 'PRESERVED_PARENT_RECEIPT_CHANGED_' + label
    return pathlib.Path(file), json.loads(pathlib.Path(file).read_text())


def final_preparer(source):
    module = load(HERE / 'prepare_sources.py', 'define_labels_release_regression_source')
    rows = module.verify_final(source)
    assert len(rows) == 201
    assert (pathlib.Path(source) / 'caps_trial.h').read_bytes().count(BUILD_ID.encode()) == 1
    return module, rows


def native_group(label, source, work, output):
    """Recompile every retained actual-module case; never execute an old binary."""
    release, inventory = final_preparer(source)
    delta = load(ROOT / 'tests/define_labels/prepare_sources.py', 'define_native_delta_' + label)
    delta.pin()
    original_file, previous = parent_record(label)
    expected_cases, expected_assertions = (636, 27376) if label == 'native' else (27, 797)
    assert previous['counts'] == dict(PASS=expected_cases, FAIL=0)
    assert previous['assertions'] == expected_assertions
    command = list(previous['command'])
    driver_name = 'previous_command_repeat_driver.cpp' if label == 'native' else 'del_alias_driver.cpp'
    drivers = [pathlib.Path(v) for v in command if v.endswith('/' + driver_name)]
    assert len(drivers) == 1
    expected_driver = previous.get('driver_sha256')
    if expected_driver is None:
        expected_driver = previous['previous_command_repeat_binding']['new_driver_sha256']
    assert sha(drivers[0]) == expected_driver, 'PRESERVED_PARENT_DRIVER_CHANGED_' + label
    old_source = drivers[0].parent
    old_work = old_source.parent
    assert not work.exists() and not output.exists(), 'PRESERVE_PRIOR_RESULTS'
    work.mkdir(parents=True)
    destination = work / 'sources'
    shutil.copytree(old_source, destination)
    before = {str(p.relative_to(destination)): sha(p)
              for p in destination.rglob('*') if p.is_file()}
    # All saved binding checks remain; generated build metadata is a declared
    # fixture boundary, while every actual production translation unit is bound
    # separately below to the current complete candidate.
    bindings = previous.get('source_bindings')
    if bindings is None:
        bindings = previous['previous_command_repeat_binding']['source_bindings']
    for row in bindings:
        assert sha(row['native']) == row['sha256'], 'PARENT_NATIVE_SOURCE_CHANGED_' + row['file']
    delta.delta(destination)
    after = {str(p.relative_to(destination)): sha(p)
             for p in destination.rglob('*') if p.is_file()}
    assert before.keys() == after.keys()
    assert {n for n in before if before[n] != after[n]} == {'core.cpp'}
    assert (destination / 'core.cpp').read_bytes() == (source / 'core.cpp').read_bytes()
    # Preserve generated include directories beside sources (the static HTTP
    # mock), but do not copy or run any parent's compiled executable.
    for value in command:
        if value.startswith('-I'):
            path = pathlib.Path(value[2:])
            if path.is_relative_to(old_work) and not path.is_relative_to(old_source):
                relative = path.relative_to(old_work)
                selected = work / relative
                if not selected.exists():
                    shutil.copytree(path, selected)
    command = [v.replace(str(old_work), str(work)) for v in command]
    at = command.index('-o')
    command[at + 1] = str(work / 'native')
    assert '-fsanitize=address,undefined' in command and '-fno-omit-frame-pointer' in command
    assert '-fno-pie' in command and '-no-pie' in command
    production, mocks = [], []
    for value in command:
        if not value.endswith('.cpp'):
            continue
        file = pathlib.Path(value)
        if file.name == driver_name:
            assert sha(file) == before[driver_name]
            continue
        candidate = source / file.name
        if candidate.exists():
            assert file.read_bytes() == candidate.read_bytes(), 'PRODUCTION_SOURCE_BINDING_' + file.name
            production.append(dict(file=file.name, native=str(file), sha256=sha(file)))
        else:
            # These are the existing RAM-only mock/lower/boot/NVS fixtures.
            assert file.name in {'platform.cpp', 'lower.cpp', 'allocations.cpp',
                                 'nvs_fixture.cpp', 'boot_fixture.cpp'}, file.name
            mocks.append(dict(file=str(file), sha256=sha(file)))
    for name in ['core.h', 'shortcut_keys.h', 'adapter.h', 'backend_lease.inc', 'seam.inc', 'webfiles.h']:
        file = destination / name
        assert file.read_bytes() == (source / name).read_bytes(), 'PRODUCTION_HEADER_BINDING_' + name
        production.append(dict(file=name, native=str(file), sha256=sha(file)))
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=300)
    result = dict(status='FAIL', command=command, compile_exit=compiled.returncode,
                  compile_stdout=compiled.stdout, compile_stderr=compiled.stderr,
                  results=[], parent_receipt=str(original_file), parent_receipt_sha256=sha(original_file),
                  parent_snapshot_hashes=before, executed_snapshot_hashes=after,
                  source_bindings=production, generated_mock_bindings=mocks,
                  driver_sha256=sha(destination / driver_name), case_bodies_or_expectations_changed=False,
                  sanitizer_flags_changed=False, sanitizers='ASan/UBSan/detect_leaks=1',
                  native_fixture_identity_policy='Historical generated mock identity retained; all production modules, actual core and key vocabulary equal the complete final candidate.',
                  fresh_execution=True, hardware=False, real_hid=False, target_firmware_built=False)
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=1:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    if compiled.returncode == 0:
        cases = [row['id'] for row in previous['results']]
        assert len(cases) == len(set(cases)) == expected_cases
        for case in cases:
            run = subprocess.run([str(work / 'native'), case], capture_output=True, text=True, timeout=45, env=env)
            matched = re.search(r'PASS ' + re.escape(case) + r' \((\d+) assertions\)', run.stdout)
            result['results'].append(dict(id=case, exit=run.returncode, stdout=run.stdout,
                stderr=run.stderr, assertions=int(matched[1]) if matched else 0,
                status='PASS' if run.returncode == 0 and matched and not run.stderr else 'FAIL'))
    result['counts'] = {s: sum(row['status'] == s for row in result['results']) for s in ['PASS', 'FAIL']}
    result['assertions'] = sum(row['assertions'] for row in result['results'])
    result['status'] = ('PASS' if compiled.returncode == 0 and
                        result['counts'] == dict(PASS=expected_cases, FAIL=0) and
                        result['assertions'] == expected_assertions else 'FAIL')
    assert release.verify_final(source) == inventory
    result['define_release_regression_binding'] = dict(
        wrapper_sha256=sha(__file__), final_build_id=BUILD_ID, final_source=str(source),
        source_manifest_sha256=sha(HERE / 'source-manifest.json'), full_source_inventory=inventory,
        only_native_production_delta=['core.cpp'], target_build=False, hardware_access=False)
    output.write_text(json.dumps(result, indent=2) + '\n')
    return int(result['status'] != 'PASS')


def reuse_web(source, output):
    """Reuse only evidence whose actual web inputs and test bytes are unchanged."""
    release, inventory = final_preparer(source)
    original_file, previous = parent_record('web')
    assert previous['status'] == 'PASS'
    for name in ['webserver.cpp', 'webfiles.h']:
        assert sha(source / name) == previous['source_hashes'][name]
    for name, expected in previous['historical_test_pins'].items():
        assert sha(ROOT / name) == expected, 'WEB_TEST_CHANGED_' + name
    assert previous['test_sha256'] == sha(ROOT / 'tests/previous_command_repeat/test_web_regressions.py')
    for row in previous['groups'].values():
        assert row['exit'] == 0 and row['counts']['FAIL'] == 0
        assert sha(row['receipt']) == row['receipt_sha256']
    native = json.loads(pathlib.Path(previous['groups']['static-native']['receipt']).read_text())
    # This native resource probe compiles extracted static HTTP functions and
    # webfiles/WString. It does not compile or invoke the changed DEFINE core.
    assert set(native['source_hashes']) == {'webserver.cpp', 'webfiles.h'}
    assert all('core.cpp' not in ' '.join(command) for command in native['commands'])
    result = dict(previous)
    result.update(reused=True, fresh_execution=False, original_receipt=str(original_file),
                  original_receipt_sha256=sha(original_file),
                  reuse_reason='Only core constant storage/length validation and build ID change. All webserver/webfiles resource bytes and web test inputs remain exact; the static resource probe does not compile the core.',
                  current_candidate_source=str(source), current_candidate_manifest_sha256=sha(HERE / 'source-manifest.json'),
                  current_candidate_inventory=inventory, wrapper_sha256=sha(__file__))
    assert release.verify_final(source) == inventory
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=pathlib.Path, required=True)
    parser.add_argument('--core', type=pathlib.Path, required=True)
    parser.add_argument('--output-dir', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert args.core.is_dir()
    assert not args.output_dir.exists() and not args.results.exists(), 'PRESERVE_PRIOR_RESULTS'
    assert not args.output_dir.resolve().is_relative_to(ROOT)
    _, inventory = final_preparer(args.source)
    args.output_dir.mkdir(parents=True)
    groups, code = {}, 0
    for label in ['native', 'del']:
        output = args.output_dir / (label + '.json')
        work = args.output_dir / (label + '-build')
        status = native_group(label, args.source, work, output)
        record = json.loads(output.read_text())
        groups[label] = dict(exit=status, stderr='', receipt=str(output), receipt_sha256=sha(output),
                             counts=record['counts'], assertions=record['assertions'], fresh_execution=True)
        if status:
            code = 1
            break
    web = args.output_dir / 'web.json'
    reused = reuse_web(args.source, web)
    groups['web'] = dict(exit=0, stderr='', receipt=str(web), receipt_sha256=sha(web),
                         groups=reused['groups'], reused=True, fresh_execution=False)
    result = dict(status='PASS' if code == 0 else 'FAIL', groups=groups,
                  wrapper_sha256=sha(__file__), source=str(args.source), full_inventory=inventory,
                  source_manifest_sha256=sha(HERE / 'source-manifest.json'), parent_receipts=PARENTS,
                  fresh_native_cases=sum(v.get('counts', {}).get('PASS', 0) for v in groups.values()),
                  fresh_native_assertions=sum(v.get('assertions', 0) for v in groups.values()),
                  reused_web_groups=86, reused_web_assertions=1518,
                  target_build=False, hardware_access=False, real_hid=False, external_requests=False,
                  limitations='RAM mocks do not establish physical High Sierra, host timing or USB receipt. Web results are retained historical evidence, not a fresh execution.')
    args.results.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'fresh_native_cases', 'fresh_native_assertions', 'reused_web_groups']}, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
