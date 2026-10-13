#!/usr/bin/env python3
"""Synthetic-only offline fresh-image and provisioning gates; never device APIs."""
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from stage24_fresh_images import prepare,validate_config,verify_fresh
from s3_migration import pack_files,source_listing,checked_mkspiffs,check_raw_relocation,mk_run,inventory
from nvs_inspect import inspect
p=argparse.ArgumentParser()
for n in ['core-dir','sdk-source','generator-dir','mkspiffs','results','fixture-output']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();rows=[];assertions=0
c={'ssid':'synthetic-ap','ap_password':'synthetic-test-only','web_password':'synthetic-web-test-only'}
def case(name,fn,reject=False):
 global assertions
 try:
  fn()
  if reject:raise AssertionError('Unsafe input accepted')
 except (ValueError,RuntimeError,OSError,subprocess.SubprocessError):
  if not reject:raise
 assertions+=1;rows.append(dict(name=name,status='PASS',assertions=1));print('PASS',name)
def make(output,config=c):return prepare(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,config,output)
report=make(a.fixture_output)
case('fresh_image_geometry',lambda: (_ for _ in ()).throw(AssertionError()) if [x['bytes'] for x in report['artifacts']]!=[0x5000,0x160000] else None)
case('fresh_image_not_authorized',lambda: (_ for _ in ()).throw(AssertionError()) if report['migration_authorized'] else None)
case('fresh_nvs_structure',lambda: (_ for _ in ()).throw(AssertionError()) if inspect((a.fixture_output/'fresh-nvs.bin').read_bytes())['classification']!='compatible-within-verified-checks' else None)
case('fresh_spiffs_empty_inventory',lambda: (_ for _ in ()).throw(AssertionError()) if source_listing(str(a.mkspiffs),a.fixture_output/'fresh-spiffs.bin',0x160000)!={} else None)
case('fresh_inventory_verified',lambda:verify_fresh(a.core_dir,a.mkspiffs,a.fixture_output))
case('existing_output_rejected',lambda:make(a.fixture_output),True)
case('no_credential_defaults',lambda:validate_config({}),True)
for key,value in [('ssid',''),('ssid','x'*33),('ap_password','short'),('web_password',''),('web_password','x'*4000),('ssid','x\x00y')]:
 bad=dict(c);bad[key]=value
 case('reject_'+key+'_'+str(len(value)),lambda b=bad:validate_config(b),True)
case('unknown_config_fields',lambda:validate_config(dict(c,autorun=True)),True)
case('unsafe_raw_old_spiffs',lambda:check_raw_relocation(0x170000,0x160000),True)
case('repository_output_rejected',lambda:make(ROOT/'private-output'),True)
with tempfile.TemporaryDirectory(prefix='fresh-infrastructure-tests-') as t:
 t=Path(t);r=make(t/'repeat')
 case('fresh_reproducible_nvs',lambda: (_ for _ in ()).throw(AssertionError()) if (t/'repeat/fresh-nvs.bin').read_bytes()!=(a.fixture_output/'fresh-nvs.bin').read_bytes() else None)
 case('fresh_reproducible_spiffs',lambda: (_ for _ in ()).throw(AssertionError()) if (t/'repeat/fresh-spiffs.bin').read_bytes()!=(a.fixture_output/'fresh-spiffs.bin').read_bytes() else None)
 empty=t/'empty';empty.mkdir();pack_files(a.mkspiffs,empty,t/'empty.bin')
 case('empty_spiffs_supported',lambda: (_ for _ in ()).throw(AssertionError()) if source_listing(str(a.mkspiffs),t/'empty.bin/spiffs-new-0x160000.bin',0x160000)!={} else None)
 truncated=t/'truncated.bin';truncated.write_bytes((a.fixture_output/'fresh-spiffs.bin').read_bytes()[:-1])
 case('truncated_spiffs_rejected',lambda:source_listing(str(a.mkspiffs),truncated,0x160000),True)
 oversize=t/'large';oversize.mkdir();(oversize/'huge').write_bytes(b'x'*0x160000)
 case('capacity_budget_rejected',lambda:pack_files(a.mkspiffs,oversize,t/'large.bin'),True)
 symlink=t/'symlink';symlink.mkdir();(symlink/'linked').symlink_to(a.fixture_output/'fresh-spiffs.bin')
 case('symlink_source_rejected',lambda:pack_files(a.mkspiffs,symlink,t/'link.bin'),True)
 # Removing any implicit private CSV/config from published output is part of preparation.
 for field,value in [('offset',0x8000),('sha256','0'*64),('bytes',0x170000)]:
  changed=json.loads(json.dumps(r));changed['artifacts'][0][field]=value
  (t/'repeat/review-inventory.json').write_text(json.dumps(changed))
  case('fresh_manifest_reject_'+field,lambda:verify_fresh(a.core_dir,a.mkspiffs,t/'repeat'),True)
 (t/'repeat/review-inventory.json').write_text(json.dumps(r))
 case('no_private_csv_published',lambda: (_ for _ in ()).throw(AssertionError()) if (t/'repeat/settings.csv').exists() else None)
with tempfile.TemporaryDirectory(prefix='fresh-interruption-') as t:
 t=Path(t)
 import stage24_fresh_images as module
 original=module.shutil.copy2
 def interrupted(*args,**kwargs):
  if Path(args[1]).parent.name=='interrupted':raise OSError('synthetic interrupted publication')
  return original(*args,**kwargs)
 module.shutil.copy2=interrupted
 try:case('interrupted_publication_rejected',lambda:make(t/'interrupted'),True)
 finally:module.shutil.copy2=original
 case('interrupted_directory_cannot_be_reused',lambda:make(t/'interrupted'),True)
 case('incomplete_inventory_not_approved',lambda:verify_fresh(a.core_dir,a.mkspiffs,t/'interrupted'),True)
 original=module.subprocess.run
 def failed(*args,**kwargs):
  if 'generate' in args[0]:return subprocess.CompletedProcess(args[0],1,'','synthetic generator fault')
  return original(*args,**kwargs)
 module.subprocess.run=failed
 try:case('generator_failure_not_published',lambda:make(t/'generation-failure'),True)
 finally:module.subprocess.run=original
 case('generator_failure_leaves_no_output',lambda: (_ for _ in ()).throw(AssertionError()) if (t/'generation-failure').exists() else None)
case('privacy_safe_inventory' ,lambda: (_ for _ in ()).throw(AssertionError()) if c['ap_password'] in json.dumps(report) or c['web_password'] in json.dumps(report) else None)
a.results.write_text(json.dumps(dict(results=rows,counts={'PASS':len(rows),'FAIL':0},assertions=assertions,offline_only=True,hardware_access=False,physical_authorization=False),indent=2)+'\n')
