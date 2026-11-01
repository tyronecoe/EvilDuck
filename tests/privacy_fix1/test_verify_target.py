"""Pure provenance-parser checks; no compiler, firmware or device operations."""
import json
import pathlib
import unittest

from verify_target import make_dependencies, source_matches


class DependencyParser(unittest.TestCase):
    def test_pinned_gcc_rule(self):
        rule = "/tmp/a.cpp.o: /tmp/a.cpp " + "\\\n" + " /tmp/webfiles.h\n"
        target, dependencies = make_dependencies(rule)
        self.assertEqual(target, "/tmp/a.cpp.o")
        self.assertEqual(dependencies, ["/tmp/a.cpp", "/tmp/webfiles.h"])

    def test_escaped_paths_and_crlf(self):
        rule = "/tmp/a\\ b.cpp.o: /tmp/a\\ b.cpp " + "\\\r\n" + " /tmp/web\\#files.h /tmp/cost$$.h\r\n"
        target, dependencies = make_dependencies(rule)
        self.assertEqual(target, "/tmp/a b.cpp.o")
        self.assertEqual(dependencies, ["/tmp/a b.cpp", "/tmp/web#files.h", "/tmp/cost$.h"])

    def test_unsupported_rules_rejected(self):
        for text in ["", "no separator", "a.o:", "a.o b.o: a.cpp", "a.o: a.cpp\nb.o: b.cpp\n"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                make_dependencies(text)


class CopiedSource(unittest.TestCase):
    def test_exact_or_correct_arduino_directive_only(self):
        path = pathlib.Path("/tmp/a b/webfiles.h")
        raw = b"reviewed source\n"
        prefix = ("#line 1 " + json.dumps(str(path)) + "\n").encode()
        self.assertTrue(source_matches(raw, raw, path))
        self.assertTrue(source_matches(raw, prefix + raw, path))
        self.assertFalse(source_matches(raw, b'#line 1 "/wrong/header"\n' + raw, path))
        self.assertFalse(source_matches(raw, prefix + raw + b"changed", path))


if __name__ == "__main__":
    unittest.main()
