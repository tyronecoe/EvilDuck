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
SUPPORT={'README.md','OWNER-CHECK.md','INSTALL-MAC.md','ROLLBACK-MAC.md','preflight.py','installer.py','install-macos.sh','rollback-macos.sh','gen_esp32part.py','APACHE-2.0.txt','source-LICENSE.txt','build-receipt.json','rollback-build-receipt.json','firmware-report.md','test-results.json','compatibility.md','owner-evidence.md','source-manifest.json','dependency-pin.json','reproduction.md','h1-fixed-copy.txt','h1-stop-held-shift.txt','h1-malformed.txt','h1-random-copy.txt'}
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
 d=pathlib.Path(directory);m=json.loads(read(d/'manifest.json',1024*1024));require(m.get('package_id')=='evilduck-routeb-inject-var-h1-experimental-macos-v1' and m.get('source_commit')==SOURCE and m.get('installation_authorized') is False and m.get('update_method')=='FUTURE_ROM_APP_ONLY_BOTH_SLOTS','WRONG_PACKAGE_IDENTITY')
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
 pin_data=read(d/'source-manifest.json',1024*1024);require(m.get('composition_pin_sha256')==digest(pin_data),'WRONG_COMPOSITION_PIN_IDENTITY');require(receipt.get('inject_var_experimental_source_pin')==json.loads(pin_data),'WRONG_LINKED_COMPOSITION_PIN');require(digest(json.dumps(receipt.get('source_text_v2_source_pin'),sort_keys=True,separators=(',',':')).encode())=='448b775c29337b3449312b33755e9518fa8c13b5e94098842aebbbed3aa501df','WRONG_INHERITED_SOURCE_TEXT_V2_PIN')
 require(m.get('firmware_source_commit')==RELEASE['firmware_source_commit'] and m.get('firmware_build_id')=='ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1','WRONG_H1_FIRMWARE_IDENTITY')
 require(m.get('official_runtime_encoding_verified') is False and m.get('physical_h1_tested') is False,'UNSUPPORTED_COMPATIBILITY_OR_PHYSICAL_CLAIM')
 require(receipt.get('inject_var_experimental_verified') is True and receipt.get('official_runtime_encoding_verified') is False,'H1_LINK_OR_LIMITATION_NOT_VERIFIED')
 require(digest(pin_data)==RELEASE['h1_pin_sha256'],'WRONG_H1_SOURCE_PIN')
 require(digest(json.dumps(receipt.get('timeout_wait_source_pin'),indent=2).encode()+b'\n')==RELEASE['timeout_pin_sha256'],'WRONG_INHERITED_TIMEOUT_PIN')
 require(receipt['inject_var_build_adapter']['build_id']=='ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1','WRONG_H1_LINKED_BUILD_ID')
 require(receipt['inject_var_build_adapter']['adapter_sha256']==RELEASE['build_adapter_sha256'] and receipt['inject_var_link_adapter']['adapter_sha256']==RELEASE['link_adapter_sha256'],'WRONG_EXECUTED_H1_WRAPPERS')
 require(receipt['inject_var_build_adapter']['inherited_safety_predicates_removed']==0 and receipt['inject_var_link_adapter']['inherited_safety_predicates_removed']==0,'REMOVED_H1_GUARDS')
 require('-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1' in receipt['report']['verified_cpp_extra_flags'].split(),'MISSING_H1_BUILD_SELECTOR')
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
