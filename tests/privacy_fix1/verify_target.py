#!/usr/bin/env python3
"""Bind the source-only privacy delta to a real clean target compile.

This supplements the unchanged builder's protected-core/startup/ELF-to-BIN
verification. It does not run or claim the historical full H1 verify_link chain,
which intentionally expects earlier final CLI/web source hashes. No device API.
"""
import argparse
import hashlib
import json
import pathlib
import shlex
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def source_matches(original, compiled, original_path):
    """Arduino may prepend this exact source-location directive to its copy."""
    prefix = ("#line 1 " + json.dumps(str(original_path)) + "\n").encode()
    return compiled == original or compiled == prefix + original


def make_dependencies(text):
    """Read one GCC -MMD rule, including continuations and escaped spaces/#/$.

    Fail closed on additional rules or an absent/unescaped target separator.
    The pinned Linux target compiler uses a single POSIX-path rule (no -MP).
    """
    logical = text.replace("\\\r\n", " ").replace("\\\n", " ")
    lines = [line for line in logical.splitlines() if line.strip()]
    require(len(lines) == 1, "Unsupported dependency-file rule count")
    logical = lines[0]
    escaped = False
    separator = None
    for index, char in enumerate(logical):
        if char == ":" and not escaped:
            separator = index
            break
        if char == "\\":
            escaped = not escaped
        else:
            escaped = False
    require(separator is not None, "Dependency target separator missing")
    words = lambda value: [word.replace("$$", "$") for word in shlex.split(value, comments=False)]
    targets, dependencies = words(logical[:separator]), words(logical[separator+1:])
    require(len(targets) == 1 and bool(dependencies), "Unsupported dependency target/dependency list")
    return targets[0], dependencies


def _profile_flags(text):
    return [word for word in shlex.split(text) if not word.startswith("-I")]


