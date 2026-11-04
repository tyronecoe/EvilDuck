#!/usr/bin/env python3
"""Inert source policy plus disposable public-package negative controls."""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PACKAGE = 'evilduck-static-response-repair-h1-macos-review-v1'
BUILD_ID = 'ROUTEB-STATIC-RESPONSE-REPAIR-v1'
FAULTY_SHA = 'e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0'
ROLLBACK_SHA = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
PRIOR_ZIP_SHA = 'ea00a7da38d775d62b28624d232de48102c459eee24195b55e185ae70d117638'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dummy_binding():
    return dict(format='evilduck-static-response-release-binding-v1', status='VERIFIED_LOCAL_RELEASE',
                build_id=BUILD_ID, source_commit='1'*40, application_sha256='2'*64,
                application_bytes=1440000, elf_sha256='3'*64, elf_bytes=24000000,
                release_receipt_sha256='4'*64, build_inputs_sha256='5'*64,
                static_target_binding_sha256='6'*64, verifier_context_commit='7'*40, verification_delta_sha256='8'*64, completion_context_commit='9'*40, completion_receipt_sha256='a'*64, completion_helper_sha256='b'*64)


class PackagePolicy(unittest.TestCase):
    def test_frozen_installer_construction_and_historical_checks(self):
        pack = load(HERE/'package.py', 'static_policy_adapter')
        namespace, inherited, changes = pack.adapter(dummy_binding(), '/public-source-attestation.json', '/public-completion.json')
        self.assertEqual(namespace['PACKAGE'], PACKAGE)
        self.assertEqual(namespace['BUILD_ID'], 'ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1')
        self.assertEqual(namespace['APP_SHA'], '2'*64)
        self.assertEqual(namespace['ROLLBACK_SHA'], ROLLBACK_SHA)
        self.assertEqual(namespace['ROLLBACK_BYTES'], 1413200)
        self.assertEqual(len(inherited), 18)
        self.assertTrue(len(changes)>0)
        for row in changes:
            for forbidden in ['RELEASE_BINDING', 'tool_process', 'original =', "for name in ('install-macos.sh'"]:
                self.assertNotIn(forbidden, row['before'])

    def test_frozen_preflight_image_ranges_ota_and_rollback_tail(self):
        parent=(ROOT/'tests/editor_review_package/package_preflight.py').read_text()
        actual=(HERE/'package_preflight.py').read_text()
        def functions(text):
            return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(text).body
                    if isinstance(node,ast.FunctionDef) and node.name!='validate'}
        self.assertEqual(functions(parent),functions(actual))
        self.assertEqual(parent[parent.index(' rollback_receipt='):],actual[actual.index(' rollback_receipt='):])
        prefix=parent[parent.index('def validate('):parent.index(' actual_sources=')]
        prefix=prefix.replace("'evilduck-editor-safety-h1-macos-review-v1'",repr(PACKAGE))
        prefix=prefix.replace("m.get('firmware_build_id')=='ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'", "m.get('firmware_build_id')==ACTUAL_BUILD_ID")
        prefix=prefix.replace("build_pin.get('build_id')==ACTUAL_BUILD_ID", "build_pin.get('build_id')==EDITOR_BUILD_ID")
        self.assertEqual(prefix,actual[actual.index('def validate('):actual.index(' # All older manifests')])

    def test_offline_docs_and_failed_candidate_classification(self):
        pack=load(HERE/'package.py','static_policy_docs')
        docs=pack.documents(dummy_binding())
        for text in docs.values():
            self.assertIn('python3 preflight.py --directory .',text)
            self.assertIn('unplugged',text)
            self.assertIn(ROLLBACK_SHA,text)
            self.assertNotIn('?pw=',text)
            self.assertIn('not a known-good recovery image',text)
        self.assertIn('before its final INSTALL confirmation',docs['INSTALL-MAC.md'])
        self.assertIn('No existing backup is deleted or overwritten',docs['INSTALL-MAC.md'])
        self.assertIn('NOT this candidate Build ID',docs['INSTALL-MAC.md'])

    def test_pending_and_previous_image_bindings_fail_closed(self):
        pack=load(HERE/'package.py','static_policy_binding')
        with tempfile.TemporaryDirectory() as temporary:
            old=pack.HERE;pack.HERE=pathlib.Path(temporary)
            try:
                good=dummy_binding()
                for change in [lambda v:v.update(status='PENDING_VERIFIED_NEW_ARTIFACTS'),
                               lambda v:v.update(application_sha256=FAULTY_SHA),
                               lambda v:v.update(application_sha256=ROLLBACK_SHA),
                               lambda v:v.update(source_commit=None)]:
                    value=dict(good);change(value)
                    (pack.HERE/'release-binding.json').write_text(json.dumps(value))
                    with self.assertRaises((AssertionError,TypeError)):
                        pack.release_binding()
                (pack.HERE/'release-binding.json').write_text(json.dumps(good))
                self.assertEqual(pack.release_binding(),good)
            finally:pack.HERE=old

    def test_single_host_verifier_delta_is_exact_and_stable_after_publication(self):
        pack=load(HERE/'package.py','static_policy_verifier_delta')
        with tempfile.TemporaryDirectory() as temporary:
            root=pathlib.Path(temporary);old_root=pack.ROOT;pack.ROOT=root
            def git(*args):
                return subprocess.check_output(['git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid']+list(args),cwd=root,stderr=subprocess.PIPE,text=True).strip()
            try:
                git('init','-q')
                names=['tests/static_response_build_integration/verify_target.py']+['tests/fixture/input%02d.txt'%i for i in range(25)]
                rows=[]
                for name in names:
                    path=root/name;path.parent.mkdir(parents=True,exist_ok=True);data=('Original '+name+'\n').encode();path.write_bytes(data)
                    rows.append(dict(file=name,size=len(data),sha256=digest(data)))
                git('add','--','.');git('commit','-q','-m','Synthetic compiler checkpoint');compiler=git('rev-parse','HEAD')
                verifier_file=root/names[0];verifier_file.write_bytes(verifier_file.read_bytes()+b'Host-only parser correction\n')
                git('add','--',names[0]);git('commit','-q','-m','Synthetic verifier checkpoint');verifier=git('rev-parse','HEAD')
                binding=dict(source_commit=compiler,verifier_context_commit=verifier)
                first=pack.verifier_delta(binding,rows)
                self.assertEqual(first['other_compile_inputs_identical'],25)
                self.assertEqual(first['before'],rows[0])
                self.assertEqual(first['after']['sha256'],digest(verifier_file.read_bytes()))
                (root/'publication.txt').write_text('Synthetic later package receipt\n');git('add','--','publication.txt');git('commit','-q','-m','Synthetic publication')
                self.assertEqual(pack.verifier_delta(binding,rows),first)
                other=root/names[1];old=other.read_bytes();other.write_bytes(old+b'Unapproved change\n')
                with self.assertRaises(AssertionError):pack.verifier_delta(binding,rows)
                other.write_bytes(old)
                corrected=verifier_file.read_bytes();verifier_file.write_bytes(corrected+b'Uncommitted verifier change\n')
                with self.assertRaises(AssertionError):pack.verifier_delta(binding,rows)
                verifier_file.write_bytes(corrected)
                changed=[dict(r) for r in rows];changed[0]['sha256']='0'*64
                with self.assertRaises(AssertionError):pack.verifier_delta(binding,changed)
            finally:pack.ROOT=old_root

    def test_python38_offline_stdlib_and_actual_proof_requirements(self):
        preflight=(HERE/'package_preflight.py').read_text()
        self.assertIn("RELEASE['static_target_binding_sha256']",preflight)
        self.assertIn("digest(data)==expected_sha and appdata.count(data)==1",preflight)
        self.assertIn("COMMITTED_CLEAN_BUILD_INPUTS",preflight)
        self.assertNotIn('POST_BUILD_CHECKPOINT_EXACT_BUILD_INPUTS',preflight)
        for name in ['package.py','package_preflight.py','test_package.py']:
            tree=ast.parse((HERE/name).read_text(),feature_version=(3,8))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
                    self.assertNotIn(node.func.attr,['is_relative_to','removeprefix','removesuffix'])
                if name=='package_preflight.py' and isinstance(node,(ast.Import,ast.ImportFrom)):
                    self.assertFalse(any(x in ast.dump(node) for x in ['socket','urllib','serial','subprocess','requests']))


