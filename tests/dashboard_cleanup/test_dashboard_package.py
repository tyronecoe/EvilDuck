#!/usr/bin/env python3
"""Focused package policy and disposable public-package semantic checks.

No firmware compiler, network, device, esptool dispatch or owner files.
"""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
import pathlib
import re
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
ROLLBACK_SHA = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
PRIOR_ZIP_SHA = '6fff7825d25df3288beb8975abbd56f464bf5ccc81a5c680fa6f5ccf7b2940cf'
BUILD_ID = 'ROUTEB-DASHBOARD-CLEANUP-v1'
PACKAGE = 'evilduck-dashboard-diagnostics-cleanup-h1-macos-review-v1'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackagePolicy(unittest.TestCase):
    def test_pinned_packager_keeps_historical_h1_metadata(self):
        pack = load(HERE / 'package.py', 'dashboard_packaging_policy')
        namespace, changes = pack.adapter('0' * 40, '1' * 64, 123, '2' * 64, '3' * 64)
        self.assertEqual(namespace['BUILD_ID'], 'ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1')
        self.assertEqual(namespace['PACKAGE'], PACKAGE)
        self.assertEqual(namespace['ROLLBACK_SHA'], ROLLBACK_SHA)
        self.assertEqual(namespace['ROLLBACK_BYTES'], 1413200)
        self.assertEqual(namespace['APP_SHA'], '1' * 64)
        self.assertEqual(namespace['APP_BYTES'], 123)
        self.assertEqual(len(changes), 18)

    def test_inherited_h1_preflight_guards_unchanged_except_three_explicit_fields(self):
        parent = (ROOT / 'tests/privacy_fix1/package_preflight.py').read_text()
        actual = (HERE / 'package_preflight.py').read_text()
        inherited = parent[parent.index('import argparse'):parent.index(' # Additional privacy identity checks;')]
        inherited = inherited.replace("'evilduck-privacy-fix1-h1-macos-review-v1'", repr(PACKAGE))
        inherited = inherited.replace("'privacy-source-manifest.json'}", "'privacy-source-manifest.json','dashboard-source-manifest.json'}")
        inherited = inherited.replace("m.get('firmware_build_id')=='ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1'", "m.get('firmware_build_id')=='" + BUILD_ID + "'")
        self.assertEqual(actual[actual.index('import argparse'):actual.index(' # Retained privacy source-layer provenance,')], inherited)
        self.assertEqual(actual[actual.index(' rollback_receipt='):], parent[parent.index(' rollback_receipt='):])

    def test_no_new_installer_or_launcher_behavior(self):
        pack = load(HERE / 'package.py', 'dashboard_packaging_installer_policy')
        _, changes = pack.adapter('0' * 40, '1' * 64, 123, '2' * 64, '3' * 64)
        self.assertFalse(any("original =" in row['before'] or "for name in ('install-macos.sh'" in row['before'] for row in changes))
        self.assertFalse(any('tool_process' in row['before'] or 'RELEASE_BINDING' in row['before'] for row in changes))

    def test_generated_docs_are_offline_first_and_clear_about_private_backup(self):
        pack = load(HERE / 'package.py', 'dashboard_packaging_docs_policy')
        docs = pack.generated_documents('1' * 64, 123, '0' * 40)
        self.assertEqual(set(docs), {'README.md', 'INSTALL-MAC.md', 'ROLLBACK-MAC.md'})
        for text in docs.values():
            self.assertIn('python3 preflight.py --directory .', text)
            self.assertIn(ROLLBACK_SHA, text)
            self.assertNotIn('?pw=', text)
        self.assertIn('before its final INSTALL confirmation', docs['INSTALL-MAC.md'])
        self.assertIn('provenance only', docs['README.md'])

    def test_final_sources_are_two_and_199_without_relabeling_privacy_base(self):
        preflight = load(HERE / 'package_preflight.py', 'dashboard_preflight_policy')
        self.assertIn('privacy-source-manifest.json', preflight.SUPPORT)
        self.assertIn('dashboard-source-manifest.json', preflight.SUPPORT)
        self.assertEqual(preflight.ROLLBACK_BYTES, 1413200)
        self.assertEqual(preflight.ROLLBACK_SHA, ROLLBACK_SHA)
        source = (HERE / 'package_preflight.py').read_text()
        self.assertIn("dashboard_binding.get('dashboard_files')==2", source)
        self.assertIn("dashboard_binding.get('unchanged_files')==199", source)
        self.assertIn("dashboard_binding.get('cumulative_h1_changed_files')==4", source)
        self.assertIn("dashboard_binding.get('cumulative_h1_unchanged_files')==197", source)
        self.assertIn('WRONG_PRIVACY_BASE_SOURCE_DELTA', source)

    def test_python38_syntax_and_bound_receipt_required(self):
        for filename in ['package.py', 'package_preflight.py', 'test_dashboard_package.py']:
            ast.parse((HERE / filename).read_text(), feature_version=(3, 8))
        self.assertIn("RELEASE['dashboard_release_receipt_sha256']", (HERE / 'package_preflight.py').read_text())


