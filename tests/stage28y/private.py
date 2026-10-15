#!/usr/bin/env python3
"""Local private fresh provisioning. Generic errors; no device operations."""
import argparse,json,os,pathlib,shutil,stat,sys,tempfile
sys.dont_write_bytecode=True
from package import ROOT,ID,sha,ordinary,validate
from stage26_private import config
from stage24_fresh_images import prepare as fresh,verify_fresh
from stage26_installation import ranges,row

def outside(p):
 p=pathlib.Path(p);require_path=p.resolve();
 if ROOT==require_path or ROOT in require_path.parents or p.is_symlink():raise ValueError('Private path rejected')
 return p

def credentials(file):
 p=ordinary(file);outside(p)
 if p.stat().st_size>32768 or p.stat().st_mode&0o077:raise ValueError('Private configuration permissions/size rejected')
 return config(json.loads(p.read_text()))

def separate(public,p):
 p=outside(p);root=pathlib.Path(public).resolve()
 if root==p.resolve() or root in p.resolve().parents:raise ValueError('Private data cannot enter public package')
 return p

def binding(public):return dict(package_id=ID,public_manifest_sha256=sha(pathlib.Path(public)/'manifest.json'),migration_authorized=False)
def write_private(path,value):
 with pathlib.Path(path).open('x') as f:os.chmod(path,0o600);json.dump(value,f,indent=2);f.write('\n')
def prepare(public,owner_config,output,core,sdk,generator,mkspiffs):
 validate(public,mkspiffs);c=credentials(owner_config);out=separate(public,output)
 if out.exists():raise ValueError('Existing output refused')
 # Every intermediate with credentials stays inside0700. No public archive call exists.
 out.mkdir(mode=0o700)
 fresh(core,sdk,generator,mkspiffs,c,out/'images')
 for f in (out/'images').iterdir():os.chmod(f,0o600)
 write_private(out/'binding.json',binding(public))
 return finalize(public,owner_config,out,core,sdk,generator,mkspiffs)

def finalize(public,owner_config,private,core,sdk,generator,mkspiffs):
 result=validate(public,mkspiffs);c=credentials(owner_config);private=separate(public,private)
 if not private.is_dir() or private.stat().st_mode&0o077:raise ValueError('Private output permissions rejected')
 if json.loads(ordinary(private/'binding.json').read_text())!=binding(public):raise ValueError('Wrong X binding')
 images=private/'images'
 for name in ['fresh-nvs.bin','fresh-spiffs.bin','review-inventory.json']:
  p=ordinary(images/name)
  if p.stat().st_mode&0o077:raise ValueError('Private image permissions rejected')
 actual=verify_fresh(core,mkspiffs,images)
 if actual['autorun_enabled'] is not False or actual['spiffs_files']!={}:raise ValueError('Unsafe startup policy')
 with tempfile.TemporaryDirectory(prefix='.stage28y-schema-',dir=private) as temp:
  expected=pathlib.Path(temp)/'expected';fresh(core,sdk,generator,mkspiffs,c,expected)
  for name in ['fresh-nvs.bin','fresh-spiffs.bin']:
   if (expected/name).read_bytes()!=(images/name).read_bytes():raise ValueError('Schema or owner-input mismatch')
 if (images/'fresh-spiffs.bin').read_bytes()!=(pathlib.Path(public)/'empty-spiffs.bin').read_bytes():raise ValueError('Nonempty filesystem')
 manifest=json.loads((pathlib.Path(public)/'manifest.json').read_text());rows=[dict(r) for r in manifest['rows']]+[row('nvs','fresh-nvs.bin',images/'fresh-nvs.bin')];ranges(rows,complete=True)
 # Finalization verifies all byte identities and ranges together; public paths remain explicit.
 for r in rows:r['artifact_source']='private/images' if r['role']=='nvs' else 'public X package'
 receipt=dict(status='PASS',private_package_complete=True,**binding(public),rows=rows,owner_credentials_verified=True,autorun_enabled=False,autorun_path_empty=True,script_files=0,physical_installation_authorized=False,hardware=False)
 return receipt

def main():
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['prepare','finalize'])
 for name in ['public','owner-config','private','core','sdk','generator','mkspiffs']:p.add_argument('--'+name,required=True,type=pathlib.Path)
 p.add_argument('--receipt',required=True,type=pathlib.Path);a=p.parse_args();separate(a.public,a.receipt)
 if a.receipt.exists() or not a.receipt.parent.is_dir() or a.receipt.parent.stat().st_mode&0o077:raise ValueError('Private receipt destination rejected')
 fn=prepare if a.operation=='prepare' else finalize;r=fn(a.public,a.owner_config,a.private,a.core,a.sdk,a.generator,a.mkspiffs);write_private(a.receipt,r)
 print('PASS: private X-bound offline finalization; physical installation NOT AUTHORIZED')
if __name__=='__main__':
 try:main()
 except Exception:sys.exit('FAIL: private workflow rejected; values and paths omitted; no device operation')
