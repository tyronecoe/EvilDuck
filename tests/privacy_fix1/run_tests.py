#!/usr/bin/env python3
"""Actual composed HTTP/CLI/settings and embedded JS; memory-only lower APIs.

No Arduino/Xtensa compilation, firmware link, package creation or device access.
The SHA-pinned historical native runner is adapted in memory, never edited.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
from prepare_sources import ROOT, delta

PARENT = ROOT / "tests/h1_right_modifiers/run_tests.py"
PARENT_SHA = "864fbb244e7c2833de5644ee3333bf47ba62649a8135902bb14542fb35a6ba90"


def main():
    # The parent validates --core, --build-dir and --results and refuses reuse.
    text = PARENT.read_text()
    assert hashlib.sha256(text.encode()).hexdigest() == PARENT_SHA
    test = ROOT / "tests/privacy_fix1/test_main.cpp"
    import re
    privacy_cases = sorted(set(re.findall(r'"(PF\d\d)"', test.read_text())))
    assert privacy_cases, "no privacy cases"
    replacements = {
        '"tests/h1_right_modifiers/test_main.cpp"': '"tests/privacy_fix1/test_main.cpp"',
        "cases=['AD%02d'%i for i in range(1,37)]": "cases=" + repr(privacy_cases + ["AD%02d" % i for i in range(1, 37)]),
        "right.delta(source);cmd.insert(1,'-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1')":
            "right.delta(source);privacy_before_compile(source,cmd);cmd.insert(1,'-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1')",
    }
    for before, after in replacements.items():
        assert text.count(before) == 1, before
        text = text.replace(before, after)

    captured = {}

    def before_compile(source, command):
        delta(source, native=True)
        driver = (ROOT / "tests/h1_right_modifiers/test_main.cpp").read_text()
        assert driver.count("int main(int argc,char**argv)") == 1
        (source / "right_modifiers_parent_cases.inc").write_text(
            driver.replace("int main(int argc,char**argv)", "int right_modifiers_main(int argc,char**argv)"))
        fixture = str(ROOT / "tests/stage28v/nvs_fixture.cpp")
        assert command.count(fixture) == 1
        command[command.index(fixture)] = str(ROOT / "tests/privacy_fix1/nvs_fixture.cpp")
        command.insert(1, "-I" + str(ROOT / "tests/privacy_fix1"))
        captured["source"] = source
        # No keyboard/core/LED implementation is patched by Privacy Fix 1.
        pin = json.loads((ROOT / "tests/privacy_fix1/source-manifest.json").read_text())
        protected = {r["file"]: r["sha256"] for r in pin["unchanged"]}
        for name in ["core.cpp", "core.h", "adapter.cpp", "adapter.h", "hid_backend.cpp",
                     "hid_backend.h", "led_receiver.cpp", "led_receiver.h", "settings.cpp",
                     "settings.h", "coordinator.cpp", "shortcut_keys.h", "hid_trace.cpp"]:
            # The historical host runner leaves some unchanged headers in the
            # firmware include directory instead of copying them to scratch.
            physical = source / name
            if not physical.exists():
                physical = ROOT / "EvilDuckS3" / name
            assert hashlib.sha256(physical.read_bytes()).hexdigest() == protected[name], name

    status = 0
    try:
        exec(compile(text, str(PARENT), "exec"), dict(__name__="__main__", __file__=str(PARENT),
                                                   privacy_before_compile=before_compile))
    except SystemExit as stopped:
        status = stopped.code if isinstance(stopped.code, int) else 1
    path = pathlib.Path(sys.argv[sys.argv.index("--results") + 1])
    result = json.loads(path.read_text())
    rows = result["results"]
    summarize = lambda selected: dict(PASS=sum(r["status"] == "PASS" for r in selected),
                                     FAIL=sum(r["status"] == "FAIL" for r in selected),
                                     assertions=sum(r["assertions"] for r in selected))
    result["privacy_fix1"] = summarize([r for r in rows if r["id"].startswith("PF")])
    result["right_modifiers"] = summarize([r for r in rows if r["id"].startswith("AD")])
    result["all_existing_composed_regressions"] = summarize([r for r in rows if not r["id"].startswith("PF")])
    assert sorted(r["id"] for r in rows if r["id"].startswith("PF")) == privacy_cases
    ui_command = ["node", str(ROOT / "tests/privacy_fix1/test_ui.cjs"), str(captured["source"] / "webfiles.h")]
    ui = subprocess.run(ui_command, capture_output=True, text=True, timeout=30)
    result["privacy_ui"] = dict(command=ui_command, exit=ui.returncode, stdout=ui.stdout, stderr=ui.stderr)
    if ui.returncode:
        status = 1
    else:
        result["privacy_ui"]["counts"] = json.loads(ui.stdout)
    result["privacy_scope"] = dict(baseline="a04e54309c9c73bae17ef23c48283828dfebc0ad",
                                   firmware_built=False, hardware=False, packaging=False,
                                   new_credential_values="synthetic test inputs only",
                                   parent_runner_sha256=PARENT_SHA,
                                   nvs_boundary="Recording typed NVS mock, not ESP-IDF recovery execution",
                                   historical_sources_edited=False)
    result["tool_versions"] = {name: subprocess.check_output(command, text=True).splitlines()[0]
                               for name, command in [("g++", ["g++", "--version"]), ("node", ["node", "--version"]),
                                                     ("python", [sys.executable, "--version"])]}
    assert hashlib.sha256(PARENT.read_bytes()).hexdigest() == PARENT_SHA
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["privacy_fix1", "all_existing_composed_regressions", "privacy_ui", "sanitizers", "privacy_scope"]}, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
