#!/usr/bin/env python3
"""Assemble exact existing dashboard images through the frozen H1 packager.

No compiler, network or hardware interface. The public installer and launchers
retain the historical H1 packager's bytes, apart from its new RELEASE_BINDING.
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / 'tests/h1_right_modifiers/package.py'
PARENT_SHA = 'b29c8995bf36668da89e092975c3f83cba7214e33349f12050dde7b82db773b2'
PRIVACY_PACKAGE = ROOT / 'tests/privacy_fix1/package.py'
PRIVACY_PACKAGE_SHA = 'e5261b560c8d8c3f83391cf47a093815f15ceb35fbc2ad327117fef58bbf7ee3'
PACKAGE = 'evilduck-dashboard-diagnostics-cleanup-h1-macos-review-v1'
BUILD_ID = 'ROUTEB-DASHBOARD-CLEANUP-v1'
BASE_COMMIT = '70d08e9f789c187c5e27350a66f4d0d52992964b'
ROLLBACK_SHA = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
ROLLBACK_BYTES = 1413200
REQUIRED_SOURCE = [
    'tests/dashboard_cleanup/' + name for name in
    ['package.py', 'package_preflight.py', 'verify_release.py', 'verify_target.py',
     'build_candidate.py', 'prepare_sources.py', 'startup_decode.py', 'application.patch',
     'source-manifest.json', 'test_dashboard_package.py']
] + ['docs/dashboard-cleanup-' + name for name in
     ['report.md', 'acceptance.md', 'reproduction.md', 'platforms.md', 'browser-results.json']]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def generated_documents(application_sha, application_bytes, firmware_source):
    identity = ('Build ID: `' + BUILD_ID + '`. Application: ' + str(application_bytes) +
                ' bytes; SHA-256 `' + application_sha + '`. Firmware source: `' + firmware_source + '`.\n')
    common = ('**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING.**\n\n'
              'Downloading or checking this package does not authorize device access, installation, boot or testing. '
              'H1 remains opt-in and experimental; canonical Hak5 numeric encoding is unresolved.\n\n')
    rollback = ('The exact older accepted source/text-v2 rollback is a standalone application: **1,413,200 bytes**, '
                'SHA-256 `' + ROLLBACK_SHA + '`. It does not contain Privacy Fix 1 or this dashboard cleanup. '
                'It is not a merged image or a complete recovery set. Preserve every existing backup unchanged.\n\n')
    offline = ('Supported interfaces: macOS High Sierra 10.13.6, Bash 3.2, Python 3.8+ (owner: 3.8.10), '
               'and preinstalled esptool 4.12.0. No dependencies are installed or downloaded. '
               'The first check reads package files only, without USB or network access:\n\n'
               '```bash\npython3 preflight.py --directory .\n```\n\n'
               'Expect exit 0, `package_integrity: PASS`, `installed_metadata: NOT_SUPPLIED`, '
               '`plan_ready: false`, `selected_write_ranges: []`, `hardware_access: false`, '
               'and `installation_authorized: false`. Stop on rejection. '
               'The launcher default is a hardware check, not this offline check.\n\n')
    install = (common + identity + '\n' + offline + rollback +
               'Read OWNER-CHECK.md. Only after separate physical authorization, use the owner-established ROM-entry '
               'procedure and rediscover the current `/dev/cu.usbmodem*` port after reconnects. Do not assume a previous suffix. '
               'The supported board is ESP32-S3 with 16 MiB flash; PSRAM remains disabled.\n\n'
               'The unchanged application-only installer refuses unsupported chip/security/layout/OTA states. '
               'Its future actions are `bash install-macos.sh --action check --port CURRENT_PORT` and, '
               'only when separately authorized, `--action install` with that freshly verified port. '
               'Do not run the placeholder literally. It requires esptool 4.12.0 and owner-controlled ROM mode; '
               'there is no automatic reset, reboot, retry, script Start or HID action.\n\n'
               'Before writing, the existing installer creates a new **private full-flash backup** on the Desktop, '
               'before its final INSTALL confirmation. That backup may include passwords, settings and scripts. '
               'Declining the final confirmation leaves it in place. No existing backup is deleted or overwritten. '
               'Keep the backup and raw local evidence private.\n\n'
               'The reviewed table and narrow app0 OTA initializer must match exactly. The only proposed writes '
               'are the same application in both OTA slots at 0x10000 and 0x750000, bounded by each 0x740000-byte '
               'slot and image-rounded sectors. The manifest gives exact ranges. Bootloader, partition table, '
               'NVS, OTA data, SPIFFS and coredump are excluded. No format, settings reset, repair or metadata rewrite '
               'is provided. A failed write/compare requires stopping in ROM and separate recovery review. '
               'A successful comparison is not a boot or USB test.\n')
    rollback_doc = (common + rollback + offline +
                    'Only after separate authorization, use `bash rollback-macos.sh --port CURRENT_PORT` '
                    'with a freshly rediscovered/verified ROM port. Do not run the placeholder literally. '
                    'The unchanged launcher selects the deliberate rollback action; it never retries or chooses '
                    'rollback automatically. It repeats chip, security, layout, OTA, image and bounded-range checks, '
                    'creates a new private full-flash backup before the final ROLLBACK confirmation, writes the '
                    'exact rollback image to both app slots and compares both. No metadata/data partition write '
                    'or automatic reboot is requested. If an earlier operation failed, remain in ROM and review '
                    'the evidence before any new action.\n')
    readme = (common + identity + '\n' + offline +
              'This additive release moves diagnostic content behind an opt-in Diagnostics area and retains '
              'Privacy Fix 1. Read OWNER-CHECK.md, INSTALL-MAC.md and ROLLBACK-MAC.md. The exact 201-file '
              'composition differs from the privacy base in two files (webfiles.h and the build-ID header); '
              '199 are unchanged. Its cumulative H1 delta is four files, with 197 unchanged. '
              'The historical H1 and privacy source manifests remain separate from the final dashboard manifest.\n\n' +
              rollback + 'The four historical `rm-*.txt` fixtures and owner evidence are provenance only, '
              'not requests to repeat accepted trials. Nothing starts a payload automatically. '
              'No new keyboard behavior or tested LED-protocol change is introduced. Native High Sierra '
              'and physical dashboard behavior remain pending owner review.\n')
    return {'README.md': readme, 'INSTALL-MAC.md': install, 'ROLLBACK-MAC.md': rollback_doc}


def adapter(firmware_source, application_sha, application_bytes, elf_sha, receipt_sha):
    assert sha(PRIVACY_PACKAGE) == PRIVACY_PACKAGE_SHA
    data = PARENT.read_bytes()
    assert hashlib.sha256(data).hexdigest() == PARENT_SHA
    text = data.decode()
    changes = []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace("PACKAGE = 'evilduck-routeb-right-modifiers-h1-experimental-macos-v1'", 'PACKAGE = ' + repr(PACKAGE))
    replace("FIRMWARE_SOURCE = '6d15952e40f9016c4374b8b0403883ebb2290d9a'", 'FIRMWARE_SOURCE = ' + repr(firmware_source))
    replace("APP_SHA = '12134383e75505704d7efebf33cb7b7fdd7bd8f609038fbc575e911a0ad69ca3'", 'APP_SHA = ' + repr(application_sha))
    replace('APP_BYTES = 1414176', 'APP_BYTES = ' + str(application_bytes))
    replace("ELF_SHA = 'b85061de399991f019e364401ef5e23a0c46e1972b34408add2ca886d0f64095'", 'ELF_SHA = ' + repr(elf_sha))
    replace("RECEIPT_SHA = 'f770fd0f49baf3b9d5a9104cd8516bee41ebce682360147dc32e5f52789ac8d1'", 'RECEIPT_SHA = ' + repr(receipt_sha))
    replace('tests/h1_right_modifiers/preflight.py', 'tests/dashboard_cleanup/package_preflight.py', 2)
    for old, new in [('acceptance', 'acceptance'), ('report', 'report'), ('compatibility', 'platforms'), ('reproduction', 'reproduction')]:
        replace('docs/h1-right-modifiers-' + old + '.md', 'docs/dashboard-cleanup-' + new + '.md')
    replace('docs/h1-right-modifiers-test-results.json', 'docs/dashboard-cleanup-browser-results.json')
    replace('    for name, source in copies.items():',
            "    copies['privacy-source-manifest.json'] = ROOT/'tests/privacy_fix1/source-manifest.json'\n"
            "    copies['dashboard-source-manifest.json'] = ROOT/'tests/dashboard_cleanup/source-manifest.json'\n"
            '    for name, source in copies.items():')
    start = text.index("    (out/'README.md').write_text(")
    end = text.index('    template = ', start)
    replace(text[start:end], "    for name, contents in GENERATED_DOCS.items():\n        (out/name).write_text(contents)\n")
    replace('firmware_build_id=BUILD_ID,', 'firmware_build_id=' + repr(BUILD_ID) + ',')
    replace("composition_base_commit='60e94cf987de4420c99f48a93bfef03f5113c82e'", 'composition_base_commit=' + repr(BASE_COMMIT))
    anchor = "    (out/'preflight.py').write_text("
    replace(anchor,
            "    bound.update(privacy_pin_sha256=sha(ROOT/'tests/privacy_fix1/source-manifest.json'),\n"
            "        dashboard_pin_sha256=sha(ROOT/'tests/dashboard_cleanup/source-manifest.json'),\n"
            "        dashboard_build_adapter_sha256=sha(ROOT/'tests/dashboard_cleanup/build_candidate.py'),\n"
            "        dashboard_release_adapter_sha256=sha(ROOT/'tests/dashboard_cleanup/verify_release.py'),\n"
            "        dashboard_target_verifier_sha256=sha(ROOT/'tests/dashboard_cleanup/verify_target.py'),\n"
            "        dashboard_release_receipt_sha256=RECEIPT_SHA)\n" + anchor)
    anchor = "    (out/'manifest.json').write_text("
    replace(anchor,
            "    manifest.update(privacy_base_source_checkpoint_commit='93cc8d1a7b162bdda91e239d840a3eee8a70c51c',\n"
            "        privacy_base_target_integration_commit='0380d1508b8f761e30a6a1fb63f67c2850cbc84a',\n"
            "        privacy_profile='PRIVACY_FIX1_RETAINED_H1_OWNER_REVIEW',\n"
            "        dashboard_profile='DASHBOARD_DIAGNOSTICS_CLEANUP_H1_OWNER_REVIEW',\n"
            "        privacy_composition_pin_sha256=sha(out/'privacy-source-manifest.json'),\n"
            "        dashboard_composition_pin_sha256=sha(out/'dashboard-source-manifest.json'),\n"
            "        runtime_build_id_distinguishes_candidate=True, rollback_is_privacy_patched=False,\n"
            '        packaging_parent_sha256=' + repr(PARENT_SHA) + ')\n' + anchor)
    namespace = dict(__name__='dashboard_package_parent', __file__=str(PARENT),
                     GENERATED_DOCS=generated_documents(application_sha, application_bytes, firmware_source))
    exec(compile(text, str(PARENT), 'exec'), namespace)
    return namespace, changes


def prepare(directory, build_root, linked_report, core, source_commit):
    from verify_target import verify
    build_root, linked_report = pathlib.Path(build_root).resolve(), pathlib.Path(linked_report).resolve()
    assert re.fullmatch('[0-9a-f]{40}', source_commit)
    receipt = json.loads(linked_report.read_text())
    evidence = receipt['dashboard_release_verification']
    firmware_source = evidence['source_commit']
    assert re.fullmatch('[0-9a-f]{40}', firmware_source)
    for ancestor in (BASE_COMMIT, firmware_source):
        subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, source_commit], cwd=ROOT, check=True)
    for name in REQUIRED_SOURCE:
        assert subprocess.check_output(['git', 'show', source_commit + ':' + name], cwd=ROOT) == (ROOT / name).read_bytes(), name
    built = json.loads((build_root / 'report.json').read_text())
    binding = verify(build_root)
    assert evidence['status'] == 'PASS' and evidence['full_frozen_h1_chain_executed'] is True
    assert evidence['adapter_sha256'] == sha(ROOT / 'tests/dashboard_cleanup/verify_release.py')
    assert evidence['assertions_preserved'] == 190 and evidence['assertions_removed'] == evidence['unrelated_expected_hashes_changed'] == 0
    assert evidence['historical_source_pin_build_ids_changed'] is False
    assert evidence['recompiled'] is False and evidence['target_source_or_images_modified'] is False
    assert evidence['actual_runtime_build_id'] == receipt['actual_runtime_build_id'] == BUILD_ID
    assert evidence['base_commit'] == BASE_COMMIT and evidence['dashboard_target_binding'] == binding
    assert built['dashboard_target_adapter']['source_commit'] == firmware_source
    assert built['dashboard_target_adapter'] == receipt['dashboard_target_adapter']
    assert receipt['source_inventory'] == built['source_inventory']
    assert receipt['report'] == built['report'] and receipt['provenance'] == built['provenance']
    assert receipt['dashboard_source_pin'] == json.loads((ROOT / 'tests/dashboard_cleanup/source-manifest.json').read_text())
    assert receipt['privacy_source_pin'] == json.loads((ROOT / 'tests/privacy_fix1/source-manifest.json').read_text())
    assert evidence['source_manifest_sha256'] == sha(ROOT / 'tests/dashboard_cleanup/source-manifest.json')
    assert evidence['privacy_source_manifest_sha256'] == sha(ROOT / 'tests/privacy_fix1/source-manifest.json')
    namespace, changes = adapter(firmware_source, evidence['application_sha256'],
                                 receipt['report']['application_bytes'], evidence['elf_sha256'], sha(linked_report))
    manifest = namespace['prepare'](directory, build_root, linked_report, core, source_commit)
    return manifest, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['directory', 'build-root', 'linked-report', 'core', 'archive']:
        parser.add_argument('--' + name, required=True, type=pathlib.Path)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    manifest, _ = prepare(args.directory, args.build_root, args.linked_report, args.core, args.source_commit)
    namespace, _ = adapter(manifest['firmware_source_commit'], manifest['application_sha256'],
                           manifest['application_bytes'], manifest['application_elf_sha256'], sha(args.linked_report))
    print(json.dumps(namespace['archive'](args.directory, args.archive), indent=2))


if __name__ == '__main__':
    main()
