#!/usr/bin/env python3
"""Select existing L01-L19 cases without modifying the historical production runner.

The only in-memory AST replacement is the top-level case-loop iterable. Source
composition, dependency pins, compiler/sanitizer flags and case assertions remain
those of the pinned caps_stop runner. This is a native mocked source test, not a
target firmware compilation or a physical USB operation.
"""
import argparse
import ast
import hashlib
import json
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tests/caps_stop/run_tests.py"
RUNNER_SHA256 = "52c71bcca3f7734b02b2b518fd5814efda55ef540d7b412e74ff52663301d225"
CASES = ["L%02d" % i for i in range(1, 20)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", type=pathlib.Path, required=True)
    parser.add_argument("--build-dir", type=pathlib.Path, required=True)
    parser.add_argument("--results", type=pathlib.Path, required=True)
    args = parser.parse_args()
    source = RUNNER.read_bytes()
    if hashlib.sha256(source).hexdigest() != RUNNER_SHA256:
        raise RuntimeError("Historical runner source mismatch; refusing adaptation")
    tree = ast.parse(source, filename=str(RUNNER))
    loops = [node for node in tree.body if isinstance(node, ast.For)
             and isinstance(node.target, ast.Name) and node.target.id == "n"]
    if len(loops) != 1:
        raise RuntimeError("Expected exactly one top-level historical case loop")
    loop = loops[0]
    original_iterable = ast.dump(loop.iter, include_attributes=False)
    replacement = ast.List(elts=[ast.Constant(value=name) for name in CASES], ctx=ast.Load())
    loop.iter = ast.copy_location(replacement, loop.iter)
    ast.fix_missing_locations(tree)
    sys.path.insert(0, str(RUNNER.parent))
    sys.argv = [str(RUNNER), "--core", str(args.core), "--build-dir", str(args.build_dir),
                "--results", str(args.results)]
    exit_code = 0
    try:
        exec(compile(tree, str(RUNNER), "exec"), {"__name__": "__main__", "__file__": str(RUNNER)})
    except SystemExit as stopped:
        exit_code = stopped.code if isinstance(stopped.code, int) else 1
    if hashlib.sha256(RUNNER.read_bytes()).hexdigest() != RUNNER_SHA256:
        raise RuntimeError("Historical runner changed during verification")
    result = json.loads(args.results.read_text())
    if [row["id"] for row in result["results"]] != CASES:
        raise RuntimeError("Unexpected selected case execution")
    result["focused_case_selection"] = {
        "historical_runner": "tests/caps_stop/run_tests.py",
        "historical_runner_sha256": RUNNER_SHA256,
        "historical_file_modified": False,
        "selected_cases": CASES,
        "method": "Only top-level for-n iterable replaced in memory via AST; setup/flags/assertions unchanged",
        "original_iterable_ast_sha256": hashlib.sha256(original_iterable.encode()).hexdigest(),
        "native_iokit_execution": False,
    }
    args.results.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("counts", "assertions", "sanitizers",
                                                 "hardware", "target_firmware_built")}, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
