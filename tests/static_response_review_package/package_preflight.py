# Static-response repair preflight: inherited image/layout/OTA/installer boundaries unchanged.
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
SUPPORT={'README.md','OWNER-CHECK.md','INSTALL-MAC.md','ROLLBACK-MAC.md','preflight.py','installer.py','install-macos.sh','rollback-macos.sh','gen_esp32part.py','APACHE-2.0.txt','source-LICENSE.txt','build-receipt.json','rollback-build-receipt.json','firmware-report.md','test-results.json','compatibility.md','owner-evidence.md','source-manifest.json','dependency-pin.json','reproduction.md','rm-shift.txt','rm-modifier-taps.txt','rm-stop.txt','rm-malformed.txt','privacy-source-manifest.json','dashboard-source-manifest.json','reviewed-editor-source-manifest.json','editor-build-source-manifest.json','build-inputs.json','source-attestation.json','response-source-manifest.json','static-response-build-source-manifest.json','postcompile-completion.json'}
ACTUAL_BUILD_ID='ROUTEB-STATIC-RESPONSE-REPAIR-v1'
EDITOR_BUILD_ID='ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
ORIGINAL_BASE='805d989c3ac50cb96025862c95916830c59f8ba7'
SOURCE_CHECKPOINT=RELEASE['firmware_source_commit'] if RELEASE else None
EDITOR_HEADER_SHA='df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445'
EXPECTED_RESOURCES={
 'INDEX_HTML':(12185,'e086c053bbc4439ad5b8515c9a42e516496ae65adcf32783cfefc9147ac66a58'),
 'INDEX_JS':(31933,'4268329ef9d387ca4732407b198e1a182f55a66d909a5a19f9fd60c099110d36'),
 'SETTINGS_HTML':(5390,'f545e9154b2cf8d5e6573075008a87704a786bceb44fc625376b7a7d64bdd4e8'),
 'SETTINGS_JS':(10503,'7ef1cc50fdbb772e7dedb2629c6004b744f5ef9b7a0e35f2abb7b93ceb2af686'),
 'STYLE_CSS':(31976,'572d65a22ddb9892bea169a8ea43ca078e3aa9207519b7cd58cb465de39428da')}
