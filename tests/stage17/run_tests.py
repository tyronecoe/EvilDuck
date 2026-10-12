#!/usr/bin/env python3
"""Offline synthetic backup/plan faults and actual setup/loop with mocked services."""
import argparse,copy,hashlib,json,struct,subprocess,sys,tempfile,shutil
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import deployment_preflight as pre
import s3_migration as migration
import s3_write_plan as plan
from s3_validation import partition_tool,LEGACY_LAYOUT,LAYOUT
from verify_patched_firmware import verify
from deployment_plan import prepare as prepare_checked_plan
from deployment_inventory import prepare as prepare_inventory

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--normal-build',type=Path,required=True);p.add_argument('--safe-build',type=Path,required=True);p.add_argument('--normal-core',type=Path,required=True);p.add_argument('--upstream-core',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
 mk=a.core_dir.parents[2]/'tools/mkspiffs/0.2.3/mkspiffs';results=[];assertions=0
 def check(ok,why):
  nonlocal assertions
  assertions+=1
  if not ok:raise AssertionError(why)
 def rejects(action):
  try:action()
  except (RuntimeError,ValueError,OSError,KeyError,subprocess.SubprocessError):check(True,'rejected');return
  check(False,'unsafe input accepted')
 def case(name,action):
  before=assertions
  try:action();status='PASS';error=''
  except Exception as e:status='FAIL';error=str(e)
  if status=='PASS' and name in ('stage17_pre_setup_nvs_erase_risk_recorded','stage17_normal_spiffs_format_risk_preserved'):status='OBSERVED'
  results.append(dict(name=name,status=status,assertions=assertions-before,error=error));print(status,name,error,flush=True)
 with tempfile.TemporaryDirectory(prefix='stage17-synthetic-') as d:
  t=Path(d);owner=t/'synthetic-owner';owner.mkdir();files=t/'files';files.mkdir()
  for name,size in pre.EXPECTED_FILES.items():
   f=files/name[1:];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'x'*size)
  old=t/'old.bin';migration.mk_run(str(mk),'-c',files,0x170000,old)
  repack=t/'repack';migration.pack_files(mk,files,repack)
  (owner/'new-spiffs-0x160000.bin').write_bytes((repack/'spiffs-new-0x160000.bin').read_bytes())
  def image():
   data=bytearray(24);data[:4]=bytes([0xe9,1,2,0x2f]);struct.pack_into('<H',data,12,9);data[23]=1
   payload=b'harmless-fixture';data+=struct.pack('<II',0x3fc88000,len(payload))+payload;checksum=0xef
   for byte in payload:checksum^=byte
   data+=b'\0'*((15-len(data)%16)%16)+bytes([checksum]);data+=hashlib.sha256(data).digest();return bytes(data)
  esp=image();sector=partition_tool(a.core_dir).PartitionTable.from_csv('\n'.join(','.join([n,str(typ),str(sub),hex(o),hex(s),'']) for n,typ,sub,o,s in LEGACY_LAYOUT)).to_binary().ljust(0x1000,b'\xff')
  full=bytearray(b'\xff'*0x1000000);full[:len(esp)]=esp;full[0x8000:0x9000]=sector
  for offset in [0x10000,0x150000]:full[offset:offset+len(esp)]=esp
  full[0x290000:0x400000]=old.read_bytes();(owner/'evilduck-16m-backup.bin').write_bytes(full);(owner/'partition-table-backup.bin').write_bytes(sector)
  pins={n:(s,migration.sha256_file(owner/n)) for n,(s,_) in pre.OWNER.items()}
  backup=lambda:pre.verify_backups(a.core_dir,owner,mk,pins,evidence='synthetic-test')
  report=backup();case('stage17_synthetic_backup_roundtrip',lambda:check(report['spiffs_roundtrip_verified'] and not report['owner_files_verified'],'synthetic status and every byte preserved'))
  case('stage17_missing_backups',lambda:rejects(lambda:pre.verify_backups(a.core_dir,t/'missing',mk)))
  case('stage17_owner_hashes_reject_synthetic_files',lambda:rejects(lambda:pre.verify_backups(a.core_dir,owner,mk)))
  case('stage17_custom_hashes_cannot_claim_owner_evidence',lambda:rejects(lambda:pre.verify_backups(a.core_dir,owner,mk,pins)))
  case('stage17_old_new_size_raw_relocation_rejected',lambda:rejects(lambda:migration.check_raw_relocation(0x170000,0x160000)))
  def mutation(name,new,expected=None):
   path=owner/name;original=path.read_bytes();path.write_bytes(new)
   try:rejects(lambda:pre.verify_backups(a.core_dir,owner,mk,expected or pins,evidence='synthetic-test'))
   finally:path.write_bytes(original)
  case('stage17_wrong_backup_hash',lambda:mutation('evilduck-16m-backup.bin',bytes([full[0]^1])+bytes(full[1:])))
  case('stage17_truncated_filesystem',lambda:mutation('new-spiffs-0x160000.bin',b'bad'))
  badsector=bytearray(sector);badsector[12]^=1
  case('stage17_corrupt_partition_sector_hash',lambda:mutation('partition-table-backup.bin',badsector))
  def structural_backup(full_bytes,sector_bytes=sector):
   originals={n:(owner/n).read_bytes() for n in pre.OWNER}
   try:
    (owner/'evilduck-16m-backup.bin').write_bytes(full_bytes);(owner/'partition-table-backup.bin').write_bytes(sector_bytes)
    changed={n:(len((owner/n).read_bytes()),migration.sha256_file(owner/n)) for n in pins}
    rejects(lambda:pre.verify_backups(a.core_dir,owner,mk,changed,evidence='synthetic-test'))
   finally:
    for n,data in originals.items():(owner/n).write_bytes(data)
  badfs=bytearray(full);badfs[0x290000:0x400000]=b'\x00'*0x170000
  case('stage17_invalid_spiffs_geometry_extractability',lambda:structural_backup(badfs))
  badfull=bytearray(full);badfull[0x8000]^=1
  case('stage17_partition_sector_full_backup_mismatch',lambda:structural_backup(badfull))
  badfull=bytearray(full);badfull[0x8000:0x9000]=badsector
  case('stage17_corrupted_partition_structure',lambda:structural_backup(badfull,badsector))
  proposed=partition_tool(a.core_dir).PartitionTable.from_csv((ROOT/'EvilDuckS3/partitions.csv').read_text()).to_binary().ljust(0x1000,b'\xff');badfull=bytearray(full);badfull[0x8000:0x9000]=proposed
  case('stage17_proposed_layout_not_original_backup',lambda:structural_backup(badfull,proposed))
  case('stage17_valid_esp_image_checksum_digest',lambda:check(pre.esp_image(esp,0x140000)['image_bytes']==len(esp),'image length'))
  for label,offset in [('chip',12),('checksum',len(esp)-33),('digest',len(esp)-1),('segment',28)]:
   damaged=bytearray(esp);damaged[offset]^=0xff
   case('stage17_invalid_esp_'+label,lambda damaged=damaged:rejects(lambda:pre.esp_image(damaged,0x140000)))
  case('stage17_truncated_esp_digest',lambda:rejects(lambda:pre.esp_image(esp[:-1],0x140000)))
  case('stage17_legacy_flash_header_not_new',lambda:rejects(lambda:pre.esp_image(esp,0x140000,True)))
  case('stage17_actual_normal_artifact_checksum',lambda:check(pre.esp_image((a.normal_build/'EvilDuckS3.ino.bin').read_bytes(),0x740000,True)['chip_id']==9,'actual image checksum/digest'))
  case('stage17_erased_recovery_image_rejected',lambda:structural_backup(bytearray(b'\xff'*0x10000)+full[0x10000:]))
  case('stage17_normal_firmware_exceeds_old_slots',lambda:check((a.normal_build/'EvilDuckS3.ino.bin').stat().st_size>0x140000,'old slots cannot hold normal firmware'))
  case('stage17_actual_patched_normal_link',lambda:check(verify(a.normal_core,a.normal_build)['single_strong_callback'],'normal link'))
  def forged_profile():
   fixture=t/'forged-profile-build';shutil.copytree(a.normal_build,fixture)
   path=fixture/'s3-build-report.json';data=json.loads(path.read_text());data['deployment_safe_start']=True;path.write_text(json.dumps(data))
   rejects(lambda:verify(a.normal_core,fixture))
  case('stage17_forged_safe_build_metadata_rejected',forged_profile)
  def swapped_binary():
   fixture=t/'swapped-image-build';shutil.copytree(a.safe_build,fixture)
   image=(a.normal_build/'EvilDuckS3.ino.bin').read_bytes();(fixture/'EvilDuckS3.ino.bin').write_bytes(image)
   with (fixture/'EvilDuckS3.ino.merged.bin').open('r+b') as out:out.seek(0x10000);out.write(image)
   rp=fixture/'s3-build-report.json';data=json.loads(rp.read_text());data['application_sha256']=migration.sha256_file(fixture/'EvilDuckS3.ino.bin');rp.write_text(json.dumps(data))
   rejects(lambda:verify(a.core_dir,fixture))
  case('stage17_rehashed_swapped_binary_rejected_by_elf',swapped_binary)
  case('stage17_actual_patched_safe_link',lambda:check(verify(a.core_dir,a.safe_build)['feature_workaround_absent'],'safe link'))
  log=t/'flash-id.txt';log.write_text('Detected flash size: 16MB\n');archive=t/'archive';migration.prepare(a.core_dir,log,owner/'evilduck-16m-backup.bin',owner/'partition-table-backup.bin',archive,pins['evilduck-16m-backup.bin'][1],pins['partition-table-backup.bin'][1])
  staged=t/'review-plan';plan.make_plan(a.core_dir,a.safe_build,archive,repack,staged,pins['evilduck-16m-backup.bin'][1],pins['partition-table-backup.bin'][1])
  valid=json.loads((staged/'review-plan.json').read_text());verify_plan=lambda:pre.verify_plan(a.core_dir,a.safe_build,staged,report)
  case('stage17_complete_safe_plan_nvs_preserved',lambda:check(verify_plan()['nvs_preserved'],'all regions/provenance verified'))
  def changed_plan(mutator):
   data=copy.deepcopy(valid);mutator(data);(staged/'review-plan.json').write_text(json.dumps(data))
   try:rejects(verify_plan)
   finally:(staged/'review-plan.json').write_text(json.dumps(valid))
  case('stage17_old_app1_offset_rejected',lambda:changed_plan(lambda d:d['writes'][4].update(offset=0x150000)))
  case('stage17_nvs_overlap_rejected',lambda:changed_plan(lambda d:d['writes'][1].update(offset=0x9000)))
  case('stage17_overlapping_stored_erases_rejected',lambda:changed_plan(lambda d:d['writes'][0].update(erase_end_exclusive=0x10000)))
  case('stage17_non_aligned_stored_erases_rejected',lambda:changed_plan(lambda d:d['writes'][0].update(erase_start=1)))
  case('stage17_plan_nvs_metadata_rejected',lambda:changed_plan(lambda d:d.update(protected_regions=[])))
  case('stage17_false_migration_authorization_rejected',lambda:changed_plan(lambda d:d.update(migration_authorized=True)))
  case('stage17_missing_plan_artifact_rejected',lambda:changed_plan(lambda d:d['writes'][0].update(file='missing.bin')))
  case('stage17_path_traversal_rejected',lambda:changed_plan(lambda d:d['writes'][0].update(file='../bootloader.bin')))
  case('stage17_wrong_application_hash_rejected',lambda:changed_plan(lambda d:d['writes'][4].update(sha256='0'*64)))
  def corrupt_artifact(role,index):
   row=next(r for r in valid['writes'] if r['role']==role);path=staged/row['file'];original=path.read_bytes();bad=bytearray(original);bad[index]^=1;path.write_bytes(bad)
   data=copy.deepcopy(valid)
   for r in data['writes']:
    if r['file']==row['file']:r['sha256']=migration.sha256_file(path)
   (staged/'review-plan.json').write_text(json.dumps(data))
   try:rejects(verify_plan)
   finally:path.write_bytes(original);(staged/'review-plan.json').write_text(json.dumps(valid))
  for role,index in [('otadata',28),('coredump',0),('partitions',12),('app0',24),('spiffs',100)]:case('stage17_corrupt_'+role+'_even_with_rehashed_manifest',lambda role=role,index=index:corrupt_artifact(role,index))
  case('stage17_normal_build_not_first_boot_safe',lambda:rejects(lambda:pre.verify_plan(a.normal_core,a.normal_build,staged,report)))
  case('stage17_sources_not_modified',lambda:check(all(migration.sha256_file(owner/n)==digest for n,(_,digest) in pins.items()),'backup bytes unchanged'))
  case('stage17_recovery_backup_exact_region',lambda:check((archive/'nvs-recovery-backup.bin').read_bytes()==full[0x9000:0xe000],'recovery preserves original NVS bytes'))
  checked=t/'complete-checked-plan'
  case('stage17_checked_plan_generation_synthetic_only',lambda:check(prepare_checked_plan(a.core_dir,a.safe_build,owner,mk,checked,pins,'synthetic-test')['owner_evidence']['owner_files_verified'] is False,'fixture remains explicitly synthetic'))
  case('stage17_checked_plan_no_overwrite',lambda:rejects(lambda:prepare_checked_plan(a.core_dir,a.safe_build,owner,mk,checked,pins,'synthetic-test')))
  case('stage17_checked_plan_missing_owner_files',lambda:rejects(lambda:prepare_checked_plan(a.core_dir,a.safe_build,t/'missing',mk,t/'missing-plan')))
  case('stage17_checked_plan_wrong_owner_hashes',lambda:rejects(lambda:prepare_checked_plan(a.core_dir,a.safe_build,owner,mk,t/'wrong-plan')))
  case('stage17_failed_plan_creates_no_output',lambda:check(not (t/'missing-plan').exists() and not (t/'wrong-plan').exists(),'failure publishes nothing'))
  provisional=t/'provisional'
  case('stage17_provisional_artifact_inventory_not_authorization',lambda:check(prepare_inventory(a.normal_core,a.normal_build,a.core_dir,a.safe_build,provisional)['owner_files_verified'] is False,'inventory cannot substitute for real backups'))
  case('stage17_artifact_inventory_no_overwrite',lambda:rejects(lambda:prepare_inventory(a.normal_core,a.normal_build,a.core_dir,a.safe_build,provisional)))
  case('stage17_no_full_chip_erase_plan',lambda:check(all(r['bytes']<0x1000000 for r in valid['writes']) and not valid['hardware_execution_supported'],'no writer/full erase'))
  case('stage17_pre_setup_nvs_erase_risk_recorded',lambda:check('esp_partition_erase_range(partition, 0, partition->size)' in (a.upstream_core/'cores/esp32/esp32-hal-misc.c').read_text(),'upstream risk exists; not fixed by application profile'))
  case('stage17_normal_spiffs_format_risk_preserved',lambda:check('SPIFFS.begin(true)' in (ROOT/'EvilDuckS3/spiffs.cpp').read_text(),'normal semantics explicitly unchanged'))
  for safe in (False,True):
   exe=t/('startup-safe' if safe else 'startup-normal');args=['g++','-DEVILDUCK_HOST_TEST','-std=gnu++17','-O1','-g','-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(ROOT/'tests/stage17/mocks'),'-I'+str(ROOT/'tests/stage1/mocks'),str(ROOT/'tests/stage17/startup.cpp'),'-o',str(exe)]
   if safe:args.insert(1,'-DEVILDUCK_DEPLOYMENT_SAFE_START=1')
   subprocess.run(args,check=True)
   r=subprocess.run([str(exe)],capture_output=True,text=True);import re
   count=re.search(r'PASS (\w+) \((\d+) assertions\)',r.stdout)
   results.append(dict(name=count[1] if count else str(exe.name),status='PASS' if r.returncode==0 else 'FAIL',assertions=int(count[2]) if count else 0,stdout=r.stdout,stderr=r.stderr));print(r.stdout,r.stderr,flush=True)
  r=subprocess.run(['g++','-E','-x','c++','-DEVILDUCK_DEPLOYMENT_SAFE_START=2','-'],input=(ROOT/'EvilDuckS3/deployment_boot.h').read_text(),capture_output=True,text=True)
  case('stage17_invalid_safe_profile_rejected',lambda:check(r.returncode!=0 and 'must be 0 or 1' in r.stderr,'invalid profile fails'))
 out=dict(results=results,pass_count=sum(r['status']=='PASS' for r in results),fail_count=sum(r['status']=='FAIL' for r in results),observation_count=sum(r['status']=='OBSERVED' for r in results),assertions=sum(r['assertions'] for r in results),evidence='synthetic tests; actual owner backups NOT verified',hardware_access=False,sanitizers='ASan/UBSan startup; Python offline checks not sanitizer targets')
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2));return bool(out['fail_count'])
if __name__=='__main__':raise SystemExit(main())
