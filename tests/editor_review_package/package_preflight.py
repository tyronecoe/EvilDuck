# Additive editor-safety preflight over exact dashboard parent SHA256 4a13c4db6cc89e8c06d8be598f41670b853ac262792f0d909a1d636a93809bd8
# Original image/layout/OTA/read-only functions and rollback tail retained unchanged.
# Dashboard cleanup additive preflight over immutable Privacy Fix 1 parent.
# Parent SHA-256: 6b27aeeaba35346ee68da840e8d3438fe0eca34b14bb61d26a9d96ce10cf1b44
# Historical H1/source-layer identities stay historical; final dashboard identity is distinct.
# Privacy Fix 1 additive package preflight. Historical H1 parent SHA256 b8de87a5b63237e5400f95e1bfb05e54aa05f3add5d4c309d2964b09b80ce79f
# Only package identity/support inventory and additional privacy provenance checks differ.
# Additive right-side modifier package preflight; parent SHA256 5ef335b22921bd3d90fcd9b6441081a538dc635067713e727dadbf5030e0f8a6
# Additive H1 package preflight; parent SHA256 8c6d10b6e2193fe625fb86ca191c09e9f0f259d87f27535a8a0d48b940fff49b
# Additive bounded-lock-wait adaptation of tests/source_text_v2/preflight.py
# Parent SHA-256: 889d4115478b06435a1efca1915581ac002bc82c51b4258c77c280415ea03b72
# Additive source/text-portability adaptation of tests/payload_restart/preflight.py
# Parent SHA-256: 09bdecd1f57a823a3c92db8f9e879981fc6f2fbbe3bc32baac0c36a6600a5418
# Additive payload-restart adaptation of tests/text_keyboard/preflight.py
# Parent SHA-256: 65afceff0e42457238c47584b5df36e0b76b2bdd58340977b3a3aff011918778
# Additive release adaptation; historical lock-feedback preflight remains unchanged.
#!/usr/bin/env python3
"""Read-only, Python3.8+ package/layout checks. No device, serial, network or write API."""
import argparse, hashlib, importlib.util, json, pathlib, struct, sys, zlib
sys.dont_write_bytecode=True
RELEASE=None
# The public package replaces only RELEASE with its exact generated identity.
SOURCE=RELEASE['source_commit'] if RELEASE else None
APP_BYTES=RELEASE['application_bytes'] if RELEASE else 0
APP_SHA=RELEASE['application_sha256'] if RELEASE else None
ROLLBACK_BYTES=1413200
ROLLBACK_SHA='cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
TABLE_SHA='b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e'
OTA_SHA='f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0'
LAYOUT=[('nvs',1,2,0x9000,0x5000),('otadata',1,0,0xe000,0x2000),('app0',0,0x10,0x10000,0x740000),('app1',0,0x11,0x750000,0x740000),('spiffs',1,0x82,0xe90000,0x160000),('coredump',1,3,0xff0000,0x10000)]
SUPPORT={'README.md','OWNER-CHECK.md','INSTALL-MAC.md','ROLLBACK-MAC.md','preflight.py','installer.py','install-macos.sh','rollback-macos.sh','gen_esp32part.py','APACHE-2.0.txt','source-LICENSE.txt','build-receipt.json','rollback-build-receipt.json','firmware-report.md','test-results.json','compatibility.md','owner-evidence.md','source-manifest.json','dependency-pin.json','reproduction.md','rm-shift.txt','rm-modifier-taps.txt','rm-stop.txt','rm-malformed.txt','privacy-source-manifest.json','dashboard-source-manifest.json','reviewed-editor-source-manifest.json','editor-build-source-manifest.json','local-build-inputs.json','source-attestation.json'}
ACTUAL_BUILD_ID='ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
ORIGINAL_BASE='805d989c3ac50cb96025862c95916830c59f8ba7'
SOURCE_CHECKPOINT='1664d4f25593e6cc99dba43ff0e5d74531555a51'
ORIGINAL_LOCAL_SHA='525fc3f9e95c65f81a1233f3f31eac1f321233d0dd87ac2517d5a4c2f2eab768'
EDITOR_HEADER_SHA='df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445'
EXPECTED_RESOURCES={
 'INDEX_HTML':(12185,'e086c053bbc4439ad5b8515c9a42e516496ae65adcf32783cfefc9147ac66a58'),
 'INDEX_JS':(31933,'4268329ef9d387ca4732407b198e1a182f55a66d909a5a19f9fd60c099110d36'),
 'SETTINGS_HTML':(5390,'f545e9154b2cf8d5e6573075008a87704a786bceb44fc625376b7a7d64bdd4e8'),
 'SETTINGS_JS':(10503,'7ef1cc50fdbb772e7dedb2629c6004b744f5ef9b7a0e35f2abb7b93ceb2af686'),
 'STYLE_CSS':(31976,'572d65a22ddb9892bea169a8ea43ca078e3aa9207519b7cd58cb465de39428da')}
