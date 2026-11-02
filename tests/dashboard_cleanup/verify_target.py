#!/usr/bin/env python3
"""Additive final-dashboard expectations over every privacy target guard."""
import argparse
import hashlib
import json
import pathlib
import shlex
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / "tests/privacy_fix1/verify_target.py"
PARENT_SHA = "d6af79682101b8ca36e0ec7a950275b2504c61c8c109083ac2aa0f170d76170e"
BUILD_ID = "ROUTEB-DASHBOARD-CLEANUP-v1"


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def parent_namespace():
    data = PARENT.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PARENT_SHA
    text = data.decode()
    changes = []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('manifest_path = ROOT / "tests/privacy_fix1/source-manifest.json"',
            'manifest_path = ROOT / "tests/dashboard_cleanup/source-manifest.json"')
    replace('sha(ROOT / "tests/h1_right_modifiers/prepare_sources.py")', 'sha(ROOT / "tests/privacy_fix1/prepare_sources.py")')
    replace('sha(ROOT / "tests/privacy_fix1/application.patch")', 'sha(ROOT / "tests/dashboard_cleanup/application.patch")')
    replace('len(pin["after"]) == 3 and len(pin["unchanged"]) == 198', 'len(pin["after"]) == 2 and len(pin["unchanged"]) == 199')
    replace('"Privacy manifest is not the reviewed 3/198 source delta"', '"Dashboard manifest is not the reviewed 2/199 source delta"')
    replace('{"cli.cpp", "webserver.cpp", "webfiles.h"}', '{"webfiles.h", "caps_trial.h"}')
    replace('require(b"ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1" in data, "Expected retained H1 build identity missing")',
            'require(' + repr(BUILD_ID.encode()) + ' in data, "Expected dashboard candidate identity missing")')
    replace('source_files=201, privacy_files=3, unchanged_files=198',
            'source_files=201, dashboard_files=2, unchanged_files=199, comparison_base="privacy-fix1", cumulative_h1_changed_files=4, cumulative_h1_unchanged_files=197')
    replace('privacy_patch_sha256=pin["patch_sha256"]', 'dashboard_patch_sha256=pin["patch_sha256"]')
    replace('profile="PRIVACY FIX 1 COMPILE-ONLY REVIEW; H1 REMAINS EXPERIMENTAL"', 'profile="DASHBOARD CLEANUP / PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW"')
    replace('build_id_policy="Historical H1 dashboard build ID retained; privacy inventory, output directory and application SHA identify this local candidate"',
            'build_id_policy="Distinct dashboard candidate BuildId; source inventory and application SHA remain exact artifact identity"')
    ns = dict(__name__="dashboard_privacy_target_verifier", __file__=str(__file__))
    exec(compile(text, str(PARENT), "exec"), ns)
    return ns, changes


