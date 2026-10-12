#!/usr/bin/env python3
"""Pinned SDK Storage component writes/reads disposable blob fixtures; no owner data."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from nvs_inspect import inspect
from nvs_source_prepare import verify

CASES = ['sdk_blob_0', 'sdk_blob_33', 'sdk_blob_4000', 'sdk_blob_8000',
         'sdk_blob_update33', 'sdk_blob_update4000']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk-source', type=Path, required=True)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    pin = verify(args.sdk_source)
    build = args.build_dir.resolve()
    if build == ROOT or ROOT in build.parents:
        raise ValueError('Synthetic outputs require an external disposable build directory')
    build.mkdir(parents=True, exist_ok=True)
    if any((build / (case + '.bin')).exists() for case in CASES):
        raise ValueError('Existing synthetic image refused; choose a fresh build directory')
    if args.results.exists():
        raise ValueError('Existing results refused')
    src = args.sdk_source / 'components/nvs_flash'
    executable = build / 'blob-sdk'
    command = ['g++', '-std=gnu++17', '-DNO_DEBUG_STORAGE', '-O1', '-g',
               '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
               '-I' + str(ROOT / 'tests/stage19/mocks'), '-I' + str(src / 'include'),
               '-I' + str(args.sdk_source / 'components/esp_common/include'),
               '-I' + str(src / 'src'), '-I' + str(src / 'private_include'),
               str(ROOT / 'tests/stage20/blob_sdk.cpp')]
    command += [str(src / 'src' / filename) for filename in
                ['nvs_page.cpp', 'nvs_pagemanager.cpp', 'nvs_types.cpp',
                 'nvs_item_hash_list.cpp', 'nvs_storage.cpp']]
    subprocess.run(command + ['-o', str(executable)], check=True)
    rows = []
    for case in CASES:
        image = build / (case + '.bin')
        result = subprocess.run([str(executable), case, str(image)],
                                capture_output=True, text=True, timeout=30)
        match = re.search(r'PASS \w+ \((\d+) assertions\)', result.stdout)
        operations = [dict(kind=op[0], address=int(op[1]), bytes=int(op[2]), success=op[3] == '1')
                      for op in re.findall(r'^PREP_OP (\w+) (\d+) (\d+) ([01])$', result.stdout, re.M)]
        rows.append(dict(name=case, target='pinned_sdk_storage_source',
                         status='PASS' if result.returncode == 0 and match else 'FAIL',
                         assertions=int(match[1]) if match else 0,
                         preparation_flash_operations=operations,
                         healthy_reinitialization_and_read_flash_operations=
                         [] if result.returncode == 0 and match else None,
                         stdout=result.stdout, stderr=result.stderr))
        print(rows[-1]['status'], case, flush=True)
        if result.returncode == 0 and match:
            before = image.read_bytes()
            finding = inspect(before)
            privacy = not any(text in json.dumps(finding) for text in ['synthetic', 'fixture'])
            compatible = finding['classification'] == 'compatible-within-verified-checks'
            unchanged = image.read_bytes() == before
            bounds = len(before) == 0x5000
            rows.append(dict(name=case + '_offline_inspection', target='read_only_inspector',
                             status='PASS' if compatible and privacy and unchanged and bounds else 'FAIL',
                             assertions=4, classification=finding['classification'],
                             issues=finding['issues'], input_unchanged=unchanged,
                             privacy=privacy, synthetic_image_sha256=hashlib.sha256(before).hexdigest()))
            print(rows[-1]['status'], rows[-1]['name'], flush=True)
    verify(args.sdk_source)
    report = dict(results=rows, counts={status: sum(row['status'] == status for row in rows)
                                      for status in ['PASS', 'FAIL']},
                  assertions=sum(row['assertions'] for row in rows),
                  sdk_source_commit=pin['commit'], sdk_storage_components_executed=True,
                  complete_sdk_initializer_executed=False, xtensa_sdk_library_executed=False,
                  sanitizers='ASan/UBSan', owner_files_inspected=False, hardware_access=False)
    with args.results.open('x') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'results'}, indent=2))
    return bool(report['counts']['FAIL'])


if __name__ == '__main__':
    raise SystemExit(main())
