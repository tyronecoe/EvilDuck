"""Focused AST policy controls; no target build or hardware execution."""
import ast
import unittest
from verify_release import FinalCandidateExpectations

FINAL = {"cli.cpp": "privacy-cli", "webserver.cpp": "privacy-web", "webfiles.h": "privacy-header"}


class FinalExpectations(unittest.TestCase):
    def adapt(self, source):
        original = ast.parse(source)
        count = sum(isinstance(x, ast.Assert) for x in ast.walk(original))
        policy = FinalCandidateExpectations(FINAL)
        tree = policy.visit(original)
        ast.fix_missing_locations(tree)
        self.assertEqual(sum(isinstance(x, ast.Assert) for x in ast.walk(tree)), count)
        return tree, policy.edits

    def test_exact_three_names_and_original_fallback(self):
        tree, edits = self.adapt("assert sha(sketch/name) == expected\n")
        self.assertEqual(len(edits), 1)
        code = compile(tree, "<policy-test>", "exec")
        for name, actual, expected, accepted in [
            ("cli.cpp", "privacy-cli", "old-cli", True),
            ("webserver.cpp", "privacy-web", "old-web", True),
            ("webfiles.h", "privacy-header", "old-header", True),
            ("core.cpp", "old-core", "old-core", True),
            ("core.cpp", "tampered-core", "old-core", False),
            ("cli.cpp", "tampered-cli", "old-cli", False),
        ]:
            with self.subTest(name=name, actual=actual):
                scope = dict(sha=lambda _: actual, sketch=FakePath(), name=name, expected=expected)
                if accepted: exec(code, scope)
                else:
                    with self.assertRaises(AssertionError): exec(code, scope)

    def test_hashlib_candidate_path_supported(self):
        _, edits = self.adapt("assert hashlib.sha256((args.build_root/'candidate/EvilDuckS3'/row['file']).read_bytes()).hexdigest() == row['sha256']")
        self.assertEqual(len(edits), 1)

    def test_historical_pins_and_other_boundaries_unchanged(self):
        source = """assert old_inventory[row['file']] == row['sha256']
assert hashlib.sha256(parent.read_bytes()).hexdigest() == PARENT_SHA
assert sha(core/archive) == archive_pin
assert sha(elf) == image_pin
assert copy.read_bytes() == original.read_bytes()
assert sha(a.build_root/'candidate'/x['file']) == x['sha256']
"""
        tree, edits = self.adapt(source)
        self.assertEqual(edits, [])
        self.assertEqual(ast.dump(tree), ast.dump(ast.parse(source)))


class FakePath:
    def __truediv__(self, value): return self


if __name__ == "__main__": unittest.main()
