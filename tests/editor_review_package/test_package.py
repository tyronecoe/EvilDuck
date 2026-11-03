#!/usr/bin/env python3
"""Inert source policy and disposable public-package semantic checks only.

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
PRIOR_ZIP_SHA = 'f9221d2f8bd397cbcaf9166126026f4712fc17fd0ae883fe05115cc33578142c'
PACKAGE = 'evilduck-editor-safety-h1-macos-review-v1'
BUILD_ID = 'ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
APP_SHA = 'e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0'
ROLLBACK_SHA = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
CHECKPOINT = '1664d4f25593e6cc99dba43ff0e5d74531555a51'
BASE = '805d989c3ac50cb96025862c95916830c59f8ba7'
LOCAL_SHA = '525fc3f9e95c65f81a1233f3f31eac1f321233d0dd87ac2517d5a4c2f2eab768'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PackagePolicy(unittest.TestCase):
    def test_pinned_adapter_keeps_historical_h1_checks(self):
        pack = load(HERE / 'package.py', 'editor_policy_packager')
        namespace, inherited, changes = pack.adapter('0' * 64, '/public-attestation.json')
        self.assertEqual(namespace['PACKAGE'], PACKAGE)
        self.assertEqual(namespace['BUILD_ID'], 'ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1')
        self.assertEqual(namespace['APP_SHA'], APP_SHA)
        self.assertEqual(namespace['APP_BYTES'], 1437696)
        self.assertEqual(namespace['ROLLBACK_SHA'], ROLLBACK_SHA)
        self.assertEqual(namespace['ROLLBACK_BYTES'], 1413200)
        self.assertEqual(namespace['ELF_BYTES'], 23645104)
        self.assertEqual(len(inherited), 18)
        self.assertEqual(len(changes), 13)
        for row in changes:
            self.assertNotIn('RELEASE_BINDING', row['before'])
            self.assertNotIn('tool_process', row['before'])
            self.assertNotIn('original =', row['before'])
            self.assertNotIn("for name in ('install-macos.sh'", row['before'])

    def test_frozen_preflight_functions_and_rollback_tail(self):
        parent = (ROOT / 'tests/dashboard_cleanup/package_preflight.py').read_text()
        actual = (HERE / 'package_preflight.py').read_text()
        def functions(source):
            return {node.name: ast.dump(node, include_attributes=False) for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef) and node.name != 'validate'}
        self.assertEqual(functions(parent), functions(actual))
        self.assertEqual(parent[parent.index(' rollback_receipt='):], actual[actual.index(' rollback_receipt='):])
        inherited = parent[parent.index('def validate('):parent.index(' final_rows=dashboard_pin')]
        inherited = inherited.replace("'evilduck-dashboard-diagnostics-cleanup-h1-macos-review-v1'", repr(PACKAGE))
        inherited = inherited.replace("m.get('firmware_build_id')=='ROUTEB-DASHBOARD-CLEANUP-v1'", "m.get('firmware_build_id')=='" + BUILD_ID + "'")
        self.assertEqual(inherited, actual[actual.index('def validate('):actual.index(' # Historical dashboard is a parent layer,')])

    def test_offline_first_documents_and_backup_boundary(self):
        pack = load(HERE / 'package.py', 'editor_policy_documents')
        docs = pack.documents()
        self.assertEqual(set(docs), {'README.md', 'INSTALL-MAC.md', 'ROLLBACK-MAC.md'})
        for text in docs.values():
            self.assertIn('python3 preflight.py --directory .', text)
            self.assertIn(ROLLBACK_SHA, text)
            self.assertIn('unplugged', text)
            self.assertNotIn('?pw=', text)
        self.assertIn('before its final INSTALL confirmation', docs['INSTALL-MAC.md'])
        self.assertIn('post-build', docs['README.md'].lower())
        self.assertIn('17 uncommitted inputs', docs['README.md'])
        self.assertIn('NOT this candidate Build ID', docs['README.md'])
        self.assertIn('do not run/reinstall', docs['README.md'])

    def test_source_provenance_and_resource_checks_exist(self):
        preflight = load(HERE / 'package_preflight.py', 'editor_policy_preflight')
        self.assertEqual(preflight.SOURCE_CHECKPOINT, CHECKPOINT)
        self.assertEqual(preflight.ORIGINAL_BASE, BASE)
        self.assertEqual(preflight.ORIGINAL_LOCAL_SHA, LOCAL_SHA)
        self.assertEqual(len(preflight.SUPPORT), 30)
        self.assertEqual(set(preflight.EXPECTED_RESOURCES), {'INDEX_HTML','INDEX_JS','SETTINGS_HTML','SETTINGS_JS','STYLE_CSS'})
        source = (HERE / 'package_preflight.py').read_text()
        self.assertIn("digest(data)==expected_sha and appdata.count(data)==1", source)
        self.assertIn("POST_BUILD_CHECKPOINT_EXACT_BUILD_INPUTS", source)
        self.assertIn("RELEASE['editor_release_receipt_sha256']", source)
        self.assertNotIn(" selected=receipt", source)

    def test_python38_syntax_and_stdlib_api(self):
        for filename in ['package.py', 'package_preflight.py', 'test_package.py', 'reproduce_checkpoint.py']:
            source = (HERE / filename).read_text()
            tree=ast.parse(source, feature_version=(3,8))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, ['is_relative_to','removeprefix','removesuffix'])
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    self.assertNotIn('tomllib', ast.dump(node))


def full_checks(original, result_path):
    original = original.resolve()
    release = load(original / 'preflight.py', 'editor_package_under_test')
    before = {p.name: digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    results = []
    with tempfile.TemporaryDirectory(prefix='public-editor-review-tests-') as temporary:
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
                results.append(dict(name=name,status='PASS'))
                print('PASS', name)
            except Exception as error:
                results.append(dict(name=name,status='FAIL',diagnostic=type(error).__name__+': '+str(error)))
                print('FAIL', name, type(error).__name__, str(error))
            finally:
                restore()

        def rejected(expected):
            try:
                release.validate(directory)
            except (ValueError, KeyError, OSError) as error:
                assert expected in str(error), (expected, str(error))
                return
            raise AssertionError('Unsafe package accepted')

        def manifest_change(change, expected):
            path = directory / 'manifest.json'
            record = json.loads(path.read_text()); change(record)
            path.write_text(json.dumps(record))
            rejected(expected)

        def support_change(name, data):
            (directory / name).write_bytes(data)
            path = directory / 'manifest.json'; record = json.loads(path.read_text())
            record['support_files'][name] = dict(bytes=len(data),sha256=digest(data))
            path.write_text(json.dumps(record))

        def receipt_change(change, expected):
            record = json.loads((directory / 'build-receipt.json').read_text()); change(record)
            support_change('build-receipt.json', json.dumps(record).encode()); rejected(expected)

        def both_bindings(record, change):
            change(record['editor_release_verification']['editor_target_binding'])
            change(record['editor_target_adapter']['editor_target_binding'])

        def positive():
            result = release.validate(directory)
            assert result['package_integrity']=='PASS' and result['plan_ready'] is False
            assert result['selected_image']=='application' and result['selected_write_ranges']==[]
            assert result['hardware_access'] is False and result['installation_authorized'] is False
            rollback = release.validate(directory, selected='rollback')
            assert rollback['selected_image']=='rollback' and rollback['selected_write_ranges']==[]
            assert len(list(directory.iterdir()))==34
            assert digest((directory/'application.bin').read_bytes())==APP_SHA
            assert len((directory/'application.bin').read_bytes())==1437696
            assert digest((directory/'rollback-application.bin').read_bytes())==ROLLBACK_SHA
            assert len((directory/'rollback-application.bin').read_bytes())==1413200
        case('exact_existing_image_and_older_rollback_offline_only_both_selections', positive)

        def frozen_installer():
            prior = ROOT/'downloads/evilduck-dashboard-diagnostics-cleanup-h1-macos-review-v1.zip'
            assert digest(prior.read_bytes())==PRIOR_ZIP_SHA
            normalize = lambda data: re.sub(rb'^RELEASE_BINDING=.*$', b'RELEASE_BINDING=BOUND_RELEASE_IDENTITY',data,flags=re.M)
            with zipfile.ZipFile(prior) as archive:
                assert archive.testzip() is None
                assert normalize((directory/'installer.py').read_bytes())==normalize(archive.read('installer.py'))
                for name in ['install-macos.sh','rollback-macos.sh','rm-shift.txt','rm-modifier-taps.txt','rm-stop.txt','rm-malformed.txt','source-manifest.json','privacy-source-manifest.json','dashboard-source-manifest.json']:
                    assert (directory/name).read_bytes()==archive.read(name), name
        case('installer_frozen_except_binding_and_exact_historical_launchers_fixtures_pins', frozen_installer)

        for name, field, value, expected in [
            ('package_identity','package_id','other','WRONG_PACKAGE_IDENTITY'),
            ('actual_build_id','firmware_build_id','ROUTEB-DASHBOARD-CLEANUP-v1','WRONG_H1_FIRMWARE_IDENTITY'),
            ('checkpoint_role','firmware_source_identity_kind','BUILT_AT_CHECKPOINT','FALSE_SOURCE_COMMIT_PROVENANCE'),
            ('original_build_base','original_build_source_base_commit',CHECKPOINT,'FALSE_SOURCE_COMMIT_PROVENANCE'),
            ('post_build_flag','source_checkpoint_after_build',False,'FALSE_SOURCE_COMMIT_PROVENANCE'),
            ('review_scope','editor_profile','OTHER','WRONG_EDITOR_REVIEW_SCOPE'),
            ('old_rollback_privacy_claim','rollback_is_privacy_patched',True,'WRONG_DASHBOARD_SCOPE_OR_ROLLBACK_CLAIM'),
            ('exact_original_manifest','original_local_inputs_sha256','0'*64,'WRONG_ORIGINAL_LOCAL_INPUTS'),
        ]:
            case(name, lambda field=field,value=value,expected=expected: manifest_change(lambda r:r.update({field:value}), expected))
        for name in ['reviewed-editor-source-manifest.json','editor-build-source-manifest.json','local-build-inputs.json','source-attestation.json']:
            def missing(name=name):
                (directory/name).unlink(); rejected('UNEXPECTED_PACKAGE_CONTENT')
            case('missing_'+name, missing)
        def changed_attestation():
            record=json.loads((directory/'source-attestation.json').read_text())
            record['source_checkpoint_after_build']=False
            support_change('source-attestation.json',json.dumps(record).encode())
            rejected('WRONG_SOURCE_ATTESTATION')
        case('rehashed_false_attestation_cannot_bypass_bound_identity', changed_attestation)
        case('release_required',lambda:receipt_change(lambda r:r.pop('editor_release_verification'),'editor_release_verification'))
        for name, field, value, expected in [
            ('release_status','status','FAIL','EDITOR_RELEASE_NOT_VERIFIED'),
            ('release_wrapper','adapter_sha256','0'*64,'EDITOR_RELEASE_NOT_VERIFIED'),
            ('all_frozen_layers','full_frozen_h1_chain_executed',False,'EDITOR_RELEASE_NOT_VERIFIED'),
            ('actual_build_context','base_commit',CHECKPOINT,'FALSE_LINKED_BUILD_PROVENANCE'),
            ('local_input_digest','local_inputs_sha256','0'*64,'FALSE_LINKED_BUILD_PROVENANCE'),
            ('all_190_checks','assertions_preserved',189,'REMOVED_EDITOR_RELEASE_GUARDS'),
            ('removed_guards','assertions_removed',1,'REMOVED_EDITOR_RELEASE_GUARDS'),
            ('unrelated_hashes','unrelated_expected_hashes_changed',1,'REMOVED_EDITOR_RELEASE_GUARDS'),
            ('historical_identity','historical_source_pin_build_ids_changed',True,'REMOVED_EDITOR_RELEASE_GUARDS'),
            ('rebuild_claim','recompiled',True,'WRONG_EDITOR_RELEASE_ARTIFACTS'),
            ('physical_claim','hardware',True,'UNSUPPORTED_BUILD_PHYSICAL_CLAIM'),
        ]:
            case(name,lambda field=field,value=value,expected=expected:receipt_change(lambda r:r['editor_release_verification'].update({field:value}),expected))
        case('all_six_layer_counts',lambda:receipt_change(lambda r:r['editor_release_verification']['compile_events'].pop(),'INCOMPLETE_FROZEN_H1_CHAIN'))
        case('exact_final_201_sources',lambda:receipt_change(lambda r:r['source_inventory'][0].update(sha256='0'*64),'WRONG_EDITOR_FINAL_SOURCE_INVENTORY'))
        for name,field,value in [('one_overlay','overlay_calls',2),('clean_compile','clean_compile',False),('adapter_guards','inherited_safety_predicates_removed',1)]:
            case(name,lambda field=field,value=value:receipt_change(lambda r:r['editor_target_adapter'].update({field:value}),'WRONG_EDITOR_BUILD_ADAPTER'))
        for name,field,value,expected in [
            ('source_count','source_files',200,'WRONG_EDITOR_TARGET_SOURCE_COUNTS'),
            ('two_final_changes','editor_build_files',3,'WRONG_EDITOR_TARGET_SOURCE_COUNTS'),
            ('199_unchanged','unchanged_files',198,'WRONG_EDITOR_TARGET_SOURCE_COUNTS'),
            ('cumulative_four','cumulative_h1_changed_files',3,'WRONG_EDITOR_TARGET_SOURCE_COUNTS'),
            ('exact_verifier','verifier_sha256','0'*64,'WRONG_EDITOR_TARGET_IDENTITY'),
            ('identity_patch','identity_patch_sha256','0'*64,'WRONG_EDITOR_TARGET_INPUT_BINDING'),
        ]:
            case(name,lambda field=field,value=value,expected=expected:receipt_change(lambda r:both_bindings(r,lambda b:b.update({field:value})),expected))
        case('compiled_editor_header',lambda:receipt_change(lambda r:both_bindings(r,lambda b:next(v for v in b['compile_inputs'] if v['source']=='webserver.cpp')['webfiles_header'].update(dependency_observed=False)),'EDITOR_COMPILED_HEADER_REQUIRED'))
        case('compiled_identity_header',lambda:receipt_change(lambda r:both_bindings(r,lambda b:b['identity_header'].update(metadata_only=False)),'EDITOR_BUILD_ID_HEADER_REQUIRED'))
        case('all_five_resources',lambda:receipt_change(lambda r:both_bindings(r,lambda b:b['bundled_resources'].pop()),'WRONG_BUNDLED_RESOURCE_INVENTORY'))
        case('resource_occurrences',lambda:receipt_change(lambda r:both_bindings(r,lambda b:b['bundled_resources'][0].update(binary_occurrences=2)),'WRONG_BUNDLED_RESOURCE_PROOF'))
        case('actual_resource_bytes',lambda:receipt_change(lambda r:both_bindings(r,lambda b:b['bundled_resources'][0].update(binary_offset=b['bundled_resources'][0]['binary_offset']+1)),'PACKAGED_RESOURCE_BYTES_MISMATCH'))
        case('exact_fresh_release_receipt',lambda:receipt_change(lambda r:r.update(unreviewed_extra_data=True),'WRONG_EXACT_EDITOR_RELEASE_RECEIPT'))

    after={p.name:digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    assert before==after, 'Original public package changed'
    output=dict(counts={status:sum(r['status']==status for r in results) for status in ['PASS','FAIL']},results=results,
                scope='Actual bound editor review preflight, disposable public copies; support hashes resealed to exercise semantic guards',
                original_package_unchanged=True,hardware=False,network=False,firmware_built=False,native_macos_tested=False,installation_authorized=False)
    result_path.write_text(json.dumps(output,indent=2)+'\n'); print(json.dumps(output['counts']))
    return bool(output['counts']['FAIL'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy-only',action='store_true')
    parser.add_argument('--directory',type=pathlib.Path)
    parser.add_argument('--results',type=pathlib.Path,required=True)
    args=parser.parse_args(); assert not args.results.exists()
    if args.policy_only:
        assert args.directory is None
        stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PackagePolicy))
        print(stream.getvalue())
        args.results.write_text(json.dumps(dict(counts=dict(PASS=result.testsRun-len(result.failures)-len(result.errors),FAIL=len(result.failures)+len(result.errors)),
            scope='Inert source/AST policy; no package construction',details=stream.getvalue(),hardware=False,network=False,firmware_built=False),indent=2)+'\n')
        return not result.wasSuccessful()
    assert args.directory is not None
    return full_checks(args.directory,args.results)


if __name__=='__main__':
    raise SystemExit(main())
