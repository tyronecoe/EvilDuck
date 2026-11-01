#!/usr/bin/env python3
"""Additional privacy package gates on disposable PUBLIC copies only.

No network, device, esptool dispatcher, compiler or owner files are accessed.
Historical package/installer suites remain unchanged and run separately.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
APP_SHA = "9e4d3b615d78e87521882a35c4b43ce66403168a15b6b39bcebc81bb32a6b96e"
ROLLBACK_SHA = "cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=pathlib.Path, required=True)
    parser.add_argument("--results", type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.results.exists()
    original = args.directory.resolve()
    spec = importlib.util.spec_from_file_location("privacy_package_under_test", original / "preflight.py")
    release = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(release)
    before = {p.name: digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    results = []
    with tempfile.TemporaryDirectory(prefix="public-privacy-package-tests-") as temporary:
        directory = pathlib.Path(temporary) / "public"
        shutil.copytree(original, directory)
        saved = {p.name: p.read_bytes() for p in directory.iterdir()}

        def restore():
            for path in directory.iterdir():
                if path.name not in saved:
                    if path.is_dir() and not path.is_symlink():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            for name, data in saved.items():
                path = directory / name
                if not path.exists() or path.read_bytes() != data:
                    path.write_bytes(data)

        def case(name, operation):
            try:
                operation()
                results.append(dict(name=name, status="PASS"))
                print("PASS", name)
            except Exception as error:
                results.append(dict(name=name, status="FAIL", diagnostic=type(error).__name__ + ": " + str(error)))
                print("FAIL", name, type(error).__name__)
            finally:
                restore()

        def rejected(expected):
            try:
                release.validate(directory)
            except (ValueError, KeyError, OSError) as error:
                assert expected in str(error), (expected, str(error))
                return
            raise AssertionError("Unsafe privacy metadata accepted")

        def manifest_change(change, expected):
            path = directory / "manifest.json"
            record = json.loads(path.read_text())
            change(record)
            path.write_text(json.dumps(record))
            rejected(expected)

        def support_change(name, data):
            path = directory / name
            path.write_bytes(data)
            manifest = json.loads((directory / "manifest.json").read_text())
            manifest["support_files"][name] = dict(bytes=len(data), sha256=digest(data))
            (directory / "manifest.json").write_text(json.dumps(manifest))

        def receipt_change(change, expected):
            record = json.loads((directory / "build-receipt.json").read_text())
            change(record)
            support_change("build-receipt.json", json.dumps(record).encode())
            rejected(expected)

        def positive():
            result = release.validate(directory)
            assert result["package_integrity"] == "PASS"
            assert result["selected_write_ranges"] == [] and result["plan_ready"] is False
            assert result["hardware_access"] is False and result["installation_authorized"] is False
            app = (directory / "application.bin").read_bytes()
            rollback = (directory / "rollback-application.bin").read_bytes()
            assert len(app) == 1415968 and digest(app) == APP_SHA
            assert len(rollback) == 1413200 and digest(rollback) == ROLLBACK_SHA
            manifest = json.loads((directory / "manifest.json").read_text())
            assert manifest["package_id"] == "evilduck-privacy-fix1-h1-macos-review-v1"
            assert manifest["runtime_build_id_distinguishes_privacy"] is False
            assert manifest["rollback_is_privacy_patched"] is False

        case("exact_privacy_application_and_older_rollback_no_hardware_or_plan", positive)

        def owner_docs():
            readme = (directory / "README.md").read_text()
            assert "python3 preflight.py --directory ." in readme
            for name in ["README.md", "OWNER-CHECK.md"]:
                for block in re.findall(r"```[^\n]*\n(.*?)```", (directory / name).read_text(), re.S):
                    assert "?pw=" not in block, "Credential-bearing query instructions"
                    assert not re.search(r"curl[^\n]*(?:-H|--header)[^\n]*X-Duck-Password", block, re.I), "Credential-bearing curl argument"

        case("readme_offline_command_and_no_credential_bearing_owner_commands", owner_docs)

        manifest_cases = [
            ("wrong_source_checkpoint", "source_checkpoint_commit", "0" * 40, "WRONG_PRIVACY_SOURCE_REVISIONS"),
            ("wrong_target_integration_commit", "target_integration_commit", "0" * 40, "WRONG_PRIVACY_SOURCE_REVISIONS"),
            ("wrong_privacy_profile", "privacy_profile", "UNRELATED", "WRONG_PRIVACY_SCOPE_OR_ROLLBACK_CLAIM"),
            ("runtime_id_cannot_claim_privacy_identity", "runtime_build_id_distinguishes_privacy", True, "WRONG_PRIVACY_SCOPE_OR_ROLLBACK_CLAIM"),
            ("older_rollback_cannot_claim_privacy_patch", "rollback_is_privacy_patched", True, "WRONG_PRIVACY_SCOPE_OR_ROLLBACK_CLAIM"),
            ("wrong_privacy_pin_hash", "privacy_composition_pin_sha256", "0" * 64, "WRONG_PRIVACY_COMPOSITION_PIN"),
        ]
        for name, field, value, expected in manifest_cases:
            case(name, lambda field=field, value=value, expected=expected:
                 manifest_change(lambda record: record.update({field: value}), expected))

        def missing_pin():
            (directory / "privacy-source-manifest.json").unlink()
            rejected("UNEXPECTED_PACKAGE_CONTENT")

        case("missing_privacy_pin_rejected", missing_pin)

        def changed_pin():
            path = directory / "privacy-source-manifest.json"
            pin = json.loads(path.read_text())
            pin["patch_sha256"] = "0" * 64
            data = json.dumps(pin).encode()
            support_change(path.name, data)
            manifest_change(lambda record: record.update(privacy_composition_pin_sha256=digest(data)), "WRONG_PRIVACY_COMPOSITION_PIN")

        case("rehashed_privacy_pin_cannot_bypass_bound_release", changed_pin)

        def missing_release(record):
            record.pop("privacy_release_verification")

        case("privacy_release_evidence_required", lambda: receipt_change(missing_release, "privacy_release_verification"))
        for name, field, value, expected in [
            ("privacy_release_pass_required", "status", "FAIL", "PRIVACY_RELEASE_NOT_VERIFIED"),
            ("full_frozen_h1_chain_required", "full_frozen_h1_chain_executed", False, "WRONG_PRIVACY_RELEASE_VERIFIER"),
            ("privacy_release_adapter_required", "adapter_sha256", "0" * 64, "WRONG_PRIVACY_RELEASE_VERIFIER"),
            ("release_source_manifest_binding_required", "source_manifest_sha256", "0" * 64, "WRONG_LINKED_PRIVACY_PIN"),
            ("release_source_checkpoint_required", "source_checkpoint", "0" * 40, "WRONG_PRIVACY_RELEASE_REVISIONS"),
            ("release_integration_revision_required", "target_integration_commit", "0" * 40, "WRONG_PRIVACY_RELEASE_REVISIONS"),
            ("removed_release_assertions_rejected", "assertions_removed", 1, "UNREVIEWED_PRIVACY_RELEASE_ADAPTATION"),
            ("unrelated_release_hash_changes_rejected", "unrelated_expected_hashes_changed", 1, "UNREVIEWED_PRIVACY_RELEASE_ADAPTATION"),
        ]:
            case(name, lambda field=field, value=value, expected=expected:
                 receipt_change(lambda record: record["privacy_release_verification"].update({field: value}), expected))

        case("exact_three_release_source_overrides_required", lambda: receipt_change(
            lambda record: record["privacy_release_verification"]["exact_final_source_overrides"].update({"cli.cpp": "0" * 64}),
            "UNREVIEWED_PRIVACY_RELEASE_ADAPTATION"))
        for name, field, value in [
            ("privacy_build_adapter_required", "adapter_sha256", "0" * 64),
            ("privacy_overlay_must_be_once", "overlay_calls", 2),
            ("privacy_clean_compile_required", "clean_compile", False),
            ("privacy_build_guards_required", "inherited_safety_predicates_removed", 1),
        ]:
            case(name, lambda field=field, value=value:
                 receipt_change(lambda record: record["privacy_target_adapter"].update({field: value}), "WRONG_PRIVACY_BUILD_ADAPTER"))

        binding = lambda record: record["privacy_release_verification"]["privacy_target_binding"]
        case("target_binding_required", lambda: receipt_change(
            lambda record: record["privacy_release_verification"].pop("privacy_target_binding"), "privacy_target_binding"))
        for name, field, value, expected in [
            ("target_binding_pass_required", "status", "FAIL", "PRIVACY_TARGET_BINDING_REQUIRED"),
            ("target_201_sources_required", "source_files", 200, "PRIVACY_TARGET_BINDING_REQUIRED"),
            ("target_application_binding_required", "application_sha256", "0" * 64, "WRONG_PRIVACY_TARGET_ARTIFACTS"),
            ("target_elf_binding_required", "elf_sha256", "0" * 64, "WRONG_PRIVACY_TARGET_ARTIFACTS"),
            ("target_pin_binding_required", "source_manifest_sha256", "0" * 64, "WRONG_PRIVACY_TARGET_SOURCE_BINDING"),
            ("target_patch_binding_required", "privacy_patch_sha256", "0" * 64, "WRONG_PRIVACY_TARGET_SOURCE_BINDING"),
        ]:
            case(name, lambda field=field, value=value, expected=expected:
                 receipt_change(lambda record: binding(record).update({field: value}), expected))

        cli = lambda record: next(row for row in binding(record)["compile_inputs"] if row["source"] == "cli.cpp")
        server = lambda record: next(row for row in binding(record)["compile_inputs"] if row["source"] == "webserver.cpp")
        case("compiled_cli_source_hash_required", lambda: receipt_change(
            lambda record: cli(record).update(candidate_sha256="0" * 64), "WRONG_PRIVACY_COMPILED_CPP"))
        case("compiled_object_link_evidence_required", lambda: receipt_change(
            lambda record: cli(record).update(linked_map_load=False), "WRONG_PRIVACY_COMPILED_CPP"))
        case("compiled_header_dependency_required", lambda: receipt_change(
            lambda record: server(record)["webfiles_header"].update(dependency_observed=False), "PRIVACY_COMPILED_HEADER_REQUIRED"))
        case("compiled_header_source_hash_required", lambda: receipt_change(
            lambda record: server(record)["webfiles_header"].update(candidate_sha256="0" * 64), "PRIVACY_COMPILED_HEADER_REQUIRED"))
        case("exact_201_receipt_source_hashes_required", lambda: receipt_change(
            lambda record: record["source_inventory"][0].update(sha256="0" * 64), "WRONG_PRIVACY_COMPOSED_SOURCES"))

    after = {p.name: digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    assert before == after, "Original public package changed during tests"
    output = dict(counts={status: sum(row["status"] == status for row in results) for status in ["PASS", "FAIL"]},
                  results=results, scope="Actual bound privacy preflight on disposable public package copies; metadata rehashed to test semantic gates",
                  original_package_unchanged=True, hardware=False, network=False, firmware_built=False,
                  native_macos_tested=False, installation_authorized=False)
    args.results.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["counts"]))
    return 1 if output["counts"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
