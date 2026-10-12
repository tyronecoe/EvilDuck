#!/usr/bin/env python3
"""Stage non-owner artifacts and a provisional inventory. No flash commands."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from s3_validation import require
from s3_write_plan import REGIONS,validate_regions,validate_ota_initializer
from deployment_preflight import OWNER,esp_image
from verify_patched_firmware import verify

def prepare(normal_core,normal_build,safe_core,safe_build,output):
 normal_build,safe_build,output=map(Path,(normal_build,safe_build,output))
 require(not output.exists(),'Artifact output exists; refusing overwrite')
 normal=verify(normal_core,normal_build);safe=verify(safe_core,safe_build)
 require(safe.get('deployment_safe_start') is True and normal.get('deployment_safe_start') is False,'Require independently verified safe and normal builds')
 require((normal_build/'EvilDuckS3.ino.bin').stat().st_size>0x140000,'Normal firmware unexpectedly fits old slot; investigate')
 payloads={'bootloader.bin':(safe_build/'EvilDuckS3.ino.bootloader.bin').read_bytes(),
 'partitions-sector.bin':(safe_build/'EvilDuckS3.ino.partitions.bin').read_bytes().ljust(0x1000,b'\xff'),
 'otadata-app0.bin':(Path(safe_core)/'tools/partitions/boot_app0.bin').read_bytes(),
 'safe-app.bin':(safe_build/'EvilDuckS3.ino.bin').read_bytes(),
 'normal-app.bin':(normal_build/'EvilDuckS3.ino.bin').read_bytes(),
 'coredump-empty.bin':b'\xff'*0x10000}
 validate_ota_initializer(payloads['otadata-app0.bin'])
 for name,limit in [('bootloader.bin',0x8000),('safe-app.bin',0x740000),('normal-app.bin',0x740000)]:esp_image(payloads[name],limit,True)
 files=dict(bootloader='bootloader.bin',partitions='partitions-sector.bin',otadata='otadata-app0.bin',app0='safe-app.bin',app1='safe-app.bin',spiffs='new-spiffs-0x160000.bin',coredump='coredump-empty.bin')
 entries=[]
 for role,name in files.items():
  data=payloads.get(name);size=len(data) if data is not None else OWNER[name][0]
  entries.append(dict(role=role,file=name,offset=REGIONS[role][0],bytes=size,sha256=hashlib.sha256(data).hexdigest() if data is not None else OWNER[name][1],external=data is None,planned_initial_write=True))
 validate_regions(entries)
 result=dict(provisional_inventory=True,review_only=True,migration_authorized=False,hardware_execution_supported=False,owner_files_verified=False,owner_evidence_missing=list(OWNER),protected_regions=[dict(name='nvs',offset=0x9000,bytes=0x5000)],writes=entries,
 artifacts={n:dict(bytes=len(d),sha256=hashlib.sha256(d).hexdigest()) for n,d in payloads.items()},normal_build_provenance=normal,safe_build_provenance=safe,
 normal_application_initial_write=False,normal_application_purpose='Separate reviewed transition out of safe-start; never automatic',arduino_nvs_auto_erase_disabled=True,sdk_nvs_mutation_risk_unresolved=True,first_boot='Quiescent application; known Arduino erase path disabled, SDK page-recovery mutations remain possible',readiness='NO-GO migration pending actual owner backup/plan preflight and individual authorization')
 output.mkdir(parents=True)
 for name,data in payloads.items():(output/name).write_bytes(data)
 (output/'artifact-inventory.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('normal-core','normal-build','safe-core','safe-build','output'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args()
 try:print(json.dumps(prepare(a.normal_core,a.normal_build,a.safe_core,a.safe_build,a.output),indent=2))
 except (RuntimeError,OSError,ValueError,KeyError,subprocess.SubprocessError) as e:sys.exit('FAIL: '+str(e))
