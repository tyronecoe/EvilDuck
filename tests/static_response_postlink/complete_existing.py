#!/usr/bin/env python3
"""Complete the recorded C post-compile verification phase; never compile firmware.

This narrowly scoped recovery applies only to the one recorded clean application
whose host-side constant decoder rejected valid MOVI/ADDMI output. The unchanged
C builder's fresh compile prefix is NOT rerun or made generally resumable. Its
exact post-compile target/release tail is executed with recorded C source inputs,
and the separately committed host-verifier context is reported explicitly.
"""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD_MODULE = ROOT / 'tests/static_response_build_integration/build_candidate.py'
VERIFY_MODULE = ROOT / 'tests/static_response_build_integration/verify_target.py'
COMPILE_COMMIT = '68f7fb2de5af2988a3136eb9222fb8c3e7dee8f5'
APPLICATION_SHA = 'd5fe0932fe915443a5e53030969c6792409f719d427681304a7102355b2d7946'
ELF_SHA = '4f530f7e0eb330585faaed3311de7b6b4227514b2517f6d6c36615da128e9c44'
INPUT_SHA = '9a3ff6f4f4ff312bd0b353bf72fbbf1e17fe82d2a28f97ad62c4ed7c17295d0d'
SNAPSHOT_SHA = 'b47a22ff4cec6eb4895423e61aee6cb6740b83d31ee8975a7d09220af2652cf9'
TAIL_MARKER = '    assert len(calls) == 1, "Target compile did not execute the selected privacy overlay"\n'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(pathlib.Path(path).read_bytes())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def firmware_inventory(source):
    rows = {}
    for p in pathlib.Path(source).rglob('*'):
        assert not p.is_symlink(), 'No source symlinks'
        if p.is_file():
            rows[str(p.relative_to(source))] = dict(size=p.stat().st_size, sha256=sha(p))
    assert len(rows) == 201
    return rows


def snapshot_inputs(build_root, snapshot):
    assert sha(snapshot / 'report.json') == SNAPSHOT_SHA, 'Wrong original clean compile snapshot'
    original = json.loads((snapshot / 'report.json').read_text())
    assert original['status'] == 'PASS' and original['verification_resumed'] is False
    assert '--clean' in original['command'] and '--verbose' in original['command']
    data = (snapshot / 'build-inputs.json').read_bytes()
    assert digest(data) == INPUT_SHA and (build_root / 'build-inputs.json').read_bytes() == data
    inputs = json.loads(data)
    assert inputs['source_commit'] == COMPILE_COMMIT and len(inputs['files']) == 26
    assert inputs['source_commit_contains_changes'] is True and inputs['uncommitted_local_changes'] is False
    for row in inputs['files']:
        blob = subprocess.check_output(['git', 'show', COMPILE_COMMIT + ':' + row['file']], cwd=ROOT)
        assert len(blob) == row['size'] and digest(blob) == row['sha256'], row['file']
    expected = {r['file'].removeprefix('EvilDuckS3/'): dict(size=r['size'], sha256=r['sha256'])
                for r in original['source_inventory']}
    actual = firmware_inventory(build_root / 'candidate/EvilDuckS3')
    assert actual == expected
    for name, expected_sha in [('EvilDuckS3.ino.bin', APPLICATION_SHA), ('EvilDuckS3.ino.elf', ELF_SHA)]:
        assert sha(build_root / 'build' / name) == sha(snapshot / 'build' / name) == expected_sha
    for row in original['artifacts']:
        p = build_root / 'build' / row['file']
        assert sha(p) == row['sha256'] and p.stat().st_size == row['size'], row['file']
    proof = json.loads((snapshot / 'static-response-composition.json').read_text())
    assert proof['source_commit'] == COMPILE_COMMIT and proof['overlay_calls'] == 1
    assert proof['source_inventory'] == original['source_inventory']
    assert (build_root / 'static-response-composition.json').read_bytes() == (snapshot / 'static-response-composition.json').read_bytes(), 'Original composition proof changed'
    return original, inputs, actual, proof


