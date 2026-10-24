"""v4 absolute sibling selection only. No real native, HTTP or HID operations."""
import contextlib
import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from test_led_action_main import Launch, m


@contextlib.contextmanager
def working_directory(path):
    old = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old)


class NativePathTests(unittest.TestCase):
    def fixture(self, root):
        source = root / 'helper directory with spaces'
        source.mkdir()
        script = source / 'led_action.py'
        script.write_text('# synthetic path fixture; never executed\n')
        native = source / 'led-action-native'
        native.write_text('synthetic non-executable contents; subprocess is mocked\n')
        native.chmod(0o700)
        other = root / 'different working directory'
        other.mkdir()
        return script, native, other

    def test_relative_absolute_other_cwd_and_spaces_use_exact_absolute_sibling(self):
        with tempfile.TemporaryDirectory(prefix='evilduck-v4-path-only-') as tmp:
            script, native, other = self.fixture(pathlib.Path(tmp))
            variants = ((script.parent, 'led_action.py'),
                        (script.parent, './led_action.py'),
                        (script.parent, str(script)),
                        (other, str(script)),
                        (other, os.path.relpath(script, other)))
            for cwd, invoked_as in variants:
                with self.subTest(absolute=pathlib.Path(invoked_as).is_absolute(), other_cwd=cwd == other):
                    with working_directory(cwd), patch.object(m, '__file__', invoked_as):
                        chosen = m.native_executable()
                        self.assertTrue(chosen.is_absolute())
                        self.assertEqual(chosen, native)
                        x = Launch(entry=12.2)
                        result, _ = x.run()
                    self.assertEqual(result, 0)
                    self.assertEqual(len(x.calls), 1)
                    self.assertEqual(x.calls[0][0], str(native))
                    self.assertIn(' ', x.calls[0][0])

    def test_missing_native_rejected_before_password_network_or_consent(self):
        with tempfile.TemporaryDirectory(prefix='evilduck-v4-path-only-') as tmp:
            script, native, _ = self.fixture(pathlib.Path(tmp))
            native.unlink()
            with patch.object(m, '__file__', str(script)):
                with self.assertRaisesRegex(ValueError, 'COMPILE_NATIVE_HELPER_FIRST'):
                    m.native_executable()

    def test_native_symlink_still_rejected_without_resolving_leaf(self):
        with tempfile.TemporaryDirectory(prefix='evilduck-v4-path-only-') as tmp:
            script, native, _ = self.fixture(pathlib.Path(tmp))
            actual = native.with_name('different-native')
            native.rename(actual)
            native.symlink_to(actual)
            with patch.object(m, '__file__', str(script)):
                with self.assertRaisesRegex(ValueError, 'COMPILE_NATIVE_HELPER_FIRST'):
                    m.native_executable()

    def test_nonexecutable_native_rejected(self):
        with tempfile.TemporaryDirectory(prefix='evilduck-v4-path-only-') as tmp:
            script, native, _ = self.fixture(pathlib.Path(tmp))
            native.chmod(0o600)
            with patch.object(m, '__file__', str(script)):
                with self.assertRaisesRegex(ValueError, 'COMPILE_NATIVE_HELPER_FIRST'):
                    m.native_executable()

    def test_script_symlink_selects_real_script_sibling_and_keeps_native_leaf_check(self):
        with tempfile.TemporaryDirectory(prefix='evilduck-v4-path-only-') as tmp:
            script, native, other = self.fixture(pathlib.Path(tmp))
            link = other / 'script-link.py'
            link.symlink_to(script)
            with patch.object(m, '__file__', str(link)):
                self.assertEqual(m.native_executable(), native)
            native.unlink()
            with patch.object(m, '__file__', str(link)):
                with self.assertRaisesRegex(ValueError, 'COMPILE_NATIVE_HELPER_FIRST'):
                    m.native_executable()


if __name__ == '__main__':
    unittest.main(verbosity=2)
