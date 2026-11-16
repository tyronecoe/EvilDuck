#!/usr/bin/env python3
"""Focused offline DEFINE selection controls. No compiler or target artifacts.

Uses the existing nested import probe up to (and stopping before) the actual
compiler driver. Real Git refusal controls use a disposable local clone only.
"""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load(HERE / 'build_candidate.py', 'define_prebuild_builder')
V = load(HERE / 'verify_target.py', 'define_prebuild_target')
R = load(HERE / 'verify_release.py', 'define_prebuild_release')
M = load(HERE / 'prepare_sources.py', 'define_prebuild_sources')
SOURCE = None
ADMISSION = None
RESULT = dict(mutations_rejected=[], nested_probes=[], syntax_only={})


class Controls(unittest.TestCase):
    def reject(self, name, transform):
        with tempfile.TemporaryDirectory(prefix='define-source-control-') as folder:
            source = pathlib.Path(folder) / 'source'
            shutil.copytree(SOURCE, source)
            transform(source)
            with self.assertRaises((ValueError, AssertionError)):
                V.verify_composed_source(source)
            RESULT['mutations_rejected'].append(name)

    def test_01_exact201_and_only_two_admission_deltas(self):
        proof = V.verify_composed_source(SOURCE)
        old = M.A.inventory(ADMISSION)
        new = M.inventory(SOURCE)
        self.assertEqual(set(new), set(old))
        self.assertEqual(len(new), 201)
        self.assertEqual({n for n in old if old[n] != new[n]}, {'core.cpp', 'caps_trial.h'})
        self.assertEqual(new['core.cpp'], M.CORE_SHA)
        self.assertEqual(proof['build_id'], M.BUILD_ID)
        RESULT['production_inventory'] = M.verify_final(SOURCE)

    def test_02_old_core_overlay_omitted(self):
        self.reject('omitted overlay/old core', lambda s: shutil.copyfile(ADMISSION / 'core.cpp', s / 'core.cpp'))

    def test_03_old_identity(self):
        self.reject('old build ID', lambda s: shutil.copyfile(ADMISSION / 'caps_trial.h', s / 'caps_trial.h'))

    def test_04_missing_identity(self):
        def mutate(s):
            p = s / 'caps_trial.h'
            p.write_bytes(p.read_bytes().replace(M.BUILD_ID.encode(), b'', 1))
        self.reject('missing build ID', mutate)

    def test_05_extra_source(self):
        self.reject('extra production source', lambda s: (s / 'unexpected.cpp').write_text('// refused\n'))

    def test_06_missing_source(self):
        self.reject('missing production source', lambda s: (s / 'coordinator.cpp').unlink())

    def test_07_unrelated_production_drift(self):
        for name in ['core.h', 'adapter.cpp', 'adapter.h', 'coordinator.cpp', 'hid_backend.cpp', 'webserver.cpp', 'webfiles.h', 'cli.cpp']:
            def mutate(s, n=name):
                p = s / n
                p.write_bytes(p.read_bytes() + b'\n')
            self.reject('drift: ' + name, mutate)

    def test_08_identity_layer_cannot_repeat(self):
        with tempfile.TemporaryDirectory(prefix='define-double-overlay-') as folder:
            source = pathlib.Path(folder) / 'source'
            shutil.copytree(SOURCE, source)
            with self.assertRaises(AssertionError):
                M.delta(source)
            self.assertEqual(M.inventory(source), M.inventory(SOURCE))
        RESULT['mutations_rejected'].append('identity applied twice')

    def probe(self, text):
        helper = load(ROOT / 'tests/usb_os_observer_v2_release/test_verify_controls.py', 'define_actual_selector_probe')
        helper.HERE = HERE
        return helper._v2_probe_nested_selection(text)

    def test_09_actual_nested_selection(self):
        text, audit = B.adapted_source('a' * 40)
        selected = self.probe(text)
        self.assertEqual(selected['preparer'], HERE / 'prepare_sources.py')
        self.assertEqual(selected['verifier'], HERE / 'verify_target.py')
        self.assertEqual(selected['verifier_globals'], selected['verifier'])
        self.assertEqual(selected['build_id'], B.BUILD_ID)
        RESULT['nested_probes'].append({k: str(v) for k, v in selected.items()})
        RESULT['builder_adaptations'] = audit

    def test_10_old_nested_preparer_rejected(self):
        text, _ = B.adapted_source('a' * 40)
        wrong = text.replace("text=text.replace('lock_feedback','define_statements_release')", "text=text.replace('lock_feedback','admission_diagnostics_release')", 1)
        self.assertNotEqual(wrong, text)
        with self.assertRaisesRegex(AssertionError, 'Nested builder selected old preparer'):
            self.probe(wrong)
        RESULT['mutations_rejected'].append('old nested preparer')

    def test_11_old_nested_verifier_rejected(self):
        text, _ = B.adapted_source('a' * 40)
        wrong = text.replace("target_path = ROOT / 'tests/define_statements_release/verify_target.py'", "target_path = ROOT / 'tests/admission_diagnostics_release/verify_target.py'", 1)
        self.assertNotEqual(wrong, text)
        with self.assertRaises(AssertionError):
            self.probe(wrong)
        RESULT['mutations_rejected'].append('old nested verifier')

    def test_12_all190_frozen_assert_nodes_retained(self):
        ns, audit = R.adapted_parent()
        final = {r['file']: r['sha256'] for r in M.pin()['cumulative_h1_after']}
        counts = [('h1_right_modifiers', 23), ('inject_var_experimental', 21), ('lock_wait_timeout', 16), ('source_text_v2', 46), ('lock_feedback', 25), ('caps_stop', 59)]
        actual = []
        for directory, count in counts:
            path = ROOT / 'tests' / directory / 'verify_link.py'
            self.assertEqual(V.sha(path), ns['FROZEN'][directory])
            original = ast.parse(path.read_text())
            self.assertEqual(sum(isinstance(n, ast.Assert) for n in ast.walk(original)), count)
            transformed = ns['FinalCandidateExpectations'](final).visit(original)
            transformed = ns['RuntimeIdentityExpectations'](original).visit(transformed)
            if directory == 'h1_right_modifiers':
                handler = R.P.CompilerHandlerExpectations()
                transformed = handler.visit(transformed)
                self.assertEqual(len(handler.edits), 2)
            self.assertEqual(sum(isinstance(n, ast.Assert) for n in ast.walk(transformed)), count)
            actual.append(dict(file=str(path.relative_to(ROOT)), sha256=V.sha(path), assert_nodes=count))
        self.assertEqual(sum(row['assert_nodes'] for row in actual), 190)
        with self.assertRaises(AssertionError):
            ns['FinalCandidateExpectations']({k: v for k, v in final.items() if k != 'adapter.cpp'})
        RESULT['syntax_only']['frozen_assert_nodes'] = actual
        RESULT['release_adaptations'] = audit

    def test_13_target_context_and_predicates(self):
        ns, audit = V.adapted_parent()
        ns['parent_namespace']()
        self.assertEqual(pathlib.Path(ns['__file__']).resolve(), HERE / 'verify_target.py')
        self.assertEqual(audit['active_verifier_context']['build_id'], M.BUILD_ID)
        self.assertGreater(audit['admission_diagnostics']['predicates_retained']['require_calls'], 0)
        RESULT['target_adaptations'] = audit

    def test_14_frozen_admission_adapters_retain_predicates(self):
        for module in [B, V, R]:
            audit = module.DEFINE_ADAPTATION
            self.assertEqual(V.sha(ROOT / audit['parent']), audit['sha256'])
            RESULT['syntax_only'][audit['parent']] = audit['syntax_predicates_retained']

    def test_15_profile_and_no_resume_bypass(self):
        text, _ = B.adapted_source('a' * 40)
        self.assertIn('assert "--verify-existing" not in sys.argv', text)
        self.assertIn('assert "--selector-off" not in sys.argv and "--diagnostics-off" not in sys.argv', text)
        self.assertIn('inherited_safety_predicates_removed=0', text)
        self.assertEqual(text.count('tests/define_statements_release/prepare_sources.py'), 4)
        # Frozen whole-file identities retain the actual dependency/SDK/profile,
        # partition, USB, startup, stack, RAM and link conditions, not token mocks.
        names = ['tools/s3_validation.py', 'tools/feedback_core.py', 'tools/verify_patched_firmware.py', 'tests/caps_stop/build_candidate.py', 'tests/privacy_fix1/verify_target.py', 'tests/static_response_build_integration/verify_target.py', 'tests/define_labels_release/verify_target.py', 'tests/usb_os_observer_release/verify_target.py', 'tests/usb_os_observer_v2_release/verify_target.py']
        baseline = 'bf339ad383e67c5ee3bb9df1a57bafe15acca8ed'
        guards = []
        for name in names:
            blob = subprocess.check_output(['git', 'show', baseline + ':' + name], cwd=ROOT)
            self.assertEqual(blob, (ROOT / name).read_bytes())
            guards.append(dict(file=name, sha256=V.sha(ROOT / name)))
        RESULT['unchanged_safety_guards'] = guards

    def test_16_committed_source_positive_gate(self):
        value = B.build_inputs()
        names = {r['file'] for r in value['files']}
        for directory in ['tests/define_statements', 'tests/define_statements_release']:
            self.assertTrue({str(p.relative_to(ROOT)) for p in (ROOT / directory).rglob('*') if p.is_file()}.issubset(names))
        self.assertEqual(value['source_commit'], subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
        RESULT['committed_build_inputs'] = value

    def test_17_real_git_input_refusals(self):
        with tempfile.TemporaryDirectory(prefix='define-git-controls-') as folder:
            clone = pathlib.Path(folder) / 'checkout'
            subprocess.run(['git', 'clone', '--shared', '--quiet', '--no-checkout', str(ROOT), str(clone)], check=True, capture_output=True)
            subprocess.run(['git', 'checkout', '--quiet', '--detach', 'HEAD'], cwd=clone, check=True, capture_output=True)
            helper = clone / 'tests/define_statements_release/native/journal.cpp'
            original = helper.read_bytes()
            command = [sys.executable, '-B', str(clone / 'tests/define_statements_release/guard_probe.py')]
            # The clone alone is deliberately mutated; the source checkpoint
            # and all original evidence remain untouched.
            helper.write_bytes(original + b'\n')
            dirty = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(dirty.returncode, 1)
            self.assertIn('Commit the selected build checkpoint first', dirty.stderr)
            helper.write_bytes(original)
            extra = clone / 'tests/define_statements_release/uncommitted-input.txt'
            extra.write_text('negative control only\n')
            untracked = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(untracked.returncode, 1)
            self.assertIn('uncommitted-input.txt', untracked.stderr)
            extra.unlink()
            # Hide a selected byte mismatch from Git's normal working-tree
            # diff in this disposable clone. The independent git-show byte
            # comparison must still refuse it.
            subprocess.run(['git', 'update-index', '--assume-unchanged', str(helper.relative_to(clone))], cwd=clone, check=True)
            helper.write_bytes(original + b'\n')
            self.assertEqual(subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=clone), b'')
            mismatch = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(mismatch.returncode, 1)
            self.assertIn('native/journal.cpp', mismatch.stderr)
            RESULT['git_refusals'] = [dict(name=n, command=command, exit=p.returncode, stdout=p.stdout, stderr=p.stderr) for n, p in [('dirty', dirty), ('uncommitted', untracked), ('mismatched', mismatch)]]
            RESULT['mutations_rejected'] += ['dirty inputs', 'uncommitted input', 'mismatched committed input']


def main():
    global SOURCE, ADMISSION
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=pathlib.Path, required=True)
    parser.add_argument('--admission-source', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    SOURCE, ADMISSION = args.source, args.admission_source
    assert not args.output.exists(), 'Keep original control evidence'
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2, failfast=True).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    RESULT.update(status='PASS' if result.wasSuccessful() else 'BLOCKED', scenario_groups_executed=result.testsRun, failures=len(result.failures), errors=len(result.errors), output=stream.getvalue(), firmware_compilation_attempts=0, runtime_assertion_total='not emitted by unittest; syntax counts are separate')
    args.output.write_text(json.dumps(RESULT, indent=2) + '\n')
    print(stream.getvalue())
    return int(not result.wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
