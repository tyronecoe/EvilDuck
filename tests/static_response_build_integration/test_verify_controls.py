#!/usr/bin/env python3
"""Fail-closed source/serving verifier controls; no compiler or hardware access."""
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
spec = importlib.util.spec_from_file_location('streaming_target_policy', HERE / 'verify_target.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
SOURCE = None


class Policy(unittest.TestCase):
    def test_frozen_target_require_counts_preserved(self):
        original = builtins.compile
        captured = {}
        paths = {str(V.PARENT), str(ROOT / 'tests/privacy_fix1/verify_target.py')}

        def audit(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kwargs):
            if str(filename) in paths and mode == 'exec' and not flags & ast.PyCF_ONLY_AST:
                tree = original(source, filename, mode, flags | ast.PyCF_ONLY_AST, dont_inherit, optimize, **kwargs)
                captured[str(filename)] = sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'require' for n in ast.walk(tree))
            return original(source, filename, mode, flags, dont_inherit, optimize, **kwargs)

        with patch.object(builtins, 'compile', audit):
            ns, changes = V.adapted_parent()
            ns['parent_namespace']()
        self.assertEqual(len(changes), 12)
        for path in paths:
            tree = ast.parse(pathlib.Path(path).read_text())
            expected = sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'require' for n in ast.walk(tree))
            self.assertEqual(captured[path], expected, path)

    def test_exact_final_composition(self):
        value = V.verify_composed_source(SOURCE)
        self.assertEqual(value['source_files'], 201)
        self.assertTrue(value['reviewed_editor_preserved'])

    def mutate(self, name, change):
        with tempfile.TemporaryDirectory(prefix='static-source-control-') as directory:
            path = pathlib.Path(directory) / 'source'
            shutil.copytree(SOURCE, path)
            target = path / name
            target.write_bytes(change(target.read_bytes()))
            with self.assertRaises((ValueError, AssertionError)):
                V.verify_composed_source(path)

    def test_omitted_static_repair_rejected(self):
        before = ROOT.parent / 'scratch/editor-build-integration/build-v2-uninstalled/candidate/EvilDuckS3/webserver.cpp'
        self.assertEqual(V.sha(before), '02b1bed01526935e7c8ec1857dfc910221dda3977efc47185eafbc796e4a22f9')
        self.mutate('webserver.cpp', lambda data: before.read_bytes())

    def test_omitted_editor_repair_rejected(self):
        old = ROOT.parent / 'scratch/dashboard-cleanup/build-v1/candidate/EvilDuckS3/webfiles.h'
        self.assertEqual(V.sha(old), '7b4be141c776fc2c8d83b6532c62b9c4b9baa033261ce16c60e509dddaea4eab')
        self.mutate('webfiles.h', lambda data: old.read_bytes())

    def test_old_identity_rejected(self):
        self.mutate('caps_trial.h', lambda data: data.replace(V.BUILD_ID.encode(), V.OLD_BUILD_ID.encode(), 1))

    def test_false_committed_input_claim_rejected(self):
        with tempfile.TemporaryDirectory(prefix='static-input-control-') as directory:
            for change in [dict(source_commit_contains_changes=False), dict(uncommitted_local_changes=True), dict(source_commit='0'*40)]:
                value = dict(format='evilduck-committed-build-inputs-v1', source_commit='e692435a7c70dbc0d917bbff733c57900cf7d57c',
                             source_commit_contains_changes=True, uncommitted_local_changes=False, build_id=V.BUILD_ID)
                value.update(change)
                pathlib.Path(directory, 'build-inputs.json').write_text(json.dumps(value))
                with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                    V.verify_input_manifest(directory)

    def test_dispatch_policy_keeps_small_unknown_path_fallback(self):
        pointers = ''.join(' .rodata._ZL%d%s\n' % (len(n), n) for n in V.RESOURCES)
        obj = ('Disassembly of section .literal._ZL12handleStaticP21AsyncWebServerRequest:\n' + pointers + V.BYTE_SEND + '\n'
               'Disassembly of section .text._ZL12handleStaticP21AsyncWebServerRequest:\n')
        linked = V.BYTE_SEND + '\n' + '\n'.join('<'+n+'>' for n in V.RESOURCES)
        linked += '\nAsyncWebServerRequest::send(int, char const*, char const*, std::function<String (String const&)>)\n'
        self.assertTrue(V.verify_dispatch_text(obj, linked)['unknown_path_char_response_allowed'])
        for bad in [obj.replace(V.BYTE_SEND, 'AsyncWebServerRequest::send_P(int, String const&, char const*,'),
                    obj.replace('.rodata._ZL8INDEX_JS', 'missing-pointer')]:
            with self.assertRaises(ValueError):
                V.verify_dispatch_text(bad, linked)

    def test_actual_old_elf_asset_dispatch_is_rejected(self):
        old = ROOT.parent / 'scratch/editor-build-integration/build-v2-uninstalled'
        self.assertEqual(V.sha(old / 'build/EvilDuckS3.ino.bin'), 'e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0')
        tool = ROOT.parent / 'scratch/led-feedback-isolated-core/data/packages/esp32/tools/esp-x32/2411/bin/xtensa-esp32s3-elf-objdump'
        obj = subprocess.check_output([str(tool), '-C', '-dr', str(old / 'build/sketch/webserver.cpp.o')], text=True)
        linked = subprocess.check_output([str(tool), '-C', '-d', '--disassemble=_ZL12handleStaticP21AsyncWebServerRequest', str(old / 'build/EvilDuckS3.ino.elf')], text=True)
        with self.assertRaisesRegex(ValueError, 'byte-pointer/length'):
            V.verify_dispatch_text(obj, linked)


def main():
    global SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=pathlib.Path)
    parser.add_argument('--results', required=True, type=pathlib.Path)
    args = parser.parse_args()
    SOURCE = args.source
    assert not args.results.exists()
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Policy))
    receipt = dict(counts=dict(PASS=result.testsRun-len(result.failures)-len(result.errors), FAIL=len(result.failures)+len(result.errors)),
                   scope='Composition/dispatch policy and actual earlier ELF negative control; no new target verification',
                   details=stream.getvalue(), hardware=False, firmware_built=False,
                   test_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest())
    args.results.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    return int(not result.wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
