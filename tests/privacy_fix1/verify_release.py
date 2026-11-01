#!/usr/bin/env python3
"""Execute the frozen full H1 release chain against the exact privacy image.

Only final candidate-source SHA expectations for the reviewed three-file delta
are adapted. No target source, image, historical verifier or before/pin check is
edited. Every unrelated assertion and linked-code predicate remains executable.
"""
import argparse
import ast
import builtins
import copy
import hashlib
import json
import pathlib
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
ORIGINAL_COMPILE = builtins.compile
FROZEN = {
    "h1_right_modifiers": "ce94c470a80843ec7dd18102739b052a0445b2a672519cf35f7e5b566f4f19cd",
    "inject_var_experimental": "6da2ddaad1800354a032193e78e6f1775da376e15c30ce77d170b0f6c87e02e4",
    "lock_wait_timeout": "d8ab7a0d35efe18ac425bcada05d21ba7d0b84108caa18781661e678e0f1776e",
    "source_text_v2": "e155bf66e2c5892b49d7241d36f21dc4b10b6ac2cb1bbf95a96596b02bb07182",
    "lock_feedback": "45d52ec2abdbc18cfcc03d24e672a8aa02088074efa119b638dc76e4af180d7d",
    "caps_stop": "bf2c6a7050a2601f285f7e76eb26936399f2b07a12bc56f212903e645ccb4e6d",
}
APPLICATION_SHA = "9e4d3b615d78e87521882a35c4b43ce66403168a15b6b39bcebc81bb32a6b96e"
ELF_SHA = "af7887ceccfe2694738c173c76b3c211b78cb0c7b667d8d7d942a1b0ef317f6e"


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


class FinalCandidateExpectations(ast.NodeTransformer):
    """Keep the original comparison, replacing only its expected hash operand.

    The fallback is byte-for-byte the original expected expression. The lookup
    has exactly three literal keys, so all other source and protection checks
    retain their expected values. Historical manifest-before/pin checks do not
    read a live candidate source hash and are therefore never adapted.
    """
    def __init__(self, final):
        assert set(final) == {"cli.cpp", "webserver.cpp", "webfiles.h"}
        self.final = final
        self.edits = []
        self.in_assert = 0

    def visit_Assert(self, node):
        self.in_assert += 1
        result = self.generic_visit(node)
        self.in_assert -= 1
        return result

    @staticmethod
    def candidate_path(node):
        # sha(candidate_path), or hashlib.sha256(candidate_path.read_bytes()).hexdigest()
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sha" and len(node.args) == 1:
            path = node.args[0]
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and
              node.func.attr == "hexdigest" and isinstance(node.func.value, ast.Call)):
            digest = node.func.value
            if not (isinstance(digest.func, ast.Attribute) and digest.func.attr == "sha256" and
                    isinstance(digest.func.value, ast.Name) and digest.func.value.id == "hashlib" and
                    len(digest.args) == 1):
                return None
            read = digest.args[0]
            if not (isinstance(read, ast.Call) and isinstance(read.func, ast.Attribute) and read.func.attr == "read_bytes"):
                return None
            path = read.func.value
        else:
            return None
        if not isinstance(path, ast.BinOp) or not isinstance(path.op, ast.Div):
            return None
        # Deliberately do not match generic report inventory paths ('candidate')
        # or pinned source files under ROOT, tool archives, ELF/BIN or manifests.
        known = any(isinstance(x, ast.Name) and x.id == "sketch" for x in ast.walk(path.left))
        known = known or any(isinstance(x, ast.Constant) and x.value == "candidate/EvilDuckS3" for x in ast.walk(path.left))
        return path if known else None

    def visit_Compare(self, node):
        node = self.generic_visit(node)
        if not self.in_assert or len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
            return node
        path = self.candidate_path(node.left)
        if path is None:
            return node
        original = copy.deepcopy(node.comparators[0])
        before = ast.unparse(node)
        lookup = ast.Dict(keys=[ast.Constant(x) for x in sorted(self.final)],
                          values=[ast.Constant(self.final[x]) for x in sorted(self.final)])
        node.comparators[0] = ast.Call(func=ast.Attribute(value=lookup, attr="get", ctx=ast.Load()),
                                      args=[copy.deepcopy(path.right), original], keywords=[])
        self.edits.append(dict(line=getattr(node, "lineno", None), before=before, after=ast.unparse(node)))
        return node


