#!/usr/bin/env python3
"""Reconstruct the recorded local build source context; never invoke a compiler.

Developer-only, not an installer or a prerequisite for owner package preflight.
Preserves original build inputs: detached old base + exact post-build Git blobs.
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECKPOINT = '1664d4f25593e6cc99dba43ff0e5d74531555a51'
BASE = '805d989c3ac50cb96025862c95916830c59f8ba7'
INPUT_SHA = '525fc3f9e95c65f81a1233f3f31eac1f321233d0dd87ac2517d5a4c2f2eab768'


def git(*args):
    return subprocess.check_output(['git'] + list(args), cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', default=CHECKPOINT)
    parser.add_argument('--local-inputs', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert args.checkpoint == CHECKPOINT and re.fullmatch('[0-9a-f]{40}', args.checkpoint)
    assert not args.output.exists() and not args.results.exists()
    assert ROOT != args.output.resolve() and ROOT not in args.output.resolve().parents
    raw = args.local_inputs.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == INPUT_SHA
    pin = json.loads(raw)
    assert pin['source_base_commit'] == BASE and pin['source_commit_contains_changes'] is False
    artifact = json.loads(git('show', CHECKPOINT + ':docs/editor-build-integration-artifacts.json'))
    assert artifact['source_base_commit'] == BASE and artifact['local_inputs_sha256'] == INPUT_SHA
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, CHECKPOINT], cwd=ROOT, check=True)
    refs = git('show-ref')
    base_names = set(git('ls-tree', '-r', '--name-only', BASE).decode().splitlines())
    rows = pin['files']
    assert len(rows) == 17 and len({r['file'] for r in rows}) == 17
    stored = []
    for row in rows:
        name = row['file']
        path = pathlib.PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts and name not in base_names
        assert '.git' not in path.parts
        data = git('show', CHECKPOINT + ':' + name)
        assert len(data) == row['size'] and hashlib.sha256(data).hexdigest() == row['sha256']
        stored.append((name, data))
    subprocess.run(['git', 'worktree', 'add', '--detach', str(args.output), BASE], cwd=ROOT, check=True)
    for name, data in stored:
        path = args.output / name
        assert not path.exists()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    command = [sys.executable, '-B', '-c',
               "import sys,json;sys.path.insert(0,'tests/editor_build_integration');"
               "import build_candidate;sys.stdout.write(json.dumps(build_candidate.local_inputs(),indent=2)+'\\n')"]
    reproduced = subprocess.check_output(command, cwd=args.output)
    assert reproduced == raw, 'Reconstructed normal builder input manifest differs'
    assert git('show-ref') == refs, 'Historical refs changed during detached source reconstruction'
    result = dict(status='SOURCE_RECONSTRUCTED_ONLY', source_checkpoint=CHECKPOINT,
                  source_checkpoint_role='Post-build attestation of exact original local inputs',
                  original_source_base_commit=BASE, materialized_files=17,
                  local_inputs_sha256=hashlib.sha256(reproduced).hexdigest(),
                  worktree=str(args.output), compiler_invoked=False, firmware_rebuilt=False,
                  hardware=False, refs_unchanged=True)
    args.results.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
