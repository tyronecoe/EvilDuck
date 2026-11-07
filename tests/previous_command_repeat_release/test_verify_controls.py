#!/usr/bin/env python3
"""Offline refusal controls for the additive REPEAT target/release verifiers."""
import argparse
import ast
import builtins
import hashlib
import importlib.util
import io
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('repeat_target_control_policy', HERE / 'verify_target.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
spec = importlib.util.spec_from_file_location('repeat_release_control_policy', HERE / 'verify_release.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
SOURCE = None


class Policy(unittest.TestCase):
    def test_all_inherited_target_require_predicates_preserved(self):
        original = builtins.compile
        captured = {}
        paths = {str(V.S.PARENT), str(ROOT / 'tests/privacy_fix1/verify_target.py')}

        def audit(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kwargs):
            if str(filename) in paths and mode == 'exec' and not flags & ast.PyCF_ONLY_AST:
                tree = original(source, filename, mode, flags | ast.PyCF_ONLY_AST, dont_inherit, optimize, **kwargs)
                captured[str(filename)] = sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'require' for n in ast.walk(tree))
            return original(source, filename, mode, flags, dont_inherit, optimize, **kwargs)

        with patch.object(builtins, 'compile', audit), patch.object(V, 'ORIGINAL_COMPILE', audit):
            namespace, changes = V.adapted_parent()
            namespace['parent_namespace']()
        self.assertTrue(changes['previous_repeat'])
        for path in paths:
            tree = ast.parse(pathlib.Path(path).read_text())
            expected = sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'require' for n in ast.walk(tree))
            self.assertEqual(captured[path], expected, path)

    def test_all_six_frozen_190_asserts_preserved(self):
        namespace, changes = R.adapted_parent()
        pin = json.loads((HERE / 'source-manifest.json').read_text())
        final = {row['file']: row['sha256'] for row in pin['cumulative_h1_after']}
        expected = [('h1_right_modifiers', 23), ('inject_var_experimental', 21),
                    ('lock_wait_timeout', 16), ('source_text_v2', 46),
                    ('lock_feedback', 25), ('caps_stop', 59)]
        total = 0
        for directory, count in expected:
            path = ROOT / 'tests' / directory / 'verify_link.py'
            self.assertEqual(V.sha(path), namespace['FROZEN'][directory])
            tree = ast.parse(path.read_text())
            self.assertEqual(sum(isinstance(n, ast.Assert) for n in ast.walk(tree)), count)
            transformed = namespace['FinalCandidateExpectations'](final).visit(tree)
            transformed = namespace['RuntimeIdentityExpectations'](tree).visit(transformed)
            self.assertEqual(sum(isinstance(n, ast.Assert) for n in ast.walk(transformed)), count)
            total += count
        self.assertEqual(total, 190)
        self.assertTrue(changes['previous_repeat'])
        with self.assertRaises(AssertionError):
            namespace['FinalCandidateExpectations']({k: v for k, v in final.items() if k != 'core.cpp'})

    def test_exact_final_composition(self):
        value = V.verify_composed_source(SOURCE)
        self.assertEqual(value['source_files'], 201)
        self.assertTrue(value['reviewed_repeat_preserved'])
        self.assertEqual(value['build_id'], V.BUILD_ID)

    def mutate(self, name, change):
        with tempfile.TemporaryDirectory(prefix='repeat-release-source-control-') as directory:
            path = pathlib.Path(directory) / 'source'
            shutil.copytree(SOURCE, path)
            target = path / name
            target.write_bytes(change(target.read_bytes()))
            with self.assertRaises((ValueError, AssertionError)):
                V.verify_composed_source(path)

    def test_omitted_standalone_compiler_rejected(self):
        old = ROOT.parent / 'scratch/static-response-repair-review/build-v1/candidate/EvilDuckS3/core.cpp'
        self.assertEqual(V.sha(old), '2876056adb42347f53ff8efdcf9cdbbce8ca04db4dc670bd1c4fdb2dc49befa5')
        self.mutate('core.cpp', lambda _: old.read_bytes())

    def test_modified_compiler_rejected(self):
        self.mutate('core.cpp', lambda data: data + b'\n')

    def test_old_identity_rejected(self):
        self.mutate('caps_trial.h', lambda data: data.replace(V.BUILD_ID.encode(), V.OLD_BUILD_ID.encode(), 1))

    def test_omitted_static_repair_rejected(self):
        old = ROOT.parent / 'scratch/editor-build-integration/build-v2-uninstalled/candidate/EvilDuckS3/webserver.cpp'
        self.assertEqual(V.sha(old), '02b1bed01526935e7c8ec1857dfc910221dda3977efc47185eafbc796e4a22f9')
        self.mutate('webserver.cpp', lambda _: old.read_bytes())

    def test_omitted_editor_repair_rejected(self):
        old = ROOT.parent / 'scratch/dashboard-cleanup/build-v1/candidate/EvilDuckS3/webfiles.h'
        self.assertEqual(V.sha(old), '7b4be141c776fc2c8d83b6532c62b9c4b9baa033261ce16c60e509dddaea4eab')
        self.mutate('webfiles.h', lambda _: old.read_bytes())

    def test_unrelated_source_tamper_rejected(self):
        self.mutate('adapter.cpp', lambda data: data + b'\n')

    def test_false_committed_provenance_rejected(self):
        with tempfile.TemporaryDirectory(prefix='repeat-release-input-control-') as directory:
            for change in [dict(source_commit_contains_changes=False), dict(uncommitted_local_changes=True), dict(source_commit='0' * 40)]:
                value = dict(format='evilduck-committed-build-inputs-v1',
                             source_commit='fcba0385ce21662c7a504e0c9b6fba0dfa2c4f8d',
                             source_commit_contains_changes=True, uncommitted_local_changes=False,
                             build_id=V.BUILD_ID)
                value.update(change)
                pathlib.Path(directory, 'build-inputs.json').write_text(json.dumps(value))
                with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                    V.verify_input_manifest(directory)

    def test_actual_previous_elf_lacks_new_compiler_path(self):
        old = ROOT.parent / 'scratch/static-response-repair-review/build-v1'
        self.assertEqual(V.sha(old / 'build/EvilDuckS3.ino.bin'), 'd5fe0932fe915443a5e53030969c6792409f719d427681304a7102355b2d7946')
        with self.assertRaisesRegex(ValueError, 'New REPEAT compiler symbol absent/ambiguous'):
            V.core_binding(old)

    def test_static_dispatch_guard_retained(self):
        pointers = ''.join(' .rodata._ZL%d%s\n' % (len(n), n) for n in V.S.RESOURCES)
        obj = ('Disassembly of section .literal._ZL12handleStaticP21AsyncWebServerRequest:\n' + pointers + V.S.BYTE_SEND + '\n'
               'Disassembly of section .text._ZL12handleStaticP21AsyncWebServerRequest:\n')
        linked = V.S.BYTE_SEND + '\n' + '\n'.join('<' + n + '>' for n in V.S.RESOURCES)
        self.assertTrue(V.S.verify_dispatch_text(obj, linked)['byte_overload_observed'])
        with self.assertRaises(ValueError):
            V.S.verify_dispatch_text(obj.replace(V.S.BYTE_SEND, 'AsyncWebServerRequest::send_P('), linked)

    def test_actual_call_graph_allows_line_wrapper_and_rejects_missing_edges(self):
        step = 'ds_preview::Compiler::step(ds_preview::CompileWork&)'
        line = 'ds_preview::Compiler::line()'
        wrapper = 'ds_preview::Compiler::statement(char*)'
        implementation = 'ds_preview::Compiler::statementImpl(char*)'
        call = lambda name: '42000000: 000005 call8 42000100 <' + name + '>\n'
        graph = {step: call(line), line: call(wrapper), wrapper: call(implementation), implementation: ''}
        self.assertEqual(V.compiler_reachability(graph)['path'], [step, line, wrapper, implementation])
        self.assertEqual(V.compiler_reachability({step: call(implementation), implementation: ''})['path'], [step, implementation])
        for broken in [{**graph, line: ''}, {**graph, wrapper: '<' + implementation + '>\n'},
                       {**graph, wrapper: '42000000: 000005 beqz a2, <' + implementation + '>\n'}]:
            with self.assertRaises(ValueError):
                V.compiler_reachability(broken)


def main():
    global SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=pathlib.Path)
    parser.add_argument('--results', required=True, type=pathlib.Path)
    args = parser.parse_args()
    SOURCE = args.source
    assert not args.results.exists(), 'Use fresh control evidence'
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Policy))
    receipt = dict(counts=dict(PASS=result.testsRun - len(result.failures) - len(result.errors),
                               FAIL=len(result.failures) + len(result.errors)),
                   details=stream.getvalue(), hardware=False, firmware_built=False,
                   test_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
                   source=str(SOURCE), scope='New source/committed-input refusals, preserved190Assert transforms and actual old ELF negative control')
    args.results.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    return int(not result.wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
