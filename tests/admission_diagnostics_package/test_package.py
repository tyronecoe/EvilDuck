#!/usr/bin/env python3
"""Admission review package policy and full inherited artifact mutation checks.
No hardware, network, installer dispatch or target compiler.
"""
import argparse,ast,contextlib,hashlib,importlib.util,io,json,pathlib,re,shutil,subprocess,sys,tempfile,unittest,zipfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent
PACKAGE='evilduck-routeb-admission-diagnostics-h1-macos-review-v1'
BUILD_ID='ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1'
FAULTY_SHA='e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0'
ROLLBACK_SHA='cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
PRIOR_ZIP_SHA='ea00a7da38d775d62b28624d232de48102c459eee24195b55e185ae70d117638'
def digest(data):return hashlib.sha256(data).hexdigest()
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def dummy_binding():
 return dict(format='evilduck-admission-diagnostics-release-binding-v1',status='VERIFIED_LOCAL_RELEASE',build_id=BUILD_ID,source_commit='1'*40,verifier_context_commit='1'*40,post_compile_verifier_delta=None,application_sha256='2'*64,application_bytes=1440000,elf_sha256='3'*64,elf_bytes=24000000,release_receipt_sha256='4'*64,build_inputs_sha256='5'*64,repeat_target_binding_sha256='6'*64,test_results_sha256='7'*64,build_input_count=40,del_core_sha256='8'*64,del_shortcuts_sha256='9'*64,del_test_receipt_sha256='a'*64,define_core_sha256='b'*64,define_test_receipt_sha256='c'*64,observer_test_receipt_sha256='d'*64,observer_web_test_receipt_sha256='e'*64,admission_test_receipt_sha256='f'*64,negative_control_receipt_sha256='0'*64)
