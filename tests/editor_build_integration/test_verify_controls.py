#!/usr/bin/env python3
"""Offline verifier-policy controls; synthetic containers are not target evidence.

Use --source plus --unsafe-header for exact-composition omission controls.
No compiler, hardware, owner file, installer or external network interface.
"""
import argparse
import ast
import builtins
import hashlib
import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
SOURCE = None
UNSAFE_HEADER = None


def load(name):
    path = HERE / (name + '.py')
    spec = importlib.util.spec_from_file_location('editor_policy_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = load('verify_target')
R = load('verify_release')


class Policy(unittest.TestCase):
    def test_exact_pinned_target_and_release_adaptations(self):
        target, target_changes = V.adapted_parent()
        release, release_changes = R.adapted_parent()
        self.assertEqual(len(target_changes), 10)
        self.assertEqual(len(release_changes), 12)
        self.assertEqual(target['BUILD_ID'], V.BUILD_ID)
        self.assertEqual(release['BUILD_ID'], V.BUILD_ID)
        self.assertEqual(release['BASE_COMMIT'], V.BASE)
        self.assertTrue(all(row['occurrences'] > 0 for row in target_changes + release_changes))

    def test_inherited_guard_counts_and_helpers_retained(self):
        original = builtins.compile
        captured = {}
        relevant = {str(V.PARENT), str(ROOT / 'tests/privacy_fix1/verify_target.py')}

        def compile_audit(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kwargs):
            if str(filename) in relevant and mode == 'exec' and not flags & ast.PyCF_ONLY_AST:
                tree = original(source, filename, mode, flags | ast.PyCF_ONLY_AST, dont_inherit, optimize, **kwargs)
                captured[str(filename)] = sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and
                                               n.func.id == 'require' for n in ast.walk(tree))
            return original(source, filename, mode, flags, dont_inherit, optimize, **kwargs)

        with patch.object(builtins, 'compile', compile_audit):
            target, _ = V.adapted_parent()
            parent, _ = target['parent_namespace']()
        for path in relevant:
            tree = ast.parse(pathlib.Path(path).read_text())
            expected = sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'require'
                           for n in ast.walk(tree))
            self.assertEqual(captured[path], expected, path)
        privacy = pathlib.Path(ROOT / 'tests/privacy_fix1/verify_target.py')
        spec = importlib.util.spec_from_file_location('original_privacy_verification_helpers', privacy)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in ['source_matches', 'make_dependencies', '_profile_flags']:
            self.assertEqual(parent[name].__code__.co_code, getattr(module, name).__code__.co_code)
            self.assertEqual(parent[name].__code__.co_consts, getattr(module, name).__code__.co_consts)

    def test_actual_runtime_id_only_not_historical_source_identity(self):
        namespace, _ = R.adapted_parent()
        code = '''BUILD_ID = "ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1"
assert pin["build_id"] == BUILD_ID
assert BUILD_ID.encode() in elf.read_bytes()
assert b"ROUTEB-HISTORICAL-ID" in source.read_bytes()
'''
        tree = ast.parse(code)
        transform = namespace['RuntimeIdentityExpectations'](tree)
        changed = transform.visit(tree)
        self.assertEqual(len(transform.edits), 1)
        text = ast.unparse(changed)
        self.assertIn("pin['build_id'] == BUILD_ID", text)
        self.assertIn('ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1', text)
        self.assertIn(V.BUILD_ID, text)
        self.assertIn('ROUTEB-HISTORICAL-ID', text)

    def test_exact_resource_matcher_accepts_complete_synthetic_container(self):
        resources = {name: (name + ': synthetic policy bytes\0').encode() for name in
                     ['INDEX_HTML', 'INDEX_JS', 'SETTINGS_HTML', 'SETTINGS_JS', 'STYLE_CSS']}
        container = b'prefix\0' + b''.join(resources.values()) + b'suffix'
        result = V.verify_resource_bytes(resources, container, container)
        self.assertEqual(len(result), 5)
        self.assertTrue(all(row['elf_occurrences'] == row['binary_occurrences'] == 1 for row in result))

    def test_resource_omission_corruption_and_marker_only_rejected(self):
        resources = {'INDEX_JS': b'full reviewed script, not merely Retry load\0'}
        for elf, binary in [(b'older unsafe dashboard', b'older unsafe dashboard'),
                            (b'Retry load\0', b'Retry load\0'),
                            (resources['INDEX_JS'], resources['INDEX_JS'][:-2] + b'X\0'),
                            (resources['INDEX_JS'] * 2, resources['INDEX_JS'])]:
            with self.assertRaisesRegex(ValueError, 'Bundled resource FAIL'):
                V.verify_resource_bytes(resources, elf, binary)

    def test_committed_source_claim_and_wrong_base_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix='editor-local-provenance-control-') as temporary:
            path = pathlib.Path(temporary) / 'local-inputs.json'
            for change in [dict(source_base_commit='0' * 40), dict(source_commit_contains_changes=True),
                           dict(uncommitted_local_changes=False)]:
                values = dict(format='evilduck-local-build-inputs-v1', source_base_commit=V.BASE,
                              source_commit_contains_changes=False, uncommitted_local_changes=True, build_id=V.BUILD_ID)
                values.update(change)
                path.write_text(json.dumps(values))
                with self.assertRaisesRegex(ValueError, 'Local source provenance'):
                    V.verify_local_inputs(temporary)