def run_chain(build_root, output):
    from verify_target import verify
    build_root = pathlib.Path(build_root).resolve()
    output = pathlib.Path(output).resolve()
    assert not output.exists(), "Refusing to overwrite release verification evidence"
    assert output.parent.is_dir()
    assert sha(build_root / "build/EvilDuckS3.ino.bin") == APPLICATION_SHA
    assert (build_root / "build/EvilDuckS3.ino.bin").stat().st_size == 1415968
    assert sha(build_root / "build/EvilDuckS3.ino.elf") == ELF_SHA
    binding_before = verify(build_root)
    pin_path = ROOT / "tests/privacy_fix1/source-manifest.json"
    pin = json.loads(pin_path.read_text())
    final = {row["file"]: row["sha256"] for row in pin["after"]}
    assert set(final) == {"cli.cpp", "webserver.cpp", "webfiles.h"}
    assert sha(ROOT / "tests/privacy_fix1/application.patch") == pin["patch_sha256"]
    allowed = {}
    for directory, digest in FROZEN.items():
        path = ROOT / "tests" / directory / "verify_link.py"
        assert sha(path) == digest, str(path)
        allowed[str(path.resolve())] = digest
    events = []

    def compile_verifier(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kwargs):
        # Leave ast.parse untouched: each frozen parent performs its own pinned
        # transformation first. Adapt only the eventual executable verification.
        name = str(pathlib.Path(filename).resolve())
        if name not in allowed or mode != "exec" or flags & ast.PyCF_ONLY_AST:
            return ORIGINAL_COMPILE(source, filename, mode, flags, dont_inherit, optimize, **kwargs)
        tree = copy.deepcopy(source) if isinstance(source, ast.AST) else ORIGINAL_COMPILE(
            source, filename, mode, flags | ast.PyCF_ONLY_AST, dont_inherit, optimize, **kwargs)
        before_ast = hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()
        count = sum(isinstance(x, ast.Assert) for x in ast.walk(tree))
        assigned_keys = {target.slice.value for item in ast.walk(tree) if isinstance(item, ast.Assign)
                         for target in item.targets if isinstance(target, ast.Subscript) and
                         isinstance(target.slice, ast.Constant) and isinstance(target.slice.value, str)}
        tags = [("right_modifiers_verified", "right-modifier H1"),
                ("inject_var_experimental_verified", "experimental H1"),
                ("timeout_wait_verified", "bounded lock waits"),
                ("source_text_v2_verified", "source/text v2"),
                ("lock_feedback_verified", "keyboard/lock feedback"),
                ("sdk_archives_identical_to_w", "caps/STOP closure")]
        layer = next((label for key, label in tags if key in assigned_keys), "unclassified")
        assert layer != "unclassified", "Unexpected executable verifier unit"
        transform = FinalCandidateExpectations(final)
        tree = transform.visit(tree)
        ast.fix_missing_locations(tree)
        assert sum(isinstance(x, ast.Assert) for x in ast.walk(tree)) == count
        events.append(dict(filename=name, logical_layer=layer, frozen_file_sha256=allowed[name],
                           generated_ast_before_sha256=before_ast,
                           generated_ast_after_sha256=hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest(),
                           assertions_preserved=count,
                           expectation_adaptations=transform.edits))
        return ORIGINAL_COMPILE(tree, filename, mode, flags, dont_inherit, optimize, **kwargs)

    parent = ROOT / "tests/h1_right_modifiers/verify_link.py"
    old_args = sys.argv
    try:
        sys.argv = [str(parent), "--build-root", str(build_root), "--output", str(output)]
        with patch.object(builtins, "compile", compile_verifier):
            namespace = {"__name__": "privacy_release_frozen_h1", "__file__": str(parent)}
            exec(compile_verifier(parent.read_bytes(), str(parent), "exec"), namespace)
            assert namespace["main"]() == 0
    finally:
        sys.argv = old_args
    assert events and sum(len(x["expectation_adaptations"]) for x in events) > 0
    # Independently preserve the privacy-specific actual header/object binding.
    binding_after = verify(build_root)
    assert binding_before == binding_after
    assert sha(build_root / "build/EvilDuckS3.ino.bin") == APPLICATION_SHA
    assert sha(build_root / "build/EvilDuckS3.ino.elf") == ELF_SHA
    report = json.loads(output.read_text())
    report["privacy_release_verification"] = dict(
        status="PASS", full_frozen_h1_chain_executed=True, source_checkpoint="93cc8d1a7b162bdda91e239d840a3eee8a70c51c",
        target_integration_commit="0380d1508b8f761e30a6a1fb63f67c2850cbc84a",
        adapter_sha256=sha(__file__), source_manifest_sha256=sha(pin_path),
        exact_final_source_overrides=final, frozen_verifiers=FROZEN, compile_events=events,
        assertions_removed=0, unrelated_expected_hashes_changed=0,
        privacy_target_binding=binding_after, application_sha256=APPLICATION_SHA, elf_sha256=ELF_SHA,
        recompiled=False, target_source_or_images_modified=False, hardware=False,
        runtime_build_id_changed=False, owner_review_candidate=True)
    report["profile"] = "PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW CANDIDATE / PHYSICAL VALIDATION PENDING"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print("PASS full frozen H1 release checks plus exact three-file privacy hash adaptation and consumed-header binding")
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
