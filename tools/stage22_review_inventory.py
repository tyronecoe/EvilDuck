#!/usr/bin/env python3
"""Offline EXPERIMENTAL review inventory. Not a deployment or migration plan."""
import argparse,json,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
from s3_validation import ROOT,APP_BYTES,require
from stage22_candidate import LABEL,PIN,verify_candidate
from patched_core import sha
FILES={
 'EXPERIMENTAL-application.bin':('EvilDuckS3.ino.bin',0x10000,APP_BYTES),
 'EXPERIMENTAL-bootloader.bin':('EvilDuckS3.ino.bootloader.bin',0,0x8000),
 'EXPERIMENTAL-partitions.bin':('EvilDuckS3.ino.partitions.bin',0x8000,0x1000),
 'EXPERIMENTAL-firmware.elf':('EvilDuckS3.ino.elf',None,None),
}
def validate(directory):
 directory=Path(directory);m=json.loads((directory/'EXPERIMENTAL-inventory.json').read_text())
 require(m['label']==LABEL and m['profile']=='experimental-readonly-quiescent' and m['authorized_for_flashing'] is False,'Wrong inventory/profile authorization')
 require(m['candidate_pin']==json.loads(PIN.read_text()),'Inventory dependency identity mismatch')
 require(set(r['filename'] for r in m['artifacts'])==set(FILES) and len(m['artifacts'])==len(FILES),'Inventory file set mismatch')
 for r in m['artifacts']:
  p=directory/r['filename'];_,address,limit=FILES[r['filename']]
  require(r['label']==LABEL and r['address_for_review_only']==address and r['region_limit']==limit,'Inventory label/geometry mismatch')
  require(p.stat().st_size==r['size'] and sha(p)==r['sha256'],'Inventory artifact size/hash mismatch')
  if limit is not None:require(r['size']<=limit,'Artifact does not fit region')
 require(sha(directory/'EXPERIMENTAL-partitions.bin')==m['candidate_pin']['partition_sha256'],'Inventory table mismatch')
 require(sha(directory/'EXPERIMENTAL-application.bin')==m['provenance']['application_sha256'] and sha(directory/'EXPERIMENTAL-firmware.elf')==m['provenance']['elf_sha256'],'Inventory linked provenance mismatch')
 return m

def create(core,build,directory):
 directory=Path(directory);require(not directory.exists() and ROOT not in directory.resolve().parents and directory.resolve()!=ROOT,'Fresh external review output required')
 provenance=verify_candidate(core,build);directory.mkdir(parents=True)
 rows=[]
 for filename,(source,address,limit) in FILES.items():
  shutil.copyfile(Path(build)/source,directory/filename)
  rows.append(dict(filename=filename,label=LABEL,size=(directory/filename).stat().st_size,sha256=sha(directory/filename),address_for_review_only=address,region_limit=limit))
 m=dict(label=LABEL,profile='experimental-readonly-quiescent',authorized_for_flashing=False,migration_plan=False,artifacts=rows,candidate_pin=json.loads(PIN.read_text()),provenance=provenance,main_app1_geometry=[0x750000,APP_BYTES],protected_nvs=[0x9000,0x5000])
 (directory/'EXPERIMENTAL-inventory.json').write_text(json.dumps(m,indent=2)+'\n');(directory/'EXPERIMENTAL-README.txt').write_text(LABEL+'\nNo owner data, flash commands, arming or transition. Physical migration/application boot/OTA NO-GO.\n')
 return validate(directory)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args();print(json.dumps(create(a.core_dir,a.build_dir,a.output_dir),indent=2))
