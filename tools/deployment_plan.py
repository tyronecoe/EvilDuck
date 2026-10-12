#!/usr/bin/env python3
"""Prepare a CHECKED REVIEW-ONLY plan from real owner files; no hardware writer."""
import argparse,hashlib,json,subprocess,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from deployment_preflight import verify_backups,verify_plan,OWNER
from s3_write_plan import REGIONS,validate_regions,validate_ota_initializer
from s3_validation import require
from verify_patched_firmware import verify

def prepare(core,build,backups,mkspiffs,output,expected=OWNER,evidence_class="owner-recorded"):
 core,build,backups,output=map(Path,(core,build,backups,output))
 require(not output.exists(),'Plan output exists; refusing overwrite')
 evidence=verify_backups(core,backups,mkspiffs,expected,evidence=evidence_class)
 provenance=verify(core,build);require(provenance.get('deployment_safe_start') is True,'Initial plan requires verified safe-start firmware')
 ota=(core/'tools/partitions/boot_app0.bin').read_bytes();validate_ota_initializer(ota)
 payloads={'bootloader':('bootloader.bin',(build/'EvilDuckS3.ino.bootloader.bin').read_bytes()),
 'partitions':('partitions-sector.bin',(build/'EvilDuckS3.ino.partitions.bin').read_bytes().ljust(0x1000,b'\xff')),
 'otadata':('otadata-app0.bin',ota),'app0':('safe-app.bin',(build/'EvilDuckS3.ino.bin').read_bytes()),
 'app1':('safe-app.bin',(build/'EvilDuckS3.ino.bin').read_bytes()),
 'spiffs':('new-spiffs-0x160000.bin',(backups/'new-spiffs-0x160000.bin').read_bytes()),
 'coredump':('coredump-empty.bin',b'\xff'*0x10000)}
 entries=[dict(role=r,file=n,offset=REGIONS[r][0],bytes=len(d),sha256=hashlib.sha256(d).hexdigest()) for r,(n,d) in payloads.items()];validate_regions(entries)
 result=dict(review_only=True,migration_authorized=False,hardware_execution_supported=False,protected_regions=[dict(name='nvs',offset=0x9000,bytes=0x5000)],original_backup_sha256=evidence['files']['evilduck-16m-backup.bin']['sha256'],original_partition_sector_sha256=evidence['files']['partition-table-backup.bin']['sha256'],file_inventory=evidence['spiffs_files'],writes=entries,deployment_safe_start=True,pre_setup_nvs_erase_risk_unresolved=True,arduino_nvs_auto_erase_disabled=True,sdk_nvs_mutation_risk_unresolved=True,owner_evidence=evidence,build_provenance=provenance)
 with tempfile.TemporaryDirectory(prefix='evilduck-reviewed-plan-') as d:
  temp=Path(d)
  for role,(name,data) in payloads.items():(temp/name).write_bytes(data)
  (temp/'review-plan.json').write_text(json.dumps(result,indent=2)+'\n')
  verify_plan(core,build,temp,evidence)
  shutil.copytree(temp,output) # Never overwrite owner input or existing output.
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('core-dir','build-dir','backup-dir','mkspiffs','output'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args()
 try:print(json.dumps(prepare(a.core_dir,a.build_dir,a.backup_dir,a.mkspiffs,a.output),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,subprocess.SubprocessError) as e:sys.exit('FAIL: '+str(e))