class Composition(unittest.TestCase):
    def test_exact_final_composition(self):
        result = V.verify_composed_source(SOURCE)
        self.assertEqual(result['source_files'], 201)
        self.assertEqual(result['webfiles_sha256'], V.REVIEWED_HEADER_SHA)

    def test_omitted_reviewed_editor_overlay_rejected(self):
        self.assertEqual(hashlib.sha256(UNSAFE_HEADER.read_bytes()).hexdigest(),
                         '7b4be141c776fc2c8d83b6532c62b9c4b9baa033261ce16c60e509dddaea4eab')
        with tempfile.TemporaryDirectory(prefix='editor-omitted-overlay-control-') as temporary:
            target = pathlib.Path(temporary) / 'candidate'
            shutil.copytree(SOURCE, target)
            shutil.copyfile(UNSAFE_HEADER, target / 'webfiles.h')
            with self.assertRaisesRegex(ValueError, 'unsafe/omitted overlay'):
                V.verify_composed_source(target)

    def test_old_candidate_identity_rejected(self):
        with tempfile.TemporaryDirectory(prefix='editor-old-identity-control-') as temporary:
            target = pathlib.Path(temporary) / 'candidate'
            shutil.copytree(SOURCE, target)
            header = target / 'caps_trial.h'
            header.write_bytes(header.read_bytes().replace(V.BUILD_ID.encode(), V.OLD_BUILD_ID.encode()))
            with self.assertRaisesRegex(ValueError, 'unsafe/omitted overlay'):
                V.verify_composed_source(target)


def main():
    global SOURCE, UNSAFE_HEADER
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy-only', action='store_true')
    parser.add_argument('--source', type=pathlib.Path)
    parser.add_argument('--unsafe-header', type=pathlib.Path)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.results.exists()
    assert args.policy_only or (args.source is not None and args.unsafe_header is not None), 'Source paths required for composition controls'
    SOURCE, UNSAFE_HEADER = args.source, args.unsafe_header
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Policy)])
    if not args.policy_only:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Composition))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = dict(counts=dict(PASS=result.testsRun-len(result.failures)-len(result.errors), FAIL=len(result.failures)+len(result.errors)),
                  policy_only=args.policy_only, target_firmware_executed=False, actual_elf_or_bin_verification=False,
                  scope='Synthetic matcher/provenance policy plus disposable public source controls; actual target proof is separate',
                  test_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
                  failures=[dict(test=str(test), trace=trace) for test, trace in result.failures+result.errors])
    args.results.write_text(json.dumps(report, indent=2)+'\n')
    return not result.wasSuccessful()


if __name__ == '__main__':
    raise SystemExit(main())
