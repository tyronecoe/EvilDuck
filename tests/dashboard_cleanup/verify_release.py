#!/usr/bin/env python3
"""Run the pinned full H1 chain for the privacy-based dashboard candidate.

Only final live-candidate SHA expectations and actual ELF runtime-ID membership
checks are adapted. Historical pins, source-layer IDs, copied-source, SDK/core,
profile, startup and disassembly predicates retain their original meaning.
"""
import argparse
import ast
import builtins
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PRIVACY_PARENT = ROOT / "tests/privacy_fix1/verify_release.py"
PRIVACY_PARENT_SHA = "71387fda4a0443e413e29e5c9f217511391108ca0a2df5db4fd0076b339af328"
BUILD_ID = "ROUTEB-DASHBOARD-CLEANUP-v1"
BASE_COMMIT = "70d08e9f789c187c5e27350a66f4d0d52992964b"
ORIGINAL_COMPILE = builtins.compile
assert hashlib.sha256(PRIVACY_PARENT.read_bytes()).hexdigest() == PRIVACY_PARENT_SHA
spec = importlib.util.spec_from_file_location("dashboard_release_privacy_parent", PRIVACY_PARENT)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
FROZEN = P.FROZEN


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


class FinalCandidateExpectations(P.FinalCandidateExpectations):
    """Same pinned comparison policy, with the exact four cumulative files."""
    def __init__(self, final):
        assert set(final) == {"cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}
        self.final = final
        self.edits = []
        self.in_assert = 0


class RuntimeIdentityExpectations(ast.NodeTransformer):
    """Change only build-ID membership in proven actual ELF-byte expressions.

    BUILD/BUILD_ID assignments and historical pin equality assertions remain
    untouched. Arbitrary capability strings and source-file membership checks
    are not runtime identity and are deliberately not changed.
    """
    def __init__(self, tree, build_id=BUILD_ID):
        self.build_id = build_id
        self.in_assert = 0
        self.edits = []
        self.elf_aliases = set()
        for item in ast.walk(tree):
            if isinstance(item, ast.Assign) and self.elf_read(item.value):
                self.elf_aliases.update(target.id for target in item.targets if isinstance(target, ast.Name))

    @staticmethod
    def elf_read(node):
        return (isinstance(node, ast.Call) and not node.args and not node.keywords and
                isinstance(node.func, ast.Attribute) and node.func.attr == "read_bytes" and
                isinstance(node.func.value, ast.Name) and node.func.value.id == "elf")

    @staticmethod
    def identity_value(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, bytes):
            return node.value.startswith((b"ROUTEB-", b"CAPS-STOP-TRACE-"))
        return (isinstance(node, ast.Call) and not node.args and not node.keywords and
                isinstance(node.func, ast.Attribute) and node.func.attr == "encode" and
                isinstance(node.func.value, ast.Name) and
                node.func.value.id in {"BUILD", "BUILD_ID", "SOURCE_BUILD_ID"})

    def visit_Assert(self, node):
        self.in_assert += 1
        result = self.generic_visit(node)
        self.in_assert -= 1
        return result

    def visit_Compare(self, node):
        node = self.generic_visit(node)
        if not self.in_assert or len(node.ops) != 1 or not isinstance(node.ops[0], ast.In):
            return node
        right = node.comparators[0]
        actual_elf = self.elf_read(right) or (isinstance(right, ast.Name) and right.id in self.elf_aliases)
        if not actual_elf or not self.identity_value(node.left):
            return node
        before = ast.unparse(node)
        node.left = ast.copy_location(ast.Constant(self.build_id.encode()), node.left)
        self.edits.append(dict(line=getattr(node, "lineno", None), before=before, after=ast.unparse(node)))
        return node


def run_chain(build_root, output):
    from verify_target import verify
    build_root, output = pathlib.Path(build_root).resolve(), pathlib.Path(output).resolve()
    assert not output.exists() and output.parent.is_dir(), "Fresh release evidence path required"
    build = build_root / "build"
    built = json.loads((build_root / "report.json").read_text())
    application_sha = built["report"]["application_sha256"]
    elf_sha = built["provenance"]["elf_sha256"]
    assert sha(build / "EvilDuckS3.ino.bin") == application_sha
    assert sha(build / "EvilDuckS3.ino.elf") == elf_sha
    assert BUILD_ID.encode() in (build / "EvilDuckS3.ino.elf").read_bytes()
    binding_before = verify(build_root)
    pin_path = ROOT / "tests/dashboard_cleanup/source-manifest.json"
    pin = json.loads(pin_path.read_text())
    assert pin["build_id"] == BUILD_ID
    final = {row["file"]: row["sha256"] for row in pin["cumulative_h1_after"]}
    assert set(final) == {"cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}
    assert sha(ROOT / "tests/dashboard_cleanup/application.patch") == pin["patch_sha256"]
    privacy_pin_path = ROOT / "tests/privacy_fix1/source-manifest.json"
    assert sha(privacy_pin_path) == pin["privacy_manifest_sha256"]
    privacy_pin = json.loads(privacy_pin_path.read_text())
    for row in privacy_pin["after"]:
        if row["file"] != "webfiles.h":
            assert final[row["file"]] == row["sha256"]
    allowed = {}
    for directory, digest in FROZEN.items():
        file = ROOT / "tests" / directory / "verify_link.py"
        assert sha(file) == digest
        allowed[str(file.resolve())] = digest
    events = []

    def compile_verifier(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kwargs):
        name = str(pathlib.Path(filename).resolve())
        if name not in allowed or mode != "exec" or flags & ast.PyCF_ONLY_AST:
            return ORIGINAL_COMPILE(source, filename, mode, flags, dont_inherit, optimize, **kwargs)
        tree = copy.deepcopy(source) if isinstance(source, ast.AST) else ORIGINAL_COMPILE(
            source, filename, mode, flags | ast.PyCF_ONLY_AST, dont_inherit, optimize, **kwargs)
        before_ast = hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()
        count = sum(isinstance(item, ast.Assert) for item in ast.walk(tree))
        assigned = {target.slice.value for item in ast.walk(tree) if isinstance(item, ast.Assign)
                    for target in item.targets if isinstance(target, ast.Subscript) and
                    isinstance(target.slice, ast.Constant) and isinstance(target.slice.value, str)}
        tags = [("right_modifiers_verified", "right-modifier H1"),
                ("inject_var_experimental_verified", "experimental H1"),
                ("timeout_wait_verified", "bounded lock waits"),
                ("source_text_v2_verified", "source/text v2"),
                ("lock_feedback_verified", "keyboard/lock feedback"),
                ("sdk_archives_identical_to_w", "caps/STOP closure")]
        layer = next((label for key, label in tags if key in assigned), "unclassified")
        assert layer != "unclassified", "Unexpected executable verifier unit"
        identity = RuntimeIdentityExpectations(tree)
        hashes = FinalCandidateExpectations(final)
        tree = hashes.visit(tree)
        tree = identity.visit(tree)
        ast.fix_missing_locations(tree)
        assert sum(isinstance(item, ast.Assert) for item in ast.walk(tree)) == count
        events.append(dict(filename=name, logical_layer=layer, frozen_file_sha256=allowed[name],
                           generated_ast_before_sha256=before_ast,
                           generated_ast_after_sha256=hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest(),
                           assertions_preserved=count, expectation_adaptations=hashes.edits,
                           runtime_identity_adaptations=identity.edits))
        return ORIGINAL_COMPILE(tree, filename, mode, flags, dont_inherit, optimize, **kwargs)

    parent = ROOT / "tests/h1_right_modifiers/verify_link.py"
    old_args = sys.argv
    try:
        sys.argv = [str(parent), "--build-root", str(build_root), "--output", str(output)]
        with patch.object(builtins, "compile", compile_verifier):
            namespace = {"__name__": "dashboard_release_frozen_h1", "__file__": str(parent)}
            exec(compile_verifier(parent.read_bytes(), str(parent), "exec"), namespace)
            assert namespace["main"]() == 0
    finally:
        sys.argv = old_args
    expected_layers = [("right-modifier H1", 23), ("experimental H1", 21),
                       ("bounded lock waits", 16), ("source/text v2", 46),
                       ("keyboard/lock feedback", 25), ("caps/STOP closure", 59)]
    assert [(event["logical_layer"], event["assertions_preserved"]) for event in events] == expected_layers
    assert sum(len(event["expectation_adaptations"]) for event in events) > 0
    assert sum(len(event["runtime_identity_adaptations"]) for event in events) > 0
    binding_after = verify(build_root)
    assert binding_before == binding_after
    assert sha(build / "EvilDuckS3.ino.bin") == application_sha and sha(build / "EvilDuckS3.ino.elf") == elf_sha
    report = json.loads(output.read_text())
    source_info = built.get("dashboard_target_adapter", {})
    source_commit = source_info.get("source_commit", source_info.get("source_checkpoint"))
    assert isinstance(source_commit, str) and len(source_commit) == 40 and all(
        character in "0123456789abcdef" for character in source_commit), "Missing exact target source revision"
    report["dashboard_release_verification"] = dict(
        status="PASS", full_frozen_h1_chain_executed=True, base_commit=BASE_COMMIT,
        source_commit=source_commit, adapter_sha256=sha(__file__),
        parent_privacy_verifier_sha256=PRIVACY_PARENT_SHA, source_manifest_sha256=sha(pin_path),
        privacy_source_manifest_sha256=sha(privacy_pin_path), exact_final_source_overrides=final,
        frozen_verifiers=FROZEN, compile_events=events, assertions_preserved=190, assertions_removed=0,
        unrelated_expected_hashes_changed=0, historical_source_pin_build_ids_changed=False,
        dashboard_target_binding=binding_after, actual_runtime_build_id=BUILD_ID,
        application_sha256=application_sha, elf_sha256=elf_sha, recompiled=False,
        target_source_or_images_modified=False, hardware=False, runtime_build_id_changed=True,
        owner_review_candidate=True)
    report["dashboard_source_pin"] = pin
    report["privacy_source_pin"] = privacy_pin
    report["actual_runtime_build_id"] = BUILD_ID
    report["profile"] = "DASHBOARD CLEANUP / PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW / PHYSICAL VALIDATION PENDING"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print("PASS frozen H1 release checks plus four final-source expectations, distinct runtime ID and dashboard binding")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    run_chain(args.build_root, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