def postcompile_source(source, proof):
    """Keep the exact C target-verification tail, recording the skipped prefix."""
    assert source.count('def main():\n') == source.count(TAIL_MARKER) == 1
    opening = source.index('def main():\n') + len('def main():\n')
    marker = source.index(TAIL_MARKER)
    suffix = source.index("\n\nif __name__", marker)
    original_prefix, tail = source[opening:marker], source[marker:suffix]
    parsed = ast.parse(source)
    main = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    olds = [n.value.value for n in main.body if isinstance(n, ast.Assign) and
            any(isinstance(t, ast.Name) and t.id == 'old' for t in n.targets) and
            isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)]
    assert len(olds) == 1
    setup = '''    assert sys.argv.count('--verify-existing') == 1, 'Completion-only flag required'
    assert '--selector-off' not in sys.argv and '--diagnostics-off' not in sys.argv
    output = pathlib.Path(sys.argv[sys.argv.index('--output-dir') + 1])
    import prepare_sources as privacy
    before_inputs = LOCAL_INPUTS()
    recorded = json.loads((output / 'static-response-composition.json').read_text())
    assert recorded['source_commit'] == CHECKPOINT and recorded['overlay_calls'] == 1
    assert recorded['source_inventory'] == expected_inventory(output / 'candidate/EvilDuckS3')
    privacy.verify_final(output / 'candidate/EvilDuckS3')
    calls = [str(output / 'candidate/EvilDuckS3')] * recorded['overlay_calls']
    old = ''' + repr(olds[0]) + '\n'
    result = source[:opening] + setup + tail + source[suffix:]
    compile(result, 'completion-tail', 'exec')
    evidence = dict(mode='COMPLETION_OF_RECORDED_C_POSTCOMPILE_TAIL',
                    original_adapted_source_sha256=digest(source.encode()),
                    skipped_fresh_compile_prefix_sha256=digest(original_prefix.encode()),
                    skipped_fresh_compile_prefix=original_prefix,
                    unmodified_postcompile_tail_sha256=digest(tail.encode()),
                    completion_setup_sha256=digest(setup.encode()), completion_setup=setup,
                    completion_adapted_source_sha256=digest(result.encode()),
                    original_overlay_calls=proof['overlay_calls'],
                    firmware_compilation_prefix_rerun=False,
                    all_target_and_release_predicates_after_compile_preserved=True)
    return result, evidence


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-root', type=pathlib.Path, required=True)
    p.add_argument('--snapshot', type=pathlib.Path, required=True)
    p.add_argument('--results', type=pathlib.Path, required=True)
    p.add_argument('--verify-existing', action='store_true', required=True)
    args = p.parse_args()
    assert args.verify_existing and not args.results.exists(), 'Fresh completion receipt required'
    root, snapshot = args.build_root.resolve(), args.snapshot.resolve()
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT), 'Commit host verifier context first'
    helper_path = str(pathlib.Path(__file__).resolve().relative_to(ROOT))
    assert subprocess.check_output(['git', 'show', 'HEAD:' + helper_path], cwd=ROOT) == pathlib.Path(__file__).read_bytes()
    original, recorded, inventory, proof = snapshot_inputs(root, snapshot)
    builder_bytes = subprocess.check_output(['git', 'show', COMPILE_COMMIT + ':tests/static_response_build_integration/build_candidate.py'], cwd=ROOT)
    assert builder_bytes == BUILD_MODULE.read_bytes(), 'Normal C builder must remain unchanged'
    verifier = load(VERIFY_MODULE, 'static_response_postlink_verifier')
    provenance = verifier.verify_input_manifest(root)
    delta = provenance.get('post_compile_verifier_delta')
    assert delta and delta['path'] == 'tests/static_response_build_integration/verify_target.py'
    assert delta['compile_source_commit'] == COMPILE_COMMIT and delta['git_compile_blob_verified'] is True
    assert delta['git_verifier_blob_verified'] is True
    assert len(provenance['verifier_context_commit']) == 40
    before = dict(application_sha256=sha(root / 'build/EvilDuckS3.ino.bin'),
                  elf_sha256=sha(root / 'build/EvilDuckS3.ino.elf'), inputs_sha256=sha(root / 'build-inputs.json'))
    assert not (root / 'static-response-release-verification.json').exists(), 'Preserve existing successful receipt'
    assert (root / 'report.json').read_bytes() == (snapshot / 'report.json').read_bytes(), 'Unexpected prior verification report'
    B = load(BUILD_MODULE, 'recorded_c_normal_builder')
    original_adapter = B.adapted_source
    adaptation = {}

    def recorded_inputs():
        assert sha(root / 'build-inputs.json') == INPUT_SHA
        return copy.deepcopy(recorded)

    def resume_adapter(commit):
        assert commit == COMPILE_COMMIT
        source, changes = original_adapter(commit)
        adapted, evidence = postcompile_source(source, proof)
        adaptation.update(evidence)
        return adapted, dict(changes, post_compile_completion=dict(evidence, helper_sha256=sha(__file__)))

    popen, commands = subprocess.Popen, []

    def inspect_command(command, *pa, **kw):
        assert not kw.get('shell') and isinstance(command, (list, tuple)), 'No shell commands in completion'
        words = [str(x) for x in command]
        executable = pathlib.Path(words[0]).name.lower()
        forbidden_device = {'--port', 'write_flash', 'read_flash', 'erase_flash', 'erase_region', 'flash_id', 'upload'}
        assert not forbidden_device.intersection(words), 'Device operation forbidden'
        assert not (('arduino' in executable and 'compile' in words) or
                    executable.endswith(('-g++', '-gcc')) or executable in {'g++', 'gcc', 'c++', 'cc'}), 'Firmware compile/link forbidden'
        commands.append(words)
        return popen(command, *pa, **kw)

    prior_args, prior_path = sys.argv, list(sys.path)
    try:
        sys.path.insert(0, str(ROOT / 'tests/static_response_build_integration'))
        sys.argv = [str(ROOT / 'tools/build_routeb_candidate.py'), '--output-dir', str(root), '--verify-existing']
        with patch.object(B, 'build_inputs', recorded_inputs), patch.object(B, 'adapted_source', resume_adapter), patch.object(subprocess, 'Popen', inspect_command):
            assert B.main() == 0
    finally:
        sys.argv, sys.path[:] = prior_args, prior_path
        assert sha(root / 'build/EvilDuckS3.ino.bin') == before['application_sha256']
        assert sha(root / 'build/EvilDuckS3.ino.elf') == before['elf_sha256']
        assert sha(root / 'build-inputs.json') == before['inputs_sha256'] == INPUT_SHA
        assert firmware_inventory(root / 'candidate/EvilDuckS3') == inventory
    result = json.loads((root / 'report.json').read_text())
    result.update(post_compile_verification_resumed=True, firmware_recompiled=False,
                  actual_compile_source_commit=COMPILE_COMMIT,
                  verifier_context_commit=provenance['verifier_context_commit'],
                  post_compile_verifier_delta=delta,
                  post_compile_completion_adapter=dict(helper_sha256=sha(__file__), **adaptation))
    (root / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    receipt = dict(status='PASS', actual_compile_source_commit=COMPILE_COMMIT,
                   verifier_context_commit=provenance['verifier_context_commit'], post_compile_verifier_delta=delta,
                   original_compile_snapshot_sha256=SNAPSHOT_SHA, original_inputs_sha256=INPUT_SHA,
                   immutable_artifacts=before, unchanged_source_entries=len(inventory),
                   post_compile_completion_adapter=dict(helper_sha256=sha(__file__), **adaptation),
                   commands=commands, firmware_recompiled=False, hardware=False,
                   release_receipt_sha256=sha(root / 'static-response-release-verification.json'))
    args.results.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in {'commands', 'post_compile_completion_adapter'}}, indent=2))


if __name__ == '__main__':
    main()
