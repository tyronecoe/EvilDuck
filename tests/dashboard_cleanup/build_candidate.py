#!/usr/bin/env python3
"""Select the pinned privacy-plus-dashboard overlay for a clean target build."""
import hashlib
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / "tests/privacy_fix1/build_candidate.py"
PARENT_SHA = "814cf12ac3ad8dd69ef460006c1610c890ea6b7ee8a9ef03daa16c1da63c1f80"
BUILD_ID = "ROUTEB-DASHBOARD-CLEANUP-v1"
PROFILE = "DASHBOARD CLEANUP / PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW ONLY"


def adapted_source(source_commit):
    data = PARENT.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PARENT_SHA
    text = data.decode()
    changes = []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('CHECKPOINT = "93cc8d1a7b162bdda91e239d840a3eee8a70c51c"', "CHECKPOINT = " + repr(source_commit))
    replace('PROFILE = "PRIVACY FIX 1 / H1 EXPERIMENTAL / CLEAN COMPILE ONLY / NOT DEPLOYMENT APPROVED"', "PROFILE = " + repr(PROFILE))
    replace("tests/privacy_fix1/prepare_sources.py", "tests/dashboard_cleanup/prepare_sources.py", 4)
    replace("tests/privacy_fix1/source-manifest.json", "tests/dashboard_cleanup/source-manifest.json")
    replace("text=text.replace('lock_feedback','privacy_fix1')", "text=text.replace('lock_feedback','dashboard_cleanup')", 2)
    replace('source_checkpoint=CHECKPOINT', 'source_commit=CHECKPOINT', 3)
    replace('parent_overlay_calls="one via privacy.overlay -> H1.overlay"', 'parent_overlay_calls="one dashboard overlay -> one privacy overlay -> one H1 composition"')
    replace('changed_sources=["cli.cpp", "webserver.cpp", "webfiles.h"],\n                     unchanged_sources=198, metadata_only_differences=[],',
            'changed_sources=["webfiles.h", "caps_trial.h"],\n                     unchanged_sources=199, comparison_base="privacy-fix1",\n                     cumulative_h1_changed_sources=["cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"],\n                     cumulative_h1_unchanged_sources=197, metadata_only_differences=["caps_trial.h: caps_trial::BuildId"],')
    replace('dashboard_build_id="ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1"', 'dashboard_build_id=' + repr(BUILD_ID))
    replace('dashboard_id_distinguishes_privacy=False', 'dashboard_id_distinguishes_candidate=True')
    for old, new, count in [
        ('privacy-composition.json', 'dashboard-composition.json', 2),
        ('privacy-target-verification.json', 'dashboard-target-verification.json', 1),
        ('privacy-target-failure.json', 'dashboard-target-failure.json', 1),
        ('privacy-target-verification', 'dashboard-target-verification', 1),
        ('report["privacy_target_adapter"]', 'report["dashboard_target_adapter"]', 1),
        ('privacy_target_binding=binding', 'dashboard_target_binding=binding', 1),
    ]:
        replace(old, new, count)
    return text, changes


def main():
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    # Record the committed implementation actually used by this target entry.
    for name in ["prepare_sources.py", "build_candidate.py", "startup_decode.py", "verify_target.py",
                 "application.patch", "source-manifest.json"]:
        relative = "tests/dashboard_cleanup/" + name
        assert subprocess.check_output(["git", "show", source_commit + ":" + relative], cwd=ROOT) == (ROOT / relative).read_bytes(), relative
    text, changes = adapted_source(source_commit)
    namespace = dict(__name__="dashboard_privacy_build_adapter", __file__=str(__file__))
    exec(compile(text, str(PARENT), "exec"), namespace)
    code = namespace["main"]()
    if code:
        return code
    output = pathlib.Path(sys.argv[sys.argv.index("--output-dir") + 1])
    path = output / "report.json"
    report = json.loads(path.read_text())
    assert report["dashboard_target_adapter"]["overlay_calls"] == 1
    assert report["dashboard_target_adapter"]["dashboard_target_binding"]["verifier_sha256"] == hashlib.sha256((ROOT / "tests/dashboard_cleanup/verify_target.py").read_bytes()).hexdigest()
    report["dashboard_build_adapter"] = dict(parent="tests/privacy_fix1/build_candidate.py",
        parent_sha256=PARENT_SHA, adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        source_commit=source_commit, build_id=BUILD_ID, comparison_base="privacy-fix1",
        exact_adaptations=changes, inherited_safety_predicates_removed=0, clean_compile=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
