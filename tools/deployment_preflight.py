#!/usr/bin/env python3
"""Read-only owner backup and REVIEW-ONLY plan checks. No device/serial APIs."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import subprocess
sys.dont_write_bytecode = True
from nvs_inspect import inspect as inspect_nvs
from s3_validation import require, partition_tool, check_table, LEGACY_LAYOUT, LAYOUT
from s3_migration import (sha256_file, checked_mkspiffs, source_listing, mk_run,
                         inventory, SPIFFS_SOURCE_BYTES, SPIFFS_DESTINATION_BYTES)
from s3_write_plan import validate_regions, validate_ota_initializer
from verify_patched_firmware import verify as verify_firmware

OWNER = {
 'evilduck-16m-backup.bin': (0x1000000,'d1712805e3282e59395efc4f10bd9496b7d338e1b18710379c1112f35248bda7'),
 'partition-table-backup.bin': (0x1000,'8edc409c4d09a6ac4cb2b3029ad9aaf2edcd2c5e0e89137861b1018a7d21ee15'),
 'new-spiffs-0x160000.bin': (0x160000,'fea8c95f9a0b49878e69fe9e9afec7472ce52f6b3d7c1b35db43e905470043fe')}
EXPECTED_FILES = {'/Define_test.txt':189,'/test.txt':459,'/examples/hello.txt':156,
 '/examples/linux_shell.txt':140,'/examples/save_log.txt':130,'/examples/attackmode_demo.txt':106,'/examples/.installed':1}

def esp_image(data, maximum, require_16m=False):
 """ESP extended header/segments/XOR checksum/appended SHA; bounded region only.
 Checksum format matches Espressif esptool image serialization. No execution.
 Trailing partition bytes are not image data and need not be erased.
 """
 require(24<=len(data)<=maximum,'ESP image region is truncated/oversized')
 require(data[0]==0xe9 and 1<=data[1]<=16,'Invalid ESP segment header')
 require(struct.unpack_from('<H',data,12)[0]==9,'Image is not ESP32-S3')
 require(data[2] in (0,1,2,3) and (data[3]&15) in (0,1,2,15),'Unsupported flash header configuration')
 require((data[3]>>4) in range(8),'Invalid flash capacity encoding')
 require(not require_16m or data[3]>>4==4,'Expected 16 MiB image header')
 require(data[23] in (0,1),'Invalid appended-hash flag')
 offset=24;checksum=0xef
 for _ in range(data[1]):
  require(offset+8<=len(data),'Truncated segment header')
  length=struct.unpack_from('<I',data,offset+4)[0];offset+=8
  require(length<=len(data)-offset,'Segment exceeds image region')
  for byte in data[offset:offset+length]:checksum^=byte
  offset+=length
 checksum_offset=(offset//16+1)*16-1
 require(checksum_offset<len(data) and data[checksum_offset]==checksum,'ESP image checksum mismatch')
 end=checksum_offset+1
 if data[23]:
  require(end+32<=len(data),'Truncated appended image digest')
  require(hashlib.sha256(data[:end]).digest()==data[end:end+32],'ESP image SHA256 mismatch');end+=32
 return dict(image_bytes=end,image_sha256=hashlib.sha256(data[:end]).hexdigest(),flash_size_code=data[3]>>4,chip_id=9,appended_hash=bool(data[23]))

def decode_fs(executable,image,size,destination):
 names=source_listing(executable,image,size)
 destination.mkdir();mk_run(executable,'-u',destination,size,image)
 files=inventory(destination)
 require({n:r['bytes'] for n,r in files.items()}==names,'SPIFFS listing/extraction mismatch')
 return files

def verify_backups(core, directory, mkspiffs, expected=OWNER, expected_files=EXPECTED_FILES, evidence='owner-recorded'):
 require(expected==OWNER or evidence=='synthetic-test','Custom evidence is permitted only for explicitly synthetic tests')
 directory=Path(directory);files={};missing=[]
 for name,(size,digest) in expected.items():
  p=directory/name
  if not p.is_file():missing.append(name);continue
  require(not p.is_symlink(),'Backup symlink rejected: '+name)
  require(p.stat().st_size==size,'Wrong backup size: '+name)
  actual=sha256_file(p);require(actual==digest,'Backup SHA256 mismatch: '+name)
  files[name]=dict(bytes=size,sha256=actual)
 require(not missing,'Missing required backups: '+', '.join(missing))
 full=(directory/'evilduck-16m-backup.bin').read_bytes();sector=(directory/'partition-table-backup.bin').read_bytes()
 require(full[0x8000:0x9000]==sector,'Partition backup does not match full image')
 check_table(partition_tool(core).PartitionTable.from_binary(sector),LEGACY_LAYOUT)
 apps={}
 for name,_,_,offset,size in LEGACY_LAYOUT:
  if name.startswith('app'):
   region=full[offset:offset+size]
   apps[name]=dict(state='erased') if region==b'\xff'*size else dict(state='valid',**esp_image(region,size))
 require(any(a['state']=='valid' for a in apps.values()),'No valid original recovery application')
 boot=esp_image(full[:0x8000],0x8000)
 executable=checked_mkspiffs(mkspiffs)
 with tempfile.TemporaryDirectory(prefix='evilduck-backup-check-') as t:
  t=Path(t);old=t/'old-spiffs.bin';old.write_bytes(full[0x290000:0x400000])
  old_files=decode_fs(executable,old,SPIFFS_SOURCE_BYTES,t/'old-files')
  new_files=decode_fs(executable,directory/'new-spiffs-0x160000.bin',SPIFFS_DESTINATION_BYTES,t/'new-files')
  require({n:r['bytes'] for n,r in old_files.items()}==expected_files,'Original file inventory differs from recorded evidence')
  require(old_files==new_files,'Old/new SPIFFS file names, sizes or hashes differ')
  for name in old_files:
   require((t/'old-files'/name[1:]).read_bytes()==(t/'new-files'/name[1:]).read_bytes(),'SPIFFS byte-for-byte mismatch: '+name)
  # Actual construction and decoding checks metadata overhead, not just payload sum.
  require(sum(r['bytes'] for r in new_files.values())<=SPIFFS_DESTINATION_BYTES*3//4,'SPIFFS capacity budget exceeded')
  repacked=t/'capacity-roundtrip.bin';mk_run(executable,'-c',t/'old-files',SPIFFS_DESTINATION_BYTES,repacked)
  require(decode_fs(executable,repacked,SPIFFS_DESTINATION_BYTES,t/'repack-files')==old_files,'Capacity/repack roundtrip failed')
 for name,row in files.items():require(sha256_file(directory/name)==row['sha256'],'Owner backup changed during verification')
 return dict(evidence=evidence,owner_files_verified=evidence=='owner-recorded',hardware_access=False,migration_authorized=False,files=files,original_layout=LEGACY_LAYOUT,proposed_layout=LAYOUT,original_applications=apps,original_bootloader=boot,spiffs_files=old_files,spiffs_roundtrip_verified=True,nvs_sha256=hashlib.sha256(full[0x9000:0xe000]).hexdigest(),nvs_settings_readability='unknown; private settings values not decoded',nvs_structure=inspect_nvs(full[0x9000:0xe000]))

def verify_plan(core, build, plan_dir, backup_report, require_safe_start=True):
 """Recompute all files/ranges/provenance; no plan booleans substitute for evidence."""
 plan_dir=Path(plan_dir);plan=json.loads((plan_dir/'review-plan.json').read_text())
 require(plan.get('review_only') is True and plan.get('migration_authorized') is False and plan.get('hardware_execution_supported') is False,'Plan is not offline/review-only')
 require(backup_report.get('spiffs_roundtrip_verified') is True and backup_report.get('migration_authorized') is False,'Missing completed backup evidence')
 require(backup_report.get('nvs_structure',{}).get('classification')=='compatible-within-verified-checks','NVS structure needs separate owner review; no checked plan')
 provenance=verify_firmware(core,build)
 report=json.loads((Path(build)/'s3-build-report.json').read_text())
 require(not require_safe_start or provenance.get('deployment_safe_start') is True,'Initial migration requires explicit deployment-safe-start build')
 for name in ('original_backup_sha256','original_partition_sector_sha256'):
  key='evilduck-16m-backup.bin' if name=='original_backup_sha256' else 'partition-table-backup.bin'
  require(plan.get(name)==backup_report['files'][key]['sha256'],'Plan original evidence differs from checked files')
 rows=plan['writes'];stored=[dict(e) for e in rows];validate_regions(rows)
 require(plan.get('protected_regions')==[dict(name='nvs',offset=0x9000,bytes=0x5000)],'NVS protection metadata changed')
 for row,old in zip(rows,stored):
  require(row['erase_start']==old.get('erase_start') and row['erase_end_exclusive']==old.get('erase_end_exclusive'),'Stored erase range is invalid')
  filename=row['file'];require(Path(filename).name==filename and filename not in ('.','..'),'Unsafe artifact path')
  path=plan_dir/filename;require(path.is_file() and not path.is_symlink(),'Missing/non-regular plan artifact')
  require(path.stat().st_size==row['bytes'] and sha256_file(path)==row['sha256'],'Plan artifact size/hash mismatch')
 roles={r['role']:r for r in rows}
 for role in ('app0','app1'):
  p=plan_dir/roles[role]['file'];require(sha256_file(p)==provenance['application_sha256'],'App slot differs from approved build');esp_image(p.read_bytes(),0x740000,True)
 boot=plan_dir/roles['bootloader']['file'];require(sha256_file(boot)==sha256_file(Path(build)/'EvilDuckS3.ino.bootloader.bin'),'Bootloader differs from approved build');esp_image(boot.read_bytes(),0x8000,True)
 table=(plan_dir/roles['partitions']['file']).read_bytes();check_table(partition_tool(core).PartitionTable.from_binary(table),LAYOUT)
 expected_table=(Path(build)/'EvilDuckS3.ino.partitions.bin').read_bytes().ljust(0x1000,b'\xff');require(table==expected_table,'Partition sector differs from approved build')
 validate_ota_initializer((plan_dir/roles['otadata']['file']).read_bytes())
 require((plan_dir/roles['coredump']['file']).read_bytes()==b'\xff'*0x10000,'Coredump must be newly erased; no old partition exists')
 require(roles['spiffs']['sha256']==backup_report['files']['new-spiffs-0x160000.bin']['sha256'],'SPIFFS is not the independently checked destination image')
 require(plan.get('file_inventory')==backup_report['spiffs_files'],'Plan file inventory differs from verified files')
 return dict(review_only=True,migration_authorized=False,hardware_access=False,verified_writes=rows,nvs_preserved=True,nvs_preservation_scope='planned writes/erases only',nvs_runtime_guaranteed=False,pre_setup_nvs_erase_risk_unresolved=True,arduino_nvs_auto_erase_disabled=True,sdk_nvs_mutation_risk_unresolved=True,deployment_safe_start=report.get('deployment_safe_start',False),application_sha256=provenance['application_sha256'])

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--backup-dir',type=Path,required=True);p.add_argument('--mkspiffs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--plan-dir',type=Path);p.add_argument('--build-dir',type=Path);a=p.parse_args()
 require(not a.output.exists(),'Output already exists; refusing overwrite')
 require((a.plan_dir is None)==(a.build_dir is None),'Plan and build directories must be supplied together')
 report=verify_backups(a.core_dir,a.backup_dir,a.mkspiffs)
 if a.plan_dir:report['plan']=verify_plan(a.core_dir,a.build_dir,a.plan_dir,report)
 a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS local evidence only; no migration authorized')
if __name__=='__main__':
 try:main()
 except (RuntimeError,ValueError,OSError,KeyError,subprocess.SubprocessError) as e:sys.exit('FAIL: '+str(e))