EXPECTED_WIRE={
 'INDEX_HTML':(12184,'149215865fe1ba4b12f20ebaf6bf4aae95070f20683e66298429d99572159026'),
 'SETTINGS_HTML':(5389,'ef9f7093b2e537dc18ab2100bc03c9cbc6a7b9886291ace5c1fcfa12c5c1ce3a'),
 'TERMINAL_HTML':(1324,'cd341048c6d0a1211bd8ff0670203d706f0247eab8c72db08243d5529ba89d51'),
 'CREDITS_HTML':(1746,'06d0f8e850c968b34a418d8b6462018811c0e7dd4d865f40c8c96644f87a2e8d'),
 'ERROR404_HTML':(869,'a8e89049a587a61fc7b2bcdd21ccedd578a4b1026df0e796be2a39108fc6da9d'),
 'STYLE_CSS':(31975,'37df80940a89fb76e7373a1f1cadb687551b068cc94e65d61a18e03100cbed50'),
 'INDEX_JS':(31932,'7fb8068beb12564dc4e5146e8b6b0a9b719b78caf3f4d94cd0f2b8a2c04baf39'),
 'SETTINGS_JS':(10502,'37cbfdbd4a4dafc50ec34c79fc862ec1c28ca69eb47d393d1f3d6e8e2101472f'),
 'TERMINAL_JS':(465,'22baafe8044c1aa1f63f8f2cd983763f4b0c0b30db1f74a988f81f15f9cc7d6b')}
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
 d=pathlib.Path(directory);m=json.loads(read(d/'manifest.json',1024*1024));require(m.get('package_id')=='evilduck-static-response-repair-h1-macos-review-v1' and m.get('source_commit')==SOURCE and m.get('installation_authorized') is False and m.get('update_method')=='FUTURE_ROM_APP_ONLY_BOTH_SLOTS','WRONG_PACKAGE_IDENTITY')
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
 require(static_pin.get('format')=='evilduck-static-response-build-integration-v1' and static_pin.get('build_id')==ACTUAL_BUILD_ID and static_pin.get('parent_manifest_sha256')==response_sha,'WRONG_STATIC_BUILD_BASE')
 require(static_pin.get('editor_manifest_sha256')==build_sha and static_pin.get('reviewed_editor_manifest_sha256')==editor_sha and static_pin.get('dashboard_manifest_sha256')==dashboard_sha and static_pin.get('privacy_manifest_sha256')==privacy_sha,'WRONG_STATIC_PARENT_PINS')
 require(len(static_pin['before'])==len(static_pin['after'])==3 and len(static_pin['unchanged'])==198 and {r['file'] for r in static_pin['after']}=={'webserver.cpp','webfiles.h','caps_trial.h'},'WRONG_STATIC_FINAL_SOURCE_DELTA')
 require({r['file']:r['sha256'] for r in static_pin['before']+static_pin['unchanged']}==privacy_sources,'WRONG_STATIC_COMPARISON_BASE')
 final_sources={r['file']:r['sha256'] for r in static_pin['after']+static_pin['unchanged']}
 require(len(final_sources)==201 and final_sources['webfiles.h']==EDITOR_HEADER_SHA and {n for n in final_sources if final_sources[n]!=response_sources[n]}=={'caps_trial.h'},'UNREVIEWED_STATIC_FINAL_DELTA')
 overrides={r['file']:r['sha256'] for r in static_pin['cumulative_h1_after']}
 require(len(static_pin['cumulative_h1_after'])==4 and set(overrides)=={'cli.cpp','webserver.cpp','webfiles.h','caps_trial.h'} and all(final_sources[n]==v for n,v in overrides.items()),'WRONG_STATIC_CUMULATIVE_H1_DELTA')
 require(receipt.get('static_response_source_pin')==response_pin and receipt.get('static_response_build_source_pin')==static_pin,'WRONG_LINKED_STATIC_SOURCE_PINS')
 actual_sources={r['file']:r['sha256'] for r in receipt['source_inventory']}
 require(len(receipt['source_inventory'])==201 and actual_sources=={'EvilDuckS3/'+n:v for n,v in final_sources.items()},'WRONG_STATIC_FINAL_SOURCE_INVENTORY')
 inputs_data=read(d/'build-inputs.json',1024*1024);inputs_sha=digest(inputs_data);inputs=json.loads(inputs_data)
 require(inputs_sha==RELEASE['build_inputs_sha256']==m.get('build_inputs_sha256'),'WRONG_COMMITTED_BUILD_INPUTS')
 require(inputs.get('format')=='evilduck-committed-build-inputs-v1' and inputs.get('source_commit')==SOURCE_CHECKPOINT and inputs.get('source_commit_contains_changes') is True and inputs.get('uncommitted_local_changes') is False,'WRONG_COMMITTED_BUILD_PROVENANCE')
 input_rows=inputs['files'];require(len(input_rows)==26 and len({r['file'] for r in input_rows})==26,'WRONG_COMMITTED_INPUT_COUNT')
 require(digest(json.dumps(input_rows,sort_keys=True,separators=(',',':')).encode())==inputs.get('files_sha256'),'WRONG_COMMITTED_FILE_LIST_DIGEST')
 for row in input_rows:
  require(set(row)=={'file','size','sha256'} and isinstance(row['file'],str) and not row['file'].startswith('/') and '..' not in row['file'].split('/') and isinstance(row['size'],int) and row['size']>=0 and isinstance(row['sha256'],str) and len(row['sha256'])==64,'INVALID_COMMITTED_INPUT_ROW')
 attestation_data=read(d/'source-attestation.json',1024*1024);attestation=json.loads(attestation_data)
 require(digest(attestation_data)==RELEASE['source_attestation_sha256']==m.get('source_attestation_sha256'),'WRONG_SOURCE_ATTESTATION')
 require(attestation.get('format')=='evilduck-committed-build-source-attestation-v1' and attestation.get('source_commit')==SOURCE_CHECKPOINT and attestation.get('git_blobs_verified') is True and attestation.get('source_commit_contains_changes') is True and attestation.get('source_checkpoint_after_build') is False,'WRONG_COMMITTED_CHECKPOINT')
 require(attestation.get('build_inputs_sha256')==inputs_sha and attestation.get('files')==input_rows and attestation.get('files_sha256')==inputs['files_sha256'] and attestation.get('hardware') is False,'WRONG_COMMITTED_SOURCE_ATTESTATION')
 delta=attestation['post_build_verifier_delta'];delta_sha=digest(json.dumps(delta,sort_keys=True,separators=(',',':')).encode())
 require(delta_sha==RELEASE['verification_delta_sha256']==m.get('verification_delta_sha256')==attestation.get('verification_delta_sha256'),'WRONG_EXACT_VERIFIER_ONLY_DELTA')
 require(attestation.get('verifier_context_commit')==m.get('verifier_context_commit')==delta.get('verifier_context_commit')==RELEASE['verifier_context_commit'] and RELEASE['verifier_context_commit']!=SOURCE_CHECKPOINT,'WRONG_VERIFIER_CONTEXT')
 require(delta.get('format')=='evilduck-static-response-host-verifier-delta-v1' and delta.get('compiler_source_commit')==SOURCE_CHECKPOINT and delta.get('role')=='HOST_VERIFICATION_ONLY' and delta.get('git_blobs_verified') is True,'FALSE_VERIFIER_ONLY_PROVENANCE')
 verifier_path='tests/static_response_build_integration/verify_target.py'
 originals=[r for r in input_rows if r['file']==verifier_path]
 require(len(originals)==1 and delta.get('file')==verifier_path and delta.get('before')==originals[0],'WRONG_ORIGINAL_VERIFIER_ROW')
 require(set(delta['after'])=={'file','size','sha256'} and delta['after'].get('file')==verifier_path and delta['after'].get('sha256')==RELEASE['static_target_verifier_sha256'] and isinstance(delta['after'].get('size'),int) and delta['after']['size']>0 and delta['after']['sha256']!=delta['before']['sha256'],'WRONG_NEW_VERIFIER_ROW')
 require(delta.get('original_compile_input_rows_verified')==26 and delta.get('other_compile_inputs_identical')==25 and delta.get('compiled_application_sources_changed') is False and delta.get('firmware_recompiled') is False and m.get('post_build_verifier_only_delta') is True,'UNAPPROVED_POST_BUILD_DELTA')
 require(m.get('firmware_source_identity_kind')=='COMMITTED_CLEAN_BUILD_INPUTS' and m.get('source_checkpoint_after_build') is False and m.get('status_label')=='NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED' and m.get('static_response_profile')=='STATIC_RESPONSE_REPAIR_H1_OWNER_REVIEW','WRONG_STATIC_REVIEW_SCOPE')
 require(m.get('application_elf_bytes')==RELEASE['application_elf_bytes'],'WRONG_STATIC_ELF_SIZE')
 require(m.get('previous_faulty_application_sha256')=='e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0' and m.get('previous_faulty_candidate_is_recovery') is False,'MISLABELED_FAULTY_RECOVERY')
 release=receipt['static_response_release_verification']
 require(release.get('status')=='PASS' and release.get('adapter_sha256')==RELEASE['static_release_adapter_sha256'] and release.get('full_frozen_h1_chain_executed') is True,'STATIC_RELEASE_NOT_VERIFIED')
 require(release.get('source_commit')==SOURCE_CHECKPOINT and release.get('source_commit_contains_changes') is True and release.get('build_inputs_sha256')==inputs_sha,'FALSE_STATIC_BUILD_PROVENANCE')
 require(release.get('assertions_preserved')==190 and release.get('assertions_removed')==0 and release.get('unrelated_expected_hashes_changed')==0 and release.get('historical_source_pin_build_ids_changed') is False,'REMOVED_STATIC_RELEASE_GUARDS')
 require(release.get('application_sha256')==APP_SHA and release.get('elf_sha256')==RELEASE['application_elf_sha256']==m.get('application_elf_sha256'),'WRONG_STATIC_RELEASE_ARTIFACTS')
 require(release.get('actual_runtime_build_id')==receipt.get('actual_runtime_build_id')==m.get('firmware_build_id')==ACTUAL_BUILD_ID,'WRONG_ACTUAL_STATIC_BUILD_ID')
 require(release.get('recompiled') is False and release.get('target_source_or_images_modified') is False and release.get('installed') is False and release.get('hardware') is False,'UNSUPPORTED_STATIC_PHYSICAL_CLAIM')
 events=release['compile_events']
 require([(e.get('logical_layer'),e.get('assertions_preserved')) for e in events]==[('right-modifier H1',23),('experimental H1',21),('bounded lock waits',16),('source/text v2',46),('keyboard/lock feedback',25),('caps/STOP closure',59)],'INCOMPLETE_FROZEN_H1_CHAIN')
 require(sum(len(e.get('expectation_adaptations',[])) for e in events)>0 and sum(len(e.get('runtime_identity_adaptations',[])) for e in events)>0,'MISSING_STATIC_ADAPTATION_AUDIT')
 adapter=receipt['static_response_target_adapter'];binding=release['static_response_target_binding']
 require(adapter.get('adapter_sha256')==RELEASE['static_build_adapter_sha256'] and adapter.get('source_commit')==SOURCE_CHECKPOINT and adapter.get('build_inputs_sha256')==inputs_sha and adapter.get('source_commit_contains_changes') is True and adapter.get('overlay_calls')==1 and adapter.get('clean_compile') is True and adapter.get('inherited_safety_predicates_removed')==0,'WRONG_STATIC_BUILD_ADAPTER')
 require(adapter.get('static_response_target_binding')==binding,'STATIC_TARGET_BINDING_DISAGREES')
 require(binding.get('status')=='PASS' and binding.get('source_files')==201 and binding.get('verifier_sha256')==RELEASE['static_target_verifier_sha256'] and binding.get('build_id')==ACTUAL_BUILD_ID and binding.get('application_sha256')==APP_SHA and binding.get('elf_sha256')==m.get('application_elf_sha256'),'WRONG_STATIC_TARGET_IDENTITY')
 verified_source=binding['committed_source_provenance']
 expected_delta=dict(path=delta['file'],compile_source_commit=SOURCE_CHECKPOINT,verification_context_commit=RELEASE['verifier_context_commit'],compile_size=delta['before']['size'],compile_sha256=delta['before']['sha256'],verification_size=delta['after']['size'],verification_sha256=delta['after']['sha256'],git_compile_blob_verified=True,git_verifier_blob_verified=True)
 require(verified_source.get('verifier_context_commit')==RELEASE['verifier_context_commit'] and verified_source.get('post_compile_verifier_delta')==expected_delta,'VERIFIER_CONTEXT_DISAGREES_WITH_TARGET_PROOF')
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
 require(digest(json.dumps(binding,sort_keys=True,separators=(',',':')).encode())==RELEASE['static_target_binding_sha256'],'WRONG_EXACT_STATIC_TARGET_BINDING')
 require(binding.get('source_commit')==SOURCE_CHECKPOINT and binding.get('build_inputs_sha256')==inputs_sha,'WRONG_STATIC_TARGET_SOURCE_CONTEXT')
 resources=binding['bundled_resources'];require(len(resources)==5 and {r['resource'] for r in resources}==set(EXPECTED_RESOURCES),'WRONG_BUNDLED_RESOURCE_INVENTORY')
 appdata=read(d/'application.bin',APP_BYTES)
 for row in resources:
  length,expected_sha=EXPECTED_RESOURCES[row['resource']];offset=row.get('binary_offset')
  require(row.get('bytes_including_nul')==length and row.get('sha256')==expected_sha and row.get('elf_occurrences')==row.get('binary_occurrences')==1 and isinstance(offset,int) and offset>=0 and offset+length<=len(appdata),'WRONG_BUNDLED_RESOURCE_PROOF')
  data=appdata[offset:offset+length]
  require(data[-1:]==b'\0' and digest(data)==expected_sha and appdata.count(data)==1 and digest(data[:-1])==EXPECTED_WIRE[row['resource']][1],'PACKAGED_RESOURCE_BYTES_MISMATCH')
 require(digest(read(d/'build-receipt.json',4*1024*1024))==RELEASE['static_release_receipt_sha256'],'WRONG_EXACT_STATIC_RELEASE_RECEIPT')
 completion_data=read(d/'postcompile-completion.json',4*1024*1024);completion=json.loads(completion_data)
 require(digest(completion_data)==RELEASE['completion_receipt_sha256']==m.get('completion_receipt_sha256'),'WRONG_EXACT_POSTCOMPILE_COMPLETION')
 require(completion.get('status')=='PASS' and completion.get('actual_compile_source_commit')==SOURCE_CHECKPOINT and completion.get('verifier_context_commit')==RELEASE['verifier_context_commit'] and completion.get('post_compile_verifier_delta')==expected_delta,'WRONG_POSTCOMPILE_CONTEXT')
 require(completion.get('firmware_recompiled') is False and completion.get('hardware') is False and completion.get('unchanged_source_entries')==201,'UNSUPPORTED_COMPLETION_CLAIM')
 require(completion.get('immutable_artifacts')==dict(application_sha256=APP_SHA,elf_sha256=m.get('application_elf_sha256'),inputs_sha256=inputs_sha) and completion.get('release_receipt_sha256')==RELEASE['static_release_receipt_sha256'],'COMPLETION_ARTIFACTS_CHANGED')
 completion_adapter=completion['post_compile_completion_adapter']
 require(completion_adapter.get('helper_sha256')==RELEASE['completion_helper_sha256']==m.get('completion_helper_sha256') and completion_adapter.get('firmware_compilation_prefix_rerun') is False and completion_adapter.get('all_target_and_release_predicates_after_compile_preserved') is True,'WRONG_POSTCOMPILE_HELPER')
 helper=attestation['postcompile_completion_helper']
 require(helper.get('file')=='tests/static_response_postlink/complete_existing.py' and helper.get('source_commit')==RELEASE['completion_context_commit']==m.get('completion_context_commit') and helper.get('sha256')==RELEASE['completion_helper_sha256'] and helper.get('git_blob_verified') is True and helper.get('role')=='HOST_POSTCOMPILE_COMPLETION_ONLY','WRONG_COMPLETION_HELPER_PROVENANCE')
 queries=completion['read_only_compiler_queries'];require(len(queries)==1,'WRONG_COMPILER_QUERY_COUNT')
 for query in queries:
  require(query.get('command')==[receipt['link_command'][0],'-print-prog-name=ld'] and query.get('classification')=='READ_ONLY_PINNED_LINKER_LOCATION_QUERY' and query.get('pinned_compiler_sha256')==receipt['compiler_sha256'],'UNREVIEWED_COMPILER_QUERY')
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
