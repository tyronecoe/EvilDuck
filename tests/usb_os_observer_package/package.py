# USB enumeration observer capture package over immutable DEFINE parent c093b0151d16ed1f0b84c6d4a884ac9d0c12a2739fd1c9c39593f4b25647613e
# Bounded DEFINE-label package over immutable DEL parent 916bf5b49984aa3394fe39ba313d30430ed7b115b108e60a2ddf0049560ee022
# Additive DEL-alias review package; immutable REPEAT parent 7d229d6b648211f59c05479d356fbdf0a7930e6d2637768720a5383ce93c3f34
#!/usr/bin/env python3
"""Capture-only USB observer package around the frozen guarded Mac installer.

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
import io
import zipfile
import stat

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ROOT / 'tests/h1_right_modifiers/package.py'
PARENT_SHA = 'b29c8995bf36668da89e092975c3f83cba7214e33349f12050dde7b82db773b2'
DASHBOARD = ROOT / 'tests/dashboard_cleanup/package.py'
DASHBOARD_SHA = 'e696ed2dcb7bea8d8cf0057e526ac86e1f283bcc0116b99fe597459493d82efa'
PACKAGE = 'evilduck-routeb-usb-enum-observer-h1-macos-review-v1'
BUILD_ID = 'ROUTEB-USB-ENUM-OBSERVER-H1-v1'
BASE = 'bdc8cbeea024ebb63f952da7fc4f39ac9e32fe29'
ROLLBACK_SHA = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
ROLLBACK_BYTES = 1413200
FAULTY_SHA = 'e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0'
OLD_STATIC_SHA = 'd5fe0932fe915443a5e53030969c6792409f719d427681304a7102355b2d7946'
OLD_REPEAT_SHA = '13cec88262afdfa641eb0fb4927fe7903abf2863295344ff316418707ba49b7f'
OLD_DEL_SHA = 'd1571be81619e464ee997d0ba8ebbf7e7b8a8b4252e4debc9d9144b9ebe6b379'
OLD_DEFINE_SHA = '167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30'
WORKING_ZIP = ROOT / 'downloads/evilduck-routeb-define-labels-h1-macos-review-v1.zip'
WORKING_ZIP_FILE = 'working-define-labels-macos-review-v1.zip'
WORKING_ZIP_SHA = 'b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed'
WORKING_ZIP_BYTES = 2691374
WORKING_APP_SHA = OLD_DEFINE_SHA
WORKING_APP_BYTES = 1438048
DEFINE_PACKAGE_PINS = {n: expected for n, expected in [
    ('package.py', 'c093b0151d16ed1f0b84c6d4a884ac9d0c12a2739fd1c9c39593f4b25647613e'),
    ('package_preflight.py', '5fbe1fa388759810f40bceeb2dbaa3d16efe633352364ec4ae550ddd12fecfd7'),
    ('test_package.py', '855aef453aae86a0ff109567552a04d2b35a3cc14a52e79ba82a18a4419c3b40'),
]}
HISTORICAL_PACKAGE_PINS = {
    'package.py': '7d229d6b648211f59c05479d356fbdf0a7930e6d2637768720a5383ce93c3f34',
    'package_preflight.py': 'd095130bfb73d75ab708be338df97739227f129cecfe2a4fb60226a94f71ab29',
    'test_package.py': '9e8047b2fef5f3210f637f7b32d41dc745a00840c05d57c9fe472ccbb0d2b168',
}
DEL_PACKAGE_PINS = {'package.py': '916bf5b49984aa3394fe39ba313d30430ed7b115b108e60a2ddf0049560ee022',
                    'package_preflight.py': '241b40e3f8284615cca8bd870022754039024a3d4d5e8316535fac5118f3b50d',
                    'test_package.py': 'f298b79278f3fdcf3325a6a75541181ea0da689c032f24417c6ef3cf9d704e5d'}
REQUIRED_SOURCE = ['tests/usb_os_observer_package/' + n for n in
                   ['package.py', 'package_preflight.py', 'test_package.py', 'release-binding.json']] + [
                   'docs/del-alias-owner-closeout.md',
                   'docs/define-labels-owner-fixtures/D01_DEFINE_27.txt',
                   'docs/define-labels-owner-fixtures/D02_DEFINE_31.txt',
                   'docs/define-labels-owner-fixtures/D03_DEFINE_32_Rejected.txt', 'docs/usb-os-observer-contract.md', 'docs/usb-os-evidence-gate.json', 'docs/define-labels-owner-acceptance.md', 'downloads/evilduck-routeb-define-labels-h1-macos-review-v1.zip']


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
    for name, expected in DEL_PACKAGE_PINS.items():
        assert sha(ROOT / 'tests/del_alias_package' / name) == expected
    for name, expected in DEFINE_PACKAGE_PINS.items():
        assert sha(ROOT / 'tests/define_labels_package' / name) == expected
    value = json.loads((HERE / 'release-binding.json').read_text())
    assert value['format'] == 'evilduck-usb-observer-release-binding-v1'
    assert value['status'] == 'VERIFIED_LOCAL_RELEASE', 'Actual new image verification required'
    assert value['build_id'] == BUILD_ID
    assert re.fullmatch('[0-9a-f]{40}', value['source_commit'])
    assert value['verifier_context_commit'] == value['source_commit']
    assert value['post_compile_verifier_delta'] is None
    for key in ['application_sha256', 'elf_sha256', 'release_receipt_sha256',
                'build_inputs_sha256', 'repeat_target_binding_sha256', 'test_results_sha256',
                'del_core_sha256', 'del_shortcuts_sha256', 'del_test_receipt_sha256',
                'define_core_sha256', 'define_test_receipt_sha256', 'observer_test_receipt_sha256', 'observer_web_test_receipt_sha256']:
        assert re.fullmatch('[0-9a-f]{64}', value[key]), key
    assert value['application_sha256'] not in (FAULTY_SHA, OLD_STATIC_SHA, OLD_REPEAT_SHA, OLD_DEL_SHA, OLD_DEFINE_SHA, ROLLBACK_SHA)
    assert value['application_bytes'] > 0 and value['elf_bytes'] > 0
    assert isinstance(value['build_input_count'], int) and value['build_input_count'] > 26
    return value


def documents(binding):
    common = ('**CAPTURE-ONLY REVIEW CANDIDATE — NOT INSTALLED — NO VALIDATED OS RULE.**\n\n'
              'This is the single authorized evidence-gathering stage, not an OS detector release. '
              'It never reports a positive OS classification, starts a payload automatically or changes USB identity. '
              'H1 remains opt-in and experimental; canonical Hak5 numeric encoding remains unresolved.\n\n')
    identity = ('Build ID: `' + BUILD_ID + '`. Capture application: **' + str(binding['application_bytes']) +
                ' bytes**, SHA-256 `' + binding['application_sha256'] + '`. Firmware checkpoint: `' +
                binding['source_commit'] + '`. This is an artifact identity, not installed device readback.\n\n')
    offline = ('Keep EvilDuck **unplugged**, extract into a new folder and run only:\n\n'
               '```bash\npython3 preflight.py --directory .\n```\n\n'
               'Expect integrity PASS, exit 0, `plan_ready: false`, empty write ranges, '
               '`installed_metadata: NOT_SUPPLIED`, and hardware/installation authorization false. '
               'The offline checker validates the nested working-return ZIP without executing it or contacting hardware.\n\n')
    rollback = ('The older source/text-v2 rollback remains **1,413,200 bytes**, SHA-256 `' + ROLLBACK_SHA + '`. '
                'It lacks later privacy/dashboard repairs and is not a full-device/filesystem restore. '
                'The e825 editor-safety candidate is not a known-good recovery image. Preserve every existing backup.\n\n')
    working = ('**Return to your working firmware:** `working-define-labels-macos-review-v1.zip` is the original '
               'unchanged DEFINE package, **2,691,374 bytes**, SHA-256 `' + WORKING_ZIP_SHA + '`. '
               'It contains working application `ROUTEB-DEFINE-LABELS-H1-v1`, **1,438,048 bytes**, SHA-256 `' +
               WORKING_APP_SHA + '`. This WORKING_DEFINE_RETURN role is distinct from the older rollback above. '
               'Extract that nested ZIP into a separate new folder, keep the board unplugged, and run its existing '
               '`python3 preflight.py --directory .`. For a later deliberate owner return, follow the unchanged kit '
               'INSTALL-MAC.md using the established ROM-entry and rediscovered-port procedure. The action is the '
               'existing guarded install of the known working image; no new return/flash option is invented. '
               'Do not run `rollback-macos.sh` expecting the DEFINE image: that selects the older source/text-v2 image. '
               'If capture is inconclusive or keyboard behavior regresses, stop and use this working-return path. '
               'No automatic return, erase, format or settings reset occurs.\n\n')
    safety = ('The supported host remains Intel macOS High Sierra 10.13.6, Bash 3.2, Python 3.8+ and preinstalled '
              'esptool 4.12. Use only the unchanged installer instructions; no dependency downloads occur. '
              'It refuses unsupported chip, security, partition and OTA states. It creates a new **private full-flash '
              'backup before its final INSTALL confirmation** (or ROLLBACK confirmation); that file may contain '
              'credentials, settings and scripts and remains if confirmation is declined. No existing backup is '
              'deleted or overwritten. Writes remain limited to the two application regions at 0x10000 and '
              '0x750000; bootloader, partition table, NVS, OTA metadata and filesystems are excluded. '
              'No automatic reboot, retry or payload start occurs.\n\n')
    provenance = ('The committed source, actual ELF/application, linked wrapper, unchanged descriptors/dependencies '
                  'and full inherited 190-assert release chain are bound in build-receipt.json and source-attestation.json. '
                  'There is no post-compilation verifier delta. Native/mock results are software evidence; they do not '
                  'establish actual USB capture or detection accuracy.\n\n')
    launch = ('Read OWNER-CHECK.md before any separately owner-operated physical action. Use the established '
              'ROM-entry procedure and rediscover the current `/dev/cu.usbmodem*` port after reconnecting. '
              'Future commands are `bash install-macos.sh --action check --port CURRENT_PORT`, then separately '
              '`bash install-macos.sh --action install --port CURRENT_PORT`. Deliberate older rollback uses '
              '`bash rollback-macos.sh --port CURRENT_PORT`. Never run the placeholder literally. These '
              'commands contact hardware and are not the offline preflight above. Hardware compatibility remains '
              'ESP32-S3 with 16 MiB flash and PSRAM disabled. The source-stage label '
              '`ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1` is historical provenance, not this candidate build ID.\n\n')
    capture = ('The observer records at most 64 whitelisted USB request headers and lifecycle/session boundaries '
               'in RAM during five seconds from its first foreground service, preserving the bounded early-boot prefix captured before Arduino setup. '
               'It captures request type/code, wValue, wIndex, wLength and ordering, not payload bodies, string/descriptor '
               'contents, HID report contents, keystrokes, host files or credentials. Overflow, incomplete capture, '
               'generation mismatch and missing data remain UNKNOWN. No counter threshold, missing LED or known-Mac '
               'connection is used to guess an OS. Captures are not uploaded automatically or learned persistently.\n\n')
    owner = (common + identity + 'Use only after a separately owner-operated installation. No physical operation '
             'or automatic payload execution is part of package preparation. Read the frozen capture contract first.\n\n' +
             '1. Confirm and record the actual running capture build ID. Connect the known High Sierra Mac using '
             'the ordinary working USB identity. Allow the bounded capture to finish; do not run an OS probe or '
             'alter lock states to force a signature.\n'
             '2. In the authenticated dashboard, open Diagnostics > USB enumeration observations and choose View or Download JSON. This requests GET '
             '`/routeb/usb-observations`. Save the returned metadata as session A. A visible UNKNOWN label is '
             'expected: this stage has no validated rule. Do not put passwords in a URL or publish private backups.\n'
             '3. Perform one fresh enumeration with the same observer image, rejoin EvilDuck Wi-Fi if USB power was removed, and save session B. Record which '
             'known Mac/OS and connection path were used, actual build ID, generation and any incomplete/overflow '
             'flags. No second observer firmware or larger campaign is assumed. Session B is held out from rule '
             'development: preserve B unchanged locally and provide A first. Freeze a proposed rule and its '
             'independent justification before examining or using B for validation. If B is used to develop a '
             'rule, it is not held-out evidence. Two captures of one Mac do not establish accuracy on other '
             'operating systems.\n'
             '4. Only if needed to check ordinary keyboard operation, use blank plain-text TextEdit and one '
             'existing benign text command; record matching request status and visible text. Do not repeat DEL, '
             'DEFINE, H1 or lock-wait campaigns. STOP remains available.\n\n'
             'Preserve the raw metadata and unexpected observations. Do not repair output or automatically retry '
             'ambiguous results. If the evidence remains inconclusive, report that clearly and return to working '
             'DEFINE firmware. A complete detector-and-branching package is produced only if the evidence supports '
             'a positive rule; an always-UNKNOWN result is not advertised as a completed detector.\n\n' + working + rollback)
    return {'README.md': common + identity + offline + capture + working + rollback +
                         'Read OWNER-CHECK.md, CAPTURE-CONTRACT.md, RETURN-WORKING.md and INSTALL-MAC.md. '
                         'Historical rm-*.txt/DEFINE fixtures are provenance only; do not execute them for capture.\n',
            'INSTALL-MAC.md': common + identity + offline + provenance + safety + launch + working + rollback,
            'ROLLBACK-MAC.md': common + rollback + offline + safety + launch + working,
            'RETURN-WORKING.md': common + working + offline + safety + rollback,
            'OWNER-CHECK.md': owner,
            'firmware-report.md': common + identity + provenance + capture + working + rollback,
            'compatibility.md': common + capture + 'Existing keyboard behavior, STOP/cleanup, privacy, LED protocol, '
                                'DEL, DEFINE and H1 are retained. No OS detector, new USB identity, mode or active probe is added.\n',
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
    replace('tests/dashboard_cleanup/package_preflight.py', 'tests/usb_os_observer_package/package_preflight.py', 2)
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
            "        'define-source-manifest.json': ROOT/'tests/define_labels/source-manifest.json',\n"
            "        'define-release-source-manifest.json': ROOT/'tests/define_labels_release/source-manifest.json',\n"
            "        'define-test-receipt.json': DEFINE_TEST_FILE,\n"
            "        'observer-source-manifest.json': ROOT/'tests/usb_os_observer/source-manifest.json',\n"
            "        'observer-web-source-manifest.json': ROOT/'tests/usb_os_observer_web/source-manifest.json',\n"
            "        'observer-release-source-manifest.json': ROOT/'tests/usb_os_observer_release/source-manifest.json',\n"
            "        'observer-test-receipt.json': OBSERVER_TEST_FILE,\n"
            "        'observer-web-test-receipt.json': OBSERVER_WEB_TEST_FILE,\n"
            "        'CAPTURE-CONTRACT.md': ROOT/'docs/usb-os-observer-contract.md',\n"
            "        'evidence-gate.json': ROOT/'docs/usb-os-evidence-gate.json',\n"
            "        'define-owner-acceptance.md': ROOT/'docs/define-labels-owner-acceptance.md',\n"
            "        'working-define-labels-macos-review-v1.zip': WORKING_ZIP,\n"
            "        'D01_DEFINE_27.txt': ROOT/'docs/define-labels-owner-fixtures/D01_DEFINE_27.txt',\n"
            "        'D02_DEFINE_31.txt': ROOT/'docs/define-labels-owner-fixtures/D02_DEFINE_31.txt',\n"
            "        'D03_DEFINE_32_Rejected.txt': ROOT/'docs/define-labels-owner-fixtures/D03_DEFINE_32_Rejected.txt',\n"
            "        'del-owner-closeout.md': ROOT/'docs/del-alias-owner-closeout.md',\n"
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
            "        define_source_pin_sha256=sha(ROOT/'tests/define_labels/source-manifest.json'),\n"
            "        define_release_pin_sha256=sha(ROOT/'tests/define_labels_release/source-manifest.json'),\n"
            "        observer_source_pin_sha256=sha(ROOT/'tests/usb_os_observer/source-manifest.json'),\n"
            "        observer_web_pin_sha256=sha(ROOT/'tests/usb_os_observer_web/source-manifest.json'),\n"
            "        observer_release_pin_sha256=sha(ROOT/'tests/usb_os_observer_release/source-manifest.json'),\n"
            "        del_source_pin_sha256=sha(ROOT/'tests/del_alias/source-manifest.json'),\n"
            "        del_release_pin_sha256=sha(ROOT/'tests/del_alias_release/source-manifest.json'),\n"
            "        repeat_build_adapter_sha256=sha(ROOT/'tests/usb_os_observer_release/build_candidate.py'),\n"
            "        repeat_release_adapter_sha256=sha(ROOT/'tests/usb_os_observer_release/verify_release.py'),\n"
            "        repeat_target_verifier_sha256=sha(ROOT/'tests/usb_os_observer_release/verify_target.py'),\n"
            "        repeat_release_receipt_sha256=RECEIPT_SHA, source_attestation_sha256=sha(ATTESTATION_FILE),\n"
            "        application_elf_sha256=ELF_SHA, application_elf_bytes=FROZEN_BINDING['elf_bytes'])\n" + anchor)
    anchor = "    (out/'manifest.json').write_text("
    replace(anchor,
            "    manifest.update(previous_repeat_profile='PREVIOUS_COMMAND_REPEAT_H1_OWNER_REVIEW',\n"
            "        del_alias_profile='DEL_ALIAS_H1_OWNER_REVIEW', define_labels_profile='DEFINE_LABELS_H1_OWNER_REVIEW',\n"
            "        define_source_pin_sha256=sha(out/'define-source-manifest.json'),\n"
            "        define_release_pin_sha256=sha(out/'define-release-source-manifest.json'),\n"
            "        usb_observer_profile='USB_ENUM_OBSERVER_CAPTURE_ONLY', classifier_implemented=False,\n"
            "        observer_source_pin_sha256=sha(out/'observer-source-manifest.json'),\n"
            "        observer_web_pin_sha256=sha(out/'observer-web-source-manifest.json'),\n"
            "        observer_release_pin_sha256=sha(out/'observer-release-source-manifest.json'),\n"
            "        working_firmware_return=WORKING_RETURN_IDENTITY,\n"
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
                     DEFINE_TEST_FILE=pathlib.Path(binding.get('define_test_receipt', '/public-define-test-receipt.json')),
                     OBSERVER_TEST_FILE=pathlib.Path(binding.get('observer_test_receipt', '/public-observer-test-receipt.json')),
                     OBSERVER_WEB_TEST_FILE=pathlib.Path(binding.get('observer_web_test_receipt', '/public-observer-web-test-receipt.json')),
                     WORKING_ZIP=WORKING_ZIP, WORKING_RETURN_IDENTITY=working_identity(),
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
    verifier = 'tests/usb_os_observer_release/verify_target.py'
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


def working_identity():
    return dict(role='WORKING_DEFINE_RETURN', file=WORKING_ZIP_FILE, bytes=WORKING_ZIP_BYTES,
                sha256=WORKING_ZIP_SHA, build_id='ROUTEB-DEFINE-LABELS-H1-v1',
                application_bytes=WORKING_APP_BYTES, application_sha256=WORKING_APP_SHA,
                older_rollback_sha256=ROLLBACK_SHA,
                method='EXTRACT_SEPARATE_FOLDER_AND_USE_UNCHANGED_GUARDED_KIT')


def verify_working_kit():
    assert WORKING_ZIP.is_file() and not WORKING_ZIP.is_symlink()
    raw = WORKING_ZIP.read_bytes()
    assert len(raw) == WORKING_ZIP_BYTES and hashlib.sha256(raw).hexdigest() == WORKING_ZIP_SHA
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert archive.testzip() is None and len(archive.infolist()) == 50
        for row in archive.infolist():
            selected = pathlib.PurePosixPath(row.filename)
            assert not selected.is_absolute() and '..' not in selected.parts and not stat.S_ISLNK(row.external_attr >> 16)
        app = archive.read('application.bin')
        rollback = archive.read('rollback-application.bin')
        assert len(app) == WORKING_APP_BYTES and hashlib.sha256(app).hexdigest() == WORKING_APP_SHA
        assert len(rollback) == ROLLBACK_BYTES and hashlib.sha256(rollback).hexdigest() == ROLLBACK_SHA
        manifest = json.loads(archive.read('manifest.json'))
        assert manifest['firmware_build_id'] == 'ROUTEB-DEFINE-LABELS-H1-v1'
        for name in ['preflight.py', 'installer.py', 'install-macos.sh', 'rollback-macos.sh', 'INSTALL-MAC.md']:
            data = archive.read(name)
            assert len(data) == manifest['support_files'][name]['bytes']
            assert hashlib.sha256(data).hexdigest() == manifest['support_files'][name]['sha256']
    return working_identity()


def prepare(directory, build_root, linked_report, core, source_commit, test_results):
    binding = release_binding()
    verify_working_kit()
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
    define_focused = pathlib.Path(binding['define_test_receipt'])
    assert sha(define_focused) == binding['define_test_receipt_sha256']
    define_tests = json.loads(define_focused.read_text())
    assert define_tests['status'] == 'PASS' and define_tests['counts']['FAIL'] == 0
    assert define_tests['hardware'] is False and define_tests['real_hid'] is False
    assert define_tests['target_firmware_built'] is False
    for file_key, hash_key in [('observer_test_receipt', 'observer_test_receipt_sha256'),
                               ('observer_web_test_receipt', 'observer_web_test_receipt_sha256')]:
        selected = pathlib.Path(binding[file_key])
        assert sha(selected) == binding[hash_key]
        value = json.loads(selected.read_text())
        assert value.get('status') == 'PASS' and value.get('counts', {}).get('FAIL') == 0
        assert value.get('hardware', value.get('hardware_access')) is False
        assert value.get('real_hid', False) is False
    target = load(ROOT / 'tests/usb_os_observer_release/verify_target.py', 'repeat_package_exact_target')
    target_binding = target.verify(build_root)
    assert canonical(target_binding) == binding['repeat_target_binding_sha256']
    assert target_binding['committed_source_provenance']['verifier_context_commit'] == binding['source_commit']
    assert target_binding['committed_source_provenance']['post_compile_verifier_delta'] is None
    assert sha(linked_report) == binding['release_receipt_sha256']
    receipt = json.loads(pathlib.Path(linked_report).read_text())
    built = json.loads((pathlib.Path(build_root) / 'report.json').read_text())
    evidence = receipt['usb_observer_release_verification']
    assert evidence['status'] == 'PASS' and evidence['full_frozen_h1_chain_executed'] is True
    assert evidence['source_commit'] == binding['source_commit'] and evidence['source_commit_contains_changes'] is True
    assert evidence['build_inputs_sha256'] == binding['build_inputs_sha256']
    assert evidence['application_sha256'] == binding['application_sha256'] and evidence['elf_sha256'] == binding['elf_sha256']
    assert evidence['actual_runtime_build_id'] == receipt['actual_runtime_build_id'] == BUILD_ID
    assert evidence['adapter_sha256'] == sha(ROOT / 'tests/usb_os_observer_release/verify_release.py')
    assert evidence['assertions_preserved'] == 190 and evidence['assertions_removed'] == evidence['unrelated_expected_hashes_changed'] == 0
    assert evidence['historical_source_pin_build_ids_changed'] is False
    assert evidence['recompiled'] is False and evidence['target_source_or_images_modified'] is False
    assert evidence['usb_observer_target_binding'] == target_binding == built['usb_observer_target_adapter']['usb_observer_target_binding']
    assert receipt['usb_observer_target_adapter'] == built['usb_observer_target_adapter']
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
