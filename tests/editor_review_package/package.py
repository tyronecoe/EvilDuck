#!/usr/bin/env python3
"""Package the existing verified editor image; never compile or access a device.

The frozen H1 installer/launcher construction is unchanged, except the generated
RELEASE_BINDING. A post-build Git checkpoint attests the original local inputs;
it is not falsely reported as the Git context in which compilation occurred.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / 'tests/h1_right_modifiers/package.py'
PARENT_SHA = 'b29c8995bf36668da89e092975c3f83cba7214e33349f12050dde7b82db773b2'
DASHBOARD = ROOT / 'tests/dashboard_cleanup/package.py'
DASHBOARD_SHA = 'e696ed2dcb7bea8d8cf0057e526ac86e1f283bcc0116b99fe597459493d82efa'
PACKAGE = 'evilduck-editor-safety-h1-macos-review-v1'
BUILD_ID = 'ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
BASE = '805d989c3ac50cb96025862c95916830c59f8ba7'
CHECKPOINT = '1664d4f25593e6cc99dba43ff0e5d74531555a51'
APP_SHA = 'e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0'
APP_BYTES = 1437696
ELF_SHA = '51e918c98249af4fb79dbd79a31a2ecdbcb92a0045e2d6f213c99cd86e755057'
ELF_BYTES = 23645104
LOCAL_SHA = '525fc3f9e95c65f81a1233f3f31eac1f321233d0dd87ac2517d5a4c2f2eab768'
ROLLBACK_SHA = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
ROLLBACK_BYTES = 1413200
REQUIRED_SOURCE = ['tests/editor_review_package/' + n for n in
                   ['package.py', 'package_preflight.py', 'test_package.py', 'reproduce_checkpoint.py']] + [
                  'docs/editor-safety-review-' + n + '.md' for n in ['report', 'acceptance', 'reproduction', 'platforms']]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def documents():
    common = ('**REVIEW ONLY — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED.**\n\n'
              'This package authorizes no installation, boot, physical test or script execution. H1 remains opt-in '
              'and experimental; canonical Hak5 numeric encoding is unresolved.\n\n')
    identity = ('Build ID: `' + BUILD_ID + '`. Application: **1,437,696 bytes**, SHA-256 `' + APP_SHA + '`. '
                'It is the verified existing application; no firmware was rebuilt for packaging. The Build ID is '
                'a static candidate label, not independent proof of a device state.\n\n')
    offline = ('First, extract into a new folder, keep EvilDuck **unplugged**, and run only:\n\n'
               '```bash\npython3 preflight.py --directory .\n```\n\n'
               'Expect exit 0, package_integrity=PASS, installed_metadata=NOT_SUPPLIED, plan_ready=false, '
               'selected_write_ranges=[], hardware_access=false and installation_authorized=false. '
               'Stop on rejection. This command is offline; it uses Python 3.8+ standard library only. '
               'The install launcher default performs hardware checks and is NOT this offline step.\n\n')
    rollback = ('Exact older source/text-v2 rollback: **1,413,200 bytes**, SHA-256 `' + ROLLBACK_SHA + '`. '
                'It does not contain Privacy Fix 1 or the later dashboard/editor repairs. It is application code, '
                'not a complete flash or filesystem backup. Existing backups remain untouched.\n\n')
    provenance = ('Post-build source checkpoint: `' + CHECKPOINT + '`. The actual build ran from base `' + BASE +
                  '` with the recorded 17 uncommitted inputs, manifest SHA-256 `' + LOCAL_SHA + '`. '
                  'source-attestation.json proves that checkpoint contains those exact file bytes; it does not '
                  'claim compilation occurred after that commit. See reproduction.md for the isolated-base '
                  'reproduction procedure.\n\n')
    future = ('Only after separate physical authorization, the unchanged Mac workflow uses '
              '`bash install-macos.sh --action check --port CURRENT_PORT`, then separately '
              '`bash install-macos.sh --action install --port CURRENT_PORT`; the deliberate rollback is '
              '`bash rollback-macos.sh --port CURRENT_PORT`. Never run the placeholder literally. Rediscover the '
              'port after reconnects. High Sierra 10.13.6, Bash 3.2, Python 3.8+ and preinstalled esptool 4.12.0 '
              'remain the reviewed workflow; no dependency is installed/downloaded by this package.\n\n'
              'The installer checks ESP32-S3/16 MiB, security state, exact current partition table/OTA metadata, '
              'image integrity and bounded write ranges. It creates a new **private full-flash backup before '
              'its final INSTALL confirmation** (or ROLLBACK confirmation); it may contain credentials, scripts '
              'and settings and remains even if confirmation is declined. Keep backups/receipts private. '
              'No existing backup is deleted or overwritten. Only both application slots, 0x10000 and 0x750000 '
              'within 0x740000-byte slots, are proposed. Bootloader, table, NVS, OTA metadata, SPIFFS and coredump '
              'are excluded. No automatic reset/reboot, retry, format, settings reset or payload Start occurs. '
              'Write/compare failure requires stopping for a separate recovery review.\n\n')
    historical = ('The inherited source-stage identity `ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1` is historical '
                  'provenance, NOT this candidate Build ID. Prior right-modifier, lock-wait, executed STOP and '
                  'privacy milestones remain accepted within their recorded limits. The four rm-*.txt files '
                  'are host provenance only; do not run/reinstall them for this review.\n\n')
    return {
        'README.md': common + identity + offline + provenance + rollback +
                     'Read OWNER-CHECK.md, INSTALL-MAC.md and ROLLBACK-MAC.md. This package adds only the reviewed '
                     'editor data-safety repair to the existing composition. Until separately installed/accepted, '
                     'keep avoiding Save/editor Run after a failed load on the currently installed firmware.\n\n' + historical,
        'INSTALL-MAC.md': common + identity + offline + provenance + rollback + 'Read OWNER-CHECK.md first.\n\n' + future + historical,
        'ROLLBACK-MAC.md': common + rollback + offline + future +
                           'Rollback never restores deleted scripts or past settings. It is separately deliberate, '
                           'never automatic or implied by downloading/checking this ZIP.\n',
    }


def adapter(receipt_sha, attestation_file):
    assert sha(PARENT) == PARENT_SHA and sha(DASHBOARD) == DASHBOARD_SHA
    dashboard = load(DASHBOARD, 'editor_review_dashboard_parent')
    _, inherited = dashboard.adapter(CHECKPOINT, APP_SHA, APP_BYTES, ELF_SHA, receipt_sha)
    text = PARENT.read_text()
    for row in inherited:
        assert text.count(row['before']) == row['occurrences']
        text = text.replace(row['before'], row['after'])
    changes = []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace(repr(dashboard.PACKAGE), repr(PACKAGE))
    replace('tests/dashboard_cleanup/package_preflight.py', 'tests/editor_review_package/package_preflight.py', 2)
    for old, new in [('acceptance', 'acceptance'), ('report', 'report'), ('platforms', 'platforms'), ('reproduction', 'reproduction')]:
        replace('docs/dashboard-cleanup-' + old + '.md', 'docs/editor-safety-review-' + new + '.md')
    replace('docs/dashboard-cleanup-browser-results.json', 'docs/editor-build-integration-results.json')
    replace('    for name, source in copies.items():',
            "    copies['reviewed-editor-source-manifest.json'] = ROOT/'tests/editor_load_safety/source-manifest.json'\n"
            "    copies['editor-build-source-manifest.json'] = ROOT/'tests/editor_build_integration/source-manifest.json'\n"
            "    copies['local-build-inputs.json'] = build_root/'local-inputs.json'\n"
            "    copies['source-attestation.json'] = ATTESTATION_FILE\n"
            '    for name, source in copies.items():')
    replace('firmware_build_id=' + repr(dashboard.BUILD_ID) + ',', 'firmware_build_id=' + repr(BUILD_ID) + ',')
    replace('composition_base_commit=' + repr(dashboard.BASE_COMMIT), 'composition_base_commit=' + repr(BASE))
    replace('dashboard_release_receipt_sha256=RECEIPT_SHA', 'editor_release_receipt_sha256=RECEIPT_SHA')
    anchor = "    (out/'preflight.py').write_text("
    replace(anchor,
            "    bound.update(editor_pin_sha256=sha(ROOT/'tests/editor_load_safety/source-manifest.json'),\n"
            "        editor_build_pin_sha256=sha(ROOT/'tests/editor_build_integration/source-manifest.json'),\n"
            "        editor_build_adapter_sha256=sha(ROOT/'tests/editor_build_integration/build_candidate.py'),\n"
            "        editor_release_adapter_sha256=sha(ROOT/'tests/editor_build_integration/verify_release.py'),\n"
            "        editor_target_verifier_sha256=sha(ROOT/'tests/editor_build_integration/verify_target.py'),\n"
            "        local_build_inputs_sha256=sha(build_root/'local-inputs.json'),\n"
            "        source_attestation_sha256=sha(ATTESTATION_FILE), application_elf_sha256=ELF_SHA)\n" + anchor)
    anchor = "    (out/'manifest.json').write_text("
    replace(anchor,
            "    manifest.update(editor_profile='EDITOR_FAILED_LOAD_SAFETY_H1_OWNER_REVIEW',\n"
            "        original_build_source_base_commit='" + BASE + "', original_source_commit_contains_changes=False,\n"
            "        original_local_inputs_sha256='" + LOCAL_SHA + "', post_build_source_checkpoint_commit=FIRMWARE_SOURCE,\n"
            "        firmware_source_identity_kind='POST_BUILD_CHECKPOINT_EXACT_BUILD_INPUTS',\n"
            "        source_checkpoint_after_build=True, application_elf_bytes=ELF_BYTES, status_label='NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED',\n"
            "        reviewed_editor_pin_sha256=sha(out/'reviewed-editor-source-manifest.json'),\n"
            "        editor_build_pin_sha256=sha(out/'editor-build-source-manifest.json'),\n"
            "        source_attestation_sha256=sha(out/'source-attestation.json'),\n"
            "        editor_packaging_parent_sha256='" + DASHBOARD_SHA + "')\n" + anchor)
    namespace = dict(__name__='editor_review_frozen_packager', __file__=str(PARENT),
                     GENERATED_DOCS=documents(), ATTESTATION_FILE=pathlib.Path(attestation_file), ELF_BYTES=ELF_BYTES)
    exec(compile(text, str(PARENT), 'exec'), namespace)
    return namespace, inherited, changes


def source_attestation(build_root):
    local_file = pathlib.Path(build_root) / 'local-inputs.json'
    assert sha(local_file) == LOCAL_SHA
    local = json.loads(local_file.read_text())
    assert local['source_base_commit'] == BASE and local['source_commit_contains_changes'] is False
    assert len(local['files']) == 17
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, CHECKPOINT], cwd=ROOT, check=True)
    for row in local['files']:
        data = subprocess.check_output(['git', 'show', CHECKPOINT + ':' + row['file']], cwd=ROOT)
        assert len(data) == row['size'] and hashlib.sha256(data).hexdigest() == row['sha256'], row['file']
        assert (ROOT / row['file']).read_bytes() == data, row['file']
    return dict(format='evilduck-post-build-source-checkpoint-v1', source_checkpoint_commit=CHECKPOINT,
                source_checkpoint_after_build=True, source_checkpoint_contains_fix=True,
                original_build_source_base_commit=BASE, original_source_commit_contains_changes=False,
                original_local_inputs_sha256=LOCAL_SHA, files=local['files'], files_sha256=local['files_sha256'],
                git_blobs_verified=True, recompilation_performed=False, hardware=False)


def prepare(directory, build_root, linked_report, core, source_commit):
    assert re.fullmatch('[0-9a-f]{40}', source_commit)
    for ancestor in (BASE, CHECKPOINT):
        subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, source_commit], cwd=ROOT, check=True)
    for name in REQUIRED_SOURCE:
        assert subprocess.check_output(['git', 'show', source_commit + ':' + name], cwd=ROOT) == (ROOT / name).read_bytes(), name
    target = load(ROOT / 'tests/editor_build_integration/verify_target.py', 'editor_review_exact_target')
    build_root, linked_report = pathlib.Path(build_root).resolve(), pathlib.Path(linked_report).resolve()
    binding = target.verify(build_root)
    receipt = json.loads(linked_report.read_text()); built = json.loads((build_root / 'report.json').read_text())
    evidence = receipt['editor_release_verification']
    assert evidence['status'] == 'PASS' and evidence['full_frozen_h1_chain_executed'] is True
    assert evidence['source_base_commit'] == evidence['base_commit'] == BASE and evidence['source_commit_contains_changes'] is False
    assert evidence['local_inputs_sha256'] == LOCAL_SHA
    assert evidence['application_sha256'] == APP_SHA and evidence['elf_sha256'] == ELF_SHA
    assert evidence['actual_runtime_build_id'] == receipt['actual_runtime_build_id'] == BUILD_ID
    assert evidence['adapter_sha256'] == sha(ROOT / 'tests/editor_build_integration/verify_release.py')
    assert evidence['assertions_preserved'] == 190 and evidence['assertions_removed'] == evidence['unrelated_expected_hashes_changed'] == 0
    assert evidence['historical_source_pin_build_ids_changed'] is False
    assert evidence['recompiled'] is False and evidence['target_source_or_images_modified'] is False
    assert evidence['editor_target_binding'] == binding == built['editor_target_adapter']['editor_target_binding']
    assert receipt['editor_target_adapter'] == built['editor_target_adapter']
    for key in ['source_inventory', 'report', 'provenance']:
        assert receipt[key] == built[key], key
    assert receipt['report']['application_bytes'] == APP_BYTES and (build_root/'build/EvilDuckS3.ino.elf').stat().st_size == ELF_BYTES
    assert receipt['editor_build_source_pin'] == json.loads((ROOT/'tests/editor_build_integration/source-manifest.json').read_text())
    assert receipt['reviewed_editor_source_pin'] == json.loads((ROOT/'tests/editor_load_safety/source-manifest.json').read_text())
    attestation = source_attestation(build_root)
    with tempfile.TemporaryDirectory(prefix='public-editor-source-attestation-') as tmp:
        attestation_file = pathlib.Path(tmp) / 'source-attestation.json'
        attestation_file.write_text(json.dumps(attestation, indent=2) + '\n')
        namespace, inherited, changes = adapter(sha(linked_report), attestation_file)
        manifest = namespace['prepare'](directory, build_root, linked_report, core, source_commit)
    return manifest, inherited, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['directory', 'build-root', 'linked-report', 'core', 'archive']:
        parser.add_argument('--'+name, type=pathlib.Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    manifest, _, _ = prepare(args.directory, args.build_root, args.linked_report, args.core, args.source_commit)
    namespace, _, _ = adapter(sha(args.linked_report), pathlib.Path(args.directory)/'source-attestation.json')
    print(json.dumps(namespace['archive'](args.directory, args.archive), indent=2))


if __name__ == '__main__':
    main()
