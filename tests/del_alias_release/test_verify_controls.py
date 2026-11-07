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
import struct
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
CANDIDATE_BUILD = None
PARTIAL_BINDING = None


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
            if directory == 'h1_right_modifiers':
                handler = R.CompilerHandlerExpectations()
                transformed = handler.visit(transformed)
                self.assertEqual(len(handler.edits), 2)
            self.assertEqual(sum(isinstance(n, ast.Assert) for n in ast.walk(transformed)), count)
            total += count
        self.assertEqual(total, 190)
        self.assertTrue(changes['previous_repeat'])
        with self.assertRaises(AssertionError):
            namespace['FinalCandidateExpectations']({k: v for k, v in final.items() if k != 'core.cpp'})

    def test_handler_retarget_is_exact_and_preserves_modifier_assertion(self):
        path = ROOT / 'tests/h1_right_modifiers/verify_link.py'
        original = ast.parse(path.read_text())
        original_asserts = sum(isinstance(n, ast.Assert) for n in ast.walk(original))
        adapter = R.CompilerHandlerExpectations()
        changed = adapter.visit(original)
        self.assertEqual(original_asserts, 23)
        self.assertEqual(sum(isinstance(n, ast.Assert) for n in ast.walk(changed)), original_asserts)
        self.assertEqual(len(adapter.edits), 2)
        self.assertEqual({r['before'] for r in adapter.edits}, {adapter.OLD})
        self.assertEqual({r['after'] for r in adapter.edits}, {adapter.NEW})
        statements = [ast.unparse(n) for n in ast.walk(changed) if isinstance(n, ast.Assert)]
        self.assertIn("assert 'ds_shortcut::modifier(' in bodies['ds_preview::Compiler::statementImpl(']", statements)
        lookalike = ast.parse("x='ds_preview::Compiler::statement( extra'; y='other handler'")
        untouched = R.CompilerHandlerExpectations()
        untouched.visit(lookalike)
        self.assertFalse(untouched.edits)

    def test_reused_filename_does_not_select_nested_handler_layer(self):
        reused = str((ROOT / 'tests/h1_right_modifiers/verify_link.py').resolve())
        single_selector = "bodies['ds_preview::Compiler::statement('] = 'nested unit'"
        for layer in ['source/text v2', 'bounded lock waits', 'experimental H1',
                      'keyboard/lock feedback', 'caps/STOP closure']:
            tree = ast.parse(single_selector)
            before = ast.dump(tree, include_attributes=False)
            after, edits = R.adapt_compiler_handler(tree, layer, reused)
            self.assertEqual(ast.dump(after, include_attributes=False), before)
            self.assertFalse(edits)
        with self.assertRaises(AssertionError):
            R.adapt_compiler_handler(ast.parse(single_selector), 'right-modifier H1', reused)
        source = (ROOT / 'tests/h1_right_modifiers/verify_link.py').read_text()
        changed, edits = R.adapt_compiler_handler(ast.parse(source), 'right-modifier H1', reused)
        self.assertEqual(len(edits), 2)
        self.assertTrue(all(e['logical_layer'] == 'right-modifier H1' and e['filename'] == reused for e in edits))
        self.assertEqual(sum(isinstance(n, ast.Assert) for n in ast.walk(changed)), 23)

    def test_actual_candidate_modifier_handler_and_reachability(self):
        global PARTIAL_BINDING
        if CANDIDATE_BUILD is None:
            self.skipTest('Read-only candidate ELF control not requested')
        binding = V.core_binding(CANDIDATE_BUILD)
        self.assertTrue(binding['standalone_branch_verified'])
        self.assertEqual(binding['compiler_call_graph']['path'][-1], 'ds_preview::Compiler::statementImpl(char*)')
        rows = {r['name']: r for r in binding['linked_symbols']}
        implementation = rows['ds_preview::Compiler::statementImpl(char*)']
        wrapper = rows['ds_preview::Compiler::statement(char*)']
        entries = json.loads((CANDIDATE_BUILD / 'build/compile_commands.json').read_text())
        compiler = pathlib.Path(next(r for r in entries if pathlib.Path(r['file']).name == 'core.cpp')['arguments'][0])
        objdump = compiler.with_name(compiler.name.rsplit('-', 1)[0] + '-objdump')
        elf = CANDIDATE_BUILD / 'build/EvilDuckS3.ino.elf'
        bodies = {}
        for name, row in [('implementation', implementation), ('wrapper', wrapper)]:
            bodies[name] = subprocess.check_output([str(objdump), '-C', '-d', '--start-address=' + str(row['address']),
                                                    '--stop-address=' + str(row['address'] + row['size']), str(elf)], text=True)
        self.assertIn('ds_shortcut::modifier(', bodies['implementation'])
        self.assertNotIn('ds_shortcut::modifier(', bodies['wrapper'])
        PARTIAL_BINDING = dict(source=str(CANDIDATE_BUILD), actual_elf_sha256=binding['actual_elf_sha256'],
                               core_sha256=binding['source_sha256'], modifier_handler='statementImpl',
                               reachable_path=binding['compiler_call_graph']['path'],
                               full_provenance_guard_executed=False,
                               scope='Read-only compiled handler equivalence control, not final release approval')

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

    def test_modifier_handler_requires_executable_edge(self):
        name = 'ds_shortcut::modifier(char const*)'
        actual = '42000000: 000005 call8 42000100 <' + name + '>\n'
        self.assertEqual(len(V.modifier_handler_edges(actual)), 1)
        for unsupported in ['', '<' + name + '>\n',
                            '42000000: 000005 beqz a2, <' + name + '>\n']:
            with self.assertRaises(ValueError):
                V.modifier_handler_edges(unsupported)


    def test_omitted_del_alias_rejected(self):
        self.mutate('shortcut_keys.h', lambda data: data.replace(b'{"DEL",0x4c},', b'', 1))

    def test_wrong_del_usage_rejected(self):
        self.mutate('shortcut_keys.h', lambda data: data.replace(b'{"DEL",0x4c},', b'{"DEL",0x2a},', 1))

    def test_del_function_preservation_omission_rejected(self):
        self.mutate('core.cpp', lambda data: data.replace(b'(key(p)&&!exact(p,"DEL"))', b'key(p)', 1))

    def test_actual_previous_repeat_elf_lacks_del_mapping(self):
        previous = ROOT.parent / 'scratch/previous-command-repeat-release/build-v3'
        self.assertEqual(V.sha(previous / 'build/EvilDuckS3.ino.bin'), '13cec88262afdfa641eb0fb4927fe7903abf2863295344ff316418707ba49b7f')
        retained = V.core_binding(previous)
        with self.assertRaisesRegex(ValueError, 'Actual linked DEL/DELETE mapping'):
            V.alias_binding(previous, retained)

    def test_actual_del_target_mapping_when_supplied(self):
        if CANDIDATE_BUILD is None:
            self.skipTest('Actual DEL target build not yet supplied')
        binding = V.alias_binding(CANDIDATE_BUILD, V.core_binding(CANDIDATE_BUILD))
        self.assertEqual(binding['usage'], 0x4c)
        self.assertTrue(binding['table_begin_end_loaded'])
        self.assertTrue(binding['compiler_calls_named'])

    @staticmethod
    def synthetic_elf():
        data = bytearray(0x400)
        data[:6] = b'\x7fELF\x01\x01'
        struct.pack_into('<I', data, 28, 52)
        struct.pack_into('<HH', data, 42, 32, 1)
        base = 0x3c100000
        struct.pack_into('<IIIIIIII', data, 52, 1, 0x100, base, base, 0x300, 0x300, 4, 4)
        struct.pack_into('<IB3xIB3x', data, 0x100, base + 0x40, 0x4c, base + 0x47, 0x4c)
        data[0x140:0x14b] = b'DELETE\x00DEL\x00'
        return data, base

    def test_named_table_decodes_pointers_and_usage_not_free_strings(self):
        data, base = self.synthetic_elf()
        rows = V.decode_named_table(bytes(data), base, 16)
        self.assertEqual([(r['name'], r['usage']) for r in rows], [('DELETE', 0x4c), ('DEL', 0x4c)])
        # The DEL string still exists, but changing the actual table usage fails.
        data[0x10c] = 0x2a
        with self.assertRaisesRegex(ValueError, 'Actual linked DEL/DELETE mapping'):
            V.decode_named_table(bytes(data), base, 16)

    def test_bad_table_ranges_duplicates_and_architecture_refused(self):
        original, base = self.synthetic_elf()
        changes = [lambda x: x.__setitem__(5, 2),
                   lambda x: struct.pack_into('<I', x, 0x108, base + 0x40),
                   lambda x: struct.pack_into('<I', x, 0x108, 0xffffffff)]
        for change in changes:
            data = bytearray(original); change(data)
            with self.assertRaises(ValueError):
                V.decode_named_table(bytes(data), base, 16)
        for size in [0, 7, 4097]:
            with self.assertRaises(ValueError):
                V.decode_named_table(bytes(original), base, size)

    def test_build_adapter_keeps_explicit_del_selection_and_old_guards(self):
        spec = importlib.util.spec_from_file_location('del_build_architecture_control', HERE / 'build_candidate.py')
        builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
        text, changes = builder.adapted_source('557dc81f65b672d5b701b681664ef6ff0a7e5d44')
        self.assertEqual(len(changes['del_alias']), 14)
        self.assertIn('tests/del_alias_release/prepare_sources.py', text)
        self.assertIn('del_alias_target_binding=binding', text)
        self.assertIn('inherited_safety_predicates_removed=0', text)
        self.assertIn('assert "--verify-existing" not in sys.argv', text)
        # The selected builder still calls the unmodified parent's guard first.
        tree = ast.parse((HERE / 'build_candidate.py').read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'build_inputs')
        self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and
                            isinstance(n.func.value, ast.Name) and n.func.value.id == 'parent' and n.func.attr == 'build_inputs'
                            for n in ast.walk(function)))


def main():
    global SOURCE, CANDIDATE_BUILD
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=pathlib.Path)
    parser.add_argument('--results', required=True, type=pathlib.Path)
    parser.add_argument('--candidate-build', type=pathlib.Path,
                        help='Optional read-only actual ELF handler/control proof; never final provenance approval')
    args = parser.parse_args()
    SOURCE = args.source
    CANDIDATE_BUILD = args.candidate_build
    assert not args.results.exists(), 'Use fresh control evidence'
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Policy))
    receipt = dict(counts=dict(PASS=result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
                               FAIL=len(result.failures) + len(result.errors)),
                   skipped=len(result.skipped), candidate_partial_binding=PARTIAL_BINDING,
                   details=stream.getvalue(), hardware=False, firmware_built=False,
                   test_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
                   source=str(SOURCE), scope='New source/committed-input refusals, preserved190Assert transforms and actual old ELF negative control')
    args.results.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    return int(not result.wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
