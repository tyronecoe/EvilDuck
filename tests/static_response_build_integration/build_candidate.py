#!/usr/bin/env python3
"""Normal clean Route B build with reviewed static streaming responses selected.

Requires a committed checkpoint containing every selected build input. Historical
profile/compiler/archive/partition/PSRAM/USB and startup guards remain unchanged.
No installer, device, network or package interface is exposed.
"""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/static_response_build_integration'
PARENT = ROOT / 'tests/editor_build_integration/build_candidate.py'
PARENT_SHA = '0f13c984ec93f77a6144f1c4567c862e2add4ccabcfa1b20295070d9dd07a285'
BUILD_ID = 'ROUTEB-STATIC-RESPONSE-REPAIR-v1'
PROFILE = 'STATIC RESPONSE STREAMING REPAIR / EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / REVIEW ONLY'
REVIEWED_CHECKPOINT = '7c3ed81238b89b89b92924c366ecbb9afe391856'


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def build_inputs():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT), 'Commit the selected build checkpoint first'
    subprocess.run(['git', 'merge-base', '--is-ancestor', REVIEWED_CHECKPOINT, head], cwd=ROOT, check=True)
    names = {'tools/build_routeb_candidate.py'}
    for directory in ['tests/static_response_build_integration', 'tests/dashboard_response_safety']:
        names.update(str(p.relative_to(ROOT)) for p in (ROOT / directory).rglob('*') if p.is_file())
    names.update('docs/' + n for n in ['dashboard-static-response-safety-report.md',
                 'dashboard-static-response-safety-results.json', 'dashboard-static-response-safety-native.json',
                 'dashboard-static-response-safety-browser.json', 'dashboard-static-response-safety-scope.json'])
    rows = []
    for name in sorted(names):
        p = ROOT / name
        assert p.is_file() and not p.is_symlink()
        assert subprocess.check_output(['git', 'show', head + ':' + name], cwd=ROOT) == p.read_bytes(), name
        rows.append(dict(file=name, size=p.stat().st_size, sha256=sha(p)))
    return dict(format='evilduck-committed-build-inputs-v1', source_commit=head,
                source_commit_contains_changes=True, uncommitted_local_changes=False,
                reviewed_repair_checkpoint=REVIEWED_CHECKPOINT, build_id=BUILD_ID, profile=PROFILE,
                files=rows, files_sha256=hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest())


def adapted_source(source_commit):
    assert sha(PARENT) == PARENT_SHA, 'Historical editor builder changed'
    spec = importlib.util.spec_from_file_location('static_response_editor_build_parent', PARENT)
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    text, inherited, editor = parent.adapted_source()
    changes = []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace("CHECKPOINT = '805d989c3ac50cb96025862c95916830c59f8ba7'", 'CHECKPOINT = ' + repr(source_commit))
    replace('tests/editor_build_integration/prepare_sources.py', 'tests/static_response_build_integration/prepare_sources.py', 4)
    replace('tests/editor_build_integration/source-manifest.json', 'tests/static_response_build_integration/source-manifest.json')
    replace("text=text.replace('lock_feedback','editor_build_integration')", "text=text.replace('lock_feedback','static_response_build_integration')", 2)
    replace('source_base_commit=CHECKPOINT', 'source_commit=CHECKPOINT', 3)
    replace('one default editor overlay -> one reviewed editor -> dashboard -> privacy -> H1 composition; identity-only last',
            'one static response target overlay -> reviewed streaming repair -> editor -> dashboard -> privacy -> H1; metadata identity last')
    replace('EDITOR FAILED-LOAD SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / UNINSTALLED', PROFILE)
    replace('dashboard_build_id=' + repr('ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'), 'dashboard_build_id=' + repr(BUILD_ID))
    replace('changed_sources=["webfiles.h", "caps_trial.h"],\n                     unchanged_sources=199, comparison_base="privacy-fix1",',
            'changed_sources=["webfiles.h", "webserver.cpp", "caps_trial.h"],\n                     unchanged_sources=198, comparison_base="privacy-fix1",')
    replace('editor-composition.json', 'static-response-composition.json', 2)
    replace('editor-target-verification.json', 'static-response-target-verification.json')
    replace('editor-target-failure.json', 'static-response-target-failure.json')
    replace('editor-target-verification', 'static-response-target-verification')
    replace('report["editor_target_adapter"]', 'report["static_response_target_adapter"]')
    replace('editor_target_binding=binding', 'static_response_target_binding=binding')
    replace('local-inputs.json', 'build-inputs.json')
    return text, dict(dashboard=inherited, editor=editor, static_response=changes)


def main():
    before = build_inputs()
    source_commit = before['source_commit']
    text, changes = adapted_source(source_commit)
    namespace = dict(__name__='static_response_default_build', __file__=str(__file__), LOCAL_INPUTS=build_inputs)
    exec(compile(text, str(PARENT), 'exec'), namespace)
    code = namespace['main']()
    if code:
        return code
    output = pathlib.Path(sys.argv[sys.argv.index('--output-dir') + 1])
    assert build_inputs() == before, 'Committed build inputs changed during compilation'
    assert json.loads((output / 'build-inputs.json').read_text()) == before
    path = output / 'report.json'
    report = json.loads(path.read_text())
    target = report['static_response_target_adapter']
    assert target['overlay_calls'] == 1
    target.update(build_inputs_sha256=sha(output / 'build-inputs.json'),
                  source_commit_contains_changes=True, source_provenance='COMMITTED_SOURCE_CHECKPOINT')
    report['static_response_build_adapter'] = dict(parent='tests/editor_build_integration/build_candidate.py',
        parent_sha256=PARENT_SHA, adapter_sha256=sha(__file__), source_commit=source_commit,
        build_inputs_sha256=sha(output / 'build-inputs.json'), source_commit_contains_changes=True,
        build_id=BUILD_ID, exact_adaptations=changes, inherited_safety_predicates_removed=0,
        clean_compile=True, installed=False, owner_hardware_verified=False,
        canonical_entry='tools/build_routeb_candidate.py')
    report['status_label'] = 'SOURCE-INTEGRATED / COMPILE PASS / FINAL RELEASE CHECKS PENDING'
    path.write_text(json.dumps(report, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('streaming_response_mandatory_release', HERE / 'verify_release.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipt = output / 'static-response-release-verification.json'
    try:
        module.run_chain(output, receipt)
    except Exception as error:
        report['status_label'] = 'BLOCKED / STATIC RESPONSE RELEASE VERIFICATION FAILED'
        report['final_static_response_release_failure'] = dict(error_type=type(error).__name__, reason=str(error))
        path.write_text(json.dumps(report, indent=2) + '\n')
        raise
    assert build_inputs() == before
    report['status_label'] = 'CANDIDATE-BUILT / NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED'
    report['mandatory_release_verification'] = dict(status='PASS', file=receipt.name, sha256=sha(receipt),
                                                  full_frozen_layers=6, static_assert_nodes_retained=190)
    path.write_text(json.dumps(report, indent=2) + '\n')
    proof_path = output / 'static-response-composition.json'
    proof = json.loads(proof_path.read_text())
    proof.update(source_commit_contains_changes=True, build_inputs_sha256=sha(output / 'build-inputs.json'),
                 source_provenance='COMMITTED_SOURCE_CHECKPOINT', status_label=report['status_label'])
    proof_path.write_text(json.dumps(proof, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
