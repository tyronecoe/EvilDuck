#!/usr/bin/env python3
"""Host-only negative controls for the one-build postcompile completion adapter."""
import argparse
import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('one_build_postlink_completion', HERE / 'complete_existing.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


class Controls(unittest.TestCase):
    def setUp(self):
        self.builder = C.load(C.BUILD_MODULE, 'postcompile_control_c_builder')
        self.text, _ = self.builder.adapted_source(C.COMPILE_COMMIT)

    def test_exact_tail_retained_and_fresh_guard_not_changed(self):
        adapted, evidence = C.postcompile_source(self.text, {'overlay_calls': 1})
        start = self.text.index(C.TAIL_MARKER)
        end = self.text.index('\n\nif __name__', start)
        tail = self.text[start:end]
        self.assertEqual(adapted.count(tail), 1)
        self.assertEqual(C.digest(tail.encode()), evidence['unmodified_postcompile_tail_sha256'])
        self.assertIn('assert "--verify-existing" not in sys.argv', self.text)
        self.assertNotIn('assert "--verify-existing" not in sys.argv', adapted)
        self.assertIn("sys.argv.count('--verify-existing') == 1", adapted)
        self.assertFalse(evidence['firmware_compilation_prefix_rerun'])
        self.assertTrue(evidence['all_target_and_release_predicates_after_compile_preserved'])

    def test_wrong_or_ambiguous_tail_refused(self):
        with self.assertRaises(AssertionError):
            C.postcompile_source(self.text.replace(C.TAIL_MARKER, '', 1), {'overlay_calls': 1})
        with self.assertRaises(AssertionError):
            C.postcompile_source(self.text + '\n' + C.TAIL_MARKER, {'overlay_calls': 1})

    def test_wrong_snapshot_refused_before_other_input_reads(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / 'report.json').write_text('{}')
            with self.assertRaisesRegex(AssertionError, 'Wrong original clean compile snapshot'):
                C.snapshot_inputs(p / 'no-build', p)

    def test_tampered_original_input_manifest_refused(self):
        known = pathlib.Path('/workspace/scratch/static-response-repair-review/original-compiled-checkpoint')
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            shutil.copyfile(known / 'report.json', p / 'report.json')
            (p / 'build-inputs.json').write_text('{}')
            with self.assertRaises(AssertionError):
                C.snapshot_inputs(p / 'no-build', p)

    def test_exact_pinned_linker_query_is_read_only_exception(self):
        original = json.loads(pathlib.Path('/workspace/scratch/static-response-repair-review/original-compiled-checkpoint/report.json').read_text())
        compiler = original['link_command'][0]
        self.assertEqual(C.command_policy([compiler, '-print-prog-name=ld'], compiler, original['compiler_sha256']),
                         'READ_ONLY_PINNED_LINKER_LOCATION_QUERY')
        with self.assertRaises(AssertionError):
            C.command_policy([compiler, '-print-prog-name=ld'], compiler, '0' * 64)

    def test_all_builds_and_other_compiler_queries_still_refused(self):
        compiler = '/workspace/scratch/led-feedback-isolated-core/data/packages/esp32/tools/esp-x32/2411/bin/xtensa-esp32s3-elf-g++'
        for suffix in [['-c', 'webserver.cpp', '-o', 'webserver.o'], ['input.o', '-o', 'application.elf'],
                       ['-E', 'input.cpp'], ['--version'], ['-print-prog-name=as'],
                       ['-print-prog-name=ld', '-c', 'input.cpp']]:
            with self.assertRaises(AssertionError):
                C.command_policy([compiler] + suffix, compiler, '0' * 64)
        with self.assertRaises(AssertionError):
            C.command_policy(['/usr/bin/arduino-cli', 'compile', '--show-properties'], compiler, '0' * 64)
        with self.assertRaises(AssertionError):
            C.command_policy(['/different/xtensa-esp32s3-elf-g++', '-print-prog-name=ld'], compiler, '0' * 64)
        with self.assertRaises(AssertionError):
            C.command_policy(['python3', 'esptool.py', '--port', '/dev/ttyUSB0', 'read_flash'], compiler, '0' * 64)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.results.exists()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Controls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    record = dict(counts=dict(PASS=result.testsRun - len(result.failures) - len(result.errors),
                             FAIL=len(result.failures) + len(result.errors)),
                  scope='Postcompile tail and immutable snapshot negative controls only; no target execution',
                  helper_sha256=C.sha(HERE / 'complete_existing.py'),
                  hardware=False, firmware_built=False)
    args.results.write_text(json.dumps(record, indent=2) + '\n')
    return int(not result.wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
