#!/usr/bin/env python3
"""Offline composition guards and normal source-entry checks; no target build."""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
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


def historical_pins():
    names = ('source-manifest.json', 'prepare_sources.py', 'application.patch')
    return {str(p.relative_to(ROOT)): digest(p)
            for name in names for p in sorted((ROOT / 'tests').rglob(name))
            if p.parent != HERE}


def load_preparer():
    spec = importlib.util.spec_from_file_location('previous_repeat_scope_prepare', HERE / 'prepare_sources.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-composed', type=pathlib.Path, required=True)
    parser.add_argument('--candidate-composed', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.results.exists(), 'RESULTS_ALREADY_EXIST'
    selected = load_preparer()
    pin = selected.pin()
    before = {r['file']: r['sha256'] for r in pin['before'] + pin['unchanged']}
    after = {r['file']: r['sha256'] for r in pin['after'] + pin['unchanged']}
    historical_before = historical_pins()
    baseline_before = selected.inventory(args.baseline_composed)
    candidate_before = selected.inventory(args.candidate_composed)
    rows, assertions = [], 0

    def check(value, reason):
        nonlocal assertions
        assertions += 1
        assert value, reason

    def refused(call, reason):
        try:
            call()
        except AssertionError:
            check(True, reason)
        else:
            raise AssertionError(reason)

    check(len(before) == len(after) == len(pin['before']) + len(pin['unchanged']) == 201,
          'Incomplete or duplicate source inventory')
    check(baseline_before == before, 'Baseline is not the exact reviewed composition')
    check(candidate_before == after, 'Candidate is not the exact new composition')
    check({name for name in before if before[name] != after[name]} == {'core.cpp'},
          'Compiler-only boundary widened')
    check(len(selected.verify_final(args.candidate_composed)) == 201, 'Final inventory incomplete')
    rows.append(dict(name='complete_201_file_compiler_only_boundary', status='PASS', changed=1, unchanged=200))

    # The existing ordinary runtime, backend, settings/auth, editor and static
    # response files must remain byte-identical, rather than merely share names.
    for name in ('core.h', 'adapter.cpp', 'adapter.h', 'seam.inc', 'backend_lease.inc',
                 'hid_backend.cpp', 'com.cpp', 'settings.cpp', 'cli.cpp', 'storage.cpp',
                 'webserver.cpp', 'webfiles.h', 'caps_trial.h'):
        check((args.baseline_composed / name).read_bytes() == (args.candidate_composed / name).read_bytes(),
              'Unrelated accepted behavior source changed: ' + name)
    rows.append(dict(name='runtime_backend_privacy_editor_and_identity_unchanged', status='PASS'))

    with tempfile.TemporaryDirectory(prefix='previous-repeat-scope-') as temporary:
        temporary = pathlib.Path(temporary)
        replay = temporary / 'replay'
        shutil.copytree(args.baseline_composed, replay)
        selected.delta(replay)
        check(selected.inventory(replay) == after, 'Exact replay differs from candidate')
        check(len(selected.verify_final(replay)) == 201, 'Replayed candidate not verified')
        refused(lambda: selected.delta(replay), 'Repeated overlay was accepted')
        rows.append(dict(name='zero_fuzz_replay_and_repeated_delta_refusal', status='PASS'))

        refused(lambda: selected.verify_final(args.baseline_composed), 'Omitted new delta was accepted')
        old_core = temporary / 'old-core'
        shutil.copytree(args.candidate_composed, old_core)
        (old_core / 'core.cpp').write_bytes((args.baseline_composed / 'core.cpp').read_bytes())
        refused(lambda: selected.verify_final(old_core), 'Historical core substituted for new compiler')
        wrong_core = temporary / 'wrong-core'
        shutil.copytree(args.baseline_composed, wrong_core)
        (wrong_core / 'core.cpp').write_bytes((wrong_core / 'core.cpp').read_bytes() + b'\n')
        original = selected.inventory(wrong_core)
        refused(lambda: selected.delta(wrong_core), 'Modified parent core was accepted')
        check(selected.inventory(wrong_core) == original, 'Rejected core input was modified')
        rows.append(dict(name='omitted_delta_old_core_and_modified_parent_refused', status='PASS'))

        wrong_other = temporary / 'wrong-other'
        shutil.copytree(args.candidate_composed, wrong_other)
        (wrong_other / 'adapter.cpp').write_bytes((wrong_other / 'adapter.cpp').read_bytes() + b'\n')
        refused(lambda: selected.verify_final(wrong_other), 'Unrelated source tampering accepted')
        extra = temporary / 'extra-source'
        shutil.copytree(args.candidate_composed, extra)
        (extra / 'unexpected.cpp').write_text('// extra public test fixture\n')
        refused(lambda: selected.verify_final(extra), 'Unexpected source file accepted')
        linked = temporary / 'linked-source'
        shutil.copytree(args.candidate_composed, linked)
        (linked / 'core.cpp').unlink()
        (linked / 'core.cpp').symlink_to(args.candidate_composed.resolve() / 'core.cpp')
        refused(lambda: selected.verify_final(linked), 'Source symlink accepted')
        rows.append(dict(name='unrelated_tamper_extra_file_and_symlink_refused', status='PASS'))

        # Exercise the actual canonical entry with the explicitly nonbuilding
        # mode. A historical selector cannot pass this check by omitting delta.
        output = temporary / 'normal-entry'
        command = [sys.executable, str(ROOT / 'tools/build_routeb_candidate.py'),
                   '--compose-only', '--from-composed', str(args.baseline_composed),
                   '--output-dir', str(output)]
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                             timeout=120, env=environment)
        check(run.returncode == 0, 'Normal source entry failed: ' + run.stderr)
        check(not run.stderr, 'Normal source entry emitted unexpected stderr')
        proof = json.loads((output / 'composition.json').read_text())
        check(proof['selected_preparer'] == 'tests/previous_command_repeat/prepare_sources.py',
              'Canonical entry selected an older overlay')
        check(proof['selected_manifest_sha256'] == digest(HERE / 'source-manifest.json'),
              'Canonical entry selected another manifest')
        check(proof['source_count'] == 201 and proof['changed_sources'] == ['core.cpp']
              and proof['unchanged_sources'] == 200, 'Composition boundary receipt differs')
        check(proof['firmware_built'] is False and proof['target_build_ready'] is False
              and proof['hardware_access'] is False, 'Source-only stage overclaimed delivery')
        check(selected.inventory(pathlib.Path(proof['source'])) == after, 'Normal entry omitted or changed delta')
        check(len(selected.verify_final(output / 'EvilDuckS3')) == 201, 'Normal output failed final verification')
        rows.append(dict(name='actual_normal_entry_selects_complete_new_source_overlay', status='PASS',
                         mode='--compose-only', firmware_built=False))

        wrong_parent = temporary / 'wrong-parent'
        shutil.copytree(args.baseline_composed, wrong_parent)
        (wrong_parent / 'adapter.cpp').write_bytes((wrong_parent / 'adapter.cpp').read_bytes() + b'\n')
        check(digest(wrong_parent / 'core.cpp') == before['core.cpp'],
              'Normal-entry unrelated-tamper control changed the core too')
        refused_output = temporary / 'refused-output'
        bad_command = list(command)
        bad_command[bad_command.index('--from-composed') + 1] = str(wrong_parent)
        bad_command[bad_command.index('--output-dir') + 1] = str(refused_output)
        denied = subprocess.run(bad_command, cwd=ROOT, capture_output=True, text=True,
                                timeout=120, env=environment)
        check(denied.returncode != 0, 'Normal entry accepted an unrelated changed source')
        check(not refused_output.exists(), 'Normal entry wrote output before rejecting wrong parent')
        rows.append(dict(name='normal_entry_rejects_nonexact_parent_before_output', status='PASS'))

    # Inspect, rather than invoke, the no-flag/default boundary. No target build
    # is attempted even as a negative control in this stage.
    tree = ast.parse((HERE / 'build_candidate.py').read_text())
    main_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
    compose_flag = next(n for n in ast.walk(main_node) if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Attribute) and n.func.attr == 'add_argument'
                        and n.args and isinstance(n.args[0], ast.Constant)
                        and n.args[0].value == '--compose-only')
    options = {k.arg: k.value for k in compose_flag.keywords}
    check(isinstance(options.get('action'), ast.Constant) and options['action'].value == 'store_true'
          and ('default' not in options or isinstance(options['default'], ast.Constant)
               and options['default'].value is False), 'Source-only mode can be enabled without an explicit flag')
    guard = next(n for n in main_node.body if isinstance(n, ast.If)
                 and isinstance(n.test, ast.UnaryOp) and isinstance(n.test.op, ast.Not)
                 and isinstance(n.test.operand, ast.Attribute) and n.test.operand.attr == 'compose_only')
    check(len(guard.body) == 1 and isinstance(guard.body[0], ast.Expr)
          and isinstance(guard.body[0].value, ast.Call)
          and isinstance(guard.body[0].value.func, ast.Attribute)
          and isinstance(guard.body[0].value.func.value, ast.Name)
          and guard.body[0].value.func.value.id == 'parser'
          and guard.body[0].value.func.attr == 'error', 'Default target refusal is not unconditional argparse failure')
    check(isinstance(guard.body[0].value.args[0], ast.Constant)
          and guard.body[0].value.args[0].value.startswith('SOURCE_ONLY_STAGE:'),
          'Default target refusal lacks explicit source-only explanation')
    compose_call = next(n for n in main_node.body if isinstance(n, ast.Assign)
                        and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
                        and n.value.func.id == 'compose')
    check(main_node.body.index(guard) < main_node.body.index(compose_call), 'Output can precede default refusal')
    imported = {alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names}
    check(imported == {'argparse', 'json', 'pathlib', 'shutil', 'sys', 'prepare_sources'},
          'Source-only entry imported another execution path')
    rows.append(dict(name='default_target_build_fail_closed_inspected_without_execution', status='PASS',
                     default_build_invoked=False))

    check(historical_pins() == historical_before, 'Historical manifests, patches or preparers changed')
    check(selected.inventory(args.baseline_composed) == baseline_before, 'Supplied baseline changed')
    check(selected.inventory(args.candidate_composed) == candidate_before, 'Supplied candidate changed')
    rows.append(dict(name='historical_pins_and_supplied_sources_preserved', status='PASS',
                     historical_pin_files=len(historical_before)))
    result = dict(counts=dict(PASS=len(rows), FAIL=0), assertions=assertions, results=rows,
                  baseline_core_sha256=before['core.cpp'], candidate_core_sha256=after['core.cpp'],
                  scope='Public source-copy composition and static entry inspection only; no target compiler, package, device or owner files',
                  target_build_invoked=False, hardware_access=False)
    args.results.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