def full_checks(original, result_path):
    original = original.resolve()
    release = load(original / 'preflight.py', 'dashboard_package_under_test')
    before = {p.name: digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    results = []
    with tempfile.TemporaryDirectory(prefix='public-dashboard-package-tests-') as temporary:
        directory = pathlib.Path(temporary) / 'public'
        shutil.copytree(original, directory)
        saved = {p.name: p.read_bytes() for p in directory.iterdir()}

        def restore():
            for path in directory.iterdir():
                if path.name not in saved:
                    if path.is_dir() and not path.is_symlink():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            for name, data in saved.items():
                path = directory / name
                if not path.exists() or path.read_bytes() != data:
                    path.write_bytes(data)

        def case(name, operation):
            try:
                operation()
                results.append(dict(name=name, status='PASS'))
                print('PASS', name)
            except Exception as error:
                results.append(dict(name=name, status='FAIL', diagnostic=type(error).__name__ + ': ' + str(error)))
                print('FAIL', name, type(error).__name__)
            finally:
                restore()

        def rejected(expected):
            try:
                release.validate(directory)
            except (ValueError, KeyError, OSError) as error:
                assert expected in str(error), (expected, str(error))
                return
            raise AssertionError('Unsafe dashboard package metadata accepted')

        def manifest_change(change, expected):
            path = directory / 'manifest.json'
            record = json.loads(path.read_text())
            change(record)
            path.write_text(json.dumps(record))
            rejected(expected)

        def support_change(name, data):
            (directory / name).write_bytes(data)
            manifest = json.loads((directory / 'manifest.json').read_text())
            manifest['support_files'][name] = dict(bytes=len(data), sha256=digest(data))
            (directory / 'manifest.json').write_text(json.dumps(manifest))

        def receipt_change(change, expected):
            record = json.loads((directory / 'build-receipt.json').read_text())
            change(record)
            support_change('build-receipt.json', json.dumps(record).encode())
            rejected(expected)

        def positive():
            result = release.validate(directory)
            assert result['package_integrity'] == 'PASS' and result['plan_ready'] is False
            assert result['selected_write_ranges'] == [] and result['hardware_access'] is False and result['installation_authorized'] is False
            app, rollback = [(directory / name).read_bytes() for name in ['application.bin', 'rollback-application.bin']]
            assert len(app) == release.APP_BYTES and digest(app) == release.APP_SHA
            assert len(rollback) == 1413200 and digest(rollback) == ROLLBACK_SHA
            manifest = json.loads((directory / 'manifest.json').read_text())
            assert manifest['package_id'] == PACKAGE and manifest['firmware_build_id'] == BUILD_ID
            assert manifest['runtime_build_id_distinguishes_candidate'] is True and manifest['rollback_is_privacy_patched'] is False

        case('exact_dashboard_application_and_exact_older_rollback_no_hardware_or_plan', positive)

        def unchanged_installer_launchers_and_fixtures():
            prior = ROOT / 'downloads/evilduck-privacy-fix1-h1-macos-review-v1.zip'
            assert digest(prior.read_bytes()) == PRIOR_ZIP_SHA
            normalize = lambda data: re.sub(rb'^RELEASE_BINDING=.*$', b'RELEASE_BINDING=BOUND_RELEASE_IDENTITY', data, flags=re.M)
            with zipfile.ZipFile(prior) as archive:
                assert archive.testzip() is None
                assert normalize((directory / 'installer.py').read_bytes()) == normalize(archive.read('installer.py'))
                for name in ['install-macos.sh', 'rollback-macos.sh', 'rm-shift.txt', 'rm-modifier-taps.txt', 'rm-stop.txt', 'rm-malformed.txt']:
                    assert (directory / name).read_bytes() == archive.read(name), name
                assert (directory / 'source-manifest.json').read_bytes() == archive.read('source-manifest.json')
                assert (directory / 'privacy-source-manifest.json').read_bytes() == archive.read('privacy-source-manifest.json')
        case('installer_and_launchers_frozen_except_release_binding_historical_fixtures_and_pins_unchanged', unchanged_installer_launchers_and_fixtures)

        def owner_docs():
            assert 'python3 preflight.py --directory .' in (directory / 'README.md').read_text()
            for name in ['README.md', 'OWNER-CHECK.md']:
                for block in re.findall(r'```[^\n]*\n(.*?)```', (directory / name).read_text(), re.S):
                    assert '?pw=' not in block
                    assert not re.search(r'curl[^\n]*(?:-H|--header)[^\n]*X-Duck-Password', block, re.I)
        case('offline_first_readme_and_no_credential_bearing_owner_commands', owner_docs)

        for name, field, value, expected in [
            ('package_identity', 'package_id', 'unrelated', 'WRONG_PACKAGE_IDENTITY'),
            ('new_runtime_id_required', 'firmware_build_id', 'ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1', 'WRONG_H1_FIRMWARE_IDENTITY'),
            ('privacy_base_revision', 'privacy_base_source_checkpoint_commit', '0' * 40, 'WRONG_PRIVACY_BASE_REVISIONS'),
            ('dashboard_scope', 'dashboard_profile', 'unrelated', 'WRONG_DASHBOARD_SCOPE_OR_ROLLBACK_CLAIM'),
            ('candidate_runtime_distinction', 'runtime_build_id_distinguishes_candidate', False, 'WRONG_DASHBOARD_SCOPE_OR_ROLLBACK_CLAIM'),
            ('older_rollback_cannot_claim_privacy_patch', 'rollback_is_privacy_patched', True, 'WRONG_DASHBOARD_SCOPE_OR_ROLLBACK_CLAIM'),
            ('privacy_pin', 'privacy_composition_pin_sha256', '0' * 64, 'WRONG_PRIVACY_COMPOSITION_PIN'),
            ('dashboard_pin', 'dashboard_composition_pin_sha256', '0' * 64, 'WRONG_DASHBOARD_COMPOSITION_PIN'),
        ]:
            case(name, lambda field=field, value=value, expected=expected:
                 manifest_change(lambda record: record.update({field: value}), expected))

        def missing_pin():
            (directory / 'dashboard-source-manifest.json').unlink()
            rejected('UNEXPECTED_PACKAGE_CONTENT')
        case('missing_final_dashboard_pin', missing_pin)

        def changed_pin():
            pin = json.loads((directory / 'dashboard-source-manifest.json').read_text())
            pin['patch_sha256'] = '0' * 64
            data = json.dumps(pin).encode()
            support_change('dashboard-source-manifest.json', data)
            manifest_change(lambda record: record.update(dashboard_composition_pin_sha256=digest(data)), 'WRONG_DASHBOARD_COMPOSITION_PIN')
        case('rehashed_dashboard_pin_cannot_bypass_bound_identity', changed_pin)
        case('dashboard_release_receipt_required', lambda: receipt_change(lambda record: record.pop('dashboard_release_verification'), 'dashboard_release_verification'))
        for name, field, value, expected in [
            ('release_status', 'status', 'FAIL', 'DASHBOARD_RELEASE_NOT_VERIFIED'),
            ('full_frozen_chain', 'full_frozen_h1_chain_executed', False, 'WRONG_DASHBOARD_RELEASE_VERIFIER'),
            ('release_adapter', 'adapter_sha256', '0' * 64, 'WRONG_DASHBOARD_RELEASE_VERIFIER'),
            ('linked_dashboard_pin', 'source_manifest_sha256', '0' * 64, 'WRONG_LINKED_DASHBOARD_PIN'),
            ('source_revision', 'source_commit', '0' * 40, 'WRONG_DASHBOARD_SOURCE_REVISION'),
            ('all_190_assertions', 'assertions_preserved', 189, 'UNREVIEWED_DASHBOARD_RELEASE_ADAPTATION'),
            ('removed_assertions', 'assertions_removed', 1, 'UNREVIEWED_DASHBOARD_RELEASE_ADAPTATION'),
            ('unrelated_hash_changes', 'unrelated_expected_hashes_changed', 1, 'UNREVIEWED_DASHBOARD_RELEASE_ADAPTATION'),
            ('historical_pin_ids', 'historical_source_pin_build_ids_changed', True, 'UNREVIEWED_DASHBOARD_RELEASE_ADAPTATION'),
            ('release_artifact', 'application_sha256', '0' * 64, 'WRONG_DASHBOARD_RELEASE_ARTIFACTS'),
            ('actual_new_runtime_id', 'actual_runtime_build_id', 'old', 'WRONG_ACTUAL_DASHBOARD_IDENTITY'),
        ]:
            case(name, lambda field=field, value=value, expected=expected:
                 receipt_change(lambda record: record['dashboard_release_verification'].update({field: value}), expected))
        case('exact_four_cumulative_overrides', lambda: receipt_change(
            lambda record: record['dashboard_release_verification']['exact_final_source_overrides'].update({'caps_trial.h': '0' * 64}),
            'UNREVIEWED_DASHBOARD_RELEASE_ADAPTATION'))
        case('all_six_frozen_layers', lambda: receipt_change(
            lambda record: record['dashboard_release_verification']['compile_events'].pop(), 'INCOMPLETE_FROZEN_H1_CHAIN'))
        case('runtime_id_adaptation_audit_required', lambda: receipt_change(
            lambda record: [event.update(runtime_identity_adaptations=[]) for event in record['dashboard_release_verification']['compile_events']],
            'MISSING_DASHBOARD_ADAPTATION_AUDIT'))
        for name, field, value in [('build_adapter', 'adapter_sha256', '0' * 64), ('one_overlay', 'overlay_calls', 2),
                                   ('clean_compile', 'clean_compile', False), ('preserved_build_guards', 'inherited_safety_predicates_removed', 1)]:
            case(name, lambda field=field, value=value:
                 receipt_change(lambda record: record['dashboard_target_adapter'].update({field: value}), 'WRONG_DASHBOARD_BUILD_ADAPTER'))

        def both_bindings(record, change):
            change(record['dashboard_release_verification']['dashboard_target_binding'])
            change(record['dashboard_target_adapter']['dashboard_target_binding'])
        for name, field, value, expected in [
            ('target_status', 'status', 'FAIL', 'DASHBOARD_TARGET_BINDING_REQUIRED'),
            ('all_201_sources', 'source_files', 200, 'DASHBOARD_TARGET_BINDING_REQUIRED'),
            ('final_two_changes', 'dashboard_files', 3, 'DASHBOARD_TARGET_BINDING_REQUIRED'),
            ('final_199_unchanged', 'unchanged_files', 198, 'DASHBOARD_TARGET_BINDING_REQUIRED'),
            ('four_cumulative_changes', 'cumulative_h1_changed_files', 3, 'DASHBOARD_TARGET_BINDING_REQUIRED'),
            ('target_app_hash', 'application_sha256', '0' * 64, 'WRONG_DASHBOARD_TARGET_ARTIFACTS'),
            ('target_verifier', 'verifier_sha256', '0' * 64, 'WRONG_DASHBOARD_TARGET_VERIFIER'),
            ('target_pin', 'source_manifest_sha256', '0' * 64, 'WRONG_DASHBOARD_TARGET_SOURCE_BINDING'),
        ]:
            case(name, lambda field=field, value=value, expected=expected:
                 receipt_change(lambda record: both_bindings(record, lambda binding: binding.update({field: value})), expected))
        case('exact_final_composed_sources', lambda: receipt_change(
            lambda record: record['source_inventory'][0].update(sha256='0' * 64), 'WRONG_DASHBOARD_COMPOSED_SOURCES'))
        case('final_webfiles_dependency', lambda: receipt_change(
            lambda record: both_bindings(record, lambda binding: next(row for row in binding['compile_inputs'] if row['source'] == 'webserver.cpp')['webfiles_header'].update(dependency_observed=False)),
            'DASHBOARD_COMPILED_HEADER_REQUIRED'))
        case('compiled_build_identity_header', lambda: receipt_change(
            lambda record: both_bindings(record, lambda binding: binding['identity_header'].update(dependency_observed=False)), 'DASHBOARD_BUILD_ID_HEADER_REQUIRED'))
        case('unreviewed_receipt_extra_data', lambda: receipt_change(
            lambda record: record.update(unreviewed_extra_data=True), 'WRONG_EXACT_DASHBOARD_RELEASE_RECEIPT'))

    after = {p.name: digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    assert before == after, 'Original public package changed during tests'
    output = dict(counts={status: sum(row['status'] == status for row in results) for status in ['PASS', 'FAIL']},
                  results=results, scope='Actual bound dashboard preflight on disposable PUBLIC copies; support metadata rehashed to test semantic gates',
                  original_package_unchanged=True, hardware=False, network=False, firmware_built=False,
                  native_macos_tested=False, installation_authorized=False)
    result_path.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output['counts']))
    return bool(output['counts']['FAIL'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy-only', action='store_true')
    parser.add_argument('--directory', type=pathlib.Path)
    parser.add_argument('--results', type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.results.exists()
    if args.policy_only:
        assert args.directory is None
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PackagePolicy))
        print(stream.getvalue())
        args.results.write_text(json.dumps(dict(counts=dict(PASS=result.testsRun-len(result.failures)-len(result.errors), FAIL=len(result.failures)+len(result.errors)),
            scope='Inert source/AST package policy tests; no image/package construction', details=stream.getvalue(), hardware=False, network=False, firmware_built=False), indent=2) + '\n')
        return not result.wasSuccessful()
    assert args.directory is not None
    return full_checks(args.directory, args.results)


if __name__ == '__main__':
    raise SystemExit(main())