class Rejected(ValueError):pass
def require(v,msg):
 if not v:raise Rejected(msg)
def digest(data):return hashlib.sha256(data).hexdigest()
def read(p,maximum):
 p=pathlib.Path(p);require(not p.is_symlink() and p.is_file(),'MISSING_OR_NONREGULAR_FILE');require(p.stat().st_size<=maximum,'OVERSIZE_FILE');d=p.read_bytes();require(len(d)<=maximum,'OVERSIZE_FILE');return d
def rows(selected="application"):
 size,sha,name=(APP_BYTES,APP_SHA,"application.bin") if selected=="application" else (ROLLBACK_BYTES,ROLLBACK_SHA,"rollback-application.bin")
 return [dict(role=role,file=name,offset=offset,bytes=size,sha256=sha,partition_bytes=0x740000,erase_start=offset,erase_end_exclusive=offset+((size+4095)//4096)*4096,selected_for_execution=False) for role,offset in [('app0',0x10000),('app1',0x750000)]]
def check_rows(actual,selected="application"):
 require(actual==rows(selected),'UNREVIEWED_WRITE_OR_ERASE_RANGE')
 for r in actual:
  require(r['offset']+r['bytes']<=r['offset']+r['partition_bytes'],'IMAGE_EXCEEDS_SLOT')
  require(r['erase_end_exclusive']<=r['offset']+r['partition_bytes'],'ERASE_EXCEEDS_SLOT')
  for name,_,_,start,size in LAYOUT:
   if name not in ('app0','app1'):require(r['erase_end_exclusive']<=start or r['erase_start']>=start+size,'PROTECTED_DATA_OVERLAP')
 require(actual[0]['erase_end_exclusive']<=actual[1]['erase_start'],'OVERLAPPING_ERASES')
def image(data,size=APP_BYTES,sha=APP_SHA):
 # Same bounded segment/checksum format as tools/deployment_preflight.py esp_image.
 require(len(data)==size and digest(data)==sha,'WRONG_APPLICATION_BYTES')
 require(data[0]==0xe9 and 1<=data[1]<=16 and data[2]==2 and data[3]==0x4f and struct.unpack_from('<H',data,12)[0]==9 and data[23]==1,'WRONG_S3_16M_DIO80_HEADER')
 pos=24;checksum=0xef
 for _ in range(data[1]):
  require(pos+8<=len(data),'TRUNCATED_IMAGE');length=struct.unpack_from('<I',data,pos+4)[0];pos+=8;require(length<=len(data)-pos,'INVALID_SEGMENT')
  for b in data[pos:pos+length]:checksum^=b
  pos+=length
 end=(pos//16+1)*16
 require(end+32==len(data) and data[end-1]==checksum,'WRONG_IMAGE_CHECKSUM_OR_LENGTH');require(hashlib.sha256(data[:end]).digest()==data[end:],'WRONG_APPENDED_DIGEST')
def table(data,tool):
 require(len(data) in (3072,4096),'WRONG_TABLE_SIZE')
 if len(data)==4096:require(data[3072:]==b'\xff'*1024,'UNREVIEWED_TABLE_TRAILER')
 require(digest(data[:3072])==TABLE_SHA,'WRONG_INSTALLED_LAYOUT')
 t=tool.PartitionTable.from_binary(data[:3072]);t.verify();require([(p.name,p.type,p.subtype,p.offset,p.size) for p in t]==LAYOUT and all(not p.readonly and not p.encrypted for p in t),'WRONG_PARTITION_GEOMETRY_OR_FLAGS')
def ota(data):
 # Intentionally narrow supported state, NOT a general active-slot decoder.
 require(len(data)==8192 and digest(data)==OTA_SHA,'UNREVIEWED_OTA_STATE_REQUIRES_SEPARATE_REVIEW')
 require(struct.unpack_from('<I',data)[0]==1 and struct.unpack_from('<I',data,24)[0]==0xffffffff and struct.unpack_from('<I',data,28)[0]==zlib.crc32(data[:4],0xffffffff),'INVALID_OTA_RECORD')
 require(struct.unpack_from('<I',data,4096)[0]==0 and struct.unpack_from('<I',data,4124)[0]==0xffffffff,'UNREVIEWED_SECOND_OTA_RECORD')
def validate(directory,installed_table=None,installed_ota=None,require_installed=False,selected="application"):
 require(RELEASE is not None,'RELEASE_NOT_BOUND')
 require(selected in ("application","rollback"),"UNKNOWN_IMAGE_SELECTION")
 d=pathlib.Path(directory);m=json.loads(read(d/'manifest.json',1024*1024));require(m.get('package_id')=='evilduck-editor-safety-h1-macos-review-v1' and m.get('source_commit')==SOURCE and m.get('installation_authorized') is False and m.get('update_method')=='FUTURE_ROM_APP_ONLY_BOTH_SLOTS','WRONG_PACKAGE_IDENTITY')
 require(m.get('application_bytes')==APP_BYTES and m.get('application_sha256')==APP_SHA and m.get('table_sha256')==TABLE_SHA,'WRONG_DECLARED_ARTIFACT_IDENTITY')
 check_rows(m['proposed_writes']);check_rows(m['rollback_writes'],'rollback');require(m.get('rollback_bytes')==ROLLBACK_BYTES and m.get('rollback_sha256')==ROLLBACK_SHA,'WRONG_ROLLBACK_IDENTITY');require(set(m['support_files'])==SUPPORT,'WRONG_SUPPORT_INVENTORY')
 expected=SUPPORT|{'manifest.json','application.bin','expected-partitions.bin','rollback-application.bin'}
 require({p.name for p in d.iterdir()}==expected and all(p.is_file() and not p.is_symlink() for p in d.iterdir()),'UNEXPECTED_PACKAGE_CONTENT')
 for n,r in m['support_files'].items():
  b=read(d/n,4*1024*1024);require(len(b)==r['bytes'] and digest(b)==r['sha256'],'SUPPORT_INTEGRITY_FAILED')
 image(read(d/'application.bin',APP_BYTES));image(read(d/'rollback-application.bin',ROLLBACK_BYTES),ROLLBACK_BYTES,ROLLBACK_SHA)
 spec=importlib.util.spec_from_file_location('pinned_partition_tool',d/'gen_esp32part.py');tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool);tool.offset_part_table=0x8000
 table(read(d/'expected-partitions.bin',4096),tool)
 receipt=json.loads(read(d/'build-receipt.json',4*1024*1024));require(receipt['status']=='PASS' and receipt['report']['application_sha256']==APP_SHA and receipt['report']['application_bytes']==APP_BYTES and receipt['sdk_archives_identical_to_w']==177,'WRONG_BUILD_RECEIPT');require(receipt.get('lock_feedback_verified') is True and receipt.get('keyboard_control_verified') is True,'LOCK_FEEDBACK_LINK_NOT_VERIFIED');require(receipt.get('random_uppercase_verified') is True,'RANDOM_UPPERCASE_LINK_NOT_VERIFIED');require(receipt.get('random_lowercase_verified') is True,'RANDOM_LOWERCASE_LINK_NOT_VERIFIED');require(receipt.get('randomization_jitter_verified') is True,'RANDOMIZATION_JITTER_LINK_NOT_VERIFIED');require(receipt.get('text_keyboard_verified') is True,'TEXT_KEYBOARD_LINK_NOT_VERIFIED');require(receipt.get('payload_restart_verified') is True,'PAYLOAD_RESTART_LINK_NOT_VERIFIED');require(receipt.get('source_text_verified') is True,'SOURCE_TEXT_V1_LINK_NOT_VERIFIED');require(receipt.get('source_text_v2_verified') is True,'SOURCE_TEXT_LINK_NOT_VERIFIED');require(receipt.get('timeout_wait_verified') is True,'LOCK_WAIT_TIMEOUT_LINK_NOT_VERIFIED');require(m.get('application_elf_sha256')==receipt['provenance']['elf_sha256'],'WRONG_DECLARED_ELF_IDENTITY')
 pin_data=read(d/'source-manifest.json',1024*1024);require(m.get('composition_pin_sha256')==digest(pin_data),'WRONG_COMPOSITION_PIN_IDENTITY');require(receipt.get('right_modifiers_source_pin')==json.loads(pin_data),'WRONG_LINKED_COMPOSITION_PIN');require(digest(json.dumps(receipt.get('source_text_v2_source_pin'),sort_keys=True,separators=(',',':')).encode())=='448b775c29337b3449312b33755e9518fa8c13b5e94098842aebbbed3aa501df','WRONG_INHERITED_SOURCE_TEXT_V2_PIN')
 require(m.get('firmware_source_commit')==RELEASE['firmware_source_commit'] and m.get('firmware_build_id')=='ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1','WRONG_H1_FIRMWARE_IDENTITY')
 require(m.get('official_runtime_encoding_verified') is False and m.get('physical_candidate_tested') is False,'UNSUPPORTED_COMPATIBILITY_OR_PHYSICAL_CLAIM')
 require(receipt.get('inject_var_experimental_verified') is True and receipt.get('official_runtime_encoding_verified') is False,'H1_LINK_OR_LIMITATION_NOT_VERIFIED')
 require(digest(pin_data)==RELEASE['right_pin_sha256'],'WRONG_RIGHT_MODIFIER_SOURCE_PIN')
 require(digest(json.dumps(receipt.get('inject_var_experimental_source_pin'),indent=2).encode()+b'\n')==RELEASE['h1_pin_sha256'],'WRONG_INHERITED_H1_PIN')
 require(digest(json.dumps(receipt.get('timeout_wait_source_pin'),indent=2).encode()+b'\n')==RELEASE['timeout_pin_sha256'],'WRONG_INHERITED_TIMEOUT_PIN')
 require(receipt['inject_var_build_adapter']['build_id']=='ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1','WRONG_H1_LINKED_BUILD_ID')
 require(receipt['inject_var_build_adapter']['adapter_sha256']==RELEASE['build_adapter_sha256'] and receipt['inject_var_link_adapter']['adapter_sha256']==RELEASE['link_adapter_sha256'],'WRONG_EXECUTED_H1_WRAPPERS')
 require(receipt['inject_var_build_adapter']['inherited_safety_predicates_removed']==0 and receipt['inject_var_link_adapter']['inherited_safety_predicates_removed']==0,'REMOVED_H1_GUARDS')
 require('-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1' in receipt['report']['verified_cpp_extra_flags'].split(),'MISSING_H1_BUILD_SELECTOR')
 require(receipt.get('right_modifiers_verified') is True,'RIGHT_MODIFIERS_NOT_VERIFIED')
 require('-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1' in receipt['report']['verified_cpp_extra_flags'].split(),'MISSING_RIGHT_MODIFIER_SELECTOR')
 for key,sha_key in [('right_modifiers_build_adapter','build_adapter_sha256'),('right_modifiers_link_adapter','link_adapter_sha256')]:
  require(receipt[key]['build_id']=='ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1' and receipt[key]['adapter_sha256']==RELEASE[sha_key] and receipt[key]['inherited_safety_predicates_removed']==0,'WRONG_RIGHT_MODIFIER_EXECUTED_WRAPPER')
 # Retained privacy source-layer provenance, not a claim that its older image was built.
 require(m.get('privacy_base_source_checkpoint_commit')=='93cc8d1a7b162bdda91e239d840a3eee8a70c51c' and m.get('privacy_base_target_integration_commit')=='0380d1508b8f761e30a6a1fb63f67c2850cbc84a','WRONG_PRIVACY_BASE_REVISIONS')
 require(m.get('privacy_profile')=='PRIVACY_FIX1_RETAINED_H1_OWNER_REVIEW' and m.get('dashboard_profile')=='DASHBOARD_DIAGNOSTICS_CLEANUP_H1_OWNER_REVIEW' and m.get('runtime_build_id_distinguishes_candidate') is True and m.get('rollback_is_privacy_patched') is False,'WRONG_DASHBOARD_SCOPE_OR_ROLLBACK_CLAIM')
 privacy_data=read(d/'privacy-source-manifest.json',1024*1024);privacy_sha=digest(privacy_data)
 require(privacy_sha==RELEASE['privacy_pin_sha256'] and m.get('privacy_composition_pin_sha256')==privacy_sha,'WRONG_PRIVACY_COMPOSITION_PIN')
 privacy_pin=json.loads(privacy_data)
 require(privacy_pin.get('format')=='evilduck-routeb-privacy-fix1-source-only-v1' and privacy_pin.get('baseline')=='a04e54309c9c73bae17ef23c48283828dfebc0ad','WRONG_PRIVACY_BASELINE')
 require(len(privacy_pin['after'])==3 and len(privacy_pin['unchanged'])==198 and {r['file'] for r in privacy_pin['after']}=={'cli.cpp','webserver.cpp','webfiles.h'},'WRONG_PRIVACY_BASE_SOURCE_DELTA')
 privacy_rows=privacy_pin['after']+privacy_pin['unchanged'];privacy_sources={r['file']:r['sha256'] for r in privacy_rows}
 require(len(privacy_rows)==len(privacy_sources)==201,'WRONG_PRIVACY_BASE_SOURCE_INVENTORY')
 dashboard_data=read(d/'dashboard-source-manifest.json',1024*1024);dashboard_sha=digest(dashboard_data);dashboard_pin=json.loads(dashboard_data)
 require(dashboard_sha==RELEASE['dashboard_pin_sha256'] and m.get('dashboard_composition_pin_sha256')==dashboard_sha,'WRONG_DASHBOARD_COMPOSITION_PIN')
 require(dashboard_pin.get('format')=='evilduck-dashboard-cleanup-v1' and dashboard_pin.get('build_id')=='ROUTEB-DASHBOARD-CLEANUP-v1' and dashboard_pin.get('baseline')=='70d08e9f789c187c5e27350a66f4d0d52992964b' and dashboard_pin.get('privacy_manifest_sha256')==privacy_sha,'WRONG_DASHBOARD_BASELINE')
 require(len(dashboard_pin['before'])==len(dashboard_pin['after'])==2 and len(dashboard_pin['unchanged'])==199 and {r['file'] for r in dashboard_pin['after']}=={'webfiles.h','caps_trial.h'},'WRONG_DASHBOARD_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in dashboard_pin['before']+dashboard_pin['unchanged']}==privacy_sources,'WRONG_DASHBOARD_PRIVACY_BASE')
 # Historical dashboard is a parent layer, not the final repaired asset table.
 dashboard_sources={r['file']:r['sha256'] for r in dashboard_pin['after']+dashboard_pin['unchanged']}
 require(len(dashboard_sources)==201 and receipt.get('dashboard_parent_source_pin')==dashboard_pin,'WRONG_HISTORICAL_DASHBOARD_PIN')
 editor_data=read(d/'reviewed-editor-source-manifest.json',1024*1024);editor_sha=digest(editor_data);editor_pin=json.loads(editor_data)
 require(editor_sha==RELEASE['editor_pin_sha256']==m.get('reviewed_editor_pin_sha256'),'WRONG_REVIEWED_EDITOR_PIN')
 require(editor_pin.get('format')=='evilduck-editor-load-safety-source-only-v1' and editor_pin.get('baseline')==ORIGINAL_BASE and editor_pin.get('parent_manifest_sha256')==dashboard_sha,'WRONG_REVIEWED_EDITOR_BASE')
 require(len(editor_pin['before'])==len(editor_pin['after'])==1 and len(editor_pin['unchanged'])==200 and editor_pin['after'][0]['file']=='webfiles.h','WRONG_REVIEWED_EDITOR_DELTA')
 require({r['file']:r['sha256'] for r in editor_pin['before']+editor_pin['unchanged']}==dashboard_sources,'WRONG_REVIEWED_EDITOR_PARENT')
 reviewed_sources={r['file']:r['sha256'] for r in editor_pin['after']+editor_pin['unchanged']}
 require(len(reviewed_sources)==201 and reviewed_sources['webfiles.h']==EDITOR_HEADER_SHA,'UNREVIEWED_EDITOR_HEADER')
 build_pin_data=read(d/'editor-build-source-manifest.json',1024*1024);build_sha=digest(build_pin_data);build_pin=json.loads(build_pin_data)
 require(build_sha==RELEASE['editor_build_pin_sha256']==m.get('editor_build_pin_sha256'),'WRONG_EDITOR_BUILD_PIN')
 require(build_pin.get('format')=='evilduck-editor-build-integration-v1' and build_pin.get('baseline')==ORIGINAL_BASE and build_pin.get('build_id')==ACTUAL_BUILD_ID and build_pin.get('comparison_base')=='privacy-fix1','WRONG_EDITOR_BUILD_BASE')
 require(build_pin.get('privacy_manifest_sha256')==privacy_sha and build_pin.get('dashboard_manifest_sha256')==dashboard_sha and build_pin.get('reviewed_editor_manifest_sha256')==editor_sha,'WRONG_EDITOR_BUILD_PARENT_PINS')
 require(len(build_pin['before'])==len(build_pin['after'])==2 and len(build_pin['unchanged'])==199 and {r['file'] for r in build_pin['after']}=={'webfiles.h','caps_trial.h'},'WRONG_EDITOR_FINAL_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in build_pin['before']+build_pin['unchanged']}==privacy_sources,'WRONG_EDITOR_FINAL_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in build_pin['after']+build_pin['unchanged']}
 require(len(final_sources)==201 and final_sources['webfiles.h']==EDITOR_HEADER_SHA and {n for n in final_sources if final_sources[n]!=reviewed_sources[n]}=={'caps_trial.h'},'UNREVIEWED_EDITOR_FINAL_DELTA')
 overrides={r['file']:r['sha256'] for r in build_pin['cumulative_h1_after']}
 require(len(build_pin['cumulative_h1_after'])==4 and set(overrides)=={'cli.cpp','webserver.cpp','webfiles.h','caps_trial.h'} and all(final_sources[n]==v for n,v in overrides.items()),'WRONG_EDITOR_CUMULATIVE_H1_DELTA')
 require(receipt.get('reviewed_editor_source_pin')==editor_pin and receipt.get('editor_build_source_pin')==build_pin and receipt.get('privacy_source_pin')==privacy_pin,'WRONG_LINKED_EDITOR_SOURCE_PINS')
 actual_sources={r['file']:r['sha256'] for r in receipt['source_inventory']}
 require(len(receipt['source_inventory'])==201 and actual_sources=={'EvilDuckS3/'+n:v for n,v in final_sources.items()},'WRONG_EDITOR_FINAL_SOURCE_INVENTORY')
 local_data=read(d/'local-build-inputs.json',1024*1024);local_sha=digest(local_data);local=json.loads(local_data)
 require(local_sha==ORIGINAL_LOCAL_SHA==RELEASE['local_build_inputs_sha256']==m.get('original_local_inputs_sha256'),'WRONG_ORIGINAL_LOCAL_INPUTS')
 require(local.get('format')=='evilduck-local-build-inputs-v1' and local.get('source_base_commit')==ORIGINAL_BASE and local.get('source_commit_contains_changes') is False and local.get('uncommitted_local_changes') is True and local.get('build_id')==ACTUAL_BUILD_ID,'WRONG_ORIGINAL_BUILD_PROVENANCE')
 rows_local=local['files'];require(len(rows_local)==17 and len({r['file'] for r in rows_local})==17,'WRONG_ORIGINAL_INPUT_COUNT')
 require(digest(json.dumps(rows_local,sort_keys=True,separators=(',',':')).encode())==local.get('files_sha256'),'WRONG_ORIGINAL_FILE_LIST_DIGEST')
 for row in rows_local:
  require(set(row)=={'file','size','sha256'} and isinstance(row['file'],str) and not row['file'].startswith('/') and '..' not in row['file'].split('/') and isinstance(row['size'],int) and row['size']>=0 and isinstance(row['sha256'],str) and len(row['sha256'])==64,'INVALID_ORIGINAL_INPUT_ROW')
 attestation_data=read(d/'source-attestation.json',1024*1024);attestation=json.loads(attestation_data)
 require(digest(attestation_data)==RELEASE['source_attestation_sha256']==m.get('source_attestation_sha256'),'WRONG_SOURCE_ATTESTATION')
 require(attestation.get('format')=='evilduck-post-build-source-checkpoint-v1' and attestation.get('source_checkpoint_commit')==m.get('firmware_source_commit')==SOURCE_CHECKPOINT and attestation.get('source_checkpoint_after_build') is True and attestation.get('source_checkpoint_contains_fix') is True and attestation.get('git_blobs_verified') is True,'WRONG_POST_BUILD_CHECKPOINT')
 require(attestation.get('original_build_source_base_commit')==ORIGINAL_BASE and attestation.get('original_source_commit_contains_changes') is False and attestation.get('original_local_inputs_sha256')==local_sha and attestation.get('files')==rows_local and attestation.get('files_sha256')==local['files_sha256'] and attestation.get('recompilation_performed') is False and attestation.get('hardware') is False,'WRONG_POST_BUILD_INPUT_ATTESTATION')
 require(m.get('post_build_source_checkpoint_commit')==SOURCE_CHECKPOINT and m.get('source_checkpoint_after_build') is True and m.get('firmware_source_identity_kind')=='POST_BUILD_CHECKPOINT_EXACT_BUILD_INPUTS' and m.get('original_build_source_base_commit')==ORIGINAL_BASE and m.get('original_source_commit_contains_changes') is False,'FALSE_SOURCE_COMMIT_PROVENANCE')
 require(m.get('status_label')=='NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED' and m.get('editor_profile')=='EDITOR_FAILED_LOAD_SAFETY_H1_OWNER_REVIEW','WRONG_EDITOR_REVIEW_SCOPE')
 require(m.get('application_elf_bytes')==23645104,'WRONG_EDITOR_ELF_SIZE')
 release=receipt['editor_release_verification']
 require(release.get('status')=='PASS' and release.get('adapter_sha256')==RELEASE['editor_release_adapter_sha256'] and release.get('full_frozen_h1_chain_executed') is True,'EDITOR_RELEASE_NOT_VERIFIED')
 require(release.get('base_commit')==release.get('source_base_commit')==ORIGINAL_BASE and release.get('source_commit_contains_changes') is False and release.get('local_inputs_sha256')==local_sha,'FALSE_LINKED_BUILD_PROVENANCE')
 require(release.get('source_manifest_sha256')==build_sha and release.get('privacy_source_manifest_sha256')==privacy_sha and release.get('exact_final_source_overrides')==overrides,'WRONG_LINKED_EDITOR_PIN')
 require(release.get('assertions_preserved')==190 and release.get('assertions_removed')==0 and release.get('unrelated_expected_hashes_changed')==0 and release.get('historical_source_pin_build_ids_changed') is False,'REMOVED_EDITOR_RELEASE_GUARDS')
 require(release.get('application_sha256')==APP_SHA and release.get('elf_sha256')==RELEASE['application_elf_sha256']==m.get('application_elf_sha256') and release.get('recompiled') is False and release.get('target_source_or_images_modified') is False,'WRONG_EDITOR_RELEASE_ARTIFACTS')
 require(release.get('actual_runtime_build_id')==receipt.get('actual_runtime_build_id')==m.get('firmware_build_id')==ACTUAL_BUILD_ID,'WRONG_ACTUAL_EDITOR_BUILD_ID')
 require(release.get('installed') is False and release.get('package_created') is False and release.get('hardware') is False,'UNSUPPORTED_BUILD_PHYSICAL_CLAIM')
 events=release['compile_events']
 require([(e.get('logical_layer'),e.get('assertions_preserved')) for e in events]==[('right-modifier H1',23),('experimental H1',21),('bounded lock waits',16),('source/text v2',46),('keyboard/lock feedback',25),('caps/STOP closure',59)],'INCOMPLETE_FROZEN_H1_CHAIN')
 require(sum(len(e.get('expectation_adaptations',[])) for e in events)>0 and sum(len(e.get('runtime_identity_adaptations',[])) for e in events)>0,'MISSING_EDITOR_ADAPTATION_AUDIT')
 build_adapter=receipt['editor_target_adapter'];binding=release['editor_target_binding']
 require(build_adapter.get('adapter_sha256')==RELEASE['editor_build_adapter_sha256'] and build_adapter.get('source_base_commit')==ORIGINAL_BASE and build_adapter.get('local_inputs_sha256')==local_sha and build_adapter.get('source_commit_contains_changes') is False and build_adapter.get('overlay_calls')==1 and build_adapter.get('clean_compile') is True and build_adapter.get('inherited_safety_predicates_removed')==0,'WRONG_EDITOR_BUILD_ADAPTER')
 require(build_adapter.get('editor_target_binding')==binding,'EDITOR_TARGET_BINDING_DISAGREES')
 require(binding.get('status')=='PASS' and binding.get('source_files')==201 and binding.get('editor_build_files')==2 and binding.get('unchanged_files')==199 and binding.get('cumulative_h1_changed_files')==4 and binding.get('cumulative_h1_unchanged_files')==197 and binding.get('comparison_base')=='privacy-fix1','WRONG_EDITOR_TARGET_SOURCE_COUNTS')
 require(binding.get('verifier_sha256')==RELEASE['editor_target_verifier_sha256'] and binding.get('build_id')==ACTUAL_BUILD_ID and binding.get('application_sha256')==APP_SHA and binding.get('elf_sha256')==m.get('application_elf_sha256'),'WRONG_EDITOR_TARGET_IDENTITY')
 require(binding.get('source_base_commit')==ORIGINAL_BASE and binding.get('local_inputs_sha256')==local_sha and binding.get('source_manifest_sha256')==binding.get('editor_build_source_manifest_sha256')==build_sha and binding.get('privacy_manifest_sha256')==privacy_sha and binding.get('identity_patch_sha256')==build_pin['patch_sha256'] and binding.get('reviewed_editor_patch_sha256')==editor_pin['patch_sha256'] and binding.get('parent_preparer_sha256')==build_pin['parent_prepare_sha256'],'WRONG_EDITOR_TARGET_INPUT_BINDING')
 require(binding.get('cumulative_h1_source_overrides')==overrides,'WRONG_EDITOR_TARGET_CUMULATIVE_DELTA')
 compile_inputs={r['source']:r for r in binding['compile_inputs']}
 require(len(binding['compile_inputs'])==2 and set(compile_inputs)=={'cli.cpp','webserver.cpp'},'PRIVACY_COMPILE_INPUTS_REQUIRED')
 for name,row in compile_inputs.items():
  require(row.get('candidate_sha256')==final_sources[name] and row.get('verbose_compile_observed') is True and row.get('linked_map_load') is True,'WRONG_PRIVACY_COMPILED_CPP')
 header=compile_inputs['webserver.cpp']['webfiles_header']
 require(header.get('candidate_sha256')==EDITOR_HEADER_SHA and header.get('dependency_observed') is True,'EDITOR_COMPILED_HEADER_REQUIRED')
 identity=binding['identity_header']
 require(identity.get('source')=='caps_trial.h' and identity.get('candidate_sha256')==final_sources['caps_trial.h'] and identity.get('dependency_observed') is True and identity.get('verbose_compile_observed') is True and identity.get('linked_map_load') is True and identity.get('metadata_only') is True,'EDITOR_BUILD_ID_HEADER_REQUIRED')
 resources=binding['bundled_resources'];require(len(resources)==5 and {r['resource'] for r in resources}==set(EXPECTED_RESOURCES),'WRONG_BUNDLED_RESOURCE_INVENTORY')
 appdata=read(d/'application.bin',APP_BYTES)
 for row in resources:
  length,expected_sha=EXPECTED_RESOURCES[row['resource']];offset=row.get('binary_offset')
  require(row.get('bytes_including_nul')==length and row.get('sha256')==expected_sha and row.get('elf_occurrences')==row.get('binary_occurrences')==1 and isinstance(offset,int) and offset>=0 and offset+length<=len(appdata),'WRONG_BUNDLED_RESOURCE_PROOF')
  data=appdata[offset:offset+length]
  require(data[-1:]==b'\0' and digest(data)==expected_sha and appdata.count(data)==1,'PACKAGED_RESOURCE_BYTES_MISMATCH')
 require(digest(read(d/'build-receipt.json',4*1024*1024))==RELEASE['editor_release_receipt_sha256'],'WRONG_EXACT_EDITOR_RELEASE_RECEIPT')
 rollback_receipt=json.loads(read(d/'rollback-build-receipt.json',4*1024*1024));require(rollback_receipt['report']['application_sha256']==ROLLBACK_SHA and rollback_receipt['report']['application_bytes']==ROLLBACK_BYTES,'WRONG_ROLLBACK_RECEIPT')
 out=dict(selected_image=selected,plan_ready=False,package_integrity='PASS',source_commit=SOURCE,application_sha256=APP_SHA,installed_metadata='NOT_SUPPLIED',selected_write_ranges=[],installation_authorized=False,hardware_access=False,device_authenticity_or_freshness_verified=False)
 require(not require_installed or (installed_table is not None and installed_ota is not None),'CURRENT_INSTALLED_METADATA_REQUIRED')
 require((installed_table is None)==(installed_ota is None),'BOTH_INSTALLED_METADATA_FILES_REQUIRED')
 if installed_table is not None:
  table(read(installed_table,4096),tool);ota(read(installed_ota,8192));out.update(installed_metadata='SUPPLIED_FILES_MATCH_SUPPORTED_LAYOUT_AND_APP0_INITIALIZER',plan_ready=True,selected_write_ranges=rows(selected),boot_selection_from_supplied_metadata='app0',metadata_provenance='OWNER_LOCAL_FILES_NOT_AUTHENTICATED_DEVICE_READ')
 return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--installed-table',type=pathlib.Path);p.add_argument('--installed-otadata',type=pathlib.Path);p.add_argument("--require-installed",action="store_true");p.add_argument("--image",choices=["application","rollback"],default="application");a=p.parse_args()
 try:print(json.dumps(validate(a.directory,a.installed_table,a.installed_otadata,a.require_installed,a.image),indent=2));return 0
 except (OSError,ValueError,KeyError,AssertionError) as e:
  print(json.dumps(dict(package_integrity='REJECTED',reason=str(e) if isinstance(e,Rejected) else 'INVALID_OR_MISSING_INPUT',installation_authorized=False,hardware_access=False)));return 1
if __name__=='__main__':raise SystemExit(main())