def verify(build_root):
    build_root = pathlib.Path(build_root).resolve()
    build, sketch = build_root / "build", build_root / "candidate/EvilDuckS3"
    report_path = build_root / "report.json"
    report = json.loads(report_path.read_text())
    baseline = json.loads((ROOT / "docs/h1-right-modifiers-build.json").read_text())
    manifest_path = ROOT / "tests/privacy_fix1/source-manifest.json"
    pin = json.loads(manifest_path.read_text())
    require(report["status"] == "PASS", "Target build did not pass")
    require(report.get("verification_resumed") is False, "Expected fresh clean compile, not resumed verification")
    require("--clean" in report["command"] and "--verbose" in report["command"], "Missing actual clean verbose compile")
    require(report["command"][-1] == str(sketch), "Compile command selected another candidate")
    require(pin["baseline_inventory_sha256"] == sha(ROOT / "docs/h1-right-modifiers-build.json"), "Baseline inventory identity changed")
    require(pin["parent_prepare_sha256"] == sha(ROOT / "tests/h1_right_modifiers/prepare_sources.py"), "Historical source preparer changed")
    require(pin["patch_sha256"] == sha(ROOT / "tests/privacy_fix1/application.patch"), "Privacy patch identity changed")

    expected = {row["file"]: row["sha256"] for row in pin["unchanged"] + pin["after"]}
    require(len(expected) == 201 and len(pin["after"]) == 3 and len(pin["unchanged"]) == 198,
            "Privacy manifest is not the reviewed 3/198 source delta")
    require({row["file"] for row in pin["after"]} == {"cli.cpp", "webserver.cpp", "webfiles.h"},
            "Unexpected privacy source changes")
    actual_files = {str(path.relative_to(sketch)) for path in sketch.rglob("*") if path.is_file()}
    require(actual_files == set(expected), "Candidate source file set differs from reviewed inventory")
    for name, digest in expected.items():
        require(sha(sketch / name) == digest, "Candidate source identity mismatch: " + name)
    inventory = {row["file"]: row for row in report["source_inventory"]}
    require(set(inventory) == {"EvilDuckS3/" + name for name in expected}, "Build report source file set differs")
    for name, digest in expected.items():
        row = inventory["EvilDuckS3/" + name]
        require(row["sha256"] == digest and row["size"] == (sketch / name).stat().st_size,
                "Build report source identity differs: " + name)

    provenance = report["provenance"]
    for name in ["single_strong_callback", "feature_workaround_absent", "hid_cdc_msc_linked",
                 "controlled_normal_start", "elf_to_image_verified", "checked_settings_persistence",
                 "settings_failure_quiescent", "nvs_preservation_policy"]:
        require(provenance.get(name) is True, "Inherited builder guard missing: " + name)
    for name in ["core_pin", "framework_pins", "supplementary_library_pin", "compiler_sha256"]:
        require(report[name] == baseline[name], "Pinned dependency/tool identity differs: " + name)
    require(provenance["compiler_sha256"] == baseline["compiler_sha256"], "Provenance compiler differs")
    require(provenance["hardware_access"] is False and report["physical"] is False, "Unexpected hardware claim")
    for name in ["core_version", "fqbn", "application_address", "flash_bytes", "ota_slot_bytes"]:
        require(report["report"][name] == baseline["report"][name], "Target geometry/profile differs: " + name)
    require(_profile_flags(report["report"]["verified_cpp_extra_flags"]) ==
            _profile_flags(baseline["report"]["verified_cpp_extra_flags"]), "Controlled H1 profile flags changed")

    entries = json.loads((build / "compile_commands.json").read_text())
    required_flags = [word for word in _profile_flags(baseline["report"]["verified_cpp_extra_flags"])
                      if word.startswith("-D")]
    for entry in entries:
        if pathlib.Path(entry["file"]).is_relative_to(build / "sketch"):
            require(all(flag in entry["arguments"] for flag in required_flags), "Application profile selector missing")
            require("-fno-access-control" not in entry["arguments"], "Native-only access override in target")
    link_inputs = {row["file"]: row for row in report["linked_input_hashes"]}
    map_path = build / "EvilDuckS3.ino.map"
    loaded = {line.removeprefix("LOAD ").strip() for line in map_path.read_text().splitlines() if line.startswith("LOAD ")}
    log_path = build / "s3-build.log"
    commands = []
    for line in log_path.read_text().splitlines():
        if " -c " not in line:
            continue
        try:
            args = shlex.split(line)
        except ValueError:
            continue
        if "-c" in args and "-o" in args:
            commands.append(args)
    evidence = []
    for name in ["cli.cpp", "webserver.cpp"]:
        matches = [entry for entry in entries if pathlib.Path(entry["file"]).name == name]
        require(len(matches) == 1, "Expected one target compile for " + name)
        entry = matches[0]
        compiled = pathlib.Path(entry["file"])
        require(compiled == build / "sketch" / name, "Compiled source selected another tree: " + name)
        require(source_matches((sketch / name).read_bytes(), compiled.read_bytes(), sketch / name),
                "Compiled source bytes differ from privacy source: " + name)
        args = entry["arguments"]
        require(sha(args[0]) == baseline["compiler_sha256"], "Actual compiler identity differs")
        obj = pathlib.Path(args[args.index("-o") + 1])
        require(obj == build / "sketch" / (name + ".o") and str(obj) in loaded,
                "Privacy object absent from actual link map: " + name)
        require(str(obj) in link_inputs and sha(obj) == link_inputs[str(obj)]["sha256"] and
                obj.stat().st_size == link_inputs[str(obj)]["size"], "Linked object identity mismatch: " + name)
        observed = [command for command in commands if str(compiled) in command and
                    command[command.index("-o") + 1] == str(obj)]
        require(len(observed) == 1, "Actual verbose target compile missing/ambiguous: " + name)
        require(sha(observed[0][0]) == baseline["compiler_sha256"] and
                all(flag in observed[0] for flag in required_flags), "Verbose compile profile/compiler mismatch")
        dependency = obj.with_suffix(".d")
        target, dependencies = make_dependencies(dependency.read_text())
        require(pathlib.Path(target) == obj and str(compiled) in dependencies, "Source dependency rule mismatch: " + name)
        row = dict(source=name, candidate_sha256=sha(sketch / name), compiled_source=str(compiled),
                   compiled_sha256=sha(compiled), object=str(obj), object_sha256=sha(obj),
                   compiler=str(args[0]), dependency_file=str(dependency), dependency_sha256=sha(dependency),
                   dependency_count=len(dependencies), verbose_compile_observed=True, linked_map_load=True)
        if name == "webserver.cpp":
            header = build / "sketch/webfiles.h"
            require(str(header) in dependencies, "Patched webfiles.h absent from actual webserver dependencies")
            require(source_matches((sketch / "webfiles.h").read_bytes(), header.read_bytes(), sketch / "webfiles.h"),
                    "Compiled webfiles.h differs from reviewed privacy header")
            row["webfiles_header"] = dict(file=str(header), sha256=sha(header),
                                          candidate_sha256=expected["webfiles.h"], dependency_observed=True)
        evidence.append(row)

    elf, binary = build / "EvilDuckS3.ino.elf", build / "EvilDuckS3.ino.bin"
    require(sha(elf) == provenance["elf_sha256"], "Final ELF differs from inherited guarded build")
    require(sha(binary) == provenance["application_sha256"] == report["report"]["application_sha256"],
            "Final application differs from guarded report")
    require(binary.stat().st_size == report["report"]["application_bytes"], "Application size differs")
    for artifact in report["artifacts"]:
        require(sha(build / artifact["file"]) == artifact["sha256"], "Recorded target artifact changed")
    data = elf.read_bytes()
    markers = [b"password_configured", b"web_password_configured", b"# set [value omitted]",
               b"updated (value omitted)", b"Replace AP password (leave blank to keep existing)"]
    require(all(marker in data for marker in markers), "Privacy CLI/UI/settings markers missing from linked ELF")
    require(b"ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1" in data, "Expected retained H1 build identity missing")
    sdk = lambda r: {row["file"].split("/esp32s3/", 1)[1]: row["sha256"] for row in r["linked_input_hashes"]
                     if "/esp32-arduino-libs/" in row["file"] and "/esp32s3/" in row["file"] and row["file"].endswith(".a")}
    # The final historical verifier inventories additional bus variants even
    # though the actual link selects qio_qspi. Preserve every historical pin,
    # while separately requiring exact report coverage of actual map LOADs.
    pinned_sdk, reported_sdk = sdk(baseline), sdk(report)
    require(bool(pinned_sdk) and bool(reported_sdk), "SDK archive evidence missing")
    sdk_root = (pathlib.Path(provenance["core"]).parents[2] /
                "tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3").resolve()
    require(sdk_root.is_dir(), "Pinned SDK archive directory missing")
    for name, digest in pinned_sdk.items():
        archive = sdk_root / name
        require(archive.is_file() and sha(archive) == digest, "Installed pinned SDK archive changed: " + name)
    selected_sdk = {str(path.relative_to(sdk_root)) for raw in loaded
                    if (path := pathlib.Path(raw).resolve()).is_relative_to(sdk_root) and path.suffix == ".a"}
    require(set(reported_sdk) == selected_sdk, "Actual map LOAD SDK coverage differs from build report")
    for name, digest in reported_sdk.items():
        require(name in pinned_sdk and digest == pinned_sdk[name], "Selected SDK archive identity changed: " + name)
    for row in report["linked_input_hashes"]:
        if "/esp32-arduino-libs/" in row["file"] and "/esp32s3/" in row["file"] and row["file"].endswith(".a"):
            name = row["file"].split("/esp32s3/", 1)[1]
            require(pathlib.Path(row["file"]).resolve() == sdk_root / name,
                    "Reported SDK archive comes from a different installation: " + name)
    installed_sdk = {str(path.relative_to(sdk_root)) for path in sdk_root.rglob("*.a")}
    unpinned_unselected = sorted(installed_sdk - set(pinned_sdk))
    require(not selected_sdk.intersection(unpinned_unselected), "Unpinned SDK archive selected")
    return dict(status="PASS", source_files=201, privacy_files=3, unchanged_files=198,
                verifier_sha256=sha(__file__), source_manifest_sha256=sha(manifest_path),
                privacy_patch_sha256=pin["patch_sha256"], parent_preparer_sha256=pin["parent_prepare_sha256"],
                compile_inputs=evidence,
                compile_log_sha256=sha(log_path), compile_commands_sha256=sha(build / "compile_commands.json"),
                map_sha256=sha(map_path), elf_sha256=sha(elf), application_sha256=sha(binary),
                application_bytes=binary.stat().st_size, sdk_archives_checked=len(pinned_sdk),
                sdk_archives_selected=len(selected_sdk),
                sdk_pin_reconciliation=dict(pinned_installed_verified=len(pinned_sdk),
                    selected_map_and_report=len(selected_sdk), installed_archive_total=len(installed_sdk),
                    pinned_but_not_selected=sorted(set(pinned_sdk) - selected_sdk),
                    unpinned_installed_and_not_selected=unpinned_unselected,
                    unpinned_archives_trusted=False),
                inherited_guard="Unchanged builder protected-core/startup/checked-settings/ELF-to-BIN verifier",
                historical_full_h1_verify_link_executed=False,
                profile="PRIVACY FIX 1 COMPILE-ONLY REVIEW; H1 REMAINS EXPERIMENTAL",
                build_id_policy="Historical H1 dashboard build ID retained; privacy inventory, output directory and application SHA identify this local candidate",
                physical=False, installation_authorized=False, package_created=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Refusing to overwrite existing verification evidence")
    result = verify(args.build_root)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS privacy target source/dependency/object/ELF provenance; no physical verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
