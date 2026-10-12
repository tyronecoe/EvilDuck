#!/usr/bin/env python3
"""Fail-closed source/artifact/offline-plan integration; no device APIs."""
import argparse,hashlib,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from nvs_source_prepare import verify as verify_sources
from nvs_generator_prepare import verify as verify_generator
from nvs_sdk_evidence import inspect as inspect_archive
from verify_patched_firmware import verify as verify_firmware
from deployment_preflight import OWNER,verify_plan
ROWS=[];ASSERTIONS=0
def check(x,m):
 global ASSERTIONS
 ASSERTIONS+=1
 if not x:raise AssertionError(m)
def case(n,fn):
 before=ASSERTIONS
 try:fn();s='PASS';e=''
 except Exception as ex:s='FAIL';e=str(ex)
 ROWS.append(dict(name=n,status=s,assertions=ASSERTIONS-before,error=e));print(s,n,e,flush=True)
def rejects(fn):
 try:fn()
 except (OSError,ValueError,RuntimeError):check(True,'rejected');return
 raise AssertionError('unsafe input accepted')
def main():
 p=argparse.ArgumentParser()
 for name in ['original-core','normal-core','safe-core','normal-build','safe-build','sdk-source','generator-dir','results']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args()
 case('sdk_source_hash_identity',lambda:check(verify_sources(a.sdk_source)['commit']=='b66b5448e0dfac6be135e6f0ac21010aba231180','source commit'))
 with tempfile.TemporaryDirectory(prefix='evilduck-nvs-pin-test-') as t:
  t=Path(t);copy=t/'src';shutil.copytree(a.sdk_source,copy)
  file=copy/'components/nvs_flash/src/nvs_page.cpp';file.write_bytes(file.read_bytes()+b'\n// mismatch\n')
  case('sdk_source_tamper_rejected',lambda:rejects(lambda:verify_sources(copy)))
 case('generator_hash_identity',lambda:check(verify_generator(a.generator_dir)['version']=='0.1.9','generator version'))
 def evidence():
  j=inspect_archive(a.original_core);functions={r['function']:r for r in j['functions']}
  for name in ['nvs::Page::mLoadEntryTable','nvs::Page::readItem']:
   check(any('eraseEntryAndSpan' in ref for s in functions[name]['sections'] for ref in s['references']),'compiled archive recovery reference')
  check(j['sdk_binary_executed'] is False,'archive inspected only')
 case('pinned_archive_mutation_call_evidence',evidence)
 for profile,core,build in [('normal',a.normal_core,a.normal_build),('safe',a.safe_core,a.safe_build)]:
  def proof(core=core,build=build,profile=profile):
   j=verify_firmware(core,build);check(j['settings_failure_quiescent'] is True,'linked policy');check(j['deployment_safe_start']==(profile=='safe'),'profile identity');check(j['sdk_nvs_immutable'] is False,'no false immutability')
  case('linked_settings_policy_'+profile,proof)
 owner=json.loads((ROOT/'docs/stage19-owner-evidence.json').read_text())
 case('owner_local_evidence_not_codex_inspection',lambda:check(not owner['codex_independently_inspected'] and not owner['full_structural_preflight_completed'] and {n:(r['bytes'],r['sha256']) for n,r in owner['files'].items()}==OWNER,'exact provenance and recorded facts'))
 def gate():
  with tempfile.TemporaryDirectory(prefix='evilduck-nvs-plan-test-') as t:
   t=Path(t);(t/'review-plan.json').write_text(json.dumps(dict(review_only=True,migration_authorized=False,hardware_execution_supported=False)))
   for classification in ['invalid','unsupported-format','recovery-potentially-required','insufficient-evidence']:
    rejects(lambda classification=classification:verify_plan(a.safe_core,a.safe_build,t,dict(spiffs_roundtrip_verified=True,migration_authorized=False,nvs_structure=dict(classification=classification))))
 case('offline_plan_rejects_unresolved_nvs_structure',gate)
 out=dict(results=ROWS,counts={s:sum(r['status']==s for r in ROWS) for s in ['PASS','FAIL']},assertions=ASSERTIONS,hardware_access=False,owner_files_inspected=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2));return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