def verify(build_root):
    ns, changes = parent_namespace()
    require = ns["require"]
    pin_path = ROOT / "tests/dashboard_cleanup/source-manifest.json"
    pin = json.loads(pin_path.read_text())
    privacy_path = ROOT / "tests/privacy_fix1/source-manifest.json"
    privacy = json.loads(privacy_path.read_text())
    require(pin["format"] == "evilduck-dashboard-cleanup-v1" and pin["build_id"] == BUILD_ID and
            pin["baseline"] == "70d08e9f789c187c5e27350a66f4d0d52992964b", "Wrong dashboard identity")
    require(pin["privacy_manifest_sha256"] == sha(privacy_path), "Privacy base manifest identity changed")
    require(privacy["parent_prepare_sha256"] == sha(ROOT / "tests/h1_right_modifiers/prepare_sources.py"), "Historical H1 preparer changed")
    require(privacy["baseline_inventory_sha256"] == sha(ROOT / "docs/h1-right-modifiers-build.json"), "Privacy dependency baseline changed")
    require(privacy["patch_sha256"] == sha(ROOT / "tests/privacy_fix1/application.patch"), "Privacy source patch changed")
    require(len(privacy["before"]) == len(privacy["after"]) == 3 and len(privacy["unchanged"]) == 198 and
            {row["file"] for row in privacy["after"]} == {"cli.cpp", "webserver.cpp", "webfiles.h"}, "Privacy base delta changed")
    prior = {row["file"]: row["sha256"] for row in privacy["after"] + privacy["unchanged"]}
    require(len(prior) == 201, "Privacy base inventory incomplete")
    require(len(pin["before"]) == 2 and {row["file"] for row in pin["before"]} == {"webfiles.h", "caps_trial.h"}, "Unexpected dashboard before set")
    for row in pin["before"] + pin["unchanged"]:
        require(prior.get(row["file"]) == row["sha256"], "Dashboard base differs from privacy: " + row["file"])
    final = {row["file"]: row["sha256"] for row in pin["after"] + pin["unchanged"]}
    baseline = json.loads((ROOT / "docs/h1-right-modifiers-build.json").read_text())
    h1 = {row["file"].removeprefix("EvilDuckS3/"): row["sha256"] for row in baseline["source_inventory"]}
    cumulative = {name: digest for name, digest in final.items() if h1.get(name) != digest}
    declared = {row["file"]: row["sha256"] for row in pin["cumulative_h1_after"]}
    require(len(pin["cumulative_h1_after"]) == 4 and cumulative == declared and
            set(cumulative) == {"cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}, "Cumulative H1 delta differs")
    binding = ns["verify"](build_root)
    root = pathlib.Path(build_root).resolve()
    build, sketch = root / "build", root / "candidate/EvilDuckS3"
    report = json.loads((root / "report.json").read_text())
    entries = json.loads((build / "compile_commands.json").read_text())
    selected = [row for row in entries if pathlib.Path(row["file"]).name == "caps_trial.cpp"]
    require(len(selected) == 1, "Expected one actual Caps-trial compilation")
    entry = selected[0]
    compiled = pathlib.Path(entry["file"])
    require(compiled == build / "sketch/caps_trial.cpp" and
            ns["source_matches"]((sketch / "caps_trial.cpp").read_bytes(), compiled.read_bytes(), sketch / "caps_trial.cpp"),
            "Compiled Caps-trial source differs")
    args = entry["arguments"]
    obj = pathlib.Path(args[args.index("-o") + 1])
    require(obj == build / "sketch/caps_trial.cpp.o" and sha(args[0]) == baseline["compiler_sha256"], "Wrong Caps-trial object/compiler")
    target, dependencies = ns["make_dependencies"](obj.with_suffix(".d").read_text())
    header = build / "sketch/caps_trial.h"
    require(pathlib.Path(target) == obj and str(compiled) in dependencies and str(header) in dependencies,
            "Distinct build-ID header missing from actual compilation dependencies")
    require(ns["source_matches"]((sketch / "caps_trial.h").read_bytes(), header.read_bytes(), sketch / "caps_trial.h"),
            "Compiled build-ID header differs")
    loaded = {line.removeprefix("LOAD ").strip() for line in (build / "EvilDuckS3.ino.map").read_text().splitlines() if line.startswith("LOAD ")}
    inputs = {row["file"]: row for row in report["linked_input_hashes"]}
    require(str(obj) in loaded and str(obj) in inputs and inputs[str(obj)]["sha256"] == sha(obj), "Build-ID consumer object not bound to link")
    command_lines = []
    for line in (build / "s3-build.log").read_text().splitlines():
        if " -c " in line:
            try:
                command = shlex.split(line)
            except ValueError:
                continue
            if "-o" in command and str(compiled) in command and command[command.index("-o") + 1] == str(obj):
                command_lines.append(command)
    require(len(command_lines) == 1, "Actual build-ID consumer compile absent/ambiguous")
    binding.update(build_id=BUILD_ID, privacy_manifest_sha256=sha(privacy_path),
        privacy_patch_sha256=privacy["patch_sha256"], parent_target_verifier_sha256=PARENT_SHA,
        dashboard_source_manifest_sha256=sha(pin_path), cumulative_h1_source_overrides=cumulative,
        identity_header=dict(source="caps_trial.h", candidate_sha256=final["caps_trial.h"],
            compiled_header=str(header), compiled_sha256=sha(header), dependency_observed=True,
            dependency_file=str(obj.with_suffix(".d")), object=str(obj), object_sha256=sha(obj),
            verbose_compile_observed=True, linked_map_load=True, metadata_only=True),
        target_verifier_adaptations=changes)
    return binding


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()
    assert not args.output.exists()
    result = verify(args.build_root)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS dashboard final source/header/object/identity binding; no physical verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
