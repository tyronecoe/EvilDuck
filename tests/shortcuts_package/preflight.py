#!/usr/bin/env python3
"""Read-only, Python3.8+ package/layout checks. No device, serial, network or write API."""
import argparse, hashlib, importlib.util, json, pathlib, struct, sys, zlib
sys.dont_write_bytecode=True
SOURCE='5c19f0dacb25960bda36a97f4ff871937a3cc9e7'
APP_BYTES=1359808
APP_SHA='de241287b972c24e510d3e8d22d888a17f13d1e972142559ba3df19f6195b41d'
TABLE_SHA='b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e'
OTA_SHA='f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0'
LAYOUT=[('nvs',1,2,0x9000,0x5000),('otadata',1,0,0xe000,0x2000),('app0',0,0x10,0x10000,0x740000),('app1',0,0x11,0x750000,0x740000),('spiffs',1,0x82,0xe90000,0x160000),('coredump',1,3,0xff0000,0x10000)]
SUPPORT={'README.md','build-receipt.json','source-manifest.json','shortcuts.patch','editor-only.duck','preflight.py','gen_esp32part.py','APACHE-2.0.txt','source-LICENSE.txt','code-review.md','implementation-report.md','design.md','reproduction.md'}
class Rejected(ValueError):pass
def require(v,msg):
 if not v:raise Rejected(msg)
def digest(data):return hashlib.sha256(data).hexdigest()
def read(p,maximum):
 p=pathlib.Path(p);require(not p.is_symlink() and p.is_file(),'MISSING_OR_NONREGULAR_FILE');require(p.stat().st_size<=maximum,'OVERSIZE_FILE');d=p.read_bytes();require(len(d)<=maximum,'OVERSIZE_FILE');return d
def rows():
 return [dict(role=role,file='application.bin',offset=offset,bytes=APP_BYTES,sha256=APP_SHA,partition_bytes=0x740000,erase_start=offset,erase_end_exclusive=offset+((APP_BYTES+4095)//4096)*4096,selected_for_execution=False) for role,offset in [('app0',0x10000),('app1',0x750000)]]
def check_rows(actual):
 require(actual==rows(),'UNREVIEWED_WRITE_OR_ERASE_RANGE')
 for r in actual:
  require(r['offset']+r['bytes']<=r['offset']+r['partition_bytes'],'IMAGE_EXCEEDS_SLOT')
  require(r['erase_end_exclusive']<=r['offset']+r['partition_bytes'],'ERASE_EXCEEDS_SLOT')
  for name,_,_,start,size in LAYOUT:
   if name not in ('app0','app1'):require(r['erase_end_exclusive']<=start or r['erase_start']>=start+size,'PROTECTED_DATA_OVERLAP')
 require(actual[0]['erase_end_exclusive']<=actual[1]['erase_start'],'OVERLAPPING_ERASES')
def image(data):
 # Same bounded segment/checksum format as tools/deployment_preflight.py esp_image.
 require(len(data)==APP_BYTES and digest(data)==APP_SHA,'WRONG_APPLICATION_BYTES')
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
def validate(directory,installed_table=None,installed_ota=None):
 d=pathlib.Path(directory);m=json.loads(read(d/'manifest.json',1024*1024));require(m.get('package_id')=='evilduck-shortcuts-5c19f0d-review-v1' and m.get('source_commit')==SOURCE and m.get('installation_authorized') is False and m.get('update_method')=='FUTURE_ROM_APP_ONLY_BOTH_SLOTS','WRONG_PACKAGE_IDENTITY')
 require(m.get('application_bytes')==APP_BYTES and m.get('application_sha256')==APP_SHA and m.get('table_sha256')==TABLE_SHA,'WRONG_DECLARED_ARTIFACT_IDENTITY')
 check_rows(m['proposed_writes']);require(set(m['support_files'])==SUPPORT,'WRONG_SUPPORT_INVENTORY')
 expected=SUPPORT|{'manifest.json','application.bin','expected-partitions.bin'}
 require({p.name for p in d.iterdir()}==expected and all(p.is_file() and not p.is_symlink() for p in d.iterdir()),'UNEXPECTED_PACKAGE_CONTENT')
 for n,r in m['support_files'].items():
  b=read(d/n,4*1024*1024);require(len(b)==r['bytes'] and digest(b)==r['sha256'],'SUPPORT_INTEGRITY_FAILED')
 image(read(d/'application.bin',APP_BYTES))
 spec=importlib.util.spec_from_file_location('pinned_partition_tool',d/'gen_esp32part.py');tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(tool);tool.offset_part_table=0x8000
 table(read(d/'expected-partitions.bin',4096),tool)
 receipt=json.loads(read(d/'build-receipt.json',4*1024*1024));require(receipt['status']=='PASS' and receipt['report']['application_sha256']==APP_SHA and receipt['report']['application_bytes']==APP_BYTES and receipt['sdk_archives_identical_to_w']==177,'WRONG_BUILD_RECEIPT');require(m.get('application_elf_sha256')==receipt['provenance']['elf_sha256'],'WRONG_DECLARED_ELF_IDENTITY')
 out=dict(package_integrity='PASS',source_commit=SOURCE,application_sha256=APP_SHA,installed_metadata='NOT_SUPPLIED',selected_write_ranges=[],installation_authorized=False,hardware_access=False,device_authenticity_or_freshness_verified=False)
 require((installed_table is None)==(installed_ota is None),'BOTH_INSTALLED_METADATA_FILES_REQUIRED')
 if installed_table is not None:
  table(read(installed_table,4096),tool);ota(read(installed_ota,8192));out.update(installed_metadata='SUPPLIED_FILES_MATCH_SUPPORTED_LAYOUT_AND_APP0_INITIALIZER',selected_write_ranges=rows(),boot_selection_from_supplied_metadata='app0',metadata_provenance='OWNER_LOCAL_FILES_NOT_AUTHENTICATED_DEVICE_READ')
 return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--installed-table',type=pathlib.Path);p.add_argument('--installed-otadata',type=pathlib.Path);a=p.parse_args()
 try:print(json.dumps(validate(a.directory,a.installed_table,a.installed_otadata),indent=2));return 0
 except (OSError,ValueError,KeyError,AssertionError) as e:
  print(json.dumps(dict(package_integrity='REJECTED',reason=str(e) if isinstance(e,Rejected) else 'INVALID_OR_MISSING_INPUT',installation_authorized=False,hardware_access=False)));return 1
if __name__=='__main__':raise SystemExit(main())
