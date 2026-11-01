#!/usr/bin/env python3
"""Privacy-only identity/doc adapter over the immutable H1 Mac packager.

Existing exact images only; no compiler, device or network interface.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / "tests/h1_right_modifiers/package.py"
PARENT_SHA = "b29c8995bf36668da89e092975c3f83cba7214e33349f12050dde7b82db773b2"
PACKAGE = "evilduck-privacy-fix1-h1-macos-review-v1"
SOURCE_CHECKPOINT = "93cc8d1a7b162bdda91e239d840a3eee8a70c51c"
INTEGRATION = "0380d1508b8f761e30a6a1fb63f67c2850cbc84a"
APP_SHA = "9e4d3b615d78e87521882a35c4b43ce66403168a15b6b39bcebc81bb32a6b96e"
ELF_SHA = "af7887ceccfe2694738c173c76b3c211b78cb0c7b667d8d7d942a1b0ef317f6e"
RECEIPT_SHA = "77b2787b0f72d92b0a8573da57419ccc362106ba0d7330e5c0da00efa95da908"
DOCS = {
    "acceptance": "owner-check", "install": "install", "rollback": "rollback",
    "report": "review", "compatibility": "compatibility", "reproduction": "reproduction",
}
REQUIRED_SOURCE = [
    "tests/privacy_fix1/package.py", "tests/privacy_fix1/package_preflight.py",
    "tests/privacy_fix1/verify_release.py", "tests/privacy_fix1/verify_target.py",
    "tests/privacy_fix1/application.patch", "tests/privacy_fix1/source-manifest.json",
    "tests/privacy_fix1/build_candidate.py", "tests/privacy_fix1/prepare_sources.py",
    *["docs/privacy-fix1-package-" + name + ".md" for name in DOCS.values()],
    "docs/privacy-fix1-package-readme.md",
]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def adapter():
    data = PARENT.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PARENT_SHA
    text = data.decode()
    changes = []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace("PACKAGE = 'evilduck-routeb-right-modifiers-h1-experimental-macos-v1'", "PACKAGE = " + repr(PACKAGE))
    replace("FIRMWARE_SOURCE = '6d15952e40f9016c4374b8b0403883ebb2290d9a'", "FIRMWARE_SOURCE = " + repr(INTEGRATION))
    replace("APP_SHA = '12134383e75505704d7efebf33cb7b7fdd7bd8f609038fbc575e911a0ad69ca3'", "APP_SHA = " + repr(APP_SHA))
    replace("APP_BYTES = 1414176", "APP_BYTES = 1415968")
    replace("ELF_SHA = 'b85061de399991f019e364401ef5e23a0c46e1972b34408add2ca886d0f64095'", "ELF_SHA = " + repr(ELF_SHA))
    replace("RECEIPT_SHA = 'f770fd0f49baf3b9d5a9104cd8516bee41ebce682360147dc32e5f52789ac8d1'", "RECEIPT_SHA = " + repr(RECEIPT_SHA))
    replace("tests/h1_right_modifiers/preflight.py", "tests/privacy_fix1/package_preflight.py", 2)
    for old, new in DOCS.items():
        replace("docs/h1-right-modifiers-" + old + ".md", "docs/privacy-fix1-package-" + new + ".md")
    replace("docs/h1-right-modifiers-test-results.json", "docs/privacy-fix1-results.json")
    replace("    for name, source in copies.items():", "    copies['privacy-source-manifest.json'] = ROOT/'tests/privacy_fix1/source-manifest.json'\n    for name, source in copies.items():")
    start = text.index("    (out/'README.md').write_text(")
    end = text.index("    template = ", start)
    old = text[start:end]
    replace(old, "    shutil.copyfile(ROOT/'docs/privacy-fix1-package-readme.md', out/'README.md')\n")
    anchor = "    (out/'preflight.py').write_text("
    replace(anchor, "    bound.update(privacy_pin_sha256=sha(ROOT/'tests/privacy_fix1/source-manifest.json'),\n"
                    "                 privacy_build_adapter_sha256=sha(ROOT/'tests/privacy_fix1/build_candidate.py'),\n"
                    "                 privacy_release_adapter_sha256=sha(ROOT/'tests/privacy_fix1/verify_release.py'))\n" + anchor)
    anchor = "    (out/'manifest.json').write_text("
    replace(anchor, "    manifest.update(source_checkpoint_commit=" + repr(SOURCE_CHECKPOINT) + ",\n"
                    "        target_integration_commit=" + repr(INTEGRATION) + ", privacy_profile='PRIVACY_FIX1_H1_OWNER_REVIEW',\n"
                    "        privacy_composition_pin_sha256=sha(out/'privacy-source-manifest.json'),\n"
                    "        runtime_build_id_distinguishes_privacy=False, rollback_is_privacy_patched=False,\n"
                    "        packaging_parent_sha256=" + repr(PARENT_SHA) + ")\n" + anchor)
    namespace = dict(__name__="privacy_package_parent", __file__=str(PARENT))
    exec(compile(text, str(PARENT), "exec"), namespace)
    return namespace, changes


def prepare(directory, build_root, linked_report, core, source_commit):
    for ancestor in (SOURCE_CHECKPOINT, INTEGRATION):
        subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, source_commit], cwd=ROOT, check=True)
    for name in REQUIRED_SOURCE:
        assert subprocess.check_output(["git", "show", source_commit + ":" + name], cwd=ROOT) == (ROOT / name).read_bytes(), name
    receipt = json.loads(pathlib.Path(linked_report).read_text())
    evidence = receipt["privacy_release_verification"]
    assert sha(linked_report) == RECEIPT_SHA
    assert evidence["status"] == "PASS" and evidence["full_frozen_h1_chain_executed"] is True
    assert evidence["adapter_sha256"] == sha(ROOT / "tests/privacy_fix1/verify_release.py")
    assert evidence["assertions_removed"] == 0 and evidence["unrelated_expected_hashes_changed"] == 0
    assert evidence["application_sha256"] == APP_SHA and evidence["elf_sha256"] == ELF_SHA
    assert evidence["source_checkpoint"] == SOURCE_CHECKPOINT and evidence["target_integration_commit"] == INTEGRATION
    assert evidence["recompiled"] is False and evidence["target_source_or_images_modified"] is False
    namespace, changes = adapter()
    manifest = namespace["prepare"](directory, build_root, linked_report, core, source_commit)
    return manifest, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["directory", "build-root", "linked-report", "core", "archive"]:
        parser.add_argument("--" + name, required=True, type=pathlib.Path)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    prepare(args.directory, args.build_root, args.linked_report, args.core, args.source_commit)
    namespace, _ = adapter()
    print(json.dumps(namespace["archive"](args.directory, args.archive), indent=2))


if __name__ == "__main__":
    main()
