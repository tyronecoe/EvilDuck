#!/usr/bin/env python3
"""Offline profile separation, dependency and linked candidate fault tests."""
import argparse,copy,json,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from stage22_candidate import candidate_table,check_candidate,verify_candidate,BASE
from stage22_review_inventory import validate,create
from s3_validation import validate_csv,ValidationError
from patched_core import check_sources

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['original-core','normal-core','safe-core','candidate-core','candidate-build','inventory','results']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();rows=[]
 def run(name,fn,deny=False):
  try:
   fn()
   if deny:raise AssertionError('unsafe input accepted')
   rows.append(dict(name=name,status='PASS',assertions=1))
  except (ValueError,OSError) as e:
   rows.append(dict(name=name,status='PASS' if deny else 'FAIL',assertions=1,error=str(e)))
  except Exception as e:rows.append(dict(name=name,status='FAIL',assertions=1,error=str(e)))
 run('unchanged_installed_core',lambda:check_sources(a.original_core))
 run('normal_core_unchanged',lambda:check_sources(a.normal_core,True))
 run('safe_core_unchanged',lambda:check_sources(a.safe_core,True))
 run('production_table_still_writable',lambda:validate_csv(a.original_core))
 run('production_rejects_candidate_table',lambda:validate_csv(a.original_core,BASE/'partitions.csv'),True)
 run('candidate_rejects_production_table',lambda:candidate_table(a.original_core,ROOT/'EvilDuckS3/partitions.csv'),True)
 run('production_rejects_candidate_core',lambda:check_sources(a.candidate_core,True),True)
 run('candidate_rejects_production_core',lambda:check_candidate(a.normal_core),True)
 run('candidate_dependency_identity',lambda:check_candidate(a.candidate_core))
 run('candidate_final_link_and_image',lambda:verify_candidate(a.candidate_core,a.candidate_build))
 run('candidate_inventory_create',lambda:create(a.candidate_core,a.candidate_build,a.inventory))
 run('candidate_inventory_verify',lambda:validate(a.inventory))
 original=json.loads((a.inventory/'EXPERIMENTAL-inventory.json').read_text())
 for name,change in [('manifest_profile',lambda m:m.update(profile='normal')),('manifest_authorization',lambda m:m.update(authorized_for_flashing=True)),('manifest_pin',lambda m:m['candidate_pin'].update(partition_sha256='0'*64)),('manifest_offset',lambda m:m['artifacts'][0].update(address_for_review_only=0x9000)),('manifest_hash',lambda m:m['artifacts'][0].update(sha256='0'*64)),('manifest_size',lambda m:m['artifacts'][0].update(size=0)),('manifest_elf_identity',lambda m:m['provenance'].update(elf_sha256='0'*64))]:
  m=copy.deepcopy(original);change(m);(a.inventory/'EXPERIMENTAL-inventory.json').write_text(json.dumps(m));run('reject_'+name,lambda:validate(a.inventory),True)
 (a.inventory/'EXPERIMENTAL-inventory.json').write_text(json.dumps(original,indent=2)+'\n')
 for filename in ['EXPERIMENTAL-application.bin','EXPERIMENTAL-partitions.bin','EXPERIMENTAL-firmware.elf']:
  path=a.inventory/filename;data=path.read_bytes();altered=bytearray(data);altered[0]^=1;path.write_bytes(altered)
  try:run('reject_corrupted_'+filename,lambda:validate(a.inventory),True)
  finally:path.write_bytes(data)
 validate(a.inventory)
 out=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),hardware_access=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
