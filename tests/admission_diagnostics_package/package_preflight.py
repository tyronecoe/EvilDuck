# Admission diagnostics additive preflight over immutable observer-v2 parent SHA256 232ef2673fcc9e29082c13c5d3c52412369f4f656c663e0a70ec9c209a994ee0
# Observer v2 additive package; immutable v1 parent SHA256 c5e8384ee40653c5b017685ce81431bc7eca4718e1a8f8b5c864ab86aff37a47
# USB enumeration observer capture package over immutable DEFINE parent 5fbe1fa388759810f40bceeb2dbaa3d16efe633352364ec4ae550ddd12fecfd7
# Bounded DEFINE-label package over immutable DEL parent 241b40e3f8284615cca8bd870022754039024a3d4d5e8316535fac5118f3b50d
# Additive DEL-alias review package; immutable REPEAT parent d095130bfb73d75ab708be338df97739227f129cecfe2a4fb60226a94f71ab29
# Bounded REPEAT preflight: inherited image/layout/OTA/installer boundaries unchanged.
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
import argparse, hashlib, importlib.util, io, json, pathlib, stat, struct, sys, zipfile, zlib
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
SUPPORT={'README.md','OWNER-CHECK.md','INSTALL-MAC.md','ROLLBACK-MAC.md','preflight.py','installer.py','install-macos.sh','rollback-macos.sh','gen_esp32part.py','APACHE-2.0.txt','source-LICENSE.txt','build-receipt.json','rollback-build-receipt.json','firmware-report.md','test-results.json','compatibility.md','owner-evidence.md','source-manifest.json','dependency-pin.json','reproduction.md','rm-shift.txt','rm-modifier-taps.txt','rm-stop.txt','rm-malformed.txt','privacy-source-manifest.json','dashboard-source-manifest.json','reviewed-editor-source-manifest.json','editor-build-source-manifest.json','build-inputs.json','source-attestation.json','response-source-manifest.json','static-response-build-source-manifest.json','previous-repeat-source-manifest.json','previous-repeat-release-source-manifest.json','native-test-receipt.json','web-test-receipt.json','current-del-regression-receipt.json','current-define-regression-receipt.json','del-source-manifest.json','del-release-source-manifest.json','del-test-receipt.json','define-source-manifest.json','define-release-source-manifest.json','define-test-receipt.json','del-owner-closeout.md','D01_DEFINE_27.txt','D02_DEFINE_31.txt','D03_DEFINE_32_Rejected.txt','observer-source-manifest.json','observer-web-source-manifest.json','observer-release-source-manifest.json','observer-v2-source-manifest.json','observer-v2-web-source-manifest.json','observer-v2-release-source-manifest.json','observer-test-receipt.json','observer-web-test-receipt.json','CAPTURE-CONTRACT.md','evidence-gate.json','observer-v1-export-0.json','observer-v1-export-1.json','observer-v1-export-2.json','observer-v1-export-3.json','observer-v1-export-4.json','observer-v1-owner-handoff.txt','define-owner-acceptance.md','working-define-labels-macos-review-v1.zip','RETURN-WORKING.md'}
SUPPORT |= {'admission-source-manifest.json','admission-release-source-manifest.json','admission-test-receipt.json','admission-negative-controls.json','FIXTURE-SHA256.txt','AD00_PRIOR_COMPILE_LINE5.txt','AD01_INVALID_BYTE_LINE3.duck','AD02_VALID_RECOVERY.txt','BYTE-FIXTURES.md'}
ACTUAL_BUILD_ID='ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1'
WORKING_ZIP_FILE='working-define-labels-macos-review-v1.zip'
WORKING_ZIP_BYTES=2691374
WORKING_ZIP_SHA='b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed'
WORKING_APP_BYTES=1438048
WORKING_APP_SHA='167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30'
WORKING_RETURN=dict(role='WORKING_DEFINE_RETURN',file=WORKING_ZIP_FILE,bytes=WORKING_ZIP_BYTES,sha256=WORKING_ZIP_SHA,build_id='ROUTEB-DEFINE-LABELS-H1-v1',application_bytes=WORKING_APP_BYTES,application_sha256=WORKING_APP_SHA,older_rollback_sha256=ROLLBACK_SHA,method='EXTRACT_SEPARATE_FOLDER_AND_USE_UNCHANGED_GUARDED_KIT')
EDITOR_BUILD_ID='ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
ORIGINAL_BASE='805d989c3ac50cb96025862c95916830c59f8ba7'
SOURCE_CHECKPOINT=RELEASE['firmware_source_commit'] if RELEASE else None
EDITOR_HEADER_SHA='df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445'
EXPECTED_RESOURCES={'INDEX_HTML': (13145, 'b12d84e89f88d1f9565192cebc940b79e4de0ee94b41f8ba186579843c571ed8'), 'INDEX_JS': (34649, 'd7fa4bcdf0d49f5770c09ffedd3515ddcbb6dbaad5f5a55091240d7c313e0cfa'), 'SETTINGS_HTML': (5390, 'f545e9154b2cf8d5e6573075008a87704a786bceb44fc625376b7a7d64bdd4e8'), 'SETTINGS_JS': (10503, '7ef1cc50fdbb772e7dedb2629c6004b744f5ef9b7a0e35f2abb7b93ceb2af686'), 'STYLE_CSS': (31976, '572d65a22ddb9892bea169a8ea43ca078e3aa9207519b7cd58cb465de39428da')}
EXPECTED_WIRE={'INDEX_HTML': (13144, '790a671f3feca307df39b200cdd4fd9ae27d0e8b4ca13d825328f25e400fe5eb'), 'SETTINGS_HTML': (5389, 'ef9f7093b2e537dc18ab2100bc03c9cbc6a7b9886291ace5c1fcfa12c5c1ce3a'), 'TERMINAL_HTML': (1324, 'cd341048c6d0a1211bd8ff0670203d706f0247eab8c72db08243d5529ba89d51'), 'CREDITS_HTML': (1746, '06d0f8e850c968b34a418d8b6462018811c0e7dd4d865f40c8c96644f87a2e8d'), 'ERROR404_HTML': (869, 'a8e89049a587a61fc7b2bcdd21ccedd578a4b1026df0e796be2a39108fc6da9d'), 'STYLE_CSS': (31975, '37df80940a89fb76e7373a1f1cadb687551b068cc94e65d61a18e03100cbed50'), 'INDEX_JS': (34648, '681192a3aa5474d4a313779ea9a661a2b234c73965f12030145bef7fbcf4409f'), 'SETTINGS_JS': (10502, '37cbfdbd4a4dafc50ec34c79fc862ec1c28ca69eb47d393d1f3d6e8e2101472f'), 'TERMINAL_JS': (465, '22baafe8044c1aa1f63f8f2cd983763f4b0c0b30db1f74a988f81f15f9cc7d6b')}
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
 d=pathlib.Path(directory);m=json.loads(read(d/'manifest.json',1024*1024));require(m.get('package_id')=='evilduck-routeb-admission-diagnostics-h1-macos-review-v1' and m.get('source_commit')==SOURCE and m.get('installation_authorized') is False and m.get('update_method')=='FUTURE_ROM_APP_ONLY_BOTH_SLOTS','WRONG_PACKAGE_IDENTITY')
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
 require(m.get('firmware_source_commit')==RELEASE['firmware_source_commit'] and m.get('firmware_build_id')==ACTUAL_BUILD_ID,'WRONG_H1_FIRMWARE_IDENTITY')
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
 require(build_pin.get('format')=='evilduck-editor-build-integration-v1' and build_pin.get('baseline')==ORIGINAL_BASE and build_pin.get('build_id')==EDITOR_BUILD_ID and build_pin.get('comparison_base')=='privacy-fix1','WRONG_EDITOR_BUILD_BASE')
 require(build_pin.get('privacy_manifest_sha256')==privacy_sha and build_pin.get('dashboard_manifest_sha256')==dashboard_sha and build_pin.get('reviewed_editor_manifest_sha256')==editor_sha,'WRONG_EDITOR_BUILD_PARENT_PINS')
 require(len(build_pin['before'])==len(build_pin['after'])==2 and len(build_pin['unchanged'])==199 and {r['file'] for r in build_pin['after']}=={'webfiles.h','caps_trial.h'},'WRONG_EDITOR_FINAL_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in build_pin['before']+build_pin['unchanged']}==privacy_sources,'WRONG_EDITOR_FINAL_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in build_pin['after']+build_pin['unchanged']}
 require(len(final_sources)==201 and final_sources['webfiles.h']==EDITOR_HEADER_SHA and {n for n in final_sources if final_sources[n]!=reviewed_sources[n]}=={'caps_trial.h'},'UNREVIEWED_EDITOR_FINAL_DELTA')
 overrides={r['file']:r['sha256'] for r in build_pin['cumulative_h1_after']}
 require(len(build_pin['cumulative_h1_after'])==4 and set(overrides)=={'cli.cpp','webserver.cpp','webfiles.h','caps_trial.h'} and all(final_sources[n]==v for n,v in overrides.items()),'WRONG_EDITOR_CUMULATIVE_H1_DELTA')
 require(receipt.get('reviewed_editor_source_pin')==editor_pin and receipt.get('editor_build_source_pin')==build_pin and receipt.get('privacy_source_pin')==privacy_pin,'WRONG_LINKED_EDITOR_SOURCE_PINS')
 # All older manifests above remain historical parent layers.
 response_data=read(d/'response-source-manifest.json',1024*1024);response_sha=digest(response_data);response_pin=json.loads(response_data)
 require(response_sha==RELEASE['response_pin_sha256']==m.get('response_composition_pin_sha256'),'WRONG_RESPONSE_SOURCE_PIN')
 require(response_pin.get('format')=='evilduck-dashboard-static-response-source-only-v1' and response_pin.get('baseline')=='e692435a7c70dbc0d917bbff733c57900cf7d57c' and response_pin.get('parent_manifest_sha256')==build_sha,'WRONG_RESPONSE_SOURCE_BASE')
 require(len(response_pin['before'])==len(response_pin['after'])==1 and len(response_pin['unchanged'])==200 and response_pin['after'][0]['file']=='webserver.cpp','WRONG_RESPONSE_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in response_pin['before']+response_pin['unchanged']}==final_sources,'WRONG_RESPONSE_EDITOR_PARENT')
 response_sources={r['file']:r['sha256'] for r in response_pin['after']+response_pin['unchanged']}
 require(len(response_sources)==201 and response_sources['webfiles.h']==EDITOR_HEADER_SHA and response_pin.get('portable_url_aliases')==12 and response_pin.get('distinct_literals')==9 and response_pin.get('static_send_replacements')==11,'WRONG_REVIEWED_RESPONSE_SCOPE')
 static_data=read(d/'static-response-build-source-manifest.json',1024*1024);static_sha=digest(static_data);static_pin=json.loads(static_data)
 require(static_sha==RELEASE['static_build_pin_sha256']==m.get('static_response_build_pin_sha256'),'WRONG_STATIC_BUILD_PIN')
 require(static_pin.get('format')=='evilduck-static-response-build-integration-v1' and static_pin.get('build_id')=='ROUTEB-STATIC-RESPONSE-REPAIR-v1' and static_pin.get('parent_manifest_sha256')==response_sha,'WRONG_STATIC_BUILD_BASE')
 require(static_pin.get('editor_manifest_sha256')==build_sha and static_pin.get('reviewed_editor_manifest_sha256')==editor_sha and static_pin.get('dashboard_manifest_sha256')==dashboard_sha and static_pin.get('privacy_manifest_sha256')==privacy_sha,'WRONG_STATIC_PARENT_PINS')
 require(len(static_pin['before'])==len(static_pin['after'])==3 and len(static_pin['unchanged'])==198 and {r['file'] for r in static_pin['after']}=={'webserver.cpp','webfiles.h','caps_trial.h'},'WRONG_STATIC_FINAL_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in static_pin['before']+static_pin['unchanged']}==privacy_sources,'WRONG_STATIC_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in static_pin['after']+static_pin['unchanged']}
 require(len(final_sources)==201 and final_sources['webfiles.h']==EDITOR_HEADER_SHA and {n for n in final_sources if final_sources[n]!=response_sources[n]}=={'caps_trial.h'},'UNREVIEWED_STATIC_FINAL_DELTA')
 overrides={r['file']:r['sha256'] for r in static_pin['cumulative_h1_after']}
 require(len(static_pin['cumulative_h1_after'])==4 and set(overrides)=={'cli.cpp','webserver.cpp','webfiles.h','caps_trial.h'} and all(final_sources[n]==v for n,v in overrides.items()),'WRONG_STATIC_CUMULATIVE_H1_DELTA')
 require(receipt.get('static_response_source_pin')==response_pin and receipt.get('static_response_build_source_pin')==static_pin,'WRONG_LINKED_STATIC_SOURCE_PINS')
 # The static-response source remains a historical parent. The compiler delta
 # and final metadata identity are individually pinned and cannot be omitted.
 repeat_data=read(d/'previous-repeat-source-manifest.json',1024*1024);repeat_sha=digest(repeat_data);repeat_pin=json.loads(repeat_data)
 require(repeat_sha==RELEASE['repeat_source_pin_sha256']==m.get('repeat_source_pin_sha256'),'WRONG_REPEAT_SOURCE_PIN')
 require(repeat_pin.get('format')=='evilduck-previous-command-repeat-source-only-v1' and repeat_pin.get('parent_manifest_sha256')==static_sha,'WRONG_REPEAT_SOURCE_PARENT')
 require(len(repeat_pin['before'])==len(repeat_pin['after'])==1 and len(repeat_pin['unchanged'])==200 and repeat_pin['after'][0]['file']=='core.cpp','WRONG_REPEAT_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in repeat_pin['before']+repeat_pin['unchanged']}==final_sources,'WRONG_REPEAT_STATIC_PARENT')
 repeat_sources={r['file']:r['sha256'] for r in repeat_pin['after']+repeat_pin['unchanged']}
 require(len(repeat_sources)==201 and {n for n in repeat_sources if repeat_sources[n]!=final_sources[n]}=={'core.cpp'} and repeat_sources['core.cpp']==RELEASE['repeat_core_sha256'],'UNREVIEWED_REPEAT_COMPILER_DELTA')
 release_pin_data=read(d/'previous-repeat-release-source-manifest.json',1024*1024);release_pin_sha=digest(release_pin_data);release_pin=json.loads(release_pin_data)
 require(release_pin_sha==RELEASE['repeat_release_pin_sha256']==m.get('repeat_release_pin_sha256'),'WRONG_REPEAT_RELEASE_PIN')
 require(release_pin.get('format')=='evilduck-previous-command-repeat-release-v1' and release_pin.get('build_id')=='ROUTEB-PREVIOUS-COMMAND-REPEAT-v1' and release_pin.get('parent_manifest_sha256')==repeat_sha,'WRONG_REPEAT_RELEASE_BASE')
 require(len(release_pin['before'])==len(release_pin['after'])==4 and len(release_pin['unchanged'])==197 and {r['file'] for r in release_pin['after']}=={'core.cpp','webserver.cpp','webfiles.h','caps_trial.h'},'WRONG_REPEAT_RELEASE_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in release_pin['before']+release_pin['unchanged']}==privacy_sources,'WRONG_REPEAT_RELEASE_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in release_pin['after']+release_pin['unchanged']}
 require(len(final_sources)==201 and {n for n in final_sources if final_sources[n]!=repeat_sources[n]}=={'caps_trial.h'} and final_sources['core.cpp']==RELEASE['repeat_core_sha256'],'UNREVIEWED_REPEAT_RELEASE_IDENTITY_DELTA')
 require(receipt.get('previous_repeat_source_pin')==repeat_pin and receipt.get('previous_repeat_build_source_pin')==release_pin,'WRONG_LINKED_REPEAT_PINS')
 # DEL is a separate bounded source delta over the exact historical REPEAT release.
 del_data=read(d/'del-source-manifest.json',1024*1024);del_sha=digest(del_data);del_pin=json.loads(del_data)
 require(del_sha==RELEASE['del_source_pin_sha256']==m.get('del_source_pin_sha256'),'WRONG_DEL_SOURCE_PIN')
 require(del_pin.get('format')=='evilduck-del-alias-source-v1' and del_pin.get('baseline_commit')=='557dc81f65b672d5b701b681664ef6ff0a7e5d44' and del_pin.get('parent_manifest_sha256')==release_pin_sha,'WRONG_DEL_SOURCE_BASE')
 require(len(del_pin['before'])==len(del_pin['after'])==2 and len(del_pin['unchanged'])==199 and {r['file'] for r in del_pin['after']}=={'core.cpp','shortcut_keys.h'},'WRONG_DEL_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in del_pin['before']+del_pin['unchanged']}==final_sources,'WRONG_DEL_REPEAT_PARENT')
 del_sources={r['file']:r['sha256'] for r in del_pin['after']+del_pin['unchanged']}
 require(len(del_sources)==201 and {n for n in del_sources if del_sources[n]!=final_sources[n]}=={'core.cpp','shortcut_keys.h'} and del_sources['core.cpp']==RELEASE['del_core_sha256'] and del_sources['shortcut_keys.h']==RELEASE['del_shortcuts_sha256'],'UNREVIEWED_DEL_SOURCE_DELTA')
 del_release_data=read(d/'del-release-source-manifest.json',1024*1024);del_release_sha=digest(del_release_data);del_release=json.loads(del_release_data)
 require(del_release_sha==RELEASE['del_release_pin_sha256']==m.get('del_release_pin_sha256'),'WRONG_DEL_RELEASE_PIN')
 require(del_release.get('format')=='evilduck-del-alias-release-v1' and del_release.get('build_id')=='ROUTEB-DEL-ALIAS-H1-v1' and del_release.get('parent_manifest_sha256')==del_sha,'WRONG_DEL_RELEASE_BASE')
 require(len(del_release['before'])==len(del_release['after'])==5 and len(del_release['unchanged'])==196 and {r['file'] for r in del_release['after']}=={'core.cpp','shortcut_keys.h','webfiles.h','webserver.cpp','caps_trial.h'},'WRONG_DEL_RELEASE_DELTA')
 require({r['file']:r['sha256'] for r in del_release['before']+del_release['unchanged']}==privacy_sources,'WRONG_DEL_RELEASE_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in del_release['after']+del_release['unchanged']}
 require(len(final_sources)==201 and {n for n in final_sources if final_sources[n]!=del_sources[n]}=={'caps_trial.h'},'UNREVIEWED_DEL_RELEASE_IDENTITY_DELTA')
 require(receipt.get('del_alias_source_pin')==del_pin and receipt.get('del_alias_build_source_pin')==del_release,'WRONG_LINKED_DEL_PINS')
 require(m.get('del_alias_profile')=='DEL_ALIAS_H1_OWNER_REVIEW','WRONG_DEL_REVIEW_SCOPE')
 # Bounded DEFINE label cells: separate source delta over the historical DEL release.
 define_data=read(d/'define-source-manifest.json',1024*1024);define_sha=digest(define_data);define_pin=json.loads(define_data)
 require(define_sha==RELEASE['define_source_pin_sha256']==m.get('define_source_pin_sha256'),'WRONG_DEFINE_SOURCE_PIN')
 require(define_pin.get('format')=='evilduck-define-labels-source-v1' and define_pin.get('baseline')=='6bcfb605c8249b63be2be9f79a00e4e81863fbf6' and define_pin.get('parent_manifest_sha256')==del_release_sha,'WRONG_DEFINE_SOURCE_BASE')
 require(len(define_pin['before'])==len(define_pin['after'])==1 and len(define_pin['unchanged'])==200 and define_pin['after'][0]['file']=='core.cpp','WRONG_DEFINE_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in define_pin['before']+define_pin['unchanged']}==final_sources,'WRONG_DEFINE_DEL_PARENT')
 define_sources={r['file']:r['sha256'] for r in define_pin['after']+define_pin['unchanged']}
 require(len(define_sources)==201 and {n for n in define_sources if define_sources[n]!=final_sources[n]}=={'core.cpp'} and define_sources['core.cpp']==RELEASE['define_core_sha256'],'UNREVIEWED_DEFINE_SOURCE_DELTA')
 define_release_data=read(d/'define-release-source-manifest.json',1024*1024);define_release_sha=digest(define_release_data);define_release=json.loads(define_release_data)
 require(define_release_sha==RELEASE['define_release_pin_sha256']==m.get('define_release_pin_sha256'),'WRONG_DEFINE_RELEASE_PIN')
 require(define_release.get('format')=='evilduck-define-labels-release-v1' and define_release.get('build_id')=='ROUTEB-DEFINE-LABELS-H1-v1' and define_release.get('parent_manifest_sha256')==define_sha,'WRONG_DEFINE_RELEASE_BASE')
 require(len(define_release['before'])==len(define_release['after'])==5 and len(define_release['unchanged'])==196 and {r['file'] for r in define_release['after']}=={'core.cpp','shortcut_keys.h','webfiles.h','webserver.cpp','caps_trial.h'},'WRONG_DEFINE_RELEASE_DELTA')
 require({r['file']:r['sha256'] for r in define_release['before']+define_release['unchanged']}==privacy_sources,'WRONG_DEFINE_RELEASE_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in define_release['after']+define_release['unchanged']}
 require(len(final_sources)==201 and {n for n in final_sources if final_sources[n]!=define_sources[n]}=={'caps_trial.h'},'UNREVIEWED_DEFINE_RELEASE_IDENTITY_DELTA')
 require(receipt.get('define_labels_source_pin')==define_pin and receipt.get('define_labels_build_source_pin')==define_release,'WRONG_LINKED_DEFINE_PINS')
 require(m.get('define_labels_profile')=='DEFINE_LABELS_H1_OWNER_REVIEW','WRONG_DEFINE_REVIEW_SCOPE')
 # Capture-only observer extends the immutable DEFINE parent; no OS rule is admitted.
 observer_data=read(d/'observer-source-manifest.json',1024*1024);observer_sha=digest(observer_data);observer_pin=json.loads(observer_data)
 require(observer_sha==RELEASE['observer_source_pin_sha256']==m.get('observer_source_pin_sha256'),'WRONG_OBSERVER_SOURCE_PIN')
 require(observer_pin.get('format')=='evilduck-usb-os-observer-source-v1' and observer_pin.get('baseline')=='bdc8cbeea024ebb63f952da7fc4f39ac9e32fe29' and observer_pin.get('parent_manifest_sha256')==define_release_sha,'WRONG_OBSERVER_SOURCE_BASE')
 require(observer_pin.get('source_count')==201 and len(observer_pin['before'])==len(observer_pin['after'])==2 and len(observer_pin['unchanged'])==199 and {r['file'] for r in observer_pin['after']}=={'hid_backend.cpp','hid_backend.h'},'WRONG_OBSERVER_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in observer_pin['before']+observer_pin['unchanged']}==final_sources,'WRONG_OBSERVER_DEFINE_PARENT')
 observer_sources={r['file']:r['sha256'] for r in observer_pin['after']+observer_pin['unchanged']}
 require(len(observer_sources)==201 and {n for n in observer_sources if observer_sources[n]!=final_sources[n]}=={'hid_backend.cpp','hid_backend.h'},'UNREVIEWED_OBSERVER_SOURCE_DELTA')
 observer_web_data=read(d/'observer-web-source-manifest.json',1024*1024);observer_web_sha=digest(observer_web_data);observer_web=json.loads(observer_web_data)
 require(observer_web_sha==RELEASE['observer_web_pin_sha256']==m.get('observer_web_pin_sha256'),'WRONG_OBSERVER_WEB_PIN')
 require(observer_web.get('format')=='evilduck-usb-os-observer-web-v1' and observer_web.get('baseline')=='bdc8cbeea024ebb63f952da7fc4f39ac9e32fe29' and observer_web.get('parent_manifest_sha256')==observer_sha,'WRONG_OBSERVER_WEB_BASE')
 require(observer_web.get('source_count')==201 and len(observer_web['before'])==len(observer_web['after'])==2 and len(observer_web['unchanged'])==199 and {r['file'] for r in observer_web['after']}=={'webserver.cpp','webfiles.h'},'WRONG_OBSERVER_WEB_DELTA')
 require({r['file']:r['sha256'] for r in observer_web['before']+observer_web['unchanged']}==observer_sources,'WRONG_OBSERVER_WEB_PARENT')
 observer_web_sources={r['file']:r['sha256'] for r in observer_web['after']+observer_web['unchanged']}
 require(len(observer_web_sources)==201 and {n for n in observer_web_sources if observer_web_sources[n]!=observer_sources[n]}=={'webserver.cpp','webfiles.h'},'UNREVIEWED_OBSERVER_WEB_DELTA')
 observer_release_data=read(d/'observer-release-source-manifest.json',1024*1024);observer_release_sha=digest(observer_release_data);observer_release=json.loads(observer_release_data)
 require(observer_release_sha==RELEASE['observer_release_pin_sha256']==m.get('observer_release_pin_sha256'),'WRONG_OBSERVER_RELEASE_PIN')
 require(observer_release.get('parent_manifest_sha256')==observer_web_sha,'WRONG_OBSERVER_RELEASE_PARENT')
 require(observer_release.get('build_id')=='ROUTEB-USB-ENUM-OBSERVER-H1-v1' and len(observer_release['before'])==len(observer_release['after'])==7 and len(observer_release['unchanged'])==194 and {r['file'] for r in observer_release['after']}=={'core.cpp','shortcut_keys.h','webfiles.h','webserver.cpp','caps_trial.h','hid_backend.cpp','hid_backend.h'},'WRONG_OBSERVER_RELEASE_DELTA')
 require({r['file']:r['sha256'] for r in observer_release['before']+observer_release['unchanged']}==privacy_sources,'WRONG_OBSERVER_RELEASE_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in observer_release['after']+observer_release['unchanged']}
 require(len(final_sources)==201 and {n for n in final_sources if final_sources[n]!=observer_web_sources[n]}=={'caps_trial.h'},'UNREVIEWED_OBSERVER_RELEASE_IDENTITY_DELTA')
 require(receipt.get('usb_observer_source_pin')==observer_pin and receipt.get('usb_observer_web_source_pin')==observer_web and receipt.get('usb_observer_build_source_pin')==observer_release,'WRONG_LINKED_OBSERVER_PINS')
 require(m.get('usb_observer_profile')=='USB_ENUM_OBSERVER_CAPTURE_ONLY' and m.get('classifier_implemented') is False,'WRONG_OBSERVER_CAPTURE_ONLY_SCOPE')
 # V1 evidence remains historical. The approved v2 delta extends that exact release.
 observer_v2_data=read(d/'observer-v2-source-manifest.json',1024*1024);observer_v2_sha=digest(observer_v2_data);observer_v2=json.loads(observer_v2_data)
 require(observer_v2_sha==RELEASE['observer_v2_source_pin_sha256']==m.get('observer_v2_source_pin_sha256'),'WRONG_OBSERVER_V2_SOURCE_PIN')
 require(observer_v2.get('format')=='evilduck-usb-os-observer-source-v2' and observer_v2.get('baseline')=='fe6ed1c291a2af234793cca86aa9b8c979ac6d8e' and observer_v2.get('parent_manifest_sha256')==observer_release_sha,'WRONG_OBSERVER_V2_SOURCE_BASE')
 require(observer_v2.get('source_count')==201 and len(observer_v2['before'])==len(observer_v2['after'])==2 and len(observer_v2['unchanged'])==199 and {r['file'] for r in observer_v2['after']}=={'hid_backend.cpp','hid_backend.h'},'WRONG_OBSERVER_V2_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in observer_v2['before']+observer_v2['unchanged']}==final_sources,'WRONG_OBSERVER_V2_V1_PARENT')
 observer_v2_sources={r['file']:r['sha256'] for r in observer_v2['after']+observer_v2['unchanged']}
 require(len(observer_v2_sources)==201 and {n for n in observer_v2_sources if observer_v2_sources[n]!=final_sources[n]}=={'hid_backend.cpp','hid_backend.h'},'UNREVIEWED_OBSERVER_V2_SOURCE_DELTA')
 observer_v2_web_data=read(d/'observer-v2-web-source-manifest.json',1024*1024);observer_v2_web_sha=digest(observer_v2_web_data);observer_v2_web=json.loads(observer_v2_web_data)
 require(observer_v2_web_sha==RELEASE['observer_v2_web_pin_sha256']==m.get('observer_v2_web_pin_sha256'),'WRONG_OBSERVER_V2_WEB_PIN')
 require(observer_v2_web.get('format')=='evilduck-usb-os-observer-web-v2' and observer_v2_web.get('baseline')=='fe6ed1c291a2af234793cca86aa9b8c979ac6d8e' and observer_v2_web.get('parent_manifest_sha256')==observer_v2_sha,'WRONG_OBSERVER_V2_WEB_BASE')
 require(observer_v2_web.get('source_count')==201 and len(observer_v2_web['before'])==len(observer_v2_web['after'])==2 and len(observer_v2_web['unchanged'])==199 and {r['file'] for r in observer_v2_web['after']}=={'webserver.cpp','webfiles.h'},'WRONG_OBSERVER_V2_WEB_DELTA')
 require({r['file']:r['sha256'] for r in observer_v2_web['before']+observer_v2_web['unchanged']}==observer_v2_sources,'WRONG_OBSERVER_V2_WEB_PARENT')
 observer_v2_web_sources={r['file']:r['sha256'] for r in observer_v2_web['after']+observer_v2_web['unchanged']}
 require(len(observer_v2_web_sources)==201 and {n for n in observer_v2_web_sources if observer_v2_web_sources[n]!=observer_v2_sources[n]}=={'webserver.cpp','webfiles.h'},'UNREVIEWED_OBSERVER_V2_WEB_DELTA')
 observer_v2_release_data=read(d/'observer-v2-release-source-manifest.json',1024*1024);observer_v2_release_sha=digest(observer_v2_release_data);observer_v2_release=json.loads(observer_v2_release_data)
 require(observer_v2_release_sha==RELEASE['observer_v2_release_pin_sha256']==m.get('observer_v2_release_pin_sha256'),'WRONG_OBSERVER_V2_RELEASE_PIN')
 require(observer_v2_release.get('format')=='evilduck-usb-os-observer-release-v2' and observer_v2_release.get('parent_manifest_sha256')==observer_v2_web_sha,'WRONG_OBSERVER_V2_RELEASE_PARENT')
 require(observer_v2_release.get('build_id')=='ROUTEB-USB-ENUM-OBSERVER-H1-v2' and len(observer_v2_release['before'])==len(observer_v2_release['after'])==7 and len(observer_v2_release['unchanged'])==194 and {r['file'] for r in observer_v2_release['after']}=={'core.cpp','shortcut_keys.h','webfiles.h','webserver.cpp','caps_trial.h','hid_backend.cpp','hid_backend.h'},'WRONG_OBSERVER_V2_RELEASE_DELTA')
 require({r['file']:r['sha256'] for r in observer_v2_release['before']+observer_v2_release['unchanged']}==privacy_sources,'WRONG_OBSERVER_V2_RELEASE_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in observer_v2_release['after']+observer_v2_release['unchanged']}
 require(len(final_sources)==201 and {n for n in final_sources if final_sources[n]!=observer_v2_web_sources[n]}=={'caps_trial.h'},'UNREVIEWED_OBSERVER_V2_RELEASE_IDENTITY_DELTA')
 require(receipt.get('usb_observer_v2_source_pin')==observer_v2 and receipt.get('usb_observer_v2_web_source_pin')==observer_v2_web and receipt.get('usb_observer_v2_build_source_pin')==observer_v2_release,'WRONG_LINKED_OBSERVER_V2_PINS')
 observer_sources=observer_v2_sources;observer_web_sources=observer_v2_web_sources
 admission_data=read(d/'admission-source-manifest.json',1024*1024);admission_sha=digest(admission_data);admission=json.loads(admission_data)
 require(admission_sha==RELEASE['admission_source_pin_sha256']==m.get('admission_source_pin_sha256'),'WRONG_ADMISSION_SOURCE_PIN')
 require(admission.get('format')=='evilduck-routeb-admission-diagnostics-source-v1' and admission.get('parent_manifest_sha256')==observer_v2_release_sha,'WRONG_ADMISSION_SOURCE_BASE')
 require(admission.get('source_count')==201 and len(admission['before'])==len(admission['after'])==2 and len(admission['unchanged'])==199 and {r['file'] for r in admission['after']}=={'adapter.cpp','adapter.h'},'WRONG_ADMISSION_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in admission['before']+admission['unchanged']}==final_sources,'WRONG_ADMISSION_PARENT')
 admission_sources={r['file']:r['sha256'] for r in admission['after']+admission['unchanged']}
 require({n for n in admission_sources if admission_sources[n]!=final_sources[n]}=={'adapter.cpp','adapter.h'},'UNREVIEWED_ADMISSION_DELTA')
 admission_release_data=read(d/'admission-release-source-manifest.json',1024*1024);admission_release_sha=digest(admission_release_data);admission_release=json.loads(admission_release_data)
 require(admission_release_sha==RELEASE['admission_release_pin_sha256']==m.get('admission_release_pin_sha256'),'WRONG_ADMISSION_RELEASE_PIN')
 require(admission_release.get('format')=='evilduck-routeb-admission-diagnostics-release-v1','WRONG_ADMISSION_RELEASE_FORMAT')
 require(admission_release.get('parent_manifest_sha256')==admission_sha and admission_release.get('build_id')==ACTUAL_BUILD_ID,'WRONG_ADMISSION_RELEASE_PARENT')
 require(len(admission_release['before'])==len(admission_release['after'])==9 and len(admission_release['unchanged'])==192,'WRONG_ADMISSION_RELEASE_DELTA')
 require({r['file']:r['sha256'] for r in admission_release['before']+admission_release['unchanged']}==privacy_sources,'WRONG_ADMISSION_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in admission_release['after']+admission_release['unchanged']}
 require(len(final_sources)==201 and {n for n in final_sources if final_sources[n]!=admission_sources[n]}=={'caps_trial.h'},'UNREVIEWED_ADMISSION_IDENTITY_DELTA')
 require(receipt.get('admission_diagnostics_source_pin')==admission and receipt.get('admission_diagnostics_build_source_pin')==admission_release,'WRONG_LINKED_ADMISSION_PINS')
 require(m.get('admission_profile')=='ROUTEB_ADMISSION_DIAGNOSTICS_V1','WRONG_ADMISSION_SCOPE')
 actual_sources={r['file']:r['sha256'] for r in receipt['source_inventory']}
 require(len(receipt['source_inventory'])==201 and actual_sources=={'EvilDuckS3/'+n:v for n,v in final_sources.items()},'WRONG_STATIC_FINAL_SOURCE_INVENTORY')
 inputs_data=read(d/'build-inputs.json',1024*1024);inputs_sha=digest(inputs_data);inputs=json.loads(inputs_data)
 require(inputs_sha==RELEASE['build_inputs_sha256']==m.get('build_inputs_sha256'),'WRONG_COMMITTED_BUILD_INPUTS')
 require(inputs.get('format')=='evilduck-committed-build-inputs-v1' and inputs.get('source_commit')==SOURCE_CHECKPOINT and inputs.get('source_commit_contains_changes') is True and inputs.get('uncommitted_local_changes') is False,'WRONG_COMMITTED_BUILD_PROVENANCE')
 input_rows=inputs['files'];require(len(input_rows)==RELEASE['build_input_count'] and len({r['file'] for r in input_rows})==RELEASE['build_input_count'],'WRONG_COMMITTED_INPUT_COUNT')
 require(digest(json.dumps(input_rows,sort_keys=True,separators=(',',':')).encode())==inputs.get('files_sha256'),'WRONG_COMMITTED_FILE_LIST_DIGEST')
 for row in input_rows:
  require(set(row)=={'file','size','sha256'} and isinstance(row['file'],str) and not row['file'].startswith('/') and '..' not in row['file'].split('/') and isinstance(row['size'],int) and row['size']>=0 and isinstance(row['sha256'],str) and len(row['sha256'])==64,'INVALID_COMMITTED_INPUT_ROW')
 attestation_data=read(d/'source-attestation.json',1024*1024);attestation=json.loads(attestation_data)
 require(digest(attestation_data)==RELEASE['source_attestation_sha256']==m.get('source_attestation_sha256'),'WRONG_SOURCE_ATTESTATION')
 require(attestation.get('format')=='evilduck-committed-build-source-attestation-v1' and attestation.get('source_commit')==SOURCE_CHECKPOINT and attestation.get('git_blobs_verified') is True and attestation.get('source_commit_contains_changes') is True and attestation.get('source_checkpoint_after_build') is False,'WRONG_COMMITTED_CHECKPOINT')
 require(attestation.get('build_inputs_sha256')==inputs_sha and attestation.get('files')==input_rows and attestation.get('files_sha256')==inputs['files_sha256'] and attestation.get('hardware') is False,'WRONG_COMMITTED_SOURCE_ATTESTATION')
 require(attestation.get('verifier_context_commit')==m.get('verifier_context_commit')==RELEASE['verifier_context_commit']==SOURCE_CHECKPOINT,'WRONG_VERIFIER_CONTEXT')
 require(attestation.get('post_build_verifier_delta') is None and m.get('post_build_verifier_only_delta') is False and RELEASE['post_compile_verifier_delta'] is None,'UNAPPROVED_POST_BUILD_DELTA')
 require(attestation.get('verification_source_policy')=='SAME_CHECKPOINT_NO_POSTBUILD_DELTA' and attestation.get('original_compile_input_rows_verified')==RELEASE['build_input_count'],'FALSE_SAME_CHECKPOINT_PROVENANCE')
 verifier_path='tests/admission_diagnostics_release/verify_target.py'
 originals=[r for r in input_rows if r['file']==verifier_path]
 require(len(originals)==1 and originals[0]['sha256']==RELEASE['repeat_target_verifier_sha256'],'WRONG_COMMITTED_VERIFIER_ROW')
 require(attestation.get('committed_verifier')==originals[0] and attestation.get('all_compile_inputs_identical') is True,'CHANGED_COMPILE_INPUT_AFTER_BUILD')
 require(m.get('firmware_source_identity_kind')=='COMMITTED_CLEAN_BUILD_INPUTS' and m.get('source_checkpoint_after_build') is False and m.get('status_label')=='NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED' and m.get('previous_repeat_profile')=='PREVIOUS_COMMAND_REPEAT_H1_OWNER_REVIEW','WRONG_STATIC_REVIEW_SCOPE')
 require(m.get('application_elf_bytes')==RELEASE['application_elf_bytes'],'WRONG_STATIC_ELF_SIZE')
 require(m.get('previous_faulty_application_sha256')=='e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0' and m.get('previous_faulty_candidate_is_recovery') is False,'MISLABELED_FAULTY_RECOVERY')
 release=receipt['usb_observer_release_verification']
 require(release.get('status')=='PASS' and release.get('adapter_sha256')==RELEASE['repeat_release_adapter_sha256'] and release.get('full_frozen_h1_chain_executed') is True,'STATIC_RELEASE_NOT_VERIFIED')
 require(release.get('source_commit')==SOURCE_CHECKPOINT and release.get('source_commit_contains_changes') is True and release.get('build_inputs_sha256')==inputs_sha,'FALSE_STATIC_BUILD_PROVENANCE')
 require(release.get('assertions_preserved')==190 and release.get('assertions_removed')==0 and release.get('unrelated_expected_hashes_changed')==0 and release.get('historical_source_pin_build_ids_changed') is False,'REMOVED_STATIC_RELEASE_GUARDS')
 require(release.get('application_sha256')==APP_SHA and release.get('elf_sha256')==RELEASE['application_elf_sha256']==m.get('application_elf_sha256'),'WRONG_STATIC_RELEASE_ARTIFACTS')
 require(release.get('actual_runtime_build_id')==receipt.get('actual_runtime_build_id')==m.get('firmware_build_id')==ACTUAL_BUILD_ID,'WRONG_ACTUAL_STATIC_BUILD_ID')
 require(release.get('recompiled') is False and release.get('target_source_or_images_modified') is False and release.get('installed') is False and release.get('hardware') is False,'UNSUPPORTED_STATIC_PHYSICAL_CLAIM')
 events=release['compile_events']
 require([(e.get('logical_layer'),e.get('assertions_preserved')) for e in events]==[('right-modifier H1',23),('experimental H1',21),('bounded lock waits',16),('source/text v2',46),('keyboard/lock feedback',25),('caps/STOP closure',59)],'INCOMPLETE_FROZEN_H1_CHAIN')
 require(sum(len(e.get('expectation_adaptations',[])) for e in events)>0 and sum(len(e.get('runtime_identity_adaptations',[])) for e in events)>0,'MISSING_STATIC_ADAPTATION_AUDIT')
 handler_changes=[r for e in events for r in e.get('compiler_handler_adaptations',[])]
 require(len(handler_changes)==2 and all(r.get('logical_layer')=='right-modifier H1' and r.get('before')=='ds_preview::Compiler::statement(' and r.get('after')=='ds_preview::Compiler::statementImpl(' and r.get('filename','').endswith('/tests/h1_right_modifiers/verify_link.py') for r in handler_changes),'UNREVIEWED_COMPILER_HANDLER_RETARGET')
 adapter=receipt['usb_observer_target_adapter'];binding=release['usb_observer_target_binding']
 require(adapter.get('adapter_sha256')==RELEASE['repeat_build_adapter_sha256'] and adapter.get('source_commit')==SOURCE_CHECKPOINT and adapter.get('build_inputs_sha256')==inputs_sha and adapter.get('source_commit_contains_changes') is True and adapter.get('overlay_calls')==1 and adapter.get('clean_compile') is True and adapter.get('inherited_safety_predicates_removed')==0,'WRONG_STATIC_BUILD_ADAPTER')
 require(adapter.get('usb_observer_target_binding')==binding,'STATIC_TARGET_BINDING_DISAGREES')
 require(binding.get('status')=='PASS' and binding.get('source_files')==201 and binding.get('verifier_sha256')==RELEASE['repeat_target_verifier_sha256'] and binding.get('build_id')==ACTUAL_BUILD_ID and binding.get('application_sha256')==APP_SHA and binding.get('elf_sha256')==m.get('application_elf_sha256'),'WRONG_STATIC_TARGET_IDENTITY')
 verified_source=binding['committed_source_provenance']
 require(verified_source.get('verifier_context_commit')==SOURCE_CHECKPOINT and verified_source.get('post_compile_verifier_delta') is None and verified_source.get('source_commit_contains_changes') is True and verified_source.get('uncommitted_local_changes') is False,'VERIFIER_CONTEXT_DISAGREES_WITH_TARGET_PROOF')
 streaming=binding['streaming_response']
 require(streaming.get('status')=='PASS' and streaming.get('asset_overload')=='const uint8_t*+size_t' and streaming.get('actual_elf_sha256')==m.get('application_elf_sha256'),'STATIC_STREAMING_NOT_VERIFIED')
 require(streaming.get('hardware') is False and streaming.get('actual_ESP32_heap_measured') is False,'UNSUPPORTED_STREAMING_PHYSICAL_CLAIM')
 compiled=streaming['compiled_object'];handler=streaming['linked_handler'];factory=streaming['linked_factory'];fill=streaming['fill_buffer']
 require(compiled.get('byte_overload_observed') is True and compiled.get('char_send_P_absent') is True and compiled.get('unknown_path_char_response_allowed') is True and set(compiled.get('resources',[]))==set(EXPECTED_WIRE),'WRONG_COMPILED_ASSET_DISPATCH')
 require(pathlib.Path(compiled['file']).name=='webserver.cpp.o' and handler.get('name','').startswith('handleStatic(') and handler.get('size',0)>0,'WRONG_STATIC_HANDLER_OBJECT')
 require(factory.get('progmem_ctor_observed') is True and factory.get('full_resource_string_copy') is False and 'beginResponse(' in factory.get('name','') and 'unsigned char const*' in factory.get('name',''),'FULL_RESOURCE_COPY_OR_WRONG_FACTORY')
 require('AsyncProgmemResponse::_fillBuffer(' in fill.get('name','') and fill.get('size',0)>0,'WRONG_STREAMING_FILL_BUFFER')
 for proof in [handler,factory,fill]:
  require(isinstance(proof.get('disassembly_sha256'),str) and len(proof['disassembly_sha256'])==64 and isinstance(proof.get('address'),int) and proof['size']>0,'INVALID_LINKED_STREAMING_PROOF')
 linked={r['file']:r['sha256'] for r in receipt['linked_input_hashes']}
 require(linked.get(compiled['file'])==compiled['sha256'],'STREAMING_OBJECT_NOT_LINKED')
 sdk=streaming['sdk_consumers'];require(len(sdk)==2 and {pathlib.Path(r['source']).name for r in sdk}=={'WebRequest.cpp','WebResponses.cpp'},'MISSING_STREAMING_SDK_CONSUMERS')
 expected_sdk={pathlib.Path(n).name:v for n,v in response_pin['sdk_pins'].items()}
 for row in sdk:
  require(row.get('linked') is True and expected_sdk.get(pathlib.Path(row['source']).name)==row.get('source_sha256') and linked.get(row['object'])==row.get('object_sha256'),'WRONG_LINKED_STREAMING_SDK')
 calls=streaming['compiled_asset_call_witnesses']
 require(len(calls)==10 and {r['resource'] for r in calls}==set(EXPECTED_WIRE) and len({r['object_call_offset'] for r in calls})==10,'WRONG_COMPILED_ASSET_CALL_WITNESSES')
 for row in calls:
  require(row.get('http_bytes')==EXPECTED_WIRE[row['resource']][0] and isinstance(row.get('object_call_offset'),int) and row['object_call_offset']>=0 and len(row.get('pointer_instructions',[]))>0 and len(row.get('length_instructions',[]))>0,'WRONG_COMPILED_ASSET_ARGUMENTS')
 wire=streaming['pointer_length_table'];require(len(wire)==9 and {r['resource'] for r in wire}==set(EXPECTED_WIRE),'WRONG_COMPILED_POINTER_LENGTH_TABLE')
 for row in wire:
  require((row.get('http_bytes'),row.get('sha256'))==EXPECTED_WIRE[row['resource']] and row.get('compiled_pointer_observed') is True and row.get('compiled_length_observed') is True and row.get('c_nul_excluded') is True,'WRONG_COMPILED_WIRE_RESOURCE')
 require(digest(json.dumps(binding,sort_keys=True,separators=(',',':')).encode())==RELEASE['repeat_target_binding_sha256'],'WRONG_EXACT_STATIC_TARGET_BINDING')
 require(binding.get('source_commit')==SOURCE_CHECKPOINT and binding.get('build_inputs_sha256')==inputs_sha,'WRONG_STATIC_TARGET_SOURCE_CONTEXT')
 resources=binding['bundled_resources'];require(len(resources)==5 and {r['resource'] for r in resources}==set(EXPECTED_RESOURCES),'WRONG_BUNDLED_RESOURCE_INVENTORY')
 appdata=read(d/'application.bin',APP_BYTES)
 for row in resources:
  length,expected_sha=EXPECTED_RESOURCES[row['resource']];offset=row.get('binary_offset')
  require(row.get('bytes_including_nul')==length and row.get('sha256')==expected_sha and row.get('elf_occurrences')==row.get('binary_occurrences')==1 and isinstance(offset,int) and offset>=0 and offset+length<=len(appdata),'WRONG_BUNDLED_RESOURCE_PROOF')
  data=appdata[offset:offset+length]
  require(data[-1:]==b'\0' and digest(data)==expected_sha and appdata.count(data)==1 and digest(data[:-1])==EXPECTED_WIRE[row['resource']][1],'PACKAGED_RESOURCE_BYTES_MISMATCH')
 require(digest(read(d/'build-receipt.json',4*1024*1024))==RELEASE['repeat_release_receipt_sha256'],'WRONG_EXACT_STATIC_RELEASE_RECEIPT')
 proof=binding['previous_command_repeat']
 require(proof.get('status')=='PASS' and proof.get('source')=='core.cpp' and proof.get('source_sha256')==final_sources['core.cpp'],'WRONG_COMPILED_REPEAT_SOURCE')
 require(proof.get('compiled_from_final_source') is True and proof.get('object_linked') is True and proof.get('standalone_branch_verified') is True and proof.get('hardware') is False,'STANDALONE_REPEAT_NOT_PROVEN')
 require(proof.get('modifier_handler_reachable') is True and len(proof.get('modifier_handler_call_edges',[]))>0 and all(r.get('opcode')=='call8' and r.get('callee')=='ds_shortcut::modifier(char const*)' for r in proof['modifier_handler_call_edges']),'MODIFIER_HANDLER_NOT_REACHABLE')
 require(pathlib.Path(proof['object_file']).name=='core.cpp.o' and linked.get(proof['object_file'])==proof.get('object_sha256'),'REPEAT_OBJECT_NOT_LINKED')
 require(len(proof.get('linked_symbols',[]))>=2 and all(isinstance(r.get('name'),str) and isinstance(r.get('address'),int) and r.get('size',0)>0 and len(r.get('disassembly_sha256',''))==64 for r in proof['linked_symbols']),'REPEAT_LINKED_SYMBOL_PROOF_MISSING')
 alias=binding['del_alias']
 require(alias.get('status')=='PASS' and alias.get('report_id')==1 and alias.get('usage')==0x4c and alias.get('alias')=='DEL' and alias.get('equivalent')=='DELETE','DEL_ALIAS_NOT_PROVEN')
 require(alias.get('source_header_sha256')==final_sources['shortcut_keys.h']==RELEASE['del_shortcuts_sha256'] and alias.get('compiled_header_dependency_verified') is True and alias.get('compiler_calls_named') is True,'DEL_HEADER_NOT_COMPILED')
 require(alias.get('table_begin_end_loaded') is True and alias.get('row_stride')==8 and alias.get('usage_offset')==4 and alias.get('del_function_name_policy_source_verified') is True,'DEL_EXECUTABLE_TABLE_NOT_PROVEN')
 alias_rows=alias.get('decoded_table',[]);alias_map={r['name']:r['usage'] for r in alias_rows}
 require(len(alias_rows)==len(alias_map) and alias_map.get('DEL')==alias_map.get('DELETE')==0x4c,'WRONG_LINKED_DEL_MAPPING')
 require(alias.get('actual_elf_sha256')==m.get('application_elf_sha256') and alias.get('hardware') is False and isinstance(alias.get('named_disassembly_sha256'),str) and len(alias['named_disassembly_sha256'])==64,'WRONG_DEL_ELF_WITNESS')
 del_tests_data=read(d/'del-test-receipt.json',4*1024*1024);del_tests=json.loads(del_tests_data)
 require(digest(del_tests_data)==RELEASE['del_test_receipt_sha256'] and del_tests.get('status')=='PASS' and del_tests['counts'].get('FAIL')==0 and del_tests.get('hardware') is False and del_tests.get('real_hid') is False and del_tests.get('target_firmware_built') is False,'WRONG_DEL_SOFTWARE_RECEIPT')
 require(del_tests.get('causal_control',{}).get('status')=='PASS' and del_tests.get('compile_exit')==0 and del_tests.get('compile_stderr')=='' and len(del_tests.get('results',[]))>0 and all(r.get('status')=='PASS' and r.get('exit')==0 and r.get('stderr')=='' for r in del_tests['results']),'DEL_SOFTWARE_CHECKS_NOT_CLEAN')
 focused_sources={(r['file'][len('EvilDuckS3/'):] if r['file'].startswith('EvilDuckS3/') else r['file']):r['sha256'] for r in del_tests['full_source_inventory']}
 require(len(del_tests['full_source_inventory'])==201 and focused_sources==del_sources,'WRONG_DEL_SOFTWARE_SOURCE_INVENTORY')
 define_proof=binding['define_labels']
 require(define_proof.get('status')=='PASS' and define_proof.get('constant_cell_bytes')==32 and define_proof.get('max_label_bytes')==31 and define_proof.get('constant_slots')==16,'DEFINE_LAYOUT_NOT_PROVEN')
 require(define_proof.get('workspace_bytes')==4096 and define_proof.get('workspace_static_assert_retained') is True,'DEFINE_WORKSPACE_GUARD_NOT_PROVEN')
 require(isinstance(define_proof.get('target_compiler_bytes'),int) and define_proof['target_compiler_bytes']<=4096 and define_proof.get('target_compiler_alignment',0)>0,'DEFINE_TARGET_LAYOUT_NOT_MEASURED')
 require(define_proof.get('baseline_target_compiler_bytes')==3800 and define_proof['target_compiler_bytes']==3928,'UNEXPECTED_DEFINE_TARGET_WORKSPACE')
 define_tests_data=read(d/'define-test-receipt.json',4*1024*1024);define_tests=json.loads(define_tests_data)
 require(digest(define_tests_data)==RELEASE['define_test_receipt_sha256'] and define_tests.get('status')=='PASS' and define_tests['counts'].get('FAIL')==0 and define_tests.get('hardware') is False and define_tests.get('real_hid') is False and define_tests.get('target_firmware_built') is False,'WRONG_DEFINE_SOFTWARE_RECEIPT')
 require(define_tests.get('compile_exit')==0 and define_tests.get('compile_stderr')=='' and len(define_tests.get('results',[]))>0 and all(r.get('status')=='PASS' and r.get('exit')==0 and r.get('stderr')=='' for r in define_tests['results']),'DEFINE_SOFTWARE_CHECKS_NOT_CLEAN')
 define_focused_sources={(r['file'][len('EvilDuckS3/'):] if r['file'].startswith('EvilDuckS3/') else r['file']):r['sha256'] for r in define_tests['full_source_inventory']}
 require(len(define_tests['full_source_inventory'])==201 and define_focused_sources==define_sources,'WRONG_DEFINE_SOFTWARE_SOURCE_INVENTORY')
 tests_data=read(d/'test-results.json',4*1024*1024);tests=json.loads(tests_data)
 require(digest(tests_data)==RELEASE['test_results_sha256'] and tests.get('status')=='PASS' and tests.get('hardware_access') is False and tests.get('target_build') is False,'WRONG_FINAL_SOFTWARE_RESULTS')
 for label,filename in [('native','native-test-receipt.json'),('web','web-test-receipt.json'),('del','current-del-regression-receipt.json'),('define','current-define-regression-receipt.json')]:
  require(tests['groups'][label].get('exit')==0 and tests['groups'][label].get('stderr')=='' and digest(read(d/filename,4*1024*1024))==tests['groups'][label].get('receipt_sha256'),'WRONG_RAW_SOFTWARE_RECEIPT')
 observer_proof=binding['usb_observer']
 require(observer_proof.get('status')=='PASS' and observer_proof.get('capture_only') is True and observer_proof.get('classification')=='UNKNOWN' and observer_proof.get('reason')=='NO_VALIDATED_RULE','USB_OBSERVER_NOT_PROVEN')
 require(observer_proof.get('source_backend_sha256')==final_sources['hid_backend.cpp'] and observer_proof.get('source_header_sha256')==final_sources['hid_backend.h'] and observer_proof.get('actual_elf_sha256')==m.get('application_elf_sha256'),'WRONG_OBSERVER_SOURCE_OR_ELF')
 require(all(observer_proof.get(k) is True for k in ['explicit_compile_selector','actual_link_wrap_flag','original_handler_called_once','dcd_calls_wrapper','original_event_arguments_source_pinned','sdk_sources_unchanged','early_bss_state','dynamic_observer_initialization_absent']),'OBSERVER_TRANSPARENCY_NOT_PROVEN')
 require(observer_proof.get('max_records')==64 and observer_proof.get('window_ms')==5000 and observer_proof.get('state_budget_bytes')==2048 and 0<observer_proof.get('dedicated_state_bytes',0)<=2048,'WRONG_OBSERVER_BOUNDS')
 require(observer_proof.get('callback_frame_budget')==256 and 0<observer_proof.get('callback_max_frame',0)<=256 and len(observer_proof.get('stack_frames',[]))>0,'OBSERVER_STACK_NOT_PROVEN')
 require(observer_proof.get('physical') is False and observer_proof.get('installed') is False and observer_proof.get('target_execution') is False,'UNSUPPORTED_OBSERVER_PHYSICAL_CLAIM')
 require('-DEVILDUCK_USB_ENUM_OBSERVER=1' in receipt['report']['verified_cpp_extra_flags'].split(),'MISSING_USB_OBSERVER_SELECTOR')
 for filename,key,expected_sources in [('observer-test-receipt.json','observer_test_receipt_sha256',observer_sources),('observer-web-test-receipt.json','observer_web_test_receipt_sha256',observer_web_sources)]:
  data=read(d/filename,4*1024*1024);focused=json.loads(data)
  require(digest(data)==RELEASE[key] and focused.get('status')=='PASS' and focused.get('counts',{}).get('FAIL')==0,'WRONG_OBSERVER_SOFTWARE_RECEIPT')
  require(focused.get('hardware',focused.get('hardware_access')) is False and focused.get('real_hid',False) is False,'UNSUPPORTED_OBSERVER_PHYSICAL_CLAIM')
  inventory=focused.get('full_source_inventory',[]);actual_focused={(r['file'][len('EvilDuckS3/'):] if r['file'].startswith('EvilDuckS3/') else r['file']):r['sha256'] for r in inventory}
  require(len(inventory)==201 and actual_focused==expected_sources,'WRONG_OBSERVER_SOFTWARE_SOURCE_INVENTORY')
 v2=observer_proof.get('v2_contract',{})
 require(v2.get('schema')=='evilduck-usb-observer-v2' and v2.get('window_ms')==5000 and v2.get('diagnostic_tail_ms')==5000 and v2.get('total_ms')==10000,'WRONG_OBSERVER_V2_CONTRACT_BOUNDS')
 require(all(v2.get(k) is True for k in ['immutable_deadline_source_pinned','generation_tagged_samples_source_pinned','timestamped_records_source_pinned','first_unsupported_witness_source_pinned','tail_cannot_revalidate_source_pinned']),'OBSERVER_V2_CONTRACT_NOT_PROVEN')
 require(observer_proof.get('state_plus_callback_bytes',2049)<=2048 and observer_proof.get('actual_setup_path_verified') is True,'OBSERVER_V2_TARGET_BOUNDS_OR_SETUP_NOT_PROVEN')
 clock=observer_proof.get('clock_api',{})
 require(clock.get('status')=='PASS' and clock.get('actual_call_reachable') is True and clock.get('api_in_iram') is True and clock.get('clock_available_before_usb_source_pinned') is True and clock.get('runtime_latency_measured') is False,'OBSERVER_V2_CLOCK_NOT_PROVEN')
 require(clock.get('api',{}).get('name')=='esp_timer_get_time' and len(clock.get('external_clock_entry_frames',[]))>0,'OBSERVER_V2_CLOCK_ACCOUNTING_MISSING')
 # Historical owner exports are original v1 evidence, never new schema or held-out input.
 owner_data=read(d/'evidence-gate.json',1024*1024);owner=json.loads(owner_data)
 require(digest(owner_data)==RELEASE['owner_evidence_sha256'],'WRONG_V1_OWNER_EVIDENCE_DIGEST')
 require(owner.get('format')=='evilduck-observer-v1-owner-evidence-v1' and owner.get('source_publication')=='fe6ed1c291a2af234793cca86aa9b8c979ac6d8e' and owner.get('source_firmware_checkpoint')=='7472de1e0edf123a9fcdf9d1d4feb1b38250280e' and owner.get('source_application_sha256')=='e60af8a1b53ab2ba9e7c79b4ff821719ddd06a0a55384dd987288c4189aed6a9','WRONG_V1_OWNER_EVIDENCE_IDENTITY')
 require(owner.get('distinct_boots')==3 and owner.get('held_out_captures_remaining')==0 and len(owner.get('exports',[]))==5,'WRONG_V1_OWNER_EVIDENCE_SCOPE')
 require(digest(read(d/'observer-v1-owner-handoff.txt',1024*1024))==owner.get('handoff_sha256'),'WRONG_V1_OWNER_HANDOFF')
 historical=[]
 for i,row in enumerate(owner['exports']):
  original=read(d/('observer-v1-export-'+str(i)+'.json'),1024*1024)
  require(digest(original)==row.get('sha256'),'WRONG_V1_OWNER_EXPORT_BYTES')
  recorded=json.loads(original)
  require(recorded.get('schema')=='evilduck-usb-observer-v1' and recorded.get('buildId')=='ROUTEB-USB-ENUM-OBSERVER-H1-v1' and recorded.get('classification')=='UNKNOWN' and recorded.get('classificationReason')=='NO_VALIDATED_RULE','WRONG_V1_OWNER_EXPORT_SCHEMA_OR_CLAIM')
  historical.append(recorded)
 require(len({x['bootMarker'] for x in historical})==3 and all({k:v for k,v in x.items() if k!='contextCapturedAtMs'}=={k:v for k,v in historical[0].items() if k!='contextCapturedAtMs'} for x in historical[:3]),'WRONG_V1_OWNER_CAPTURE_GROUPING')
 # Working return is an exact original reviewed kit, not a relabelled old rollback.
 require(m.get('working_firmware_return')==WORKING_RETURN,'WRONG_WORKING_RETURN_IDENTITY')
 working=read(d/WORKING_ZIP_FILE,WORKING_ZIP_BYTES)
 require(len(working)==WORKING_ZIP_BYTES and digest(working)==WORKING_ZIP_SHA,'WRONG_WORKING_RETURN_ZIP')
 with zipfile.ZipFile(io.BytesIO(working)) as return_zip:
  require(return_zip.testzip() is None and len(return_zip.infolist())==50,'INVALID_WORKING_RETURN_ARCHIVE')
  for item in return_zip.infolist():
   selected_path=pathlib.PurePosixPath(item.filename)
   require(not selected_path.is_absolute() and '..' not in selected_path.parts and not stat.S_ISLNK(item.external_attr>>16),'UNSAFE_WORKING_RETURN_ARCHIVE')
  return_manifest=json.loads(return_zip.read('manifest.json'))
  require(return_manifest.get('firmware_build_id')=='ROUTEB-DEFINE-LABELS-H1-v1','WRONG_WORKING_RETURN_BUILD_ID')
  working_app=return_zip.read('application.bin');working_rollback=return_zip.read('rollback-application.bin')
  require(len(working_app)==WORKING_APP_BYTES and digest(working_app)==WORKING_APP_SHA,'WRONG_WORKING_RETURN_APPLICATION')
  require(len(working_rollback)==ROLLBACK_BYTES and digest(working_rollback)==ROLLBACK_SHA,'WRONG_WORKING_RETURN_OLDER_ROLLBACK')
  for name in ['preflight.py','installer.py','install-macos.sh','rollback-macos.sh','INSTALL-MAC.md']:
   contents=return_zip.read(name);declared=return_manifest['support_files'][name]
   require(len(contents)==declared['bytes'] and digest(contents)==declared['sha256'],'WRONG_WORKING_RETURN_HELPER')
 admission_tests_data=read(d/'admission-test-receipt.json',4*1024*1024);admission_tests=json.loads(admission_tests_data)
 require(digest(admission_tests_data)==RELEASE['admission_test_receipt_sha256'] and admission_tests.get('status')=='PASS','WRONG_ADMISSION_SOFTWARE_RECEIPT')
 negative_data=read(d/'admission-negative-controls.json',4*1024*1024);negative=json.loads(negative_data)
 require(digest(negative_data)==RELEASE['negative_control_receipt_sha256'] and negative.get('status')=='PASS','WRONG_ADMISSION_NEGATIVE_CONTROLS')
 require(all(admission_tests.get(k,False) is False for k in ['hardware','hardware_access','real_hid','target_firmware_built']),'UNSUPPORTED_ADMISSION_PHYSICAL_CLAIM')
 require(admission_tests.get('compile_exit')==0 and admission_tests.get('compile_stderr')=='' and admission_tests.get('counts',{}).get('FAIL')==0 and len(admission_tests.get('results',[]))>0 and all(r.get('status')=='PASS' and r.get('exit')==0 and r.get('stderr')=='' for r in admission_tests['results']),'ADMISSION_SOFTWARE_CHECKS_NOT_CLEAN')
 require({r['file']:r['sha256'] for r in admission_tests['full_source_inventory']}==actual_sources and len(admission_tests['full_source_inventory'])==201,'WRONG_ADMISSION_SOFTWARE_INVENTORY')
 require(negative.get('counts')=={'PASS':2,'FAIL':0} and negative.get('source_checkpoint')=='b075e551e07f7b15124bdad3caa564c614f78ba4' and negative.get('hardware') is False,'WRONG_NEGATIVE_CONTROL_SCOPE')
 observed={r['id']:r['observation'] for r in negative['results']}
 require(set(observed)=={'N01','N02'} and all(o.get('rejected') is True and o.get('report_delta')==0 and o.get('expected_code')==2 and o.get('expected_line')==1 for o in observed.values()),'NEGATIVE_CONTROLS_NOT_REPRODUCED')
 require(observed['N01']['observed_code']==observed['N01']['observed_line']==0 and observed['N02']['observed_code']==observed['N02']['prior_code']==15 and observed['N02']['observed_line']==observed['N02']['prior_line']==3,'WRONG_PREF1X_DIAGNOSTIC_OBSERVATIONS')

 proof=binding.get('admission_diagnostics',{})
 require(proof.get('status')=='PASS' and proof.get('existing_error_code')==2 and proof.get('coordinator_source_unchanged') is True and proof.get('status_schema_unchanged') is True and proof.get('source_acceptance_unchanged') is True and proof.get('compiler_workspace_bytes')==4096 and {r['file'] for r in proof.get('compiled_units',[])}=={'adapter.cpp','coordinator.cpp'},'ADMISSION_LINK_NOT_PROVEN')
 expected_fixture_names={'AD00_PRIOR_COMPILE_LINE5.txt','AD01_INVALID_BYTE_LINE3.duck','AD02_VALID_RECOVERY.txt'}
 fixture_lines=read(d/'FIXTURE-SHA256.txt',2048).decode('ascii').splitlines()
 require(len(fixture_lines)==3 and {x.split('  ',1)[1] for x in fixture_lines}==expected_fixture_names,'WRONG_ADMISSION_FIXTURE_INVENTORY')
 for row in fixture_lines:
  expected_hash,name=row.split('  ',1);require(digest(read(d/name,1024))==expected_hash,'WRONG_ADMISSION_FIXTURE_BYTES')
 require(read(d/'AD01_INVALID_BYTE_LINE3.duck',1024)==b'REM byte-exact admission diagnostic\r\nREM line two\nSTRING \xc3\xa9\n','WRONG_INVALID_BYTE_FIXTURE')
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
