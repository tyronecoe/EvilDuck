#!/usr/bin/env python3
"""Normal Route B candidate build: repaired editor selected, uninstalled only.

The Git base and uncommitted implementation digest are separate provenance.
There is no compiler/profile bypass, installation, package or device interface.
"""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE_COMMIT = '805d989c3ac50cb96025862c95916830c59f8ba7'
BUILD_ID = 'ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
PROFILE = 'EDITOR FAILED-LOAD SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / UNINSTALLED'
PARENT = ROOT / 'tests/dashboard_cleanup/build_candidate.py'
PARENT_SHA = '6389e9bbc1f61ce3d63e19635524eb01eea7c1518e26325865bacd09cc32b17f'
REVIEWED = ['docs/editor-load-safety-report.md', 'docs/editor-load-safety-browser-results.json',
            'docs/editor-load-safety-results.json'] + ['tests/editor_load_safety/' + name for name in
            ['application.patch', 'source-manifest.json', 'prepare_sources.py', 'test_browser.py', 'test_scope.py']]
INPUTS = REVIEWED + ['tools/build_routeb_candidate.py'] + ['tests/editor_build_integration/' + name for name in
          ['build_candidate.py', 'prepare_sources.py', 'startup_decode.py', 'verify_target.py',
           'verify_release.py', 'identity.patch', 'source-manifest.json', 'test_verify_controls.py']]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def local_inputs():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert head == BASE_COMMIT, 'Review a changed source base explicitly; no commit is created by this builder'
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT), 'Historical tracked inputs changed'
    rows = [dict(file=name, size=(ROOT / name).stat().st_size, sha256=sha(ROOT / name)) for name in sorted(INPUTS)]
    return dict(format='evilduck-local-build-inputs-v1', source_base_commit=head,
                source_commit_contains_changes=False, uncommitted_local_changes=True,
                files=rows, files_sha256=hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                reviewed_checkpoint_files=[r for r in rows if r['file'] in REVIEWED],
                build_id=BUILD_ID, profile=PROFILE)


def adapted_source():
    assert sha(PARENT) == PARENT_SHA, 'Historical dashboard builder changed'
    spec = importlib.util.spec_from_file_location('editor_dashboard_build_parent', PARENT)
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    text, inherited = parent.adapted_source(BASE_COMMIT)
    edits = []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        edits.append(dict(before=old, after=new, occurrences=count))

    replace('tests/dashboard_cleanup/prepare_sources.py', 'tests/editor_build_integration/prepare_sources.py', 4)
    replace('tests/dashboard_cleanup/source-manifest.json', 'tests/editor_build_integration/source-manifest.json')
    replace("text=text.replace('lock_feedback','dashboard_cleanup')", "text=text.replace('lock_feedback','editor_build_integration')", 2)
    replace('source_commit=CHECKPOINT', 'source_base_commit=CHECKPOINT', 3)
    replace('parent_overlay_calls="one dashboard overlay -> one privacy overlay -> one H1 composition"',
            'parent_overlay_calls="one default editor overlay -> one reviewed editor -> dashboard -> privacy -> H1 composition; identity-only last"')
    replace('DASHBOARD CLEANUP / PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW ONLY', PROFILE)
    replace('dashboard_build_id=' + repr('ROUTEB-DASHBOARD-CLEANUP-v1'), 'dashboard_build_id=' + repr(BUILD_ID))
    replace('dashboard-composition.json', 'editor-composition.json', 2)
    replace('dashboard-target-verification.json', 'editor-target-verification.json')
    replace('dashboard-target-failure.json', 'editor-target-failure.json')
    replace('dashboard-target-verification', 'editor-target-verification')
    replace('report["dashboard_target_adapter"]', 'report["editor_target_adapter"]')
    replace('dashboard_target_binding=binding', 'editor_target_binding=binding')
    # The normal source selection verifies final bundled resources before compile.
    replace('    original_overlay = privacy.overlay',
            '    original_overlay = privacy.overlay\n'
            '    before_inputs = LOCAL_INPUTS()')
    replace('        rows = expected_inventory(sketch)',
            '        rows = expected_inventory(sketch)\n'
            '        privacy.verify_final(sketch)\n'
            '        (output / "local-inputs.json").write_text(json.dumps(before_inputs, indent=2) + "\\n")')
    return text, inherited, edits


def main():
    before = local_inputs()
    text, inherited, edits = adapted_source()
    namespace = dict(__name__='editor_default_build', __file__=str(__file__), LOCAL_INPUTS=local_inputs)
    exec(compile(text, str(PARENT), 'exec'), namespace)
    code = namespace['main']()
    if code:
        return code
    output = pathlib.Path(sys.argv[sys.argv.index('--output-dir') + 1])
    assert local_inputs() == before, 'Local implementation changed while compiling'
    stored = json.loads((output / 'local-inputs.json').read_text())
    assert stored == before
    path = output / 'report.json'
    report = json.loads(path.read_text())
    assert report['editor_target_adapter']['overlay_calls'] == 1
    report['editor_target_adapter'].update(local_inputs_sha256=sha(output / 'local-inputs.json'),
        source_commit_contains_changes=False, source_provenance='UNCOMMITTED_LOCAL_INPUT_MANIFEST')
    report['editor_build_adapter'] = dict(parent='tests/dashboard_cleanup/build_candidate.py', parent_sha256=PARENT_SHA,
        adapter_sha256=sha(__file__), source_base_commit=BASE_COMMIT,
        local_inputs_sha256=sha(output / 'local-inputs.json'), source_commit_contains_changes=False,
        build_id=BUILD_ID, inherited_adaptations=inherited, exact_adaptations=edits,
        inherited_safety_predicates_removed=0, clean_compile=True, installed=False,
        owner_hardware_verified=False, canonical_entry='tools/build_routeb_candidate.py')
    report['status_label'] = 'SOURCE-INTEGRATED / COMPILE PASS / FINAL RELEASE CHECKS PENDING'
    path.write_text(json.dumps(report, indent=2) + '\n')
    release_file = ROOT / 'tests/editor_build_integration/verify_release.py'
    spec = importlib.util.spec_from_file_location('editor_mandatory_release_checks', release_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipt = output / 'editor-release-verification.json'
    try:
        module.run_chain(output, receipt)
    except Exception as error:
        report['status_label'] = 'BLOCKED / FINAL EDITOR RELEASE VERIFICATION FAILED'
        report['final_editor_release_failure'] = dict(error_type=type(error).__name__, reason=str(error))
        path.write_text(json.dumps(report, indent=2) + '\n')
        raise
    assert local_inputs() == before, 'Local implementation changed during final verification'
    report['status_label'] = 'CANDIDATE-BUILT / NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED'
    report['mandatory_release_verification'] = dict(status='PASS', file=receipt.name, sha256=sha(receipt),
                                                  full_frozen_layers=6, static_assert_nodes_retained=190)
    path.write_text(json.dumps(report, indent=2) + '\n')
    proof_path = output / 'editor-composition.json'
    proof = json.loads(proof_path.read_text())
    proof.update(source_commit_contains_changes=False, local_inputs_sha256=sha(output / 'local-inputs.json'),
                 source_provenance='UNCOMMITTED_LOCAL_INPUT_MANIFEST', status_label=report['status_label'])
    proof_path.write_text(json.dumps(proof, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
