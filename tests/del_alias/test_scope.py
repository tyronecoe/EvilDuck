#!/usr/bin/env python3
"""Exact composition and negative controls for the two-file DEL source delta."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-composed', type=pathlib.Path, required=True)
    parser.add_argument('--candidate-composed', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.results.exists(), 'PRESERVE_PRIOR_RESULTS'
    spec = importlib.util.spec_from_file_location('scope_del_sources', HERE / 'prepare_sources.py')
    selected = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(selected)
    value = selected.pin()
    before = {r['file']: r['sha256'] for r in value['before'] + value['unchanged']}
    after = {r['file']: r['sha256'] for r in value['after'] + value['unchanged']}
    historical = {str(p.relative_to(ROOT)): digest(p) for n in ['application.patch', 'source-manifest.json', 'prepare_sources.py'] for p in sorted((ROOT / 'tests').rglob(n)) if p.parent != HERE and p.parent.name != 'del_alias_release'}
    rows, assertions = [], 0

    def check(ok, message):
        nonlocal assertions
        assertions += 1
        assert ok, message

    def refused(call, message):
        try:
            call()
        except AssertionError:
            check(True, message)
        else:
            raise AssertionError(message)

    check(selected.inventory(args.baseline_composed) == before, 'BASELINE_CHANGED')
    check(selected.inventory(args.candidate_composed) == after, 'CANDIDATE_MISMATCH')
    check(len(before) == len(after) == 201 and {n for n in before if before[n] != after[n]} == {'core.cpp', 'shortcut_keys.h'}, 'DEL_BOUNDARY_WIDENED')
    check(len(selected.verify_final(args.candidate_composed)) == 201, 'INCOMPLETE_CANDIDATE')
    rows.append(dict(id='DS01', status='PASS', behavior='exact201sources; two vocabulary/compiler files,199 unchanged'))
    for name in ['core.h', 'adapter.cpp', 'adapter.h', 'seam.inc', 'backend_lease.inc', 'hid_backend.cpp', 'com.cpp', 'settings.cpp', 'cli.cpp', 'storage.cpp', 'webserver.cpp', 'webfiles.h', 'led_receiver.cpp', 'caps_trial.h']:
        check((args.baseline_composed / name).read_bytes() == (args.candidate_composed / name).read_bytes(), 'ACCEPTED_BEHAVIOR_CHANGED_' + name)
    rows.append(dict(id='DS02', status='PASS', behavior='runtime/HID/STOP/storage/privacy/dashboard/LED/identity exact'))
    with tempfile.TemporaryDirectory(prefix='del-alias-scope-') as temporary:
        folder = pathlib.Path(temporary)
        replay = folder / 'replay'
        shutil.copytree(args.baseline_composed, replay)
        selected.delta(replay)
        check(selected.inventory(replay) == after, 'REPLAY_DIFFERS')
        refused(lambda: selected.delta(replay), 'DUPLICATE_DELTA_ACCEPTED')
        rows.append(dict(id='DS03', status='PASS', behavior='zero-fuzz exact replay and duplicate refusal'))
        refused(lambda: selected.verify_final(args.baseline_composed), 'OMITTED_DELTA_ACCEPTED')
        for name in ['core.cpp', 'shortcut_keys.h']:
            partial = folder / ('missing-' + name)
            shutil.copytree(args.candidate_composed, partial)
            (partial / name).write_bytes((args.baseline_composed / name).read_bytes())
            refused(lambda: selected.verify_final(partial), 'PARTIAL_DELTA_ACCEPTED_' + name)
            wrong = folder / ('wrong-' + name)
            shutil.copytree(args.baseline_composed, wrong)
            (wrong / name).write_bytes((wrong / name).read_bytes() + b'\n')
            snapshot = selected.inventory(wrong)
            refused(lambda: selected.delta(wrong), 'WRONG_PARENT_ACCEPTED_' + name)
            check(selected.inventory(wrong) == snapshot, 'REJECTED_PARENT_MUTATED_' + name)
        rows.append(dict(id='DS04', status='PASS', behavior='omitted/partial delta and modified parents refused before mutation'))
        tampered = folder / 'unrelated-change'
        shutil.copytree(args.candidate_composed, tampered)
        (tampered / 'adapter.cpp').write_bytes((tampered / 'adapter.cpp').read_bytes() + b'\n')
        refused(lambda: selected.verify_final(tampered), 'UNRELATED_TAMPER_ACCEPTED')
        extra = folder / 'extra-file'
        shutil.copytree(args.candidate_composed, extra)
        (extra / 'unexpected.cpp').write_text('// public test fixture\n')
        refused(lambda: selected.verify_final(extra), 'EXTRA_FILE_ACCEPTED')
        linked = folder / 'symlink'
        shutil.copytree(args.candidate_composed, linked)
        (linked / 'core.cpp').unlink()
        (linked / 'core.cpp').symlink_to((args.candidate_composed / 'core.cpp').resolve())
        refused(lambda: selected.verify_final(linked), 'SYMLINK_ACCEPTED')
        rows.append(dict(id='DS05', status='PASS', behavior='unrelated/extra/symlink source refusal'))
        output = folder / 'cli'
        run = subprocess.run([sys.executable, '-B', str(HERE / 'prepare_sources.py'), '--from-composed', str(args.baseline_composed), '--output-dir', str(output)], cwd=ROOT, capture_output=True, text=True, timeout=120)
        check(run.returncode == 0 and not run.stderr, 'SOURCE_ENTRY_FAILED_' + run.stderr)
        receipt = json.loads((output / 'composition.json').read_text())
        check(receipt['selected_preparer'] == 'tests/del_alias/prepare_sources.py' and receipt['selected_manifest_sha256'] == digest(HERE / 'source-manifest.json'), 'WRONG_ENTRY_SELECTION')
        check(receipt['changed_sources'] == ['core.cpp', 'shortcut_keys.h'] and receipt['unchanged_sources'] == 199 and not receipt['firmware_built'] and not receipt['hardware_access'], 'WRONG_SCOPE_RECEIPT')
        check(selected.inventory(output / 'EvilDuckS3') == after, 'SOURCE_ENTRY_OMITTED_DELTA')
        rows.append(dict(id='DS06', status='PASS', behavior='actual source CLI exact composition; no target build'))
    check(selected.inventory(args.baseline_composed) == before and selected.inventory(args.candidate_composed) == after, 'SUPPLIED_SOURCES_CHANGED')
    check(all(digest(ROOT / name) == sha for name, sha in historical.items()), 'HISTORICAL_LAYERS_CHANGED')
    rows.append(dict(id='DS07', status='PASS', behavior='supplied compositions and historical layers preserved'))
    result = dict(status='PASS', counts=dict(PASS=len(rows), FAIL=0), assertions=assertions, results=rows,
                  source_manifest_sha256=digest(HERE / 'source-manifest.json'), baseline=str(args.baseline_composed), candidate=str(args.candidate_composed),
                  inventory=selected.verify_final(args.candidate_composed), historical_pins=historical,
                  target_firmware_built=False, hardware_access=False, real_hid=False)
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'counts', 'assertions']}, indent=2))


if __name__ == '__main__':
    main()
