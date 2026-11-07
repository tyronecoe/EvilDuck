#!/usr/bin/env python3
"""Focused actual-module DEL checks over a pinned preserved RAM-only harness.

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
DEFAULT_RECEIPT = pathlib.Path('/workspace/scratch/previous-command-repeat-release/final-regressions-v1/native.json')
PARENT_RECEIPT_SHA = 'e0f5e730fa0a4d8e6483ad0355551ac74683829fc32c15380a86e6926584de30'
PARENT_DRIVER_SHA = '80cd858daf73af57612f6bc356a45a537cb5ddf4f0b0e3ca089c128a879e933d'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load_preparer():
    spec = importlib.util.spec_from_file_location('focused_del_source', HERE / 'prepare_sources.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def causal_control(command, folder, env, parent_source):
    """Demonstrate the exact prior vocabulary failure without changing history."""
    destination = folder / 'old-core-control'
    destination.mkdir()
    for name in ['core.cpp', 'core.h', 'shortcut_keys.h']:
        shutil.copyfile(parent_source / name, destination / name)
    probe = destination / 'probe.cpp'
    probe.write_text('''#include "core.h"
#include <cstring>
#include <cstdio>
int main(){ds_preview::Program p;const char* s="DEL\\n";
if(p.compile(s,strlen(s))||p.error().code!=ds_preview::ErrorCode::UnknownStatement||p.error().line!=1)return 1;
s="DELETE\\n";if(!p.compile(s,strlen(s)))return 2;
s="FUNCTION DEL()\\nRETURN 1\\nEND_FUNCTION\\nVAR $DEL=DEL()\\n";if(!p.compile(s,strlen(s)))return 3;
std::printf("PASS prior-vocabulary-control checks=3\\n");}
''')
    selected = [v for v in command if not v.endswith('.cpp') and not v.startswith('-I')]
    at = selected.index('-o')
    del selected[at:at + 2]
    selected += ['-I' + str(destination), str(probe), str(destination / 'core.cpp'), '-o', str(destination / 'probe')]
    compiled = subprocess.run(selected, capture_output=True, text=True, timeout=120)
    row = dict(command=selected, compile_exit=compiled.returncode, compile_stdout=compiled.stdout,
               compile_stderr=compiled.stderr, status='FAIL', checks=0)
    if compiled.returncode == 0:
        run = subprocess.run([str(destination / 'probe')], capture_output=True, text=True, timeout=30, env=env)
        row.update(exit=run.returncode, stdout=run.stdout, stderr=run.stderr,
                   status='PASS' if run.returncode == 0 and not run.stderr else 'FAIL',
                   checks=3 if run.returncode == 0 else 0)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-composed', type=pathlib.Path, required=True)
    parser.add_argument('--output-dir', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    parser.add_argument('--parent-native-receipt', type=pathlib.Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    assert not args.output_dir.exists() and not args.results.exists(), 'PRESERVE_PRIOR_RESULTS'
    layer = load_preparer()
    inventory = layer.verify_final(args.target_composed)
    assert digest(args.parent_native_receipt) == PARENT_RECEIPT_SHA, 'PARENT_RECEIPT_CHANGED'
    parent = json.loads(args.parent_native_receipt.read_text())
    assert parent['counts'] == dict(PASS=636, FAIL=0)
    parent_sources = args.parent_native_receipt.parent / 'native-build/sources'
    parent_driver = parent_sources / 'previous_command_repeat_driver.cpp'
    assert digest(parent_driver) == PARENT_DRIVER_SHA, 'PARENT_DRIVER_CHANGED'
    for row in parent['previous_command_repeat_binding']['source_bindings']:
        assert digest(row['native']) == row['sha256'], 'PRESERVED_PARENT_SOURCE_CHANGED'
    args.output_dir.mkdir(parents=True)
    source = args.output_dir / 'sources'
    shutil.copytree(parent_sources, source)
    layer.delta(source)
    # Preserve every historical body; rename its entry only for the new driver.
    text = parent_driver.read_text()
    anchor = 'int main(int argc,char**argv)'
    assert text.count(anchor) == 1
    (source / 'previous_repeat_parent_cases.inc').write_text(text.replace(anchor, 'int previous_repeat_parent_main(int argc,char**argv)', 1))
    driver = HERE / 'test_main.cpp'
    snapshot = source / 'del_alias_driver.cpp'
    snapshot.write_bytes(driver.read_bytes())
    cases = sorted(set(re.findall(r'"(DA\d\d)"', snapshot.read_text())))
    assert cases == ['DA%02d' % n for n in range(1, 28)]
    command = list(parent['command'])
    for i, value in enumerate(command):
        command[i] = value.replace(str(parent_sources), str(source))
    old_driver = str(source / 'previous_command_repeat_driver.cpp')
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
        result['causal_control'] = causal_control(command, args.output_dir, env, parent_sources)
    result['counts'] = {s: sum(r['status'] == s for r in result['results']) for s in ['PASS', 'FAIL']}
    result['assertions'] = sum(r['assertions'] for r in result['results'])
    result['status'] = 'PASS' if compiled.returncode == 0 and result['counts'] == dict(PASS=27, FAIL=0) and result['causal_control']['status'] == 'PASS' else 'FAIL'
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