class PackagePolicy(unittest.TestCase):
 def test_frozen_installer_construction(self):
  pack=load(HERE/'package.py','admission_policy_adapter');namespace,inherited,changes=pack.adapter(dummy_binding(),'/public-attestation.json','/public-test-results.json')
  self.assertEqual(namespace['PACKAGE'],PACKAGE);self.assertEqual(namespace['BUILD_ID'],'ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1');self.assertEqual(len(inherited),18)
  self.assertEqual(namespace['ROLLBACK_SHA'],ROLLBACK_SHA);self.assertEqual(namespace['ROLLBACK_BYTES'],1413200)
  for row in changes:
   for forbidden in ['RELEASE_BINDING','tool_process','original =',"for name in ('install-macos.sh'"]:self.assertNotIn(forbidden,row['before'])
 def test_original_image_layout_ota_functions_and_tail(self):
  old=(ROOT/'tests/usb_os_observer_v2_package/package_preflight.py').read_text();new=(HERE/'package_preflight.py').read_text()
  def functions(text):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name!='validate'}
  self.assertEqual(functions(old),functions(new));self.assertEqual(old[old.index(' rollback_receipt='):],new[new.index(' rollback_receipt='):])
 def test_all_inherited_require_predicates_preserved(self):
  from collections import Counter
  def messages(path):
   tree=ast.parse(path.read_text());return Counter(n.args[-1].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' and n.args and isinstance(n.args[-1],ast.Constant) and isinstance(n.args[-1].value,str))
  old=messages(ROOT/'tests/usb_os_observer_v2_package/package_preflight.py');new=messages(HERE/'package_preflight.py')
  self.assertFalse(old-new);self.assertGreater(len(new),len(old))
 def test_inherited_require_conditions_preserved(self):
  from collections import Counter
  old=(ROOT/'tests/usb_os_observer_v2_package/package_preflight.py').read_text();new=(HERE/'package_preflight.py').read_text()
  new=new.replace(PACKAGE,'evilduck-routeb-usb-enum-observer-h1-macos-review-v2')
  new=new.replace("observer_v2_release.get('build_id')=='ROUTEB-USB-ENUM-OBSERVER-H1-v2'","observer_v2_release.get('build_id')==ACTUAL_BUILD_ID")
  def predicates(text):
   return Counter(ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(text)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require')
  self.assertFalse(predicates(old)-predicates(new))
 def test_all_parent_tool_hashes(self):
  manifest=json.loads((HERE/'adaptation-manifest.json').read_text())
  for name,expected in manifest['parents'].items():self.assertEqual(digest((ROOT/'tests/usb_os_observer_v2_package'/name).read_bytes()),expected)
  self.assertEqual(manifest['inherited_require_predicates_removed'],0);self.assertFalse(manifest['installer_construction_changed'])
  for name,expected in manifest['generated_sha256'].items():self.assertEqual(digest((HERE/name).read_bytes()),expected)
 def test_docs_and_acceptance(self):
  pack=load(HERE/'package.py','admission_policy_docs');docs=pack.documents(dummy_binding())
  for n in ['README.md','INSTALL-MAC.md','ROLLBACK-MAC.md']:
   self.assertIn('python3 preflight.py --directory .',docs[n]);self.assertIn('UNPLUGGED',docs[n]);self.assertIn(ROLLBACK_SHA,docs[n]);self.assertIn('not a known-good recovery image',docs[n]);self.assertNotIn('?pw=',docs[n])
  self.assertIn('before its final INSTALL',docs['INSTALL-MAC.md']);self.assertIn('No existing backup is deleted or overwritten',docs['INSTALL-MAC.md'])
  self.assertIn('code **2**, line **3**',docs['OWNER-CHECK.md']);self.assertIn('matching successful request status',docs['OWNER-CHECK.md']);self.assertIn('No broad',docs['OWNER-CHECK.md']);self.assertIn('WORKING_DEFINE_RETURN',docs['RETURN-WORKING.md'])
  self.assertNotIn('save session B',docs['OWNER-CHECK.md']);self.assertNotIn('one development capture, session A',docs['OWNER-CHECK.md'])
 def test_pending_old_image_and_false_delta_bindings_refused(self):
  pack=load(HERE/'package.py','admission_policy_binding')
  with tempfile.TemporaryDirectory() as tmp:
   before=pack.HERE;pack.HERE=pathlib.Path(tmp)
   try:
    good=dummy_binding()
    for change in [dict(status='PENDING_VERIFIED_TARGET_ARTIFACTS'),dict(application_sha256=FAULTY_SHA),dict(application_sha256=ROLLBACK_SHA),dict(application_sha256=pack.OLD_STATIC_SHA),dict(application_sha256=pack.OLD_REPEAT_SHA),dict(application_sha256=pack.OLD_DEL_SHA),dict(application_sha256=pack.OLD_DEFINE_SHA),dict(application_sha256=pack.OBSERVER_V1_SHA),dict(application_sha256='b7ac50eebe6fb5e3d69d97f20004e1014c46fb116845e30864f56de5de6d384e'),dict(verifier_context_commit='9'*40),dict(post_compile_verifier_delta={'invented':True}),dict(source_commit=None)]:
     value=dict(good);value.update(change);(pack.HERE/'release-binding.json').write_text(json.dumps(value))
     with self.assertRaises((AssertionError,TypeError)):pack.release_binding()
    (pack.HERE/'release-binding.json').write_text(json.dumps(good));self.assertEqual(pack.release_binding(),good)
   finally:pack.HERE=before
 def test_python38_stdlib_readonly_preflight(self):
  for n in ['package.py','package_preflight.py','test_package.py']:
   tree=ast.parse((HERE/n).read_text(),feature_version=(3,8))
   for node in ast.walk(tree):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):self.assertNotIn(node.func.attr,['is_relative_to','removeprefix','removesuffix'])
    if n=='package_preflight.py' and isinstance(node,(ast.Import,ast.ImportFrom)):self.assertFalse(any(x in ast.dump(node) for x in ['socket','urllib','serial','subprocess','requests']))
 def test_exact_byte_fixture(self):
  pack=load(HERE/'package.py','admission_fixtures');fixtures=pack.fixture_bytes();raw=fixtures['AD01_INVALID_BYTE_LINE3.duck']
  self.assertEqual(raw,b'REM byte-exact admission diagnostic\r\nREM line two\nSTRING \xc3\xa9\n')
  self.assertEqual(raw[:raw.index(b'\xc3')].count(b'\n')+1,3)
  self.assertEqual(len(fixtures),3);self.assertEqual(len(pack.fixture_inventory().splitlines()),3)
 def test_exact_original_working_return(self):
  pack=load(HERE/'package.py','admission_exact_return');value=pack.verify_working_kit()
  self.assertEqual(value['sha256'],'b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed')
  self.assertEqual(value['application_sha256'],'167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30');self.assertNotEqual(value['application_sha256'],ROLLBACK_SHA)
 def test_new_proof_and_scope_guards(self):
  text=(HERE/'package_preflight.py').read_text()
  for reason in ['WRONG_ADMISSION_SOURCE_PIN','WRONG_ADMISSION_PARENT','UNREVIEWED_ADMISSION_DELTA','WRONG_ADMISSION_RELEASE_PIN','UNREVIEWED_ADMISSION_IDENTITY_DELTA','WRONG_ADMISSION_SOFTWARE_RECEIPT','WRONG_ADMISSION_NEGATIVE_CONTROLS','ADMISSION_LINK_NOT_PROVEN','WRONG_INVALID_BYTE_FIXTURE']:self.assertIn(reason,text)

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
        for name in ['admission-source-manifest.json','admission-release-source-manifest.json','admission-test-receipt.json','admission-negative-controls.json','FIXTURE-SHA256.txt','AD00_PRIOR_COMPILE_LINE5.txt','AD01_INVALID_BYTE_LINE3.duck','AD02_VALID_RECOVERY.txt','BYTE-FIXTURES.md','response-source-manifest.json','static-response-build-source-manifest.json','build-inputs.json','source-attestation.json','previous-repeat-source-manifest.json','previous-repeat-release-source-manifest.json','native-test-receipt.json','web-test-receipt.json','current-del-regression-receipt.json','current-define-regression-receipt.json','del-source-manifest.json','del-release-source-manifest.json','del-test-receipt.json','define-source-manifest.json','define-release-source-manifest.json','define-test-receipt.json','del-owner-closeout.md','D01_DEFINE_27.txt','D02_DEFINE_31.txt','D03_DEFINE_32_Rejected.txt','observer-source-manifest.json','observer-web-source-manifest.json','observer-release-source-manifest.json','observer-v2-source-manifest.json','observer-v2-web-source-manifest.json','observer-v2-release-source-manifest.json','observer-test-receipt.json','observer-web-test-receipt.json','CAPTURE-CONTRACT.md','evidence-gate.json','observer-v1-export-0.json','observer-v1-export-1.json','observer-v1-export-2.json','observer-v1-export-3.json','observer-v1-export-4.json','observer-v1-owner-handoff.txt','define-owner-acceptance.md','working-define-labels-macos-review-v1.zip','RETURN-WORKING.md']:
            def missing(name=name):
                (directory/name).unlink();rejected('UNEXPECTED_PACKAGE_CONTENT')
            case('missing_'+name,missing)
        case('faulty_previous_image_not_accepted',lambda:((directory/'application.bin').write_bytes(zipfile.ZipFile(ROOT/'downloads/evilduck-editor-safety-h1-macos-review-v1.zip').read('application.bin')),rejected('WRONG_APPLICATION_BYTES')))
        case('faulty_candidate_not_labeled_recovery',lambda:manifest(lambda m:m.update(previous_faulty_candidate_is_recovery=True),'MISLABELED_FAULTY_RECOVERY'))
        case('verifier_context_must_equal_compiler_context',lambda:manifest(lambda m:m.update(verifier_context_commit='0'*40),'WRONG_VERIFIER_CONTEXT'))
        case('postbuild_delta_not_allowed',lambda:manifest(lambda m:m.update(post_build_verifier_only_delta=True),'UNAPPROVED_POST_BUILD_DELTA'))
        case('repeat_review_scope_bound',lambda:manifest(lambda m:m.update(previous_repeat_profile='OTHER'),'WRONG_STATIC_REVIEW_SCOPE'))
        case('repeat_release_pin_bound',lambda:manifest(lambda m:m.update(repeat_release_pin_sha256='0'*64),'WRONG_REPEAT_RELEASE_PIN'))
        case('del_review_scope_bound',lambda:manifest(lambda m:m.update(del_alias_profile='OTHER'),'WRONG_DEL_REVIEW_SCOPE'))
        case('del_source_pin_bound',lambda:manifest(lambda m:m.update(del_source_pin_sha256='0'*64),'WRONG_DEL_SOURCE_PIN'))
        case('del_release_pin_bound',lambda:manifest(lambda m:m.update(del_release_pin_sha256='0'*64),'WRONG_DEL_RELEASE_PIN'))
        case('define_review_scope_bound',lambda:manifest(lambda m:m.update(define_labels_profile='OTHER'),'WRONG_DEFINE_REVIEW_SCOPE'))
        case('define_source_pin_bound',lambda:manifest(lambda m:m.update(define_source_pin_sha256='0'*64),'WRONG_DEFINE_SOURCE_PIN'))
        case('define_release_pin_bound',lambda:manifest(lambda m:m.update(define_release_pin_sha256='0'*64),'WRONG_DEFINE_RELEASE_PIN'))
        case('observer_review_scope_bound',lambda:manifest(lambda m:m.update(usb_observer_profile='OTHER'),'WRONG_OBSERVER_CAPTURE_ONLY_SCOPE'))
        case('observer_cannot_claim_classifier',lambda:manifest(lambda m:m.update(classifier_implemented=True),'WRONG_OBSERVER_CAPTURE_ONLY_SCOPE'))
        for key,reason in [('observer_source_pin_sha256','WRONG_OBSERVER_SOURCE_PIN'),('observer_web_pin_sha256','WRONG_OBSERVER_WEB_PIN'),('observer_release_pin_sha256','WRONG_OBSERVER_RELEASE_PIN')]:
            case(key,lambda key=key,reason=reason:manifest(lambda m:m.update({key:'0'*64}),reason))
        for key,reason in [('observer_v2_source_pin_sha256','WRONG_OBSERVER_V2_SOURCE_PIN'),('observer_v2_web_pin_sha256','WRONG_OBSERVER_V2_WEB_PIN'),('observer_v2_release_pin_sha256','WRONG_OBSERVER_V2_RELEASE_PIN')]:
            case(key,lambda key=key,reason=reason:manifest(lambda m:m.update({key:'0'*64}),reason))
        case('working_return_role_bound',lambda:manifest(lambda m:m['working_firmware_return'].update(role='OLDER_ROLLBACK'),'WRONG_WORKING_RETURN_IDENTITY'))
        case('working_return_app_identity_bound',lambda:manifest(lambda m:m['working_firmware_return'].update(application_sha256=ROLLBACK_SHA),'WRONG_WORKING_RETURN_IDENTITY'))
        case('working_return_archive_hash_bound',lambda:manifest(lambda m:m['working_firmware_return'].update(sha256='0'*64),'WRONG_WORKING_RETURN_IDENTITY'))
        case('observer_v1_is_not_working_return',lambda:manifest(lambda m:m['working_firmware_return'].update(application_sha256='e60af8a1b53ab2ba9e7c79b4ff821719ddd06a0a55384dd987288c4189aed6a9'),'WRONG_WORKING_RETURN_IDENTITY'))
        def swapped_return():
            support('working-define-labels-macos-review-v1.zip',(directory/'rollback-application.bin').read_bytes())
            rejected('WRONG_WORKING_RETURN_ZIP')
        case('old_rollback_cannot_replace_working_return',swapped_return)
        def old_working_as_candidate():
            with zipfile.ZipFile(directory/'working-define-labels-macos-review-v1.zip') as z:
                (directory/'application.bin').write_bytes(z.read('application.bin'))
            rejected('WRONG_APPLICATION_BYTES')
        case('working_define_cannot_replace_capture_candidate',old_working_as_candidate)
        def nested_working_integrity():
            pack=load(HERE/'package.py','actual_observer_working_identity')
            value=pack.verify_working_kit();m=json.loads((directory/'manifest.json').read_text())
            assert value==m['working_firmware_return']
            with zipfile.ZipFile(directory/value['file']) as z:
                assert z.testzip() is None and len(z.namelist())==50
                assert digest(z.read('application.bin'))==value['application_sha256']
                assert digest(z.read('rollback-application.bin'))==ROLLBACK_SHA
        case('actual_nested_working_kit_helpers_and_both_images',nested_working_integrity)

        for key,change,reason in [
            ('release_status',lambda r:r['usb_observer_release_verification'].update(status='PENDING'),'STATIC_RELEASE_NOT_VERIFIED'),
            ('release_wrapper',lambda r:r['usb_observer_release_verification'].update(adapter_sha256='0'*64),'STATIC_RELEASE_NOT_VERIFIED'),
            ('full_frozen_chain',lambda r:r['usb_observer_release_verification'].update(full_frozen_h1_chain_executed=False),'STATIC_RELEASE_NOT_VERIFIED'),
            ('committed_source_context',lambda r:r['usb_observer_release_verification'].update(source_commit_contains_changes=False),'FALSE_STATIC_BUILD_PROVENANCE'),
            ('preserved190guards',lambda r:r['usb_observer_release_verification'].update(assertions_preserved=189),'REMOVED_STATIC_RELEASE_GUARDS'),
            ('removed_guard',lambda r:r['usb_observer_release_verification'].update(assertions_removed=1),'REMOVED_STATIC_RELEASE_GUARDS'),
            ('all_six_layers',lambda r:r['usb_observer_release_verification']['compile_events'].pop(),'INCOMPLETE_FROZEN_H1_CHAIN'),
                        ('not_physically_passed',lambda r:r['usb_observer_release_verification'].update(installed=True),'UNSUPPORTED_STATIC_PHYSICAL_CLAIM'),
            ('rebuild_claim',lambda r:r['usb_observer_release_verification'].update(recompiled=True),'UNSUPPORTED_STATIC_PHYSICAL_CLAIM')]:
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
                value=r['usb_observer_release_verification']['usb_observer_target_binding']
                change(value)
                r['usb_observer_target_adapter']['usb_observer_target_binding']=value
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

        case('repeat_source_object_hash_bound',lambda:binding_change(lambda b:b['previous_command_repeat'].update(object_sha256='0'*64),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('standalone_branch_proof_bound',lambda:binding_change(lambda b:b['previous_command_repeat'].update(standalone_branch_verified=False),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('del_compiled_header_bound',lambda:binding_change(lambda b:b['del_alias'].update(compiled_header_dependency_verified=False),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('del_usage_bound',lambda:binding_change(lambda b:b['del_alias'].update(usage=0x2a),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('del_function_name_preservation_bound',lambda:binding_change(lambda b:b['del_alias'].update(del_function_name_policy_source_verified=False),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('del_executable_table_bound',lambda:binding_change(lambda b:b['del_alias'].update(table_begin_end_loaded=False),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        def wrong_del_row(binding):
            next(row for row in binding['del_alias']['decoded_table'] if row['name']=='DEL')['usage']=0x2a
        case('del_linked_table_row_bound',lambda:binding_change(wrong_del_row,'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('define_workspace_bound',lambda:binding_change(lambda b:b['define_labels'].update(workspace_bytes=8192),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('define_target_size_bound',lambda:binding_change(lambda b:b['define_labels'].update(target_compiler_bytes=5000),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('define_label_limit_bound',lambda:binding_change(lambda b:b['define_labels'].update(max_label_bytes=32),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('define_cell_size_bound',lambda:binding_change(lambda b:b['define_labels'].update(constant_cell_bytes=24),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('define_guard_bound',lambda:binding_change(lambda b:b['define_labels'].update(workspace_static_assert_retained=False),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        for name,changes in [('classifier_claim',dict(classification='MACOS')),('capture_only',dict(capture_only=False)),('forwarding_once',dict(original_handler_called_once=False)),('DCD_wrapper',dict(dcd_calls_wrapper=False)),('BSS',dict(early_bss_state=False)),('bounds',dict(max_records=65)),('state_budget',dict(dedicated_state_bytes=2049)),('stack_budget',dict(callback_max_frame=257)),('execution_claim',dict(target_execution=True))]:
            case('observer_'+name+'_bound',lambda changes=changes:binding_change(lambda b:b['usb_observer'].update(changes),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        for name,changes in [('schema',dict(schema='evilduck-usb-observer-v1')),('window',dict(window_ms=10000)),('tail',dict(diagnostic_tail_ms=10000)),('total',dict(total_ms=15000)),('immutable',dict(immutable_deadline_source_pinned=False)),('generation',dict(generation_tagged_samples_source_pinned=False)),('timestamps',dict(timestamped_records_source_pinned=False)),('unsupported',dict(first_unsupported_witness_source_pinned=False)),('tail_revalidation',dict(tail_cannot_revalidate_source_pinned=False))]:
            case('observer_v2_'+name+'_bound',lambda changes=changes:binding_change(lambda b:b['usb_observer']['v2_contract'].update(changes),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('observer_v2_combined_budget_bound',lambda:binding_change(lambda b:b['usb_observer'].update(state_plus_callback_bytes=2049),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        case('observer_v2_setup_path_bound',lambda:binding_change(lambda b:b['usb_observer'].update(actual_setup_path_verified=False),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        for name,changes in [('reachable',dict(actual_call_reachable=False)),('IRAM',dict(api_in_iram=False)),('initialization',dict(clock_available_before_usb_source_pinned=False)),('no_runtime_measurement_claim',dict(runtime_latency_measured=True))]:
            case('observer_v2_clock_'+name+'_bound',lambda changes=changes:binding_change(lambda b:b['usb_observer']['clock_api'].update(changes),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        def changed_owner_export():
            value=json.loads((directory/'observer-v1-export-3.json').read_text());value['classification']='MACOS'
            support('observer-v1-export-3.json',json.dumps(value).encode());rejected('WRONG_V1_OWNER_EXPORT_BYTES')
        case('historical_owner_export_cannot_be_rewritten',changed_owner_export)
        def changed_owner_scope():
            value=json.loads((directory/'evidence-gate.json').read_text());value['held_out_captures_remaining']=1
            support('evidence-gate.json',json.dumps(value).encode());rejected('WRONG_V1_OWNER_EVIDENCE_DIGEST')
        case('historical_owner_exports_cannot_become_heldout',changed_owner_scope)
        case('admission_scope_bound',lambda:manifest(lambda m:m.update(admission_profile='OTHER'),'WRONG_ADMISSION_SCOPE'))
        case('admission_source_pin_bound',lambda:manifest(lambda m:m.update(admission_source_pin_sha256='0'*64),'WRONG_ADMISSION_SOURCE_PIN'))
        case('admission_release_pin_bound',lambda:manifest(lambda m:m.update(admission_release_pin_sha256='0'*64),'WRONG_ADMISSION_RELEASE_PIN'))
        case('admission_exact_target_proof_bound',lambda:binding_change(lambda b:b['admission_diagnostics'].update(existing_error_code=0),'WRONG_EXACT_STATIC_TARGET_BINDING'))
        def bad_admission_receipt():
            value=json.loads((directory/'admission-test-receipt.json').read_text());value['status']='FAIL'
            support('admission-test-receipt.json',json.dumps(value).encode());rejected('WRONG_ADMISSION_SOFTWARE_RECEIPT')
        case('admission_focused_receipt_bound',bad_admission_receipt)
        def bad_control_receipt():
            value=json.loads((directory/'admission-negative-controls.json').read_text());value['status']='FAIL'
            support('admission-negative-controls.json',json.dumps(value).encode());rejected('WRONG_ADMISSION_NEGATIVE_CONTROLS')
        case('admission_negative_control_bound',bad_control_receipt)
        def byte_fixture():
            support('AD01_INVALID_BYTE_LINE3.duck',b'REM changed\n')
            rejected('WRONG_ADMISSION_FIXTURE_BYTES')
        case('admission_byte_fixture_hash_bound',byte_fixture)
        case('same_checkpoint_proof_bound',lambda:binding_change(lambda b:b['committed_source_provenance'].update(post_compile_verifier_delta={'unexpected':True}),'VERIFIER_CONTEXT_DISAGREES_WITH_TARGET_PROOF'))
        case('exact_release_receipt_bound',lambda:receipt(lambda r:r.update(extra_unreviewed_field=True),'WRONG_EXACT_STATIC_RELEASE_RECEIPT'))
    assert before=={p.name:digest(p.read_bytes()) for p in original.iterdir() if p.is_file()}
    value=dict(counts=dict(PASS=sum(r['status']=='PASS' for r in results),FAIL=sum(r['status']=='FAIL' for r in results)),results=results,
               scope='Disposable local package/source/identity controls; no device/network/installer dispatch',hardware=False,firmware_built=False)
    result_path.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value['counts']));return int(value['counts']['FAIL']!=0)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=pathlib.Path);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args()
 if a.directory:return full_checks(a.directory,a.results)
 out=io.StringIO();run=unittest.TextTestRunner(stream=out,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PackagePolicy))
 result=dict(counts=dict(PASS=run.testsRun-len(run.failures)-len(run.errors),FAIL=len(run.failures)+len(run.errors)),details=out.getvalue(),scope='Inert package/source policy only',hardware=False,target_build=False)
 a.results.write_text(json.dumps(result,indent=2)+'\n');print(out.getvalue());return int(not run.wasSuccessful())
if __name__=='__main__':raise SystemExit(main())
