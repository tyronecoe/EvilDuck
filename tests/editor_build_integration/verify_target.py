#!/usr/bin/env python3
"""Bind the editor-default local composition to real compiled inputs and resources.

The local input digest is not a Git commit containing the uncommitted repair.
All older compiler/core/SDK, startup, USB/NVS and object/header predicates remain.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / 'tests/dashboard_cleanup/verify_target.py'
PARENT_SHA = '01ff00b6dfe7fe74baf2854123a1a65af38837eb7ee58e7c6f9a82eab8221bb1'
BASE = '805d989c3ac50cb96025862c95916830c59f8ba7'
BUILD_ID = 'ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
OLD_BUILD_ID = 'ROUTEB-DASHBOARD-CLEANUP-v1'
REVIEWED_HEADER_SHA = 'df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445'
PIN = ROOT / 'tests/editor_build_integration/source-manifest.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def adapted_parent():
    data = PARENT.read_bytes()
    require(hashlib.sha256(data).hexdigest() == PARENT_SHA, 'Historical dashboard verifier changed')
    text, changes = data.decode(), []

    def replace(old, new, count=1):
        nonlocal text
        require(text.count(old) == count, 'Target adapter occurrence mismatch: ' + old)
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('BUILD_ID = "ROUTEB-DASHBOARD-CLEANUP-v1"', 'BUILD_ID = ' + repr(BUILD_ID))
    replace('tests/dashboard_cleanup/source-manifest.json', 'tests/editor_build_integration/source-manifest.json', 2)
    replace('tests/dashboard_cleanup/application.patch', 'tests/editor_build_integration/identity.patch')
    replace("'sha(ROOT / \"tests/privacy_fix1/prepare_sources.py\")'", "'sha(ROOT / \"tests/editor_load_safety/prepare_sources.py\")'")
    replace('pin["format"] == "evilduck-dashboard-cleanup-v1"', 'pin["format"] == "evilduck-editor-build-integration-v1"')
    replace('pin["baseline"] == "70d08e9f789c187c5e27350a66f4d0d52992964b"', 'pin["baseline"] == ' + repr(BASE))
    replace('source_files=201, dashboard_files=2', 'source_files=201, editor_build_files=2')
    replace('dashboard_patch_sha256=pin["patch_sha256"]', 'identity_patch_sha256=pin["patch_sha256"]')
    replace('dashboard_source_manifest_sha256=sha(pin_path)', 'editor_build_source_manifest_sha256=sha(pin_path)')
    replace('DASHBOARD CLEANUP / PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW',
            'EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / UNINSTALLED')
    namespace = dict(__name__='editor_target_frozen_dashboard', __file__=str(__file__))
    exec(compile(text, str(PARENT), 'exec'), namespace)
    return namespace, changes


def expected_composition():
    pin = json.loads(PIN.read_text())
    dashboard_path = ROOT / 'tests/dashboard_cleanup/source-manifest.json'
    editor_path = ROOT / 'tests/editor_load_safety/source-manifest.json'
    privacy_path = ROOT / 'tests/privacy_fix1/source-manifest.json'
    dashboard, editor, privacy = [json.loads(p.read_text()) for p in (dashboard_path, editor_path, privacy_path)]
    require(pin['format'] == 'evilduck-editor-build-integration-v1' and pin['baseline'] == BASE and
            pin['build_id'] == BUILD_ID and pin['comparison_base'] == 'privacy-fix1', 'Wrong editor integration identity')
    require(pin['parent_prepare_sha256'] == sha(ROOT / 'tests/editor_load_safety/prepare_sources.py'), 'Reviewed editor preparer changed')
    require(pin['reviewed_editor_manifest_sha256'] == sha(editor_path), 'Reviewed editor source pin changed')
    require(pin['dashboard_manifest_sha256'] == sha(dashboard_path), 'Dashboard parent source pin changed')
    require(pin['privacy_manifest_sha256'] == sha(privacy_path), 'Privacy source pin changed')
    require(pin['baseline_inventory_sha256'] == sha(ROOT / 'docs/h1-right-modifiers-build.json'), 'H1 baseline inventory changed')
    require(pin['patch_sha256'] == sha(ROOT / 'tests/editor_build_integration/identity.patch'), 'Identity patch changed')
    require(editor['parent_prepare_sha256'] == sha(ROOT / 'tests/dashboard_cleanup/prepare_sources.py') and
            editor['parent_manifest_sha256'] == sha(dashboard_path) and
            editor['patch_sha256'] == sha(ROOT / 'tests/editor_load_safety/application.patch'), 'Reviewed editor overlay dependency changed')
    parent_final = {r['file']: r['sha256'] for r in dashboard['after'] + dashboard['unchanged']}
    reviewed_before = {r['file']: r['sha256'] for r in editor['before'] + editor['unchanged']}
    reviewed_final = {r['file']: r['sha256'] for r in editor['after'] + editor['unchanged']}
    require(len(parent_final) == len(reviewed_before) == len(reviewed_final) == 201 and
            reviewed_before == parent_final, 'Editor review is not the complete dashboard parent')
    require(len(editor['after']) == 1 and len(editor['unchanged']) == 200 and
            editor['after'][0]['file'] == 'webfiles.h' and reviewed_final['webfiles.h'] == REVIEWED_HEADER_SHA,
            'Reviewed editor repair missing or changed')
    privacy_final = {r['file']: r['sha256'] for r in privacy['after'] + privacy['unchanged']}
    declared_before = {r['file']: r['sha256'] for r in pin['before'] + pin['unchanged']}
    require(len(privacy_final) == 201 and declared_before == privacy_final and
            pin['before'] == dashboard['before'] and pin['unchanged'] == dashboard['unchanged'],
            'Final expectation comparison base is not the declared privacy layer')
    final = {r['file']: r['sha256'] for r in pin['after'] + pin['unchanged']}
    require(len(pin['after']) == 2 and len(pin['unchanged']) == 199 and len(final) == 201 and
            {r['file'] for r in pin['after']} == {'webfiles.h', 'caps_trial.h'}, 'Wrong final expectation inventory')
    require(final['webfiles.h'] == REVIEWED_HEADER_SHA and
            {name for name in final if final[name] != reviewed_final[name]} == {'caps_trial.h'},
            'Build changes extend beyond reviewed editor and identity-only header')
    return pin, final, reviewed_final


def verify_composed_source(source):
    source = pathlib.Path(source)
    pin, final, reviewed = expected_composition()
    actual = {str(p.relative_to(source)): sha(p) for p in source.rglob('*') if p.is_file()}
    require(actual == final, 'Editor composition FAIL: unsafe/omitted overlay or mismatched final source')
    caps = (source / 'caps_trial.h').read_bytes()
    require(caps.count(BUILD_ID.encode()) == 1 and OLD_BUILD_ID.encode() not in caps,
            'Uninstalled candidate identity missing/ambiguous')
    prior = caps.replace(BUILD_ID.encode(), OLD_BUILD_ID.encode(), 1)
    require(hashlib.sha256(prior).hexdigest() == reviewed['caps_trial.h'], 'Identity header changed beyond its literal label')
    return dict(status='PASS', source_files=201, editor_repair_files=1, identity_only_files=1,
                final_expectation_base='privacy-fix1', final_changed_files=2, final_unchanged_files=199,
                source_manifest_sha256=sha(PIN), reviewed_editor_manifest_sha256=pin['reviewed_editor_manifest_sha256'],
                webfiles_sha256=final['webfiles.h'], build_id=BUILD_ID)


def verify_local_inputs(build_root):
    path = pathlib.Path(build_root) / 'local-inputs.json'
    local = json.loads(path.read_text())
    require(local['format'] == 'evilduck-local-build-inputs-v1' and local['source_base_commit'] == BASE and
            local['source_commit_contains_changes'] is False and local['uncommitted_local_changes'] is True and
            local['build_id'] == BUILD_ID, 'Local source provenance is absent or pretends changes are committed')
    rows = local['files']
    names = [row['file'] for row in rows]
    require(bool(rows) and len(names) == len(set(names)), 'Local source input inventory incomplete/duplicated')
    required = {'tools/build_routeb_candidate.py'} | {'tests/editor_build_integration/' + n for n in
        ['build_candidate.py', 'prepare_sources.py', 'identity.patch', 'source-manifest.json', 'verify_target.py', 'verify_release.py']}
    require(required.issubset(names), 'Normal builder/selected overlay/verifiers missing from local input pin')
    require(hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == local['files_sha256'],
            'Local source file-list identity mismatch')
    reviewed = local['reviewed_checkpoint_files']
    reviewed_names = {'tests/editor_load_safety/' + n for n in
        ['application.patch', 'source-manifest.json', 'prepare_sources.py', 'test_browser.py', 'test_scope.py']} | {
        'docs/editor-load-safety-report.md', 'docs/editor-load-safety-browser-results.json', 'docs/editor-load-safety-results.json'}
    require(len(reviewed) == 8 and {row['file'] for row in reviewed} == reviewed_names,
            'The exact eight reviewed source-only checkpoint files are not pinned')
    for row in rows + reviewed:
        selected = ROOT / row['file']
        require(not pathlib.PurePosixPath(row['file']).is_absolute() and '..' not in pathlib.PurePosixPath(row['file']).parts and
                selected.resolve().is_relative_to(ROOT) and not selected.is_symlink() and selected.is_file(), 'Unsupported local input path')
        require(selected.stat().st_size == row['size'] and sha(selected) == row['sha256'], 'Local source bytes changed: ' + row['file'])
    return dict(source_base_commit=BASE, local_inputs_sha256=sha(path), files_sha256=local['files_sha256'],
                input_count=len(rows), source_commit_contains_changes=False, uncommitted_local_changes=True)


def literal_resources(header):
    text = pathlib.Path(header).read_text()
    found = re.findall(r'static const char (\w+)\[\] PROGMEM = R"rawliteral\((.*?)\)rawliteral";', text, re.S)
    resources = dict(found)
    require(len(resources) == len(found), 'Duplicate raw-literal resource')
    names = ['INDEX_HTML', 'INDEX_JS', 'SETTINGS_HTML', 'SETTINGS_JS', 'STYLE_CSS']
    require(set(names).issubset(resources), 'Dashboard literal resource inventory missing')
    return {name: resources[name].encode() + b'\0' for name in names}


def verify_resource_bytes(resources, elf_bytes, bin_bytes):
    evidence = []
    for name, data in resources.items():
        require(elf_bytes.count(data) == 1 and bin_bytes.count(data) == 1,
                'Bundled resource FAIL: missing/older/ambiguous ' + name)
        evidence.append(dict(resource=name, bytes_including_nul=len(data), sha256=hashlib.sha256(data).hexdigest(),
                             elf_occurrences=1, binary_occurrences=1, elf_offset=elf_bytes.index(data), binary_offset=bin_bytes.index(data)))
    return evidence


def verify(build_root):
    root = pathlib.Path(build_root).resolve()
    source = verify_composed_source(root / 'candidate/EvilDuckS3')
    local = verify_local_inputs(root)
    namespace, changes = adapted_parent()
    binding = namespace['verify'](root)
    resources = literal_resources(root / 'candidate/EvilDuckS3/webfiles.h')
    linked = verify_resource_bytes(resources, (root / 'build/EvilDuckS3.ino.elf').read_bytes(),
                                   (root / 'build/EvilDuckS3.ino.bin').read_bytes())
    binding.update(build_id=BUILD_ID, status='PASS', source_base_commit=BASE,
                   local_inputs_sha256=local['local_inputs_sha256'], local_source_provenance=local,
                   editor_source_composition=source, bundled_resources=linked,
                   actual_parent_verifier_sha256=PARENT_SHA, integration_verifier_adaptations=changes,
                   dashboard_parent_manifest_sha256=sha(ROOT / 'tests/dashboard_cleanup/source-manifest.json'),
                   reviewed_editor_patch_sha256=sha(ROOT / 'tests/editor_load_safety/application.patch'),
                   physical=False, installed=False, package_created=False)
    return binding


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Fresh evidence path required')
    args.output.write_text(json.dumps(verify(args.build_root), indent=2) + '\n')
    print('PASS actual target source/header/object/resources bound; UNINSTALLED, NOT OWNER-HARDWARE-VERIFIED')


if __name__ == '__main__':
    main()
