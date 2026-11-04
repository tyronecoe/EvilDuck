#!/usr/bin/env python3
"""Full frozen six-layer release chain plus actual streaming target verification.

Final source expectations and runtime identity advance to this exact candidate;
all 190 inherited Assert nodes and the original SDK/startup/link guards remain.
Every textual adaptation is occurrence-checked and retained in the receipt.
"""
import argparse
import builtins
import hashlib
import importlib.util
import json
import pathlib
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
EDITOR = ROOT / 'tests/editor_build_integration/verify_release.py'
EDITOR_SHA = '223ce8a330d33607710d9eea5ec9fbf378dc53e0707b1c3e0b8f0860a3756fb8'
BUILD_ID = 'ROUTEB-STATIC-RESPONSE-REPAIR-v1'
BASE = 'e692435a7c70dbc0d917bbff733c57900cf7d57c'
ORIGINAL_COMPILE = builtins.compile


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def adapted_parent():
    assert sha(EDITOR) == EDITOR_SHA, 'Historical editor release verifier changed'
    spec = importlib.util.spec_from_file_location('streaming_release_editor_parent', EDITOR)
    editor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(editor)
    editor.BUILD_ID, editor.BASE = BUILD_ID, BASE
    captured = []

    def capture(source, filename, mode, *args, **kwargs):
        if str(filename) == str(editor.PARENT) and mode == 'exec' and isinstance(source, str):
            captured.append(source)
        return ORIGINAL_COMPILE(source, filename, mode, *args, **kwargs)

    with patch.object(builtins, 'compile', capture):
        _, inherited = editor.adapted_parent()
    assert len(captured) == 1
    text, changes = captured[0], []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, ('Release adapter occurrence mismatch', old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('tests/editor_build_integration/source-manifest.json', 'tests/static_response_build_integration/source-manifest.json')
    replace('tests/editor_build_integration/identity.patch', 'tests/static_response_build_integration/identity.patch')
    replace('tests/editor_build_integration/verify_target.py', 'tests/static_response_build_integration/verify_target.py')
    replace('editor_target_adapter', 'static_response_target_adapter')
    replace('editor_target_binding', 'static_response_target_binding', 2)
    replace('editor_release_verification', 'static_response_release_verification')
    replace('report["editor_build_source_pin"] = pin', 'report["static_response_build_source_pin"] = pin')
    replace('if row["file"] != "webfiles.h":', 'if row["file"] not in {"webfiles.h", "webserver.cpp"}:')
    old = '''    local_inputs_sha256 = sha(build_root / "local-inputs.json")
    assert source_info.get("source_base_commit") == BASE_COMMIT, "Wrong source base commit"
    assert source_info.get("local_inputs_sha256") == local_inputs_sha256, "Wrong local uncommitted-input identity"
'''
    new = '''    committed_inputs = target_module.verify_input_manifest(build_root)
    source_commit = committed_inputs["source_commit"]
    build_inputs_sha256 = sha(build_root / "build-inputs.json")
    assert source_info.get("source_commit") == source_commit, "Wrong committed source revision"
    assert source_info.get("build_inputs_sha256") == build_inputs_sha256, "Wrong committed-input identity"
    assert source_info.get("source_commit_contains_changes") is True, "Missing committed implementation proof"
'''
    replace(old, new)
    replace('source_base_commit=BASE_COMMIT, source_commit_contains_changes=False, local_inputs_sha256=local_inputs_sha256, adapter_sha256=sha(__file__),',
            'source_commit=source_commit, source_commit_contains_changes=True, build_inputs_sha256=build_inputs_sha256, adapter_sha256=sha(__file__),')
    replace('EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / UNINSTALLED / NOT OWNER-HARDWARE-VERIFIED',
            'STATIC RESPONSE REPAIR / EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / REVIEW / NOT OWNER-HARDWARE-VERIFIED')
    namespace = dict(__name__='streaming_release_frozen_chain', __file__=str(__file__))
    exec(ORIGINAL_COMPILE(text, str(editor.PARENT), 'exec'), namespace)
    return namespace, dict(editor=inherited, static_response=changes)


def run_chain(build_root, output):
    namespace, changes = adapted_parent()
    report = namespace['run_chain'](build_root, output)
    info = report['static_response_release_verification']
    binding = info['static_response_target_binding']
    assert info['assertions_preserved'] == 190 and info['assertions_removed'] == 0
    assert len(binding['bundled_resources']) == 5
    assert binding['streaming_response']['status'] == 'PASS'
    info.update(actual_parent_verifier_sha256=EDITOR_SHA, integration_adaptations=changes,
                installed=False, owner_hardware_verified=False, status_label='REVIEW ONLY / NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED')
    for key, directory in [('dashboard_parent_source_pin', 'dashboard_cleanup'),
                           ('reviewed_editor_source_pin', 'editor_load_safety'),
                           ('editor_build_source_pin', 'editor_build_integration'),
                           ('static_response_source_pin', 'dashboard_response_safety')]:
        report[key] = json.loads((ROOT / 'tests' / directory / 'source-manifest.json').read_text())
    pathlib.Path(output).write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    run_chain(args.build_root, args.output)
    print('PASS full six-layer190assert release chain and actual static streaming target; review only')


if __name__ == '__main__':
    main()
