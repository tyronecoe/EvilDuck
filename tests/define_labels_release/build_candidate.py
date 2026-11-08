#!/usr/bin/env python3
"""Committed, clean Route B build with the bounded 31-byte DEFINE-label addition.

The unchanged static-response committed-source guard runs before the additive
input manifest is assembled. All inherited archive/profile/compiler/startup/link
guards remain in the selected parent driver. No installer or device interface.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/define_labels_release'
PARENT = ROOT / 'tests/del_alias_release/build_candidate.py'
PARENT_SHA = '5f0496f5e40e9e8da4b4ca7276dfb1c05a52de2d251895c97febee242b83b15b'
BUILD_ID = 'ROUTEB-DEFINE-LABELS-H1-v1'
OLD_BUILD_ID = 'ROUTEB-DEL-ALIAS-H1-v1'
PROFILE = 'DEFINE LABELS / DEL ALIAS / PREVIOUS-COMMAND REPEAT / STATIC RESPONSE REPAIR / EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / REVIEW ONLY'
BASELINE = '6bcfb605c8249b63be2be9f79a00e4e81863fbf6'
DOC_INPUTS = ['docs/define-labels-design.md', 'docs/define-labels-references.json',
              'docs/routeb-current-compatibility.md', 'docs/del-alias-owner-closeout.md']


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def parent_module():
    assert sha(PARENT) == PARENT_SHA, 'Historical committed-source builder changed'
    spec = importlib.util.spec_from_file_location('repeat_committed_static_parent', PARENT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_inputs():
    # This is an actual call to the unchanged committed-source guard, not a
    # recreated predicate, mock, fallback or uncommitted provenance mode.
    parent = parent_module()
    inherited = parent.build_inputs()
    head = inherited['source_commit']
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASELINE, head],
                   cwd=ROOT, check=True)
    names = {row['file'] for row in inherited['files']}
    for directory in ['tests/define_labels', 'tests/define_labels_release']:
        names.update(str(p.relative_to(ROOT)) for p in (ROOT / directory).rglob('*') if p.is_file())
    names.update(DOC_INPUTS)
    rows = []
    for name in sorted(names):
        relative = pathlib.PurePosixPath(name)
        selected = ROOT / name
        assert not relative.is_absolute() and '..' not in relative.parts
        assert selected.is_file() and not selected.is_symlink(), name
        assert subprocess.check_output(['git', 'show', head + ':' + name], cwd=ROOT) == selected.read_bytes(), name
        rows.append(dict(file=name, size=selected.stat().st_size, sha256=sha(selected)))
    value = dict(inherited)
    value.update(build_id=BUILD_ID, profile=PROFILE, files=rows,
                 files_sha256=hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                 define_labels_source_baseline=BASELINE,
                 inherited_previous_repeat_guard=dict(file='tests/del_alias_release/build_candidate.py',
                    sha256=PARENT_SHA, function='build_inputs', executed_unmodified=True,
                    inherited_build_id=inherited['build_id'], inherited_files_sha256=inherited['files_sha256']))
    return value


def adapted_source(source_commit):
    parent = parent_module()
    text, inherited = parent.adapted_source(source_commit)
    changes = []
    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, ('DEFINE build adaptation occurrence mismatch', old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))
    replace('tests/del_alias_release/prepare_sources.py', 'tests/define_labels_release/prepare_sources.py', 4)
    replace('tests/del_alias_release/source-manifest.json', 'tests/define_labels_release/source-manifest.json')
    replace("text=text.replace('lock_feedback','del_alias_release')", "text=text.replace('lock_feedback','define_labels_release')", 2)
    replace('one DEL alias release overlay -> complete reviewed REPEAT parent -> exact key alias and preserved DEL() identifier -> metadata identity last',
            'one DEFINE-label release overlay -> complete DEL parent -> bounded constant cells and collection/flag length checks -> metadata identity last')
    replace(parent.PROFILE, PROFILE)
    replace('dashboard_build_id=' + repr(OLD_BUILD_ID), 'dashboard_build_id=' + repr(BUILD_ID))
    replace('del-alias-composition.json', 'define-labels-composition.json', 2)
    replace('del-alias-target-verification.json', 'define-labels-target-verification.json')
    replace('del-alias-target-failure.json', 'define-labels-target-failure.json')
    replace('del-alias-target-verification', 'define-labels-target-verification')
    replace('report["del_alias_target_adapter"]', 'report["define_labels_target_adapter"]')
    replace('del_alias_target_binding=binding', 'define_labels_target_binding=binding')
    return text, dict(del_alias=inherited, define_labels=changes)

def target_main():
    before = build_inputs()
    source_commit = before['source_commit']
    text, changes = adapted_source(source_commit)
    namespace = dict(__name__='previous_repeat_default_build', __file__=str(__file__), LOCAL_INPUTS=build_inputs)
    exec(compile(text, str(PARENT), 'exec'), namespace)
    code = namespace['main']()
    if code:
        return code
    output = pathlib.Path(sys.argv[sys.argv.index('--output-dir') + 1])
    assert build_inputs() == before, 'Committed build inputs changed during compilation'
    assert json.loads((output / 'build-inputs.json').read_text()) == before
    path = output / 'report.json'
    report = json.loads(path.read_text())
    target = report['define_labels_target_adapter']
    assert target['overlay_calls'] == 1
    target.update(build_inputs_sha256=sha(output / 'build-inputs.json'),
                  source_commit_contains_changes=True, source_provenance='COMMITTED_SOURCE_CHECKPOINT')
    report['define_labels_build_adapter'] = dict(parent='tests/del_alias_release/build_candidate.py',
        parent_sha256=PARENT_SHA, adapter_sha256=sha(__file__), source_commit=source_commit,
        build_inputs_sha256=sha(output / 'build-inputs.json'), source_commit_contains_changes=True,
        build_id=BUILD_ID, exact_adaptations=changes, inherited_safety_predicates_removed=0,
        clean_compile=True, installed=False, owner_hardware_verified=False,
        canonical_entry='tools/build_routeb_candidate.py')
    report['status_label'] = 'SOURCE-INTEGRATED / COMPILE PASS / FINAL RELEASE CHECKS PENDING'
    path.write_text(json.dumps(report, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('repeat_mandatory_release', HERE / 'verify_release.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipt = output / 'define-labels-release-verification.json'
    try:
        module.run_chain(output, receipt)
    except Exception as error:
        report['status_label'] = 'BLOCKED / DEFINE LABEL RELEASE VERIFICATION FAILED'
        report['define_labels_release_failure'] = dict(error_type=type(error).__name__, reason=str(error))
        path.write_text(json.dumps(report, indent=2) + '\n')
        raise
    assert build_inputs() == before
    report['status_label'] = 'CANDIDATE-BUILT / NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED'
    report['mandatory_release_verification'] = dict(status='PASS', file=receipt.name, sha256=sha(receipt),
                                                  full_frozen_layers=6, static_assert_nodes_retained=190)
    path.write_text(json.dumps(report, indent=2) + '\n')
    proof_path = output / 'define-labels-composition.json'
    proof = json.loads(proof_path.read_text())
    proof.update(source_commit_contains_changes=True, build_inputs_sha256=sha(output / 'build-inputs.json'),
                 source_provenance='COMMITTED_SOURCE_CHECKPOINT', status_label=report['status_label'])
    proof_path.write_text(json.dumps(proof, indent=2) + '\n')
    return 0


def source_main():
    parser = argparse.ArgumentParser(description='Source-only DEFINE-label release identity composition; no compiler')
    parser.add_argument('--compose-only', action='store_true', required=True)
    parser.add_argument('--from-composed', type=pathlib.Path, required=True)
    parser.add_argument('--output-dir', type=pathlib.Path, required=True)
    args = parser.parse_args()
    import prepare_sources as selected
    assert pathlib.Path(selected.__file__).resolve() == HERE / 'prepare_sources.py'
    selected.pin()
    selected.B.verify_final(args.from_composed)
    output = args.output_dir
    assert not output.exists() and not output.is_symlink(), 'OUTPUT_ALREADY_EXISTS'
    for ancestor in (ROOT, args.from_composed):
        assert not output.resolve().is_relative_to(ancestor.resolve()), 'OUTPUT_INSIDE_INPUT_REJECTED'
    output.mkdir(parents=True)
    destination = output / 'EvilDuckS3'
    shutil.copytree(args.from_composed, destination)
    selected.delta(destination)
    rows = selected.verify_final(destination)
    proof = dict(status='SOURCE_ONLY_COMPOSED', source=str(destination), source_count=len(rows), sources=rows,
                 selected_preparer='tests/define_labels_release/prepare_sources.py',
                 selected_manifest_sha256=sha(HERE / 'source-manifest.json'),
                 changed_sources=['caps_trial.h'], comparison_base='define-labels-source-only',
                 unchanged_sources=200, build_id=BUILD_ID, firmware_built=False, hardware_access=False)
    (output / 'composition.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k != 'sources'}, indent=2))
    return 0


def main():
    if '--compose-only' in sys.argv:
        return source_main()
    return target_main()


if __name__ == '__main__':
    raise SystemExit(main())
