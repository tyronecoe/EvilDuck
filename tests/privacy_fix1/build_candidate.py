#!/usr/bin/env python3
"""Pinned privacy-specific clean target compile. No upload/package interface."""
import hashlib
import json
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / "tests/h1_right_modifiers/build_candidate.py"
PARENT_SHA = "f3a62aacd0fe125b69b0b67323c55853de77f37bdac4b446d811d078d6c6ff0d"
CHECKPOINT = "93cc8d1a7b162bdda91e239d840a3eee8a70c51c"
PROFILE = "PRIVACY FIX 1 / H1 EXPERIMENTAL / CLEAN COMPILE ONLY / NOT DEPLOYMENT APPROVED"


def expected_inventory(sketch):
    from prepare_sources import delta  # Explicit privacy module, not historical H1.
    assert pathlib.Path(sys.modules[delta.__module__].__file__).resolve() == ROOT / "tests/privacy_fix1/prepare_sources.py"
    pin = json.loads((ROOT / "tests/privacy_fix1/source-manifest.json").read_text())
    rows = pin["after"] + pin["unchanged"]
    expected = {row["file"]: row["sha256"] for row in rows}
    actual = {str(p.relative_to(sketch)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sketch.rglob("*") if p.is_file()}
    assert len(expected) == len(rows) == 201 and actual == expected, "final privacy composition differs"
    return [dict(file="EvilDuckS3/" + name, size=(sketch / name).stat().st_size, sha256=actual[name])
            for name in sorted(actual)]


def main():
    assert "--verify-existing" not in sys.argv, "Privacy target integration requires a fresh clean compile"
    assert "--selector-off" not in sys.argv and "--diagnostics-off" not in sys.argv, "Use the reviewed controlled H1 profile"
    data = PARENT.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PARENT_SHA, "historical H1 builder changed"
    text = data.decode()
    # The pinned H1 adapter already sets every reviewed experimental selector.
    # Change only its explicit preparer/decoder selection; do not call H1 twice.
    old = "text=text.replace('lock_feedback','h1_right_modifiers')"
    assert text.count(old) == 1
    text = text.replace(old, "text=text.replace('lock_feedback','privacy_fix1')")
    import prepare_sources as privacy
    assert pathlib.Path(privacy.__file__).resolve() == ROOT / "tests/privacy_fix1/prepare_sources.py"
    original_overlay = privacy.overlay
    calls = []
    output = None if "--output-dir" not in sys.argv else pathlib.Path(sys.argv[sys.argv.index("--output-dir") + 1])

    def selected_overlay(sketch):
        assert not calls, "Privacy overlay must be applied exactly once"
        calls.append(str(sketch))
        original_overlay(sketch)
        rows = expected_inventory(sketch)
        proof = dict(status="COMPOSED_NOT_YET_COMPILED", source_checkpoint=CHECKPOINT,
                     selected_preparer="tests/privacy_fix1/prepare_sources.py",
                     preparer_sha256=hashlib.sha256(pathlib.Path(privacy.__file__).read_bytes()).hexdigest(),
                     overlay_calls=len(calls), parent_overlay_calls="one via privacy.overlay -> H1.overlay",
                     source_inventory=rows, changed_sources=["cli.cpp", "webserver.cpp", "webfiles.h"],
                     unchanged_sources=198, metadata_only_differences=[],
                     dashboard_build_id="ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1",
                     dashboard_id_distinguishes_privacy=False, profile=PROFILE)
        assert output is not None
        (output / "privacy-composition.json").write_text(json.dumps(proof, indent=2) + "\n")

    privacy.overlay = selected_overlay
    namespace = {"__name__": "privacy_target_parent_adapter", "__file__": str(PARENT)}
    try:
        exec(compile(text, str(PARENT), "exec"), namespace)
        code = namespace["main"]()
    finally:
        privacy.overlay = original_overlay
    if code:
        return code
    assert len(calls) == 1, "Target compile did not execute the selected privacy overlay"
    from verify_target import verify
    try:
        binding = verify(output)
    except Exception as error:
        # The inherited report can legitimately say compiler/provenance PASS;
        # keep a separate fail-closed result for this additional integration gate.
        failure = dict(status="FAIL", stage="privacy-target-verification",
                       compiler_and_inherited_provenance_status="PASS",
                       error_type=type(error).__name__, reason=str(error),
                       source_checkpoint=CHECKPOINT, profile=PROFILE)
        (output / "privacy-target-failure.json").write_text(json.dumps(failure, indent=2) + "\n")
        raise
    (output / "privacy-target-verification.json").write_text(json.dumps(binding, indent=2) + "\n")
    report_path = output / "report.json"
    report = json.loads(report_path.read_text())
    report["profile"] = PROFILE
    report["privacy_target_adapter"] = dict(source_checkpoint=CHECKPOINT, parent=str(PARENT.relative_to(ROOT)),
        parent_sha256=PARENT_SHA, adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        preparer="tests/privacy_fix1/prepare_sources.py", overlay_calls=len(calls),
        exact_selection_replacement=dict(before=old, after="text=text.replace('lock_feedback','privacy_fix1')"),
        inherited_safety_predicates_removed=0, clean_compile=True,
        full_historical_h1_verify_link_rerun=False, privacy_target_binding=binding)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    proof_path = output / "privacy-composition.json"
    proof = json.loads(proof_path.read_text())
    proof["status"] = "PASS_COMPILED_INPUTS_BOUND"
    proof["application_sha256"] = report["report"]["application_sha256"]
    proof_path.write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(dict(status="PASS", profile=PROFILE, composition_entries=201,
                         overlay_calls=1, report=report["report"], target_binding=binding["status"]), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
