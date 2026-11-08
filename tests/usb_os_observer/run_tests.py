#!/usr/bin/env python3
"""Focused actual-module USB observer checks over a pinned preserved RAM-only harness.

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
DEFAULT_RECEIPT = pathlib.Path('/workspace/scratch/define-labels-release/focused-v1.json')
PARENT_RECEIPT_SHA = 'b391c771232948cd5e60c81f86f3db7e4f623d443ebd11e526bd431284fc0db3'
PARENT_DRIVER_SHA = '6498a01aed964a340aade174b66e4e9957dcedeb35203121611b0e608895c08c'


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load_preparer():
    spec = importlib.util.spec_from_file_location('focused_usb_observer_source', HERE / 'prepare_sources.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value



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
    assert parent['counts'] == dict(PASS=28, FAIL=0)
    parent_sources = pathlib.Path(parent['source_bindings'][0]['native']).parent
    parent_driver = parent_sources / 'define_labels_driver.cpp'
    assert digest(parent_driver) == PARENT_DRIVER_SHA, 'PARENT_DRIVER_CHANGED'
    for row in parent['source_bindings']:
        assert digest(row['native']) == row['sha256'], 'PRESERVED_PARENT_SOURCE_CHANGED'
    args.output_dir.mkdir(parents=True)
    source = args.output_dir / 'sources'
    shutil.copytree(parent_sources, source)
    layer.delta(source)
    # Preserve every historical body; rename its entry only for the new driver.
    text = parent_driver.read_text()
    anchor = 'int main(int argc,char**argv)'
    assert text.count(anchor) == 1
    (source / 'define_labels_parent_cases.inc').write_text(text.replace(anchor, 'int define_labels_parent_main(int argc,char**argv)', 1))
    driver = HERE / 'test_main.cpp'
    snapshot = source / 'usb_observer_driver.cpp'
    snapshot.write_bytes(driver.read_bytes())
    cases = sorted(set(re.findall(r'"(UO\d\d)"', snapshot.read_text())))
    assert cases == ['UO%02d' % n for n in range(1, 31)]
    command = list(parent['command'])
    for i, value in enumerate(command):
        command[i] = value.replace(str(parent_sources), str(source))
    old_driver = str(source / 'define_labels_driver.cpp')
    assert command.count(old_driver) == 1
    command[command.index(old_driver)] = str(snapshot)
    at = command.index('-o')
    command[at + 1] = str(args.output_dir / 'native')
    mocks = args.output_dir / 'observer-mocks'
    shutil.copytree(HERE / 'mocks', mocks)
    command.insert(1, '-I' + str(mocks))
    command.insert(1, '-DEVILDUCK_USB_ENUM_OBSERVER=1')
    command.append(str(mocks / 'mock_real.cpp'))
    # Bind the production files actually compiled by the mocked module harness.
    bindings, generated = [], []
    names = sorted({pathlib.Path(v).name for v in command if v.endswith('.cpp') and v.startswith(str(source)) and pathlib.Path(v) != snapshot})
    for name in names + ['core.h', 'shortcut_keys.h', 'adapter.h', 'seam.inc', 'backend_lease.inc', 'webfiles.h', 'hid_backend.h']:
        physical = source / name
        if not (args.target_composed / name).exists():
            assert name == 'platform.cpp', 'UNEXPECTED_GENERATED_MODULE_' + name
            generated.append(dict(file=name, native=str(physical), sha256=digest(physical), purpose='inherited RAM-only platform mock'))
            continue
        assert physical.read_bytes() == (args.target_composed / name).read_bytes(), 'FOCUSED_TARGET_BINDING_' + name
        bindings.append(dict(file=name, native=str(physical), sha256=digest(physical)))
    generated.extend(dict(file='observer-mocks/'+str(p.relative_to(mocks)), native=str(p), sha256=digest(p), purpose='RAM-only DCD type/forwarding mock') for p in sorted(mocks.rglob('*')) if p.is_file())
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
    result['counts'] = {s: sum(r['status'] == s for r in result['results']) for s in ['PASS', 'FAIL']}
    result['assertions'] = sum(r['assertions'] for r in result['results'])
    result['status'] = 'PASS' if compiled.returncode == 0 and result['counts'] == dict(PASS=30, FAIL=0) else 'FAIL'
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
