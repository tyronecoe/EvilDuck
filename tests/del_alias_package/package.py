# Additive DEL-alias review package; immutable REPEAT parent 7d229d6b648211f59c05479d356fbdf0a7930e6d2637768720a5383ce93c3f34
#!/usr/bin/env python3
"""Review-only DEL alias package around the frozen guarded Mac installer.

The exact clean-build identities are committed in release-binding.json after
verification. No target compiler, hardware, network or private-backup access.
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
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ROOT / 'tests/h1_right_modifiers/package.py'
PARENT_SHA = 'b29c8995bf36668da89e092975c3f83cba7214e33349f12050dde7b82db773b2'
DASHBOARD = ROOT / 'tests/dashboard_cleanup/package.py'
DASHBOARD_SHA = 'e696ed2dcb7bea8d8cf0057e526ac86e1f283bcc0116b99fe597459493d82efa'
PACKAGE = 'evilduck-routeb-del-alias-h1-macos-review-v1'
BUILD_ID = 'ROUTEB-DEL-ALIAS-H1-v1'
BASE = '557dc81f65b672d5b701b681664ef6ff0a7e5d44'
ROLLBACK_SHA = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
ROLLBACK_BYTES = 1413200
FAULTY_SHA = 'e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0'
OLD_STATIC_SHA = 'd5fe0932fe915443a5e53030969c6792409f719d427681304a7102355b2d7946'
OLD_REPEAT_SHA = '13cec88262afdfa641eb0fb4927fe7903abf2863295344ff316418707ba49b7f'
HISTORICAL_PACKAGE_PINS = {
    'package.py': '7d229d6b648211f59c05479d356fbdf0a7930e6d2637768720a5383ce93c3f34',
    'package_preflight.py': 'd095130bfb73d75ab708be338df97739227f129cecfe2a4fb60226a94f71ab29',
    'test_package.py': '9e8047b2fef5f3210f637f7b32d41dc745a00840c05d57c9fe472ccbb0d2b168',
}
REQUIRED_SOURCE = ['tests/del_alias_package/' + n for n in
                   ['package.py', 'package_preflight.py', 'test_package.py', 'release-binding.json']]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def release_binding():
    for name, expected in HISTORICAL_PACKAGE_PINS.items():
        assert sha(ROOT / 'tests/previous_command_repeat_package' / name) == expected
    value = json.loads((HERE / 'release-binding.json').read_text())
    assert value['format'] == 'evilduck-del-alias-release-binding-v1'
    assert value['status'] == 'VERIFIED_LOCAL_RELEASE', 'Actual new image verification required'
    assert value['build_id'] == BUILD_ID
    assert re.fullmatch('[0-9a-f]{40}', value['source_commit'])
    assert value['verifier_context_commit'] == value['source_commit']
    assert value['post_compile_verifier_delta'] is None
    for key in ['application_sha256', 'elf_sha256', 'release_receipt_sha256',
                'build_inputs_sha256', 'repeat_target_binding_sha256', 'test_results_sha256',
                'del_core_sha256', 'del_shortcuts_sha256', 'del_test_receipt_sha256']:
        assert re.fullmatch('[0-9a-f]{64}', value[key]), key
    assert value['application_sha256'] not in (FAULTY_SHA, OLD_STATIC_SHA, OLD_REPEAT_SHA, ROLLBACK_SHA)
    assert value['application_bytes'] > 0 and value['elf_bytes'] > 0
    assert isinstance(value['build_input_count'], int) and value['build_input_count'] > 26
    return value


def documents(binding):
    common = ('**REVIEW ONLY — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED.**\n\n'
              'Downloading or checking this package authorizes no hardware access, installation, boot or '
              'payload execution. H1 remains opt-in and experimental; canonical Hak5 numeric encoding is unresolved.\n\n')
    identity = ('Build ID: `' + BUILD_ID + '`. Application: **' + str(binding['application_bytes']) +
                ' bytes**, SHA-256 `' + binding['application_sha256'] + '`. Firmware source checkpoint: `' +
                binding['source_commit'] + '`. These identify the local candidate, not installed device bytes.\n\n')
    offline = ('Extract into a new folder and keep EvilDuck **unplugged**. Run only:\n\n'
               '```bash\npython3 preflight.py --directory .\n```\n\n'
               'Expect exit 0, `package_integrity: PASS`, `installed_metadata: NOT_SUPPLIED`, '
               '`plan_ready: false`, `selected_write_ranges: []`, `hardware_access: false` and '
               '`installation_authorized: false`. Stop on rejection. This is Python 3.8+ standard-library-only '
               'offline checking. The install launcher default contacts hardware and is NOT this offline step.\n\n')
    rollback = ('Exact older source/text-v2 rollback: **1,413,200 bytes**, SHA-256 `' + ROLLBACK_SHA + '`. '
                'It lacks Privacy Fix 1 and the later dashboard/editor/static-response repairs. It is a standalone '
                'application, not a full-device restore; it cannot restore deleted scripts or past settings. '
                'The e825 editor-safety candidate is not a known-good recovery image. Preserve every existing backup.\n\n')
    provenance = ('The application was clean-built from committed source `' + binding['source_commit'] +
                  '`. Every selected compile input is bound to its Git blob in build-inputs.json and '
                  'source-attestation.json. The verifier is from that same checkpoint, with no post-build '
                  'source or verifier delta. build-receipt.json retains the complete 190-assert release chain, '
                  'actual static-response linkage, compiled/linked standalone REPEAT proof and DEL alias '
                  'source/object/linked-table witnesses.\n\n')
    future = ('Only after separate physical authorization, use the owner-established ROM-entry procedure and '
              'rediscover the current `/dev/cu.usbmodem*` port after reconnecting. Future commands are '
              '`bash install-macos.sh --action check --port CURRENT_PORT`, then separately '
              '`bash install-macos.sh --action install --port CURRENT_PORT`. Deliberate rollback uses '
              '`bash rollback-macos.sh --port CURRENT_PORT`. Never run the placeholder literally. The supported '
              'host is macOS High Sierra 10.13.6, Bash 3.2, Python 3.8+ and preinstalled esptool 4.12.0; no '
              'dependency download/install occurs. Hardware compatibility remains ESP32-S3/16 MiB, PSRAM disabled.\n\n'
              'The source-stage label `ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1` is historical provenance, '
              'not this candidate Build ID.\n\n'
              'The unchanged installer refuses unsupported chip, security, partition and OTA states. It creates '
              'a new **private full-flash backup before its final INSTALL confirmation** (or ROLLBACK confirmation). '
              'That backup may contain credentials, scripts and settings and remains if confirmation is declined. '
              'No existing backup is deleted or overwritten. Keep backups and raw device receipts private.\n\n'
              'Only the two application regions at 0x10000 and 0x750000, each bounded by 0x740000 bytes, are '
              'proposed writes. Bootloader, partition table, NVS, OTA metadata, SPIFFS and coredump are excluded. '
              'No automatic reboot/reset, retry, formatting, settings reset or script Start occurs. A failed '
              'write/compare requires stopping in ROM for separate recovery review. Matching flash bytes do '
              'not establish boot, USB or TextEdit success.\n\n')
    semantics = ('Exact uppercase `DEL` is an alias of `DELETE`: keyboard usage 0x4c, forward delete. '
                 'Existing modifier chords, HOLD/RELEASE and supported REPEAT positions reuse the ordinary '
                 'key path. `STRING DEL` and text blocks remain literal; `DEL()` functions and `$DEL` '
                 'variables remain valid. Raw source byte 0x7f is still rejected. No new layout or Unicode '
                 'support is added. This profile still requires the US device mapping.\n\n'
                 'Standalone `REPEAT 1..128` means additional executions of an eligible preceding leaf; inline '
                 '`REPEAT 2..128 leaf` retains total-count semantics. The whole program still fits at most '
                 '128 IR instructions. Comments/directives preserve eligible history, while runtime structural '
                 'boundaries, state commands and multiline blocks clear it. Standalone chaining rejects. '
                 'These are bounded EvilDuck policies, not blanket Hak5 DS3 certification. INJECT_VAR is '
                 'unchanged and is not an inline-REPEAT leaf.\n\n')
    acceptance = (common + identity + 'Use only after a separately authorized owner installation. These are '
                  'small benign TextEdit checks, not requests to repeat accepted baseline milestones. '
                  'Record the actual assigned request ID, dashboard terminal status and visible text separately; '
                  'HTTP 202 or a Completed label alone does not prove exact typed output. Leave unavailable '
                  'boot/session evidence unknown.\n\n'
                  '1. Confirm the new dashboard Build ID, authenticated Route B status and STOP availability. '
                  'Do not retrieve saved secrets. Open blank TextEdit, plain text mode.\n'
                  '2. Trial A: run the following once in a blank plain-text document. Expect two lines '
                  '`ac` and `ac`, then matching Completed. DEL is forward delete, not Backspace.\n\n'
                  '```ducky\nDELAY 5000\nSTRING abc\nLEFTARROW\nLEFTARROW\nDEL\nRIGHTARROW\nENTER\nSTRING abc\nLEFTARROW\nLEFTARROW\nDELETE\n```\n\n'
                  '3. Trial B: run once in another blank document; expect `ade` and matching Completed.\n\n'
                  '```ducky\nDELAY 5000\nSTRING abcde\nLEFTARROW\nLEFTARROW\nLEFTARROW\nLEFTARROW\nDEL\nREPEAT 1\n```\n\n'
                  '4. Trial C: on blank TextEdit, submit the source below once. Expect compile failure '
                  'at physical line 2, code 13, and blank TextEdit. Retained malformed source rejects '
                  'before the first STRING executes.\n\n'
                  '```ducky\nSTRING SHOULD_NOT_APPEAR\nDEL extra\n```\n\n'
                  'STOP remains available. Do not automatically retry a failed or ambiguous trial. '
                  'No command above opens a shell, reads host files or accesses passwords.\n\n' + rollback)
    return {'README.md': common + identity + offline + semantics + provenance + rollback +
                         'Read OWNER-CHECK.md, INSTALL-MAC.md and ROLLBACK-MAC.md. The historical rm-*.txt '
                         'fixtures are provenance only; do not execute them for this release.\n',
            'INSTALL-MAC.md': common + identity + offline + provenance + rollback +
                              'Read OWNER-CHECK.md before any separately authorized physical action.\n\n' + future,
            'ROLLBACK-MAC.md': common + rollback + offline + future,
            'OWNER-CHECK.md': acceptance,
            'firmware-report.md': common + identity + provenance + semantics + rollback,
            'compatibility.md': common + semantics + 'Existing H1/right modifiers, lock waits, privacy, '
                                'editor/dashboard/static responses, STOP and EDR1 are retained. Physical '
                                'High Sierra/iPhone acceptance of this candidate remains pending.\n',
            'reproduction.md': common + identity + provenance + offline}


def adapter(binding, attestation_file, test_results_file):
    assert sha(PARENT) == PARENT_SHA and sha(DASHBOARD) == DASHBOARD_SHA
    dashboard = load(DASHBOARD, 'repeat_review_dashboard_parent')
    _, inherited = dashboard.adapter(binding['source_commit'], binding['application_sha256'],
                                     binding['application_bytes'], binding['elf_sha256'], binding['release_receipt_sha256'])
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
    replace('tests/dashboard_cleanup/package_preflight.py', 'tests/del_alias_package/package_preflight.py', 2)
    replace('firmware_build_id=' + repr(dashboard.BUILD_ID) + ',', 'firmware_build_id=' + repr(BUILD_ID) + ',')
    replace('composition_base_commit=' + repr(dashboard.BASE_COMMIT), 'composition_base_commit=' + repr(BASE))
    replace('    for name, source in copies.items():',
            "    copies.update({\n"
            "        'reviewed-editor-source-manifest.json': ROOT/'tests/editor_load_safety/source-manifest.json',\n"
            "        'editor-build-source-manifest.json': ROOT/'tests/editor_build_integration/source-manifest.json',\n"
            "        'response-source-manifest.json': ROOT/'tests/dashboard_response_safety/source-manifest.json',\n"
            "        'static-response-build-source-manifest.json': ROOT/'tests/static_response_build_integration/source-manifest.json',\n"
            "        'previous-repeat-source-manifest.json': ROOT/'tests/previous_command_repeat/source-manifest.json',\n"
            "        'previous-repeat-release-source-manifest.json': ROOT/'tests/previous_command_repeat_release/source-manifest.json',\n"
            "        'del-source-manifest.json': ROOT/'tests/del_alias/source-manifest.json',\n"
            "        'del-release-source-manifest.json': ROOT/'tests/del_alias_release/source-manifest.json',\n"
            "        'del-test-receipt.json': DEL_TEST_FILE,\n"
            "        'build-inputs.json': build_root/'build-inputs.json',\n"
            "        'source-attestation.json': ATTESTATION_FILE,\n"
            "        'native-test-receipt.json': NATIVE_TEST_FILE,\n"
            "        'web-test-receipt.json': WEB_TEST_FILE,\n"
            "        'test-results.json': TEST_RESULTS_FILE})\n"
            '    for name, source in copies.items():')
    # All generated owner-facing documents replace stale inherited copies before
    # support hashes are calculated. No installer construction is adapted.
    replace('    template = ', "    for name, contents in GENERATED_DOCS.items():\n        (out/name).write_text(contents)\n    template = ")
    anchor = "    (out/'preflight.py').write_text("
    replace(anchor,
            "    bound.update({k: v for k, v in FROZEN_BINDING.items() if k != 'source_commit'})\n"
            "    bound.update(firmware_source_commit=FIRMWARE_SOURCE,\n"
            "        editor_pin_sha256=sha(ROOT/'tests/editor_load_safety/source-manifest.json'),\n"
            "        editor_build_pin_sha256=sha(ROOT/'tests/editor_build_integration/source-manifest.json'),\n"
            "        response_pin_sha256=sha(ROOT/'tests/dashboard_response_safety/source-manifest.json'),\n"
            "        static_build_pin_sha256=sha(ROOT/'tests/static_response_build_integration/source-manifest.json'),\n"
            "        repeat_source_pin_sha256=sha(ROOT/'tests/previous_command_repeat/source-manifest.json'),\n"
            "        repeat_release_pin_sha256=sha(ROOT/'tests/previous_command_repeat_release/source-manifest.json'),\n"
            "        del_source_pin_sha256=sha(ROOT/'tests/del_alias/source-manifest.json'),\n"
            "        del_release_pin_sha256=sha(ROOT/'tests/del_alias_release/source-manifest.json'),\n"
            "        repeat_build_adapter_sha256=sha(ROOT/'tests/del_alias_release/build_candidate.py'),\n"
            "        repeat_release_adapter_sha256=sha(ROOT/'tests/del_alias_release/verify_release.py'),\n"
            "        repeat_target_verifier_sha256=sha(ROOT/'tests/del_alias_release/verify_target.py'),\n"
            "        repeat_release_receipt_sha256=RECEIPT_SHA, source_attestation_sha256=sha(ATTESTATION_FILE),\n"
            "        application_elf_sha256=ELF_SHA, application_elf_bytes=FROZEN_BINDING['elf_bytes'])\n" + anchor)
    anchor = "    (out/'manifest.json').write_text("
    replace(anchor,
            "    manifest.update(previous_repeat_profile='PREVIOUS_COMMAND_REPEAT_H1_OWNER_REVIEW',\n"
            "        del_alias_profile='DEL_ALIAS_H1_OWNER_REVIEW',\n"
            "        firmware_source_identity_kind='COMMITTED_CLEAN_BUILD_INPUTS', source_checkpoint_after_build=False,\n"
            "        status_label='NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED', application_elf_bytes=FROZEN_BINDING['elf_bytes'],\n"
            "        reviewed_editor_pin_sha256=sha(out/'reviewed-editor-source-manifest.json'),\n"
            "        editor_build_pin_sha256=sha(out/'editor-build-source-manifest.json'),\n"
            "        response_composition_pin_sha256=sha(out/'response-source-manifest.json'),\n"
            "        static_response_build_pin_sha256=sha(out/'static-response-build-source-manifest.json'),\n"
            "        repeat_source_pin_sha256=sha(out/'previous-repeat-source-manifest.json'),\n"
            "        repeat_release_pin_sha256=sha(out/'previous-repeat-release-source-manifest.json'),\n"
            "        del_source_pin_sha256=sha(out/'del-source-manifest.json'),\n"
            "        del_release_pin_sha256=sha(out/'del-release-source-manifest.json'),\n"
            "        build_inputs_sha256=FROZEN_BINDING['build_inputs_sha256'],\n"
            "        source_attestation_sha256=sha(out/'source-attestation.json'),\n"
            "        verifier_context_commit=FROZEN_BINDING['source_commit'], post_build_verifier_only_delta=False,\n"
            "        previous_faulty_application_sha256='" + FAULTY_SHA + "', previous_faulty_candidate_is_recovery=False)\n" + anchor)
    tests = json.loads(pathlib.Path(test_results_file).read_text()) if pathlib.Path(test_results_file).is_file() else None
    namespace = dict(__name__='repeat_review_frozen_packager', __file__=str(PARENT),
                     GENERATED_DOCS=documents(binding), ATTESTATION_FILE=pathlib.Path(attestation_file),
                     TEST_RESULTS_FILE=pathlib.Path(test_results_file),
                     NATIVE_TEST_FILE=pathlib.Path(tests['groups']['native']['receipt']) if tests else pathlib.Path('/public-native-test-receipt.json'),
                     WEB_TEST_FILE=pathlib.Path(tests['groups']['web']['receipt']) if tests else pathlib.Path('/public-web-test-receipt.json'),
                     DEL_TEST_FILE=pathlib.Path(binding.get('del_test_receipt', '/public-del-test-receipt.json')),
                     FROZEN_BINDING=binding)
    exec(compile(text, str(PARENT), 'exec'), namespace)
    return namespace, inherited, changes


def source_attestation(build_root, binding):
    file = pathlib.Path(build_root) / 'build-inputs.json'
    assert sha(file) == binding['build_inputs_sha256']
    value = json.loads(file.read_text())
    assert value['format'] == 'evilduck-committed-build-inputs-v1'
    assert value['source_commit'] == binding['source_commit'] and value['source_commit_contains_changes'] is True
    assert value['uncommitted_local_changes'] is False
    assert canonical(value['files']) == value['files_sha256'] and len(value['files']) == binding['build_input_count']
    verifier = 'tests/del_alias_release/verify_target.py'
    for row in value['files']:
        relative = pathlib.PurePosixPath(row['file'])
        assert not relative.is_absolute() and '..' not in relative.parts
        path = ROOT / row['file']
        assert path.is_file() and not path.is_symlink() and ROOT in path.resolve().parents
        blob = subprocess.check_output(['git', 'show', binding['source_commit'] + ':' + row['file']], cwd=ROOT)
        assert blob == path.read_bytes() and len(blob) == row['size'] and hashlib.sha256(blob).hexdigest() == row['sha256'], row['file']
    selected = [r for r in value['files'] if r['file'] == verifier]
    assert len(selected) == 1 and selected[0]['sha256'] == sha(ROOT / verifier)
    return dict(format='evilduck-committed-build-source-attestation-v1', source_commit=binding['source_commit'],
                source_commit_contains_changes=True, source_checkpoint_after_build=False,
                git_blobs_verified=True, build_inputs_sha256=sha(file), files=value['files'],
                files_sha256=value['files_sha256'], hardware=False,
                verifier_context_commit=binding['source_commit'], post_build_verifier_delta=None,
                verification_source_policy='SAME_CHECKPOINT_NO_POSTBUILD_DELTA',
                original_compile_input_rows_verified=len(value['files']),
                committed_verifier=selected[0], all_compile_inputs_identical=True)


def prepare(directory, build_root, linked_report, core, source_commit, test_results):
    binding = release_binding()
    for ancestor in [BASE, binding['source_commit']]:
        subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, source_commit], cwd=ROOT, check=True)
    for name in REQUIRED_SOURCE:
        assert subprocess.check_output(['git', 'show', source_commit + ':' + name], cwd=ROOT) == (ROOT / name).read_bytes(), name
    assert sha(test_results) == binding['test_results_sha256']
    tests = json.loads(pathlib.Path(test_results).read_text())
    assert tests['status'] == 'PASS' and tests['target_build'] is False and tests['hardware_access'] is False
    for label in ['native', 'web']:
        assert tests['groups'][label]['exit'] == 0 and not tests['groups'][label]['stderr']
        assert sha(tests['groups'][label]['receipt']) == tests['groups'][label]['receipt_sha256']
    focused = pathlib.Path(binding['del_test_receipt'])
    assert sha(focused) == binding['del_test_receipt_sha256']
    del_tests = json.loads(focused.read_text())
    assert del_tests['status'] == 'PASS' and del_tests['counts']['FAIL'] == 0
    assert del_tests['hardware'] is False and del_tests['real_hid'] is False
    assert del_tests['target_firmware_built'] is False
    target = load(ROOT / 'tests/del_alias_release/verify_target.py', 'repeat_package_exact_target')
    target_binding = target.verify(build_root)
    assert canonical(target_binding) == binding['repeat_target_binding_sha256']
    assert target_binding['committed_source_provenance']['verifier_context_commit'] == binding['source_commit']
    assert target_binding['committed_source_provenance']['post_compile_verifier_delta'] is None
    assert sha(linked_report) == binding['release_receipt_sha256']
    receipt = json.loads(pathlib.Path(linked_report).read_text())
    built = json.loads((pathlib.Path(build_root) / 'report.json').read_text())
    evidence = receipt['del_alias_release_verification']
    assert evidence['status'] == 'PASS' and evidence['full_frozen_h1_chain_executed'] is True
    assert evidence['source_commit'] == binding['source_commit'] and evidence['source_commit_contains_changes'] is True
    assert evidence['build_inputs_sha256'] == binding['build_inputs_sha256']
    assert evidence['application_sha256'] == binding['application_sha256'] and evidence['elf_sha256'] == binding['elf_sha256']
    assert evidence['actual_runtime_build_id'] == receipt['actual_runtime_build_id'] == BUILD_ID
    assert evidence['adapter_sha256'] == sha(ROOT / 'tests/del_alias_release/verify_release.py')
    assert evidence['assertions_preserved'] == 190 and evidence['assertions_removed'] == evidence['unrelated_expected_hashes_changed'] == 0
    assert evidence['historical_source_pin_build_ids_changed'] is False
    assert evidence['recompiled'] is False and evidence['target_source_or_images_modified'] is False
    assert evidence['del_alias_target_binding'] == target_binding == built['del_alias_target_adapter']['del_alias_target_binding']
    assert receipt['del_alias_target_adapter'] == built['del_alias_target_adapter']
    for name in ['source_inventory', 'report', 'provenance']:
        assert receipt[name] == built[name], name
    build = pathlib.Path(build_root) / 'build'
    for name, size_key, hash_key in [('EvilDuckS3.ino.bin', 'application_bytes', 'application_sha256'),
                                    ('EvilDuckS3.ino.elf', 'elf_bytes', 'elf_sha256')]:
        path = build / name
        assert path.stat().st_size == binding[size_key] and sha(path) == binding[hash_key]
    attestation = source_attestation(build_root, binding)
    with tempfile.TemporaryDirectory(prefix='public-repeat-source-attestation-') as temporary:
        path = pathlib.Path(temporary) / 'source-attestation.json'
        path.write_text(json.dumps(attestation, indent=2) + '\n')
        namespace, inherited, changes = adapter(binding, path, test_results)
        manifest = namespace['prepare'](directory, build_root, linked_report, core, source_commit)
    return manifest, inherited, changes


def archive(directory, destination):
    assert sha(PARENT) == PARENT_SHA
    parent = load(PARENT, 'repeat_exact_frozen_archiver')
    return parent.archive(directory, destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['directory', 'build-root', 'linked-report', 'core', 'archive', 'test-results']:
        parser.add_argument('--' + name, type=pathlib.Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    prepare(args.directory, args.build_root, args.linked_report, args.core, args.source_commit, args.test_results)
    namespace, _, _ = adapter(release_binding(), args.directory / 'source-attestation.json', args.test_results)
    print(json.dumps(namespace['archive'](args.directory, args.archive), indent=2))


if __name__ == '__main__':
    raise SystemExit(main())
