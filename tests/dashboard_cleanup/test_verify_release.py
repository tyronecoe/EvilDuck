"""Inert AST policy tests. No target build, image execution or hardware."""
import ast
import unittest
from verify_release import FinalCandidateExpectations, RuntimeIdentityExpectations, BUILD_ID

FINAL = {"cli.cpp": "private-cli", "webserver.cpp": "private-server",
         "webfiles.h": "dashboard-web", "caps_trial.h": "dashboard-id"}


class FakePath:
    def __truediv__(self, value):
        return self


class FakeElf:
    def __init__(self, data):
        self.data = data

    def read_bytes(self):
        return self.data


class SourcePolicy(unittest.TestCase):
    def test_exact_four_hashes_original_fallback_and_tamper(self):
        tree = ast.parse("assert sha(sketch/name) == original\n")
        policy = FinalCandidateExpectations(FINAL)
        transformed = ast.fix_missing_locations(policy.visit(tree))
        self.assertEqual(len(policy.edits), 1)
        for name, actual, original, accepted in [
            ("cli.cpp", "private-cli", "old", True),
            ("webserver.cpp", "private-server", "old", True),
            ("webfiles.h", "dashboard-web", "old", True),
            ("caps_trial.h", "dashboard-id", "old", True),
            ("core.cpp", "unchanged", "unchanged", True),
            ("core.cpp", "tampered", "unchanged", False),
            ("caps_trial.h", "tampered", "old", False),
        ]:
            with self.subTest(name=name, actual=actual):
                run = lambda: exec(compile(transformed, "<source-policy>", "exec"),
                                   dict(sha=lambda _: actual, sketch=FakePath(), name=name, original=original))
                if accepted:
                    run()
                else:
                    with self.assertRaises(AssertionError):
                        run()

    def test_historical_pins_and_source_copy_guards_unchanged(self):
        source = """assert pin['build_id'] == BUILD
assert old_inventory[row['file']] == row['sha256']
assert sha(core/archive) == expected
assert sha(elf) == expected
assert copy.read_bytes() == original.read_bytes()
"""
        tree = ast.parse(source)
        policy = FinalCandidateExpectations(FINAL)
        changed = policy.visit(tree)
        self.assertEqual(policy.edits, [])
        self.assertEqual(ast.dump(changed), ast.dump(ast.parse(source)))


class RuntimeIdentityPolicy(unittest.TestCase):
    def adapt(self, source):
        tree = ast.parse(source)
        before = sum(isinstance(node, ast.Assert) for node in ast.walk(tree))
        policy = RuntimeIdentityExpectations(tree)
        tree = ast.fix_missing_locations(policy.visit(tree))
        self.assertEqual(sum(isinstance(node, ast.Assert) for node in ast.walk(tree)), before)
        return tree, policy.edits

    def test_new_runtime_id_does_not_change_historical_pin_or_assignment(self):
        source = """BUILD='HISTORICAL-H1'
data=elf.read_bytes()
assert pin['build_id'] == BUILD
assert BUILD.encode() in data
"""
        tree, edits = self.adapt(source)
        self.assertEqual(len(edits), 1)
        for actual, accepted in [(BUILD_ID.encode(), True), (b"HISTORICAL-H1", False), (b"unrelated", False)]:
            with self.subTest(actual=actual):
                scope = dict(elf=FakeElf(actual), pin={"build_id": "HISTORICAL-H1"})
                run = lambda: exec(compile(tree, "<identity-policy>", "exec"), scope)
                if accepted:
                    run()
                    self.assertEqual(scope["BUILD"], "HISTORICAL-H1")
                else:
                    with self.assertRaises(AssertionError):
                        run()

    def test_direct_memberships_and_boolean_compound_keep_other_capability(self):
        tree, edits = self.adapt("assert BUILD_ID.encode() in elf.read_bytes() and b'$_EVILDUCK_LOCK_TIMEOUT' in elf.read_bytes()")
        self.assertEqual(len(edits), 1)
        exec(compile(tree, "<identity-policy>", "exec"), dict(elf=FakeElf(BUILD_ID.encode()+b" $_EVILDUCK_LOCK_TIMEOUT")))
        with self.assertRaises(AssertionError):
            exec(compile(tree, "<identity-policy>", "exec"), dict(elf=FakeElf(BUILD_ID.encode())))
        tree, edits = self.adapt("assert b'ROUTEB-OLD' in elf.read_bytes()")
        self.assertEqual(len(edits), 1)
        exec(compile(tree, "<identity-policy>", "exec"), dict(elf=FakeElf(BUILD_ID.encode())))

    def test_non_elf_and_nonidentity_membership_untouched(self):
        source = """data=parent.read_bytes()
assert BUILD.encode() in data
assert b'INJECT_VAR' in elf.read_bytes()
assert token.encode()+b'\\0' in data
assert pin['build_id'] == BUILD
"""
        tree, edits = self.adapt(source)
        self.assertEqual(edits, [])
        self.assertEqual(ast.dump(tree), ast.dump(ast.parse(source)))


if __name__ == "__main__":
    unittest.main()
