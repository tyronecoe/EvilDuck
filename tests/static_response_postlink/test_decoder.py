#!/usr/bin/env python3
"""Actual-object post-link decoder controls; no firmware compiler or image edit.

Corruptions affect only in-memory disassembly/literal copies or disposable input
copies. The decoder-only mode can run before committing the host verifier D;
provenance controls require the current verifier to be committed first.
"""
import argparse
import hashlib
import importlib.util
import io
import json
import pathlib
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGET = ROOT / 'tests/static_response_build_integration/verify_target.py'
spec = importlib.util.spec_from_file_location('postlink_decoder', TARGET)
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
BUILD = None
DISASSEMBLY = None
POOL = None
LENGTHS = None


class Decoder(unittest.TestCase):
    def decode(self, text=None, pool=None):
        return V.decode_asset_calls(DISASSEMBLY if text is None else text,
                                    POOL if pool is None else pool, LENGTHS)

    def test_actual_all_ten_calls_and_nine_exact_resource_lengths(self):
        rows = self.decode()
        self.assertEqual(len(rows), 10)
        self.assertEqual({r['resource'] for r in rows}, set(LENGTHS))
        for row in rows:
            self.assertEqual(row['http_bytes'], LENGTHS[row['resource']])
            self.assertTrue(row['pointer_instructions'])
            self.assertTrue(row['length_instructions'])

    def test_signed_movi_and_already_shifted_addmi(self):
        rows = {r['resource']: r for r in self.decode()}
        self.assertEqual(rows['INDEX_HTML']['http_bytes'], 152 + 0x2f00)
        self.assertEqual(rows['STYLE_CSS']['http_bytes'], -25 + 0x7d00)
        self.assertIn('movi.n a14, -25', '\n'.join(rows['STYLE_CSS']['length_instructions']))
        self.assertIn('addmi a14, a14, 0x7d00', '\n'.join(rows['STYLE_CSS']['length_instructions']))

    def test_corrupt_addmi_is_rejected(self):
        self.assertEqual(DISASSEMBLY.count('addmi\ta14, a14, 0x2f00'), 1)
        bad = DISASSEMBLY.replace('addmi\ta14, a14, 0x2f00', 'addmi\ta14, a14, 0x2e00', 1)
        with self.assertRaisesRegex(ValueError, 'argument length mismatch: INDEX_HTML'):
            self.decode(bad)

    def test_corrupt_signed_immediate_is_rejected(self):
        bad = DISASSEMBLY.replace('movi.n\ta14, -25', 'movi.n\ta14, 25', 1)
        self.assertNotEqual(bad, DISASSEMBLY)
        with self.assertRaisesRegex(ValueError, 'argument length mismatch: STYLE_CSS'):
            self.decode(bad)

    def test_extra_nul_in_literal_length_is_rejected(self):
        old = struct.pack('<I', LENGTHS['INDEX_JS'])
        self.assertEqual(POOL.count(old), 1)
        bad = POOL.replace(old, struct.pack('<I', LENGTHS['INDEX_JS'] + 1), 1)
        with self.assertRaisesRegex(ValueError, 'argument length mismatch: INDEX_JS'):
            self.decode(pool=bad)

    def test_swapped_pointer_cannot_borrow_an_unrelated_correct_length(self):
        bad = DISASSEMBLY.replace('.rodata._ZL10INDEX_HTML', '.rodata._ZL13SETTINGS_HTML', 1)
        with self.assertRaisesRegex(ValueError, 'argument length mismatch: SETTINGS_HTML'):
            self.decode(bad)

    def test_missing_second_js_length_does_not_reuse_first_call_register(self):
        needle = 'l32r\ta14, fffc01f0'
        self.assertEqual(DISASSEMBLY.count(needle), 1)
        bad = DISASSEMBLY.replace(needle, 'l32r\ta0, fffc01f0', 1)
        with self.assertRaisesRegex(ValueError, 'argument length mismatch: INDEX_JS'):
            self.decode(bad)

    def test_asset_witness_omission_is_rejected(self):
        needle = '.rodata._ZL13TERMINAL_HTML'
        self.assertEqual(DISASSEMBLY.count(needle), 1)
        bad = DISASSEMBLY.replace(needle, '.rodata._ZL13UNKNOWN_BYTES', 1)
        with self.assertRaisesRegex(ValueError, 'decoded resource pointer'):
            self.decode(bad)


