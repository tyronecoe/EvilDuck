#!/usr/bin/env python3
"""Focused actual-module DEFINE-label checks over a pinned preserved RAM-only harness.

Historical case bodies are included for their existing mocks/helpers but are not
executed here. The independent release regression runner reexecutes those cases.
This runner never invokes Arduino, a device, payload, installer or network client.
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
DEFAULT_RECEIPT = pathlib.Path('/workspace/scratch/del-alias/focused-v2.json')
PARENT_RECEIPT_SHA = 'bee4546913c336387d62143288020897b85784acdb57b58f6c79eb8713eecd02'
PARENT_DRIVER_SHA = '2c61c75484ee958e3157ce3fb10c863e1c3df3548886419510b6735d21b3c203'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load_preparer():
    spec = importlib.util.spec_from_file_location('focused_define_source', HERE / 'prepare_sources.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def auxiliary_checks(command, folder, env, baseline, candidate, official):
    """Original-source compiler/layout observations only; Runtime is never started."""
    assert digest(official) == 'ef137faf626782fdcc6b43405f361b7a3c923c634f98dfd7774c73072e18399f'
    results = {}
    for label, production in [('parent', baseline), ('candidate', candidate)]:
        destination = folder / ('compiler-' + label)
        destination.mkdir()
        for name in ['core.cpp', 'core.h', 'shortcut_keys.h']:
            shutil.copyfile(production / name, destination / name)
        probe = destination / 'probe.cpp'
        probe.write_text(r'''#include "core.cpp"
#include <cstdio>
#include <fstream>
#include <iterator>
#include <string>
int main(int argc,char** argv){
 if(argc!=2)return 2;
 std::ifstream f(argv[1],std::ios::binary);if(!f)return 3;
 std::string source((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
 ds_preview::Program p;bool accepted=p.compile(source.data(),source.size());
 std::printf("{\"compiler_bytes\":%zu,\"compiler_alignment\":%zu,\"workspace_bytes\":%zu,\"workspace_alignment\":%zu,\"compile_session_bytes\":%zu,\"program_bytes\":%zu,\"runtime_bytes\":%zu,\"accepted\":%s,\"physical_line\":%u,\"column\":%u,\"error_code\":%u,\"ir_instructions\":%zu}\n",sizeof(ds_preview::Compiler),alignof(ds_preview::Compiler),ds_preview::CompileStorage,alignof(max_align_t),sizeof(ds_preview::CompileSession),sizeof(ds_preview::Program),sizeof(ds_preview::Runtime),accepted?"true":"false",unsigned(p.error().line),unsigned(p.error().column),unsigned(p.error().code),p.instructions());
}
''')
        selected = [v for v in command if not v.endswith('.cpp') and not v.startswith('-I')]
        at = selected.index('-o');del selected[at:at+2]
        selected += ['-I' + str(destination), str(probe), '-o', str(destination / 'probe')]
        compiled = subprocess.run(selected, capture_output=True, text=True, timeout=120)
        row = dict(command=selected, compile_exit=compiled.returncode, compile_stdout=compiled.stdout,
                   compile_stderr=compiled.stderr, status='FAIL', source_core_sha256=digest(destination/'core.cpp'))
        if compiled.returncode == 0:
            run = subprocess.run([str(destination/'probe'), str(official)], capture_output=True, text=True, timeout=30, env=env)
            row.update(exit=run.returncode, stdout=run.stdout, stderr=run.stderr)
            if run.returncode == 0 and not run.stderr:
                row['observation'] = json.loads(run.stdout)
                row['status'] = 'PASS'
        results[label] = row
    if all(r['status'] == 'PASS' for r in results.values()):
        old, new = results['parent']['observation'], results['candidate']['observation']
        assert not old['accepted'] and old['physical_line'] == 50 and old['error_code'] == 6
        assert not new['accepted'] and (new['physical_line'], new['error_code']) != (50,6)
        assert new['compiler_bytes'] == old['compiler_bytes'] + 128
        assert new['compiler_alignment'] == old['compiler_alignment']
        assert old['workspace_bytes'] == new['workspace_bytes'] == 4096
        assert old['compile_session_bytes'] == new['compile_session_bytes']
        assert old['program_bytes'] == new['program_bytes'] and old['runtime_bytes'] == new['runtime_bytes']
        assert new['compiler_bytes'] <= new['workspace_bytes'] and new['compiler_alignment'] <= new['workspace_alignment']
        results.update(status='PASS', official_source=str(official), official_source_sha256=digest(official),
                       compiler_delta_bytes=128, host_only_layout=True, target_layout_measured=False,
                       official_runtime_executed=False, hardware_access=False,
                       next_diagnostic_policy='Observed unchanged official source rejection; not OS detector support')
    else:
        results['status'] = 'FAIL'
    return results

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-composed', type=pathlib.Path, required=True)
    parser.add_argument('--output-dir', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    parser.add_argument('--parent-native-receipt', type=pathlib.Path, default=DEFAULT_RECEIPT)
    parser.add_argument('--baseline-composed', type=pathlib.Path, default=pathlib.Path('/workspace/scratch/del-alias-release/build-v1/candidate/EvilDuckS3'))
    parser.add_argument('--official-source', type=pathlib.Path, default=pathlib.Path('/workspace/scratch/os-detect-audit/os_detect-official-unmodified.txt'))
    args = parser.parse_args()
    assert not args.output_dir.exists() and not args.results.exists(), 'PRESERVE_PRIOR_RESULTS'
    layer = load_preparer()
    inventory = layer.verify_final(args.target_composed)
    assert digest(args.parent_native_receipt) == PARENT_RECEIPT_SHA, 'PARENT_RECEIPT_CHANGED'
    parent = json.loads(args.parent_native_receipt.read_text())
    assert parent['counts'] == dict(PASS=27, FAIL=0)
    parent_sources = pathlib.Path(parent['source_bindings'][0]['native']).parent
    parent_driver = parent_sources / 'del_alias_driver.cpp'
    assert digest(parent_driver) == PARENT_DRIVER_SHA, 'PARENT_DRIVER_CHANGED'
    for row in parent['source_bindings']:
        assert digest(row['native']) == row['sha256'], 'PRESERVED_PARENT_SOURCE_CHANGED'
    args.output_dir.mkdir(parents=True)
    source = args.output_dir / 'sources'
    shutil.copytree(parent_sources, source)
    layer.delta(source)
    # Preserve every historical body; rename its entry only for the new driver.
    text = parent_driver.read_text()
    anchor = 'int main(int argc,char** argv)'
    assert text.count(anchor) == 1
    (source / 'del_alias_parent_cases.inc').write_text(text.replace(anchor, 'int del_alias_parent_main(int argc,char** argv)', 1))
    driver = HERE / 'test_main.cpp'
    snapshot = source / 'define_labels_driver.cpp'
    snapshot.write_bytes(driver.read_bytes())
    cases = sorted(set(re.findall(r'"(DL\d\d)"', snapshot.read_text())))
    assert cases == ['DL%02d' % n for n in range(1, 29)]
    command = list(parent['command'])
    for i, value in enumerate(command):
        command[i] = value.replace(str(parent_sources), str(source))
    old_driver = str(source / 'del_alias_driver.cpp')
    assert command.count(old_driver) == 1
    command[command.index(old_driver)] = str(snapshot)
    at = command.index('-o')
    command[at + 1] = str(args.output_dir / 'native')
    # Bind the production files actually compiled by the mocked module harness.
    bindings, generated = [], []
    names = sorted({pathlib.Path(v).name for v in command if v.endswith('.cpp') and v.startswith(str(source)) and pathlib.Path(v) != snapshot})
    for name in names + ['core.h', 'shortcut_keys.h', 'adapter.h', 'seam.inc', 'backend_lease.inc', 'webfiles.h']:
        physical = source / name
        if not (args.target_composed / name).exists():
            assert name == 'platform.cpp', 'UNEXPECTED_GENERATED_MODULE_' + name
            generated.append(dict(file=name, native=str(physical), sha256=digest(physical), purpose='inherited RAM-only platform mock'))
            continue
        assert physical.read_bytes() == (args.target_composed / name).read_bytes(), 'FOCUSED_TARGET_BINDING_' + name
        bindings.append(dict(file=name, native=str(physical), sha256=digest(physical)))
    compiled = subprocess.run(command, capture_output=True, text=True, timeout=300)
    result = dict(command=command, compile_exit=compiled.returncode, compile_stdout=compiled.stdout,
                  compile_stderr=compiled.stderr, results=[], source=str(args.target_composed),
                  full_source_inventory=inventory, source_manifest_sha256=digest(HERE / 'source-manifest.json'),
                  source_bindings=bindings, generated_mock_bindings=generated,
                  native_identity_boundary='Inherited generated Caps fixture identity retained; core, key vocabulary and compiled production modules equal the reviewed target bytes. No target identity or hardware claim is made by this harness.',
                  driver_sha256=digest(snapshot), runner_sha256=digest(__file__),
                  parent_receipt=str(args.parent_native_receipt), parent_receipt_sha256=PARENT_RECEIPT_SHA,
                  parent_driver_sha256=PARENT_DRIVER_SHA, historical_cases_executed=False,
                  historical_case_bodies_unchanged=True, sanitizers='ASan/UBSan/leak detect_leaks=1',
                  hardware=False, real_hid=False, target_firmware_built=False, packaging=False)
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=1:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
    if compiled.returncode == 0:
        for case in cases:
            run = subprocess.run([str(args.output_dir / 'native'), case], capture_output=True, text=True, timeout=45, env=env)
            match = re.search(r'PASS ' + case + r' \((\d+) assertions\)', run.stdout)
            result['results'].append(dict(id=case, exit=run.returncode, stdout=run.stdout, stderr=run.stderr,
                status='PASS' if run.returncode == 0 and match and not run.stderr else 'FAIL',
                assertions=int(match[1]) if match else 0))
        result['auxiliary_checks'] = auxiliary_checks(command, args.output_dir, env, args.baseline_composed, args.target_composed, args.official_source)
    result['counts'] = {s: sum(r['status'] == s for r in result['results']) for s in ['PASS', 'FAIL']}
    result['assertions'] = sum(r['assertions'] for r in result['results'])
    result['status'] = 'PASS' if compiled.returncode == 0 and result['counts'] == dict(PASS=28, FAIL=0) and result['auxiliary_checks']['status'] == 'PASS' else 'FAIL'
    layer.verify_final(args.target_composed)
    assert digest(driver) == result['driver_sha256'] and digest(args.parent_native_receipt) == PARENT_RECEIPT_SHA
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'compile_exit', 'counts', 'assertions', 'sanitizers']}, indent=2))
    for row in result['results']:
        if row['status'] != 'PASS':
            print(row['id'], row['stdout'], row['stderr'])
    if compiled.returncode:
        print(compiled.stderr)
    return int(result['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