def full_checks(original,result_path):
    original=original.resolve();release=load(original/'preflight.py','static_package_under_test')
    before={p.name:digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    results=[]
    with tempfile.TemporaryDirectory(prefix='public-static-response-package-') as temporary:
        directory=pathlib.Path(temporary)/'public';shutil.copytree(original,directory)
        saved={p.name:p.read_bytes() for p in directory.iterdir()}
        def restore():
            for p in directory.iterdir():
                if p.name not in saved:
                    if p.is_dir() and not p.is_symlink():shutil.rmtree(p)
                    else:p.unlink()
            for name,data in saved.items():(directory/name).write_bytes(data)
        def case(name,action):
            try:action();results.append(dict(name=name,status='PASS'));print('PASS',name)
            except Exception as error:
                results.append(dict(name=name,status='FAIL',diagnostic=type(error).__name__+': '+str(error)));print('FAIL',name,str(error))
            finally:restore()
        def rejected(reason):
            try:release.validate(directory)
            except (ValueError,KeyError,OSError) as error:
                assert reason in str(error),(reason,str(error));return
            raise AssertionError('Unsafe package accepted')
        def support(name,data):
            (directory/name).write_bytes(data)
            p=directory/'manifest.json';value=json.loads(p.read_text());value['support_files'][name]=dict(bytes=len(data),sha256=digest(data));p.write_text(json.dumps(value))
        def manifest(change,reason):
            p=directory/'manifest.json';v=json.loads(p.read_text());change(v);p.write_text(json.dumps(v));rejected(reason)
        def receipt(change,reason):
            v=json.loads((directory/'build-receipt.json').read_text());change(v);support('build-receipt.json',json.dumps(v).encode());rejected(reason)
        def normal():
            for selected in ['application','rollback']:
                v=release.validate(directory,selected=selected)
                assert v['package_integrity']=='PASS' and v['plan_ready'] is False and v['selected_write_ranges']==[]
                assert v['hardware_access'] is False and v['installation_authorized'] is False
            m=json.loads((directory/'manifest.json').read_text())
            assert m['firmware_build_id']==BUILD_ID and m['firmware_source_identity_kind']=='COMMITTED_CLEAN_BUILD_INPUTS'
            assert m['source_checkpoint_after_build'] is False and m['previous_faulty_candidate_is_recovery'] is False
            assert m['application_sha256'] not in [FAULTY_SHA,ROLLBACK_SHA]
        case('new_exact_candidate_and_old_rollback_offline_both_selections',normal)
        def inherited_bytes():
            p=ROOT/'downloads/evilduck-editor-safety-h1-macos-review-v1.zip';assert digest(p.read_bytes())==PRIOR_ZIP_SHA
            with zipfile.ZipFile(p) as z:
                old=z.read('installer.py').decode();new=(directory/'installer.py').read_text()
                norm=lambda text:re.sub(r'^RELEASE_BINDING=.*$', 'RELEASE_BINDING=BOUND',text,flags=re.M)
                assert norm(old)==norm(new)
                for name in ['install-macos.sh','rollback-macos.sh','rm-shift.txt','rm-modifier-taps.txt','rm-stop.txt','rm-malformed.txt','dependency-pin.json']:
                    assert z.read(name)==(directory/name).read_bytes(),name
        case('installer_frozen_except_binding_launchers_and_inherited_support_exact',inherited_bytes)
        for name in ['response-source-manifest.json','static-response-build-source-manifest.json','build-inputs.json','source-attestation.json','postcompile-completion.json']:
            def missing(name=name):
                (directory/name).unlink();rejected('UNEXPECTED_PACKAGE_CONTENT')
            case('missing_'+name,missing)
        case('faulty_previous_image_not_accepted',lambda:((directory/'application.bin').write_bytes(zipfile.ZipFile(ROOT/'downloads/evilduck-editor-safety-h1-macos-review-v1.zip').read('application.bin')),rejected('WRONG_APPLICATION_BYTES')))
        case('faulty_candidate_not_labeled_recovery',lambda:manifest(lambda m:m.update(previous_faulty_candidate_is_recovery=True),'MISLABELED_FAULTY_RECOVERY'))
        case('verifier_context_not_compiler_context',lambda:manifest(lambda m:m.update(verifier_context_commit=m['firmware_source_commit']),'WRONG_VERIFIER_CONTEXT'))
        case('completion_receipt_bound',lambda:manifest(lambda m:m.update(completion_receipt_sha256='0'*64),'WRONG_EXACT_POSTCOMPILE_COMPLETION'))
        case('completion_helper_bound',lambda:manifest(lambda m:m.update(completion_helper_sha256='0'*64),'WRONG_POSTCOMPILE_HELPER'))
        case('completion_context_distinct',lambda:manifest(lambda m:m.update(completion_context_commit=m['firmware_source_commit']),'WRONG_COMPLETION_HELPER_PROVENANCE'))

        for key,change,reason in [
            ('release_status',lambda r:r['static_response_release_verification'].update(status='PENDING'),'STATIC_RELEASE_NOT_VERIFIED'),
            ('release_wrapper',lambda r:r['static_response_release_verification'].update(adapter_sha256='0'*64),'STATIC_RELEASE_NOT_VERIFIED'),
            ('full_frozen_chain',lambda r:r['static_response_release_verification'].update(full_frozen_h1_chain_executed=False),'STATIC_RELEASE_NOT_VERIFIED'),
            ('committed_source_context',lambda r:r['static_response_release_verification'].update(source_commit_contains_changes=False),'FALSE_STATIC_BUILD_PROVENANCE'),
            ('preserved190guards',lambda r:r['static_response_release_verification'].update(assertions_preserved=189),'REMOVED_STATIC_RELEASE_GUARDS'),
            ('removed_guard',lambda r:r['static_response_release_verification'].update(assertions_removed=1),'REMOVED_STATIC_RELEASE_GUARDS'),
            ('all_six_layers',lambda r:r['static_response_release_verification']['compile_events'].pop(),'INCOMPLETE_FROZEN_H1_CHAIN'),
                        ('not_physically_passed',lambda r:r['static_response_release_verification'].update(installed=True),'UNSUPPORTED_STATIC_PHYSICAL_CLAIM'),
            ('rebuild_claim',lambda r:r['static_response_release_verification'].update(recompiled=True),'UNSUPPORTED_STATIC_PHYSICAL_CLAIM')]:
            case(key,lambda change=change,reason=reason:receipt(change,reason))
        def old_inventory(r):
            row=next(x for x in r['source_inventory'] if x['file']=='EvilDuckS3/webserver.cpp');row['sha256']='02b1bed01526935e7c8ec1857dfc910221dda3977efc47185eafbc796e4a22f9'
        case('old_response_source_inventory_rejected',lambda:receipt(old_inventory,'WRONG_STATIC_FINAL_SOURCE_INVENTORY'))
        def bad_inputs():
            v=json.loads((directory/'build-inputs.json').read_text());v['source_commit_contains_changes']=False;support('build-inputs.json',json.dumps(v).encode());rejected('WRONG_COMMITTED_BUILD_INPUTS')
        case('build_inputs_hash_bound',bad_inputs)
        def bad_attestation():
            v=json.loads((directory/'source-attestation.json').read_text());v['source_checkpoint_after_build']=True;support('source-attestation.json',json.dumps(v).encode());rejected('WRONG_SOURCE_ATTESTATION')
        case('no_false_postbuild_provenance',bad_attestation)
        def binding_change(change, reason):
            def both(r):
                value=r['static_response_release_verification']['static_response_target_binding']
                change(value)
                r['static_response_target_adapter']['static_response_target_binding']=value
            receipt(both,reason)
        case('new_target_binding_status',lambda:binding_change(lambda b:b.update(status='PENDING'),'WRONG_STATIC_TARGET_IDENTITY'))
        case('full_actual_target_proof_hash_bound',lambda:binding_change(lambda b:b.update(invented_marker=True),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        for key,change,reason in [
            ('streaming_required',lambda b:b['streaming_response'].update(status='PENDING'),'STATIC_STREAMING_NOT_VERIFIED'),
            ('streamed_elf_identity',lambda b:b['streaming_response'].update(actual_elf_sha256='0'*64),'STATIC_STREAMING_NOT_VERIFIED'),
            ('byte_overload_observed',lambda b:b['streaming_response']['compiled_object'].update(byte_overload_observed=False),'WRONG_COMPILED_ASSET_DISPATCH'),
            ('char_copy_not_used_for_assets',lambda b:b['streaming_response']['compiled_object'].update(char_send_P_absent=False),'WRONG_COMPILED_ASSET_DISPATCH'),
            ('factory_is_progmem',lambda b:b['streaming_response']['linked_factory'].update(progmem_ctor_observed=False),'FULL_RESOURCE_COPY_OR_WRONG_FACTORY'),
            ('no_full_resource_string',lambda b:b['streaming_response']['linked_factory'].update(full_resource_string_copy=True),'FULL_RESOURCE_COPY_OR_WRONG_FACTORY'),
            ('actual_object_linked',lambda b:b['streaming_response']['compiled_object'].update(sha256='0'*64),'STREAMING_OBJECT_NOT_LINKED'),
            ('sdk_consumer_linked',lambda b:b['streaming_response']['sdk_consumers'][0].update(linked=False),'WRONG_LINKED_STREAMING_SDK'),
            ('all_ten_paired_asset_calls',lambda b:b['streaming_response']['compiled_asset_call_witnesses'].pop(),'WRONG_COMPILED_ASSET_CALL_WITNESSES'),
            ('paired_pointer_and_length',lambda b:b['streaming_response']['compiled_asset_call_witnesses'][0].update(http_bytes=0),'WRONG_COMPILED_ASSET_ARGUMENTS'),
            ('all_nine_wire_rows',lambda b:b['streaming_response']['pointer_length_table'].pop(),'WRONG_COMPILED_POINTER_LENGTH_TABLE'),
            ('wire_length_excludes_nul',lambda b:b['streaming_response']['pointer_length_table'][0].update(c_nul_excluded=False),'WRONG_COMPILED_WIRE_RESOURCE'),
            ('no_claimed_board_heap_measurement',lambda b:b['streaming_response'].update(actual_ESP32_heap_measured=True),'UNSUPPORTED_STREAMING_PHYSICAL_CLAIM')]:
            case(key,lambda change=change,reason=reason:binding_change(change,reason))

        case('exact_release_receipt_bound',lambda:receipt(lambda r:r.update(extra_unreviewed_field=True),'WRONG_EXACT_STATIC_RELEASE_RECEIPT'))
    assert before=={p.name:digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    value=dict(counts=dict(PASS=sum(r['status']=='PASS' for r in results),FAIL=sum(r['status']=='FAIL' for r in results)),results=results,
               scope='Disposable local package/source/identity controls; no device/network/installer dispatch',hardware=False,firmware_built=False)
    result_path.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value['counts']));return int(value['counts']['FAIL']!=0)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=pathlib.Path)
    parser.add_argument('--results',type=pathlib.Path,required=True)
    args=parser.parse_args()
    if args.directory:return full_checks(args.directory,args.results)
    out=io.StringIO();run=unittest.TextTestRunner(stream=out,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PackagePolicy))
    value=dict(counts=dict(PASS=run.testsRun-len(run.failures)-len(run.errors),FAIL=len(run.failures)+len(run.errors)),details=out.getvalue(),scope='Inert source/AST/package policy only',hardware=False,firmware_built=False)
    args.results.write_text(json.dumps(value,indent=2)+'\n');print(out.getvalue());return int(not run.wasSuccessful())


if __name__=='__main__':raise SystemExit(main())
