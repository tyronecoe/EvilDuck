#!/usr/bin/env python3
"""Source-boundary and zero-fuzz replay checks on public composed source only."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-composed', type=pathlib.Path, required=True)
    parser.add_argument('--candidate-composed', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.results.exists()
    old = (args.baseline_composed / 'webfiles.h').read_text()
    new = (args.candidate_composed / 'webfiles.h').read_text()
    checks, rows = 0, []

    def check(value, reason):
        nonlocal checks
        checks += 1
        assert value, reason

    def literals(text):
        return dict(re.findall(r'static const char (\w+)\[\] PROGMEM = R"rawliteral\((.*?)\)rawliteral";', text, re.S))

    before, after = literals(old), literals(new)
    check(before.keys() == after.keys(), 'Literal inventory changed')
    changed = sorted(k for k in before if before[k] != after[k])
    check(changed == ['INDEX_HTML', 'INDEX_JS'], 'Settings, CSS, Terminal or other resources changed')
    rows.append(dict(name='only_home_editor_literals_changed', status='PASS', changed=changed))

    index_before, index_after = before['INDEX_JS'], after['INDEX_JS']
    boundaries = [('// BEGIN STOP CONTROLS', '// END STOP CONTROLS'),
                  ('async function delScript(', "document.getElementById('uploadForm')"),
                  ('function saveDuckPw(', 'async function refreshStatus('),
                  ('function appendScriptRow(', 'function renderList(')]
    for start, end in boundaries:
        a = index_before.split(start, 1)[1].split(end, 1)[0]
        b = index_after.split(start, 1)[1].split(end, 1)[0]
        check(a == b, 'Unrelated STOP/auth/delete/direct row execution code changed: ' + start)
    rows.append(dict(name='stop_auth_deletion_and_direct_row_run_unchanged', status='PASS'))

    spec = importlib.util.spec_from_file_location('editor_scope_prepare', ROOT / 'tests/editor_load_safety/prepare_sources.py')
    prepare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare)
    pin = json.loads((ROOT / 'tests/editor_load_safety/source-manifest.json').read_text())
    before_map = {r['file']: r['sha256'] for r in pin['before'] + pin['unchanged']}
    after_map = {r['file']: r['sha256'] for r in pin['after'] + pin['unchanged']}
    check(len(before_map) == len(after_map) == 201, 'Incomplete inventory')
    check(prepare.inventory(args.baseline_composed) == before_map, 'Wrong baseline')
    check(prepare.inventory(args.candidate_composed) == after_map, 'Wrong candidate')
    check({k for k in before_map if before_map[k] != after_map[k]} == {'webfiles.h'}, 'Non-UI source changed')
    check(sha(ROOT / 'tests/editor_load_safety/application.patch') == pin['patch_sha256'], 'Patch identity changed')
    rows.append(dict(name='complete_201_file_source_boundary', status='PASS', changed=1, unchanged=200))

    with tempfile.TemporaryDirectory(prefix='editor-source-audit-') as tmp:
        replay = pathlib.Path(tmp) / 'replay'
        shutil.copytree(args.baseline_composed, replay)
        prepare.delta(replay)
        check(prepare.inventory(replay) == after_map, 'Replay mismatch')
        try:
            prepare.delta(replay)
        except AssertionError:
            check(True, 'Repeated patch refused')
        else:
            raise AssertionError('Repeated overlay was accepted')
        wrong = pathlib.Path(tmp) / 'wrong'
        shutil.copytree(args.baseline_composed, wrong)
        (wrong / 'caps_trial.h').write_bytes((wrong / 'caps_trial.h').read_bytes() + b'\n')
        try:
            prepare.delta(wrong)
        except AssertionError:
            check(True, 'Modified unrelated source refused')
        else:
            raise AssertionError('Wrong base was accepted')
    rows.append(dict(name='zero_fuzz_replay_and_denied_wrong_or_repeated_input', status='PASS'))
    result = dict(counts=dict(PASS=len(rows), FAIL=0), assertions=checks, results=rows,
                  baseline_header_sha256=sha(args.baseline_composed / 'webfiles.h'),
                  candidate_header_sha256=sha(args.candidate_composed / 'webfiles.h'),
                  scope='Public source copies only; no native build, hardware or owner files')
    args.results.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
