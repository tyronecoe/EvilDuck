#!/usr/bin/env python3
"""Focused composed-production verification; no hardware or target firmware build.

The historical Caps/STOP runner is hash-pinned and retained unchanged. Its native
driver and top-level case selection are explicitly adapted in memory, after which
the new source overlay/selector and copied test-only buildId expectations apply.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tests/caps_stop/run_tests.py"
RUNNER_SHA = "52c71bcca3f7734b02b2b518fd5814efda55ef540d7b412e74ff52663301d225"
NEW = ["Q%02d" % i for i in range(1, 38)]
REGRESSION = (["M%02d" % i for i in (1, 2, 3, 4, 7, 8, 14, 16, 24, 25, 26, 27, 32)] +
              ["G%02d" % i for i in (3, 5, 8, 16, 17, 18)] +
              ["E%02d" % i for i in (17, 20, 21)] +
              ["K%02d" % i for i in (1, 3, 4, 5, 7, 8, 11, 12, 13, 16, 17, 18, 24, 25)] +
              ["L%02d" % i for i in range(1, 20)] +
              ["W%02d" % i for i in (11, 15, 17, 18, 19, 20, 22, 23, 25, 27, 31, 32, 33)] +
              ["H%02d" % i for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 17, 18)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", type=pathlib.Path, required=True)
    parser.add_argument("--build-dir", type=pathlib.Path, required=True)
    parser.add_argument("--results", type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.build_dir.exists() and not args.results.exists()
    source = RUNNER.read_bytes()
    assert hashlib.sha256(source).hexdigest() == RUNNER_SHA, "historical runner changed"
    spec = importlib.util.spec_from_file_location("keyboard_prepare", ROOT / "tests/keyboard_control/prepare_sources.py")
    prepare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare)
    parent_spec = importlib.util.spec_from_file_location("prepare_sources", ROOT / "tests/caps_stop/prepare_sources.py")
    parent = importlib.util.module_from_spec(parent_spec)
    parent_spec.loader.exec_module(parent)
    sys.modules["prepare_sources"] = parent
    sys.path.insert(0, str(RUNNER.parent))
    tree = ast.parse(source, filename=str(RUNNER))
    changes = dict(driver=0, selection=0, pre_compile_hook=0)

    class Adapt(ast.NodeTransformer):
        def visit_Constant(self, node):
            if node.value == "tests/caps_stop/test_main.cpp":
                changes["driver"] += 1
                return ast.copy_location(ast.Constant(value="tests/keyboard_control/test_main.cpp"), node)
            return node

    tree = Adapt().visit(tree)
    for index, node in enumerate(list(tree.body)):
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == "n":
            node.iter = ast.copy_location(ast.List(elts=[ast.Constant(value=n) for n in NEW + REGRESSION], ctx=ast.Load()), node.iter)
            changes["selection"] += 1
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and
                isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "run" and
                isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == "subprocess"):
            hook = ast.parse("keyboard_before_compile(s, cmd)").body[0]
            # Index in the live list, not the enumeration snapshot.
            tree.body.insert(tree.body.index(node), ast.copy_location(hook, node))
            changes["pre_compile_hook"] += 1
    assert changes == dict(driver=1, selection=1, pre_compile_hook=1), changes
    ast.fix_missing_locations(tree)
    guard_results = []

    def before_compile(source_dir, command):
        prepare.delta(source_dir)
        command.insert(1, "-DEVILDUCK_ROUTE_B_KEYBOARD_CONTROL=1")
        for test_copy in source_dir.glob("*_cases.inc"):
            original = test_copy.read_text()
            test_copy.write_text(original.replace("CAPS-STOP-TRACE-", "ROUTEB-KEYBOARD-CONTROL-"))
        parent_driver = (ROOT / "tests/caps_stop/test_main.cpp").read_text()
        assert hashlib.sha256(parent_driver.encode()).hexdigest() == "a3649e68681e3457cff40058dec5c456b1e7796dc325ed2b27e552b78e8b8230"
        assert parent_driver.count("int main(int argc,char**argv)") == 1
        (source_dir / "control_parent_cases.inc").write_text(parent_driver.replace("int main(int argc,char**argv)", "int historical_caps_stop_main(int argc,char**argv)"))
        # Preprocess the exact changed compiler source with omitted/zero selector.
        # This checks the explicit profile rejection, not another firmware build.
        base = [arg for arg in command if not arg.endswith('.cpp') and arg != '-DEVILDUCK_ROUTE_B_KEYBOARD_CONTROL=1']
        out_at = base.index('-o')
        del base[out_at:out_at+2]
        base += ['-E', str(source_dir / 'core.cpp')]
        for label, flag in (('missing', []), ('zero', ['-DEVILDUCK_ROUTE_B_KEYBOARD_CONTROL=0'])):
            negative = subprocess.run(base + flag, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=30)
            expected = 'Explicit Route B keyboard-control candidate profile required'
            assert negative.returncode != 0 and expected in negative.stderr, label
            guard_results.append(dict(selector=label, result='EXPECTED_REJECTION', exit=negative.returncode, diagnostic=expected))

    sys.argv = [str(RUNNER), "--core", str(args.core), "--build-dir", str(args.build_dir), "--results", str(args.results)]
    exit_code = 0
    try:
        exec(compile(tree, str(RUNNER), "exec"), dict(__name__="__main__", __file__=str(RUNNER), keyboard_before_compile=before_compile))
    except SystemExit as stopped:
        exit_code = stopped.code if isinstance(stopped.code, int) else 1
    assert hashlib.sha256(RUNNER.read_bytes()).hexdigest() == RUNNER_SHA
    result = json.loads(args.results.read_text())
    assert [row["id"] for row in result["results"]] == NEW + REGRESSION
    for name, cases in (("keyboard_control", NEW), ("selected_unchanged_regressions", REGRESSION)):
        rows = [r for r in result["results"] if r["id"] in cases]
        result[name] = dict(PASS=sum(r["status"] == "PASS" for r in rows), FAIL=sum(r["status"] == "FAIL" for r in rows), assertions=sum(r["assertions"] for r in rows))
    result["historical_runner_sha256"] = RUNNER_SHA
    result["candidate_profile_negative_controls"] = guard_results
    result["in_memory_runner_adaptations"] = changes
    result["copied_test_identity_adjustment"] = "CAPS-STOP-TRACE- -> ROUTEB-KEYBOARD-CONTROL- in generated *_cases.inc only"
    result["new_case_ids"] = NEW
    result["regression_case_ids"] = REGRESSION
    result["historical_capability_refusals_replaced_not_relabelled"] = ["E18", "K23"]
    result["previously_superseded_historical_expectations"] = [dict(id="W34", expected_by_old_fixture="401 on auth contention", current_baseline_contract="409 on bounded auth-lock timeout", evidence="docs/http-snapshot-report.md:90-97; unchanged H09/H10/H18 rerun", disposition="not relabelled PASS; retained separate baseline observation")]
    args.results.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("counts", "assertions", "keyboard_control", "selected_unchanged_regressions", "sanitizers", "hardware", "target_firmware_built")}, indent=2))
    return exit_code


if __name__ == "__main__": raise SystemExit(main())