class Provenance(unittest.TestCase):
    def test_compilation_c_and_last_touch_d_are_distinguished(self):
        value = V.verify_input_manifest(BUILD)
        self.assertEqual(value['source_commit'], V.POST_COMPILE_SOURCE)
        delta = value['post_compile_verifier_delta']
        self.assertEqual(delta['path'], V.SELF_PATH)
        self.assertEqual(delta['compile_sha256'], V.POST_COMPILE_VERIFIER_SHA)
        self.assertTrue(delta['git_compile_blob_verified'] and delta['git_verifier_blob_verified'])
        last = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', V.SELF_PATH], cwd=ROOT, text=True).strip()
        self.assertEqual(value['verifier_context_commit'], last)
        self.assertEqual(delta['verification_context_commit'], last)

    def fixture(self, change):
        temporary = tempfile.TemporaryDirectory(prefix='postlink-provenance-')
        fake = pathlib.Path(temporary.name)
        manifest = json.loads((BUILD / 'build-inputs.json').read_text())
        for row in manifest['files']:
            target = fake / row['file']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row['file'], target)
        change(fake)
        return temporary, fake

    def checked_copy(self, fake):
        output, run = subprocess.check_output, subprocess.run

        def read_git(argv, **kwargs):
            kwargs['cwd'] = ROOT
            return output(argv, **kwargs)

        def run_git(argv, **kwargs):
            kwargs['cwd'] = ROOT
            return run(argv, **kwargs)

        with patch.object(V, 'ROOT', fake), patch.object(V.subprocess, 'check_output', read_git), patch.object(V.subprocess, 'run', run_git):
            return V.verify_input_manifest(BUILD)

    def test_any_other_current_input_difference_is_rejected(self):
        def change(fake):
            p = fake / 'tools/build_routeb_candidate.py'
            p.write_bytes(p.read_bytes() + b'\n# disposable corrupt input\n')
        temporary, fake = self.fixture(change)
        try:
            with self.assertRaisesRegex(ValueError, 'Non-verifier input changed'):
                self.checked_copy(fake)
        finally:
            temporary.cleanup()

    def test_uncommitted_host_verifier_edit_is_rejected(self):
        def change(fake):
            p = fake / V.SELF_PATH
            p.write_bytes(p.read_bytes() + b'\n# disposable uncommitted verifier\n')
        temporary, fake = self.fixture(change)
        try:
            with self.assertRaisesRegex(ValueError, 'last-touch Git revision'):
                self.checked_copy(fake)
        finally:
            temporary.cleanup()


def main():
    global BUILD, DISASSEMBLY, POOL, LENGTHS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', type=pathlib.Path, required=True)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    parser.add_argument('--decoder-only', action='store_true')
    args = parser.parse_args()
    BUILD = args.build_root.resolve()
    assert not args.results.exists()
    binary = BUILD / 'build/EvilDuckS3.ino.bin'
    assert V.sha(binary) == 'd5fe0932fe915443a5e53030969c6792409f719d427681304a7102355b2d7946'
    objects = BUILD / 'build/sketch/webserver.cpp.o'
    elf = BUILD / 'build/EvilDuckS3.ino.elf'
    before = {str(p): V.sha(p) for p in [binary, objects, elf, BUILD / 'build-inputs.json']}
    entries = json.loads((BUILD / 'build/compile_commands.json').read_text())
    compiler = pathlib.Path(next(r for r in entries if pathlib.Path(r['file']).name == 'webserver.cpp')['arguments'][0])
    tool = compiler.with_name(compiler.name.rsplit('-', 1)[0] + '-objdump')
    DISASSEMBLY = subprocess.check_output([str(tool), '-C', '-dr', str(objects)], text=True)
    raw = subprocess.check_output([str(tool), '-s', '-j', '.literal._ZL12handleStaticP21AsyncWebServerRequest', str(objects)], text=True)
    POOL = V.decode_literal_pool(raw)
    LENGTHS = {name: len(body) for name, body in V.resource_literals(BUILD / 'candidate/EvilDuckS3/webfiles.h').items()}
    suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Decoder)])
    if not args.decoder_only:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Provenance))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    assert all(V.sha(path) == digest for path, digest in before.items()), 'A compiled artifact or manifest changed'
    receipt = dict(counts=dict(PASS=result.testsRun-len(result.failures)-len(result.errors), FAIL=len(result.failures)+len(result.errors)),
                   details=stream.getvalue(), decoder_only=args.decoder_only, actual_artifact_hashes=before,
                   verifier_sha256=V.sha(TARGET), test_sha256=V.sha(pathlib.Path(__file__)),
                   scope='Actual-object pointer/length decoding and disposable provenance negative controls; no rebuild',
                   firmware_rebuilt=False, firmware_sources_modified=False, hardware=False)
    args.results.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    return int(not result.wasSuccessful())


if __name__ == '__main__':
    raise SystemExit(main())
