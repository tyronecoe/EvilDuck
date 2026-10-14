#!/usr/bin/env python3
"""Read-only Gate B evidence/scope check; writes only a fresh external receipt.

No patching, compilation, runtime adapter, device, USB, network or owner files.
Static checks are not language compatibility assertions or tabletop execution.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = '220970bc633d969e76d1d8c91750b5939377df0a'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protected-core', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    output = args.results.resolve()
    if output.exists() or output.is_relative_to(ROOT):
        raise ValueError('Receipt must be fresh and outside the checkout')
    evidence = json.loads((ROOT / 'docs/stage28j-source-evidence.json').read_text())
    if evidence['baseline'] != BASE:
        raise ValueError('Wrong evidence baseline')
    roots = {'protected-core': args.protected_core, 'sdk': args.sdk}
    anchors = evidence['repo_anchors'] + evidence['dependency_anchors']
    for row in anchors:
        root = roots[row['root']] if 'root' in row else ROOT
        path = Path(row['file'])
        if path.is_absolute() or '..' in path.parts:
            raise ValueError('Nonrelative evidence path')
        raw = (root / path).read_bytes()
        lines = raw.decode().splitlines()
        if not 1 <= row['start'] <= row['end'] <= len(lines):
            raise ValueError('Invalid source range: ' + str(path))
        span = ('\n'.join(lines[row['start'] - 1:row['end']]) + '\n').encode()
        if (hashlib.sha256(raw).hexdigest() != row['file_sha256'] or
                hashlib.sha256(span).hexdigest() != row['span_sha256']):
            raise ValueError('Evidence drift: ' + str(path))
    old = git('ls-tree', '-r', '--name-only', BASE).decode().splitlines()
    for name in old:
        if (ROOT / name).read_bytes() != git('show', BASE + ':' + name):
            raise ValueError('Historical input changed: ' + name)
    current = set(git('ls-files', '--cached', '--others', '--exclude-standard').decode().splitlines())
    additions = sorted(current - set(old))
    for name in additions:
        if not (name.startswith('docs/stage28j-') or name.startswith('tests/stage28j/')):
            raise ValueError('Out-of-scope path: ' + name)
    sheet = (ROOT / 'docs/stage28j-owner-decisions.md').read_text()
    ids = re.findall(r'^\| (D\d\d) \|.*$', sheet, re.M)
    if ids != ['D%02d' % n for n in range(1, 11)]:
        raise ValueError('Missing, duplicate or unordered owner decision')
    for line in sheet.splitlines():
        if re.match(r'^\| D\d\d \|', line) and line.split('|')[-2].strip():
            raise ValueError('Owner acceptance must remain empty')
    contract = (ROOT / 'docs/stage28j-report-contract.md').read_text()
    traces = re.findall(r'^\| (T\d\d) ', contract, re.M)
    if traces != ['T%02d' % n for n in range(1, 19)]:
        raise ValueError('Missing, duplicate or unordered specification trace')
    if 'SPECIFICATION-ONLY' not in contract or 'not new executed tests' not in contract:
        raise ValueError('Missing specification-only boundary')
    result = dict(status='PASS', baseline=BASE, historical_files_byte_identical=len(old),
                  verified_source_spans=len(anchors), allowed_added_files=additions,
                  proposed_decisions=len(ids), empty_owner_acceptance_fields=len(ids),
                  specification_only_traces=len(traces), runtime_tests=0,
                  physical_testing=False, kind='Static audit checks, not runtime assertion totals')
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
