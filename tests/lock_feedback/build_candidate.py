#!/usr/bin/env python3
"""Hash-pinned additive offline build adapter. No port/upload/device interface."""
import hashlib
import json
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / "tests/caps_stop/build_candidate.py"
PARENT_SHA = "b82c46dad3ca8c8c5ea910607b7cc1ab6b22fd0d313a1c9c3fcccb8b57afc773"


def main():
    source = PARENT.read_bytes()
    assert hashlib.sha256(source).hexdigest() == PARENT_SHA
    text = source.decode()
    changes = [
        ("parents[1]/'caps_stop'", "parents[1]/'lock_feedback'", 1),
        ("str(ROOT/'tests/caps_stop')", "str(ROOT/'tests/lock_feedback')", 1),
        ("flags='-DEVILDUCK_VERIFIED_LED_DIAGNOSTICS=1", "flags='-DEVILDUCK_ROUTE_B_LOCK_FEEDBACK=1 -DEVILDUCK_ROUTE_B_KEYBOARD_CONTROL=1 -DEVILDUCK_VERIFIED_LED_DIAGNOSTICS=1", 1),
        ("sha(ROOT/'tests/caps_stop/startup_decode.py')", "sha(ROOT/'tests/lock_feedback/startup_decode.py')", 1),
        ("'BOUNDED CAPS STOP TRACE REVIEW ONLY'", "'ROUTE B LOCK FEEDBACK REVIEW ONLY; PHYSICAL VALIDATION PENDING'", 1),
    ]
    for old, new, count in changes:
        assert text.count(old) == count, old
        text = text.replace(old, new)
    # The setup decoder, dependency/archive guards, controlled startup, source
    # equality and ELF-to-BIN regeneration checks remain those of the parent.
    namespace = {"__name__": "keyboard_control_build_adapter", "__file__": str(__file__)}
    exec(compile(text, str(__file__), "exec"), namespace)
    code = namespace["main"]()
    if code:
        return code
    index = sys.argv.index("--output-dir")
    out = pathlib.Path(sys.argv[index+1]) / "report.json"
    report = json.loads(out.read_text())
    report["keyboard_build_adapter"] = dict(
        historical_source="tests/caps_stop/build_candidate.py",
        historical_sha256=PARENT_SHA,
        adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        adaptations=[dict(before=old, after=new, exact_occurrences=count) for old, new, count in changes],
        parent_startup_adapter_sha256="48406180324f41371d0803547edc4d0844caf1a7c424f965372de045cbce3aba",
        inherited_safety_predicates_removed=0,
    )
    out.write_text(json.dumps(report, indent=2)+"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
