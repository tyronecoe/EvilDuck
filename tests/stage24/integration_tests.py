#!/usr/bin/env python3
"""Actual isolated SDK/object/ELF and early-source evidence checks. Offline only."""
import argparse,hashlib,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from patched_core import check_sources,sha,tree_hash
from stage22_candidate import check_candidate as check22,candidate_table
from stage24_candidate import check_candidate,verify_candidate
from stage24_sdk_scanner import compare,validate_output

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['original-core','normal-core','safe-core','candidate-core','candidate-build','sdk-rebuild','sdk-repeat','reference-source','startup-audit','results']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();rows=[]
 def run(name,fn,deny=False):
  try:
   fn()
   if deny:raise AssertionError('unexpected acceptance')
   rows.append(dict(name=name,status='PASS',assertions=1))
  except (ValueError,OSError) as e:rows.append(dict(name=name,status='PASS' if deny else 'FAIL',assertions=1,error=str(e)))
  except Exception as e:rows.append(dict(name=name,status='FAIL',assertions=1,error=str(e)))
 for name,path in [('global_data',a.original_core.parents[4]/'stage23-forbidden-output'),('repo',ROOT/'stage23-forbidden-output'),('source',a.reference_source/'components/spi_flash/stage23-forbidden-output')]:
  run('reject_output_in_'+name,lambda path=path:validate_output(path,a.normal_core,a.candidate_build,a.reference_source/'components/spi_flash/esp_flash_spi_init.c'),True)
 run('global_core_unchanged',lambda:check_sources(a.original_core))
 run('normal_production_dependency_unchanged',lambda:check_sources(a.normal_core,True))
 run('safe_production_dependency_unchanged',lambda:check_sources(a.safe_core,True))
 run('stage22_builder_rejects_corrected_sdk_without_new_profile',lambda:check22(a.candidate_core),True)
 run('stage23_builder_rejects_unmodified_sdk',lambda:check_candidate(a.normal_core),True)
 run('corrected_candidate_exact_identity',lambda:check_candidate(a.candidate_core))
 run('actual_final_elf_bin_gate_callback_cleanup',lambda:verify_candidate(a.candidate_core,a.candidate_build))
 run('unpatched_component_runtime_and_abi_equivalence',lambda:compare(a.sdk_rebuild/'original/partition_target.c.obj',a.sdk_rebuild/'reference/partition_target.c.obj'))
 run('only_scanner_runtime_changed',lambda:compare(a.sdk_rebuild/'original/partition_target.c.obj',a.sdk_rebuild/'cleanup/partition_target.c.obj',True))
 run('unmodified_equivalence_check_rejects_patched_object',lambda:compare(a.sdk_rebuild/'original/partition_target.c.obj',a.sdk_rebuild/'cleanup/partition_target.c.obj'),True)
 def same():
  assert sha(a.sdk_rebuild/'libesp_partition.a')==sha(a.sdk_repeat/'libesp_partition.a')
 run('independent_rebuilds_identical_archive',same)
 def body_fault():
  with tempfile.TemporaryDirectory(prefix='stage23-object-fault-') as t:
   file=Path(t)/'corrupt.o';data=bytearray((a.sdk_rebuild/'cleanup/partition_target.c.obj').read_bytes());data[0]^=1;file.write_bytes(data)
   compare(a.sdk_rebuild/'original/partition_target.c.obj',file,True)
 run('corrupt_object_rejected',body_fault,True)
 def refcheck():
  for r in json.loads((ROOT/'docs/stage23-startup-reference-pin.json').read_text()):
   if r['retrieved']:
    path=r['url'].split('b66b5448e0dfac6be135e6f0ac21010aba231180/',1)[1]
    assert sha(a.reference_source/path)==r['sha256']
 run('new_immutable_startup_sources_verified',refcheck)
 def order():
  inv=json.loads(a.startup_audit.read_text())['inventory'];arrays=inv['arrays'];assert len(next(x['entries'] for x in arrays if x['start_symbol']=='__init_array_start'))==36
  system=next(x['entries'] for x in arrays if 'system_init' in x['start_symbol']);assert len(system)==24 and sum(x['stage']==0 for x in system)==17 and sum(x['stage']==1 for x in system)==7
 run('native_candidate_17_core_36_ctors_7_secondary',order)
 def calls():
  audit=json.loads(a.startup_audit.read_text());r=audit['records'];assert 'initArduino' in r['app_main']['named_calls'];assert 'esp_flash_app_enable_os_functions' in r['esp_flash_app_init']['named_calls'];assert 'esp_partition_iterator_release' in r['esp_partition_is_flash_region_writable']['named_calls'];assert not audit['complete_transitive_audit'] and audit['unresolved_indirect_calls']>0
 run('bounded_call_audit_records_cleanup_and_unresolved_paths',calls)
 def table():
  from s3_validation import validate_csv
  validate_csv(a.original_core);b=candidate_table(a.candidate_core);assert hashlib.sha256(b).hexdigest()==json.load(open(ROOT/'docs/stage22-candidate-pin.json'))['partition_sha256'];assert b==(a.candidate_build/'EvilDuckS3.ino.partitions.bin').read_bytes()
 run('production_and_experimental_partition_identity_preserved',table)
 out=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),hardware_access=False,physical_authorization=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
