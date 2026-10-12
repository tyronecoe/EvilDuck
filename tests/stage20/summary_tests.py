#!/usr/bin/env python3
"""Synthetic private reports; no owner files. Verify whitelist privacy and interpretation."""
import argparse,copy,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from deployment_summary import summary
from deployment_preflight import OWNER,EXPECTED_FILES
from s3_validation import LEGACY_LAYOUT,LAYOUT
ROWS=[];ASSERTIONS=0
def check(x,m):
 global ASSERTIONS
 ASSERTIONS+=1
 if not x:raise AssertionError(m)
def base():
 return dict(evidence='owner-recorded',owner_files_verified=True,hardware_access=False,migration_authorized=False,files={n:dict(bytes=s,sha256=h) for n,(s,h) in OWNER.items()},original_layout=json.loads(json.dumps(LEGACY_LAYOUT)),proposed_layout=json.loads(json.dumps(LAYOUT)),spiffs_roundtrip_verified=True,spiffs_files={n:dict(bytes=s,sha256='synthetic-hash') for n,s in EXPECTED_FILES.items()},original_applications=dict(app0=dict(state='valid'),app1=dict(state='erased')),original_bootloader=dict(chip_id=9,image_bytes=20256),nvs_structure=dict(classification='compatible-within-verified-checks',bytes=0x5000,issues=[],sdk_immutability_verified=False,settings_values_validated=False,migration_authorized=False))
def reject(fn):
 try:fn()
 except (ValueError,TypeError,KeyError,AttributeError):check(True,'rejected');return
 raise AssertionError('invalid summary accepted')
def case(n,fn):
 before=ASSERTIONS
 try:fn();s='PASS';e=''
 except Exception as ex:s='FAIL';e=str(ex)
 ROWS.append(dict(name=n,status=s,assertions=ASSERTIONS-before,error=e));print(s,n,e,flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);a=p.parse_args()
 def privacy():
  r=base();r['private-key']='synthetic-secret';r['nvs_structure']['pages']=[dict(password='synthetic-password')];r['spiffs_files']['/test.txt']['extra']='private-payload';before=copy.deepcopy(r);out=summary(r);encoded=json.dumps(out);check(all(s not in encoded for s in ['synthetic-secret','synthetic-password','private-payload','/test.txt','private-key']),'private data not projected');check(r==before,'input report not modified');check(out['migration_authorized'] is False and out['sdk_immutability_proven'] is False,'no false assurance')
 case('summary_privacy_whitelist',privacy)
 for c,code in [('invalid','page_header_crc'),('unsupported-format','page_version'),('recovery-potentially-required','freeing_page'),('insufficient-evidence','blob_index_relationships_unverified')]:
  def classification(c=c,code=code):
   r=base();r['nvs_structure'].update(classification=c,issues=[dict(category=c,code=code,page=0,entry=1)]);out=summary(r);check(out['nvs_classification']==c and out['readiness'].startswith('NO-GO'),'no relabel as compatible')
  case('summary_'+c.replace('-','_'),classification)
 for name,mutation in [('wrong_backup_hash',lambda r:r['files']['evilduck-16m-backup.bin'].update(sha256='bad')),('wrong_backup_size',lambda r:r['files']['evilduck-16m-backup.bin'].update(bytes=16)),('wrong_partition_layout',lambda r:r['original_layout'][0].__setitem__(3,0xa000)),('missing_spiffs_roundtrip',lambda r:r.update(spiffs_roundtrip_verified=False)),('unknown_private_code',lambda r:r['nvs_structure'].update(issues=[dict(category='invalid',code='private-secret')])),('bad_page_location',lambda r:r['nvs_structure'].update(issues=[dict(category='invalid',code='page_header_crc',page=5)])),('bad_entry_location',lambda r:r['nvs_structure'].update(issues=[dict(category='invalid',code='page_header_crc',entry=126)])),('false_immutability',lambda r:r['nvs_structure'].update(sdk_immutability_verified=True)),('inconsistent_classification',lambda r:r['nvs_structure'].update(classification='invalid')),('false_authorization',lambda r:r.update(migration_authorized=True)),('no_recovery_app',lambda r:r['original_applications']['app0'].update(state='erased')),('missing_bootloader_check',lambda r:r.pop('original_bootloader'))]:
  def invalid(mutation=mutation):r=base();mutation(r);reject(lambda:summary(r))
  case('summary_reject_'+name,invalid)
 def cli():
  with tempfile.TemporaryDirectory(prefix='evilduck-safe-summary-') as t:
   t=Path(t);private=t/'private.json';private.write_text(json.dumps(base()));digest=hashlib.sha256(private.read_bytes()).hexdigest();output=t/'share.json';cmd=[sys.executable,str(ROOT/'tools/deployment_summary.py'),'--private-report',str(private),'--output',str(output)];check(subprocess.run(cmd,capture_output=True).returncode==0,'CLI success');check(subprocess.run(cmd,capture_output=True).returncode!=0,'no output overwrite');check(hashlib.sha256(private.read_bytes()).hexdigest()==digest,'private report unchanged')
 case('summary_cli_read_only_no_overwrite',cli)
 out=dict(results=ROWS,counts={s:sum(r['status']==s for r in ROWS) for s in ['PASS','FAIL']},assertions=ASSERTIONS,owner_files_inspected=False,hardware_access=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
