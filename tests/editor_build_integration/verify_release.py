#!/usr/bin/env python3
"""Execute the unchanged six-layer H1 release chain for the uninstalled local build.

The only inherited expectation changes are exact final four-file source hashes,
actual runtime-ID membership and honest local-input provenance. Older stage IDs,
all 190 static Assert nodes, source pins, SDK/core/startup and linked guards remain.
"""
import argparse
import hashlib
import json
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / 'tests/dashboard_cleanup/verify_release.py'
PARENT_SHA = 'eca7a6797940b158935bbc1352550652a93f99b4e7283d0d1eab04662330ed54'
BASE = '805d989c3ac50cb96025862c95916830c59f8ba7'
BUILD_ID = 'ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def adapted_parent():
    data = PARENT.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PARENT_SHA, 'Historical dashboard release verifier changed'
    text, changes = data.decode(), []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, ('Release adapter occurrence mismatch', old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('BUILD_ID = "ROUTEB-DASHBOARD-CLEANUP-v1"', 'BUILD_ID = ' + repr(BUILD_ID))
    replace('BASE_COMMIT = "70d08e9f789c187c5e27350a66f4d0d52992964b"', 'BASE_COMMIT = ' + repr(BASE))
    replace('tests/dashboard_cleanup/source-manifest.json', 'tests/editor_build_integration/source-manifest.json')
    replace('tests/dashboard_cleanup/application.patch', 'tests/editor_build_integration/identity.patch')
    replace('    from verify_target import verify', '''    target_path = ROOT / "tests/editor_build_integration/verify_target.py"
    target_spec = importlib.util.spec_from_file_location("editor_selected_target_verify", target_path)
    target_module = importlib.util.module_from_spec(target_spec)
    target_spec.loader.exec_module(target_module)
    verify = target_module.verify''')
    replace('dashboard_target_adapter', 'editor_target_adapter')
    replace('dashboard_target_binding', 'editor_target_binding')
    replace('dashboard_release_verification', 'editor_release_verification')
    replace('report["dashboard_source_pin"] = pin', 'report["editor_build_source_pin"] = pin')
    old = '''    source_info = built.get("editor_target_adapter", {})
    source_commit = source_info.get("source_commit", source_info.get("source_checkpoint"))
    assert isinstance(source_commit, str) and len(source_commit) == 40 and all(
        character in "0123456789abcdef" for character in source_commit), "Missing exact target source revision"
'''
    new = '''    source_info = built.get("editor_target_adapter", {})
    local_inputs_sha256 = sha(build_root / "local-inputs.json")
    assert source_info.get("source_base_commit") == BASE_COMMIT, "Wrong source base commit"
    assert source_info.get("local_inputs_sha256") == local_inputs_sha256, "Wrong local uncommitted-input identity"
    assert source_info.get("overlay_calls") == 1 and source_info.get("clean_compile") is True, "Default overlay/clean build evidence missing"
    assert source_info.get("editor_target_binding") == binding_after, "Target binding differs from executed build"
'''
    replace(old, new)
    replace('source_commit=source_commit, adapter_sha256=sha(__file__),',
            'source_base_commit=BASE_COMMIT, source_commit_contains_changes=False, local_inputs_sha256=local_inputs_sha256, adapter_sha256=sha(__file__),')
    replace('DASHBOARD CLEANUP / PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW / PHYSICAL VALIDATION PENDING',
            'EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / UNINSTALLED / NOT OWNER-HARDWARE-VERIFIED')
    namespace = dict(__name__='editor_release_frozen_dashboard', __file__=str(__file__))
    exec(compile(text, str(PARENT), 'exec'), namespace)
    return namespace, changes


def run_chain(build_root, output):
    namespace, changes = adapted_parent()
    report = namespace['run_chain'](build_root, output)
    binding = report['editor_release_verification']['editor_target_binding']
    assert len(binding['bundled_resources']) == 5
    assert report['editor_release_verification']['assertions_preserved'] == 190
    report['editor_release_verification'].update(
        actual_parent_verifier_sha256=PARENT_SHA, integration_adaptations=changes,
        installed=False, package_created=False, status_label='CANDIDATE-BUILT / UNINSTALLED / NOT OWNER-HARDWARE-VERIFIED')
    report['dashboard_parent_source_pin'] = json.loads((ROOT / 'tests/dashboard_cleanup/source-manifest.json').read_text())
    report['reviewed_editor_source_pin'] = json.loads((ROOT / 'tests/editor_load_safety/source-manifest.json').read_text())
    pathlib.Path(output).write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    run_chain(args.build_root, args.output)
    print('PASS full six-layer release checks and exact bundled editor resources; UNINSTALLED')


if __name__ == '__main__':
    main()
