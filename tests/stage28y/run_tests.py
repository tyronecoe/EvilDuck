#!/usr/bin/env python3
"""Focused artifact/schema tests; synthetic local inputs only, no hardware."""
import argparse,copy,csv,json,os,pathlib,re,shutil,subprocess,sys,tempfile,zipfile
sys.dont_write_bytecode=True
import package as pkg
import private as priv
from s3_validation import require
from s3_migration import pack_files
p=argparse.ArgumentParser()
for n in ['public','core','sdk','generator','mkspiffs','results']:p.add_argument('--'+n,required=True,type=pathlib.Path)
a=p.parse_args();assert not a.results.exists();results=[];commands=[]
def case(name,fn,deny=False):
 try:
  fn()
  if deny:raise AssertionError('negative accepted')
  status='PASS';classification='EXPECTED REJECTION' if deny else 'POSITIVE'
 except (ValueError,OSError,RuntimeError,KeyError,TypeError):status='PASS' if deny else 'FAIL';classification='EXPECTED REJECTION' if deny else 'UNEXPECTED REJECTION'
 except Exception:status='FAIL';classification='UNEXPECTED TEST ERROR; private data omitted'
 results.append(dict(id=name,status=status,classification=classification,assertions=1));print(name,status,classification,flush=True)
with tempfile.TemporaryDirectory(prefix='stage28y-tests-') as tmp:
 t=pathlib.Path(tmp);os.chmod(t,0o700);original=json.loads((a.public/'manifest.json').read_text());trusted=pkg.PIN
 case('actual_public_images_table_ota_fs',lambda:pkg.validate(a.public,a.mkspiffs))
 def changed(name,change,repin=False):
  d=t/name;shutil.copytree(a.public,d);m=copy.deepcopy(original);change(d,m);(d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
  if repin:
   pkg.PIN=t/(name+'-pin.json');pkg.PIN.write_bytes((d/'manifest.json').read_bytes());(d/'source/docs/stage28y-public-manifest.json').write_bytes(pkg.PIN.read_bytes())
  try:return pkg.validate(d,a.mkspiffs)
  finally:pkg.PIN=trusted
 def replace(d,m,name,data):
  (d/name).write_bytes(data)
  for r in m['rows']:
   if r['file']==name:r.update(bytes=len(data),sha256=pkg.sha(d/name))
 for name,change in [
 ('byte_tamper',lambda d,m:(d/'controlled-stage28x.bin').write_bytes(bytes(1358224))),
 ('missing_app',lambda d,m:(d/'controlled-stage28x.bin').unlink()),
 ('wrong_profile',lambda d,m:m.update(profile='safe')),
 ('missing_role',lambda d,m:m['rows'].pop()),
 ('mixed_app',lambda d,m:replace(d,m,'controlled-stage28x.bin',(pkg.ROOT/'review/stage26-installation/controlled-stage26.bin').read_bytes())),
 ('historical_manifest_app_swap',lambda d,m:(d/'manifest.json').write_text('{}'))]:
  if name=='historical_manifest_app_swap':
   def oldpin():
    from stage26_installation import verify_public
    d=t/'stage26';shutil.copytree(pkg.ROOT/'review/stage26-installation',d);shutil.copyfile(a.public/'controlled-stage28x.bin',d/'controlled-stage26.bin');verify_public(a.core,a.mkspiffs,d)
   case(name,oldpin,True)
  else:case(name,lambda n=name,c=change:changed(n,c),True)
 for name,change in [('overlap',lambda d,m:m['rows'][1].update(offset=0x4000,erase_start=0x4000)),('whole_slot_erase',lambda d,m:m['rows'][3].update(erase_end_exclusive=0x750000)),('wrong_ota',lambda d,m:replace(d,m,'ota-app0.bin',bytes(8192))),('bad_coredump',lambda d,m:replace(d,m,'coredump-erased.bin',bytes(65536)))]:case(name,lambda n=name,c=change:changed(n,c,True),True)
 def wrongtable(d,m):
  spec=pkg.importlib.util.spec_from_file_location('fixture_part',d/'partition-tool/gen_esp32part.py');mod=pkg.importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);tab=mod.PartitionTable.from_binary((d/'partitions.bin').read_bytes());tab[0].readonly=True;replace(d,m,'partitions.bin',tab.to_binary())
 case('readonly_table_even_rehashed_fixture',lambda:changed('readonly',wrongtable,True),True)
 def badimage(d,m):
  data=bytearray((d/'controlled-stage28x.bin').read_bytes());data[12]=0;data[-32:]=pkg.hashlib.sha256(data[:-32]).digest();replace(d,m,'controlled-stage28x.bin',data)
 case('wrong_chip_even_rehashed_fixture',lambda:changed('wrongchip',badimage,True),True)
 archive=t/'public.zip';case('deterministic_zip_creation',lambda:pkg.archive(a.public,archive));other=t/'again.zip';pkg.archive(a.public,other);case('repeat_zip_identical',lambda:require(archive.read_bytes()==other.read_bytes(),'not reproducible'))
 case('safe_extract_validate',lambda:pkg.extract(archive,t/'extracted'))
 case('extracted_validator_executes',lambda:subprocess.run([sys.executable,str(t/'extracted/source/tests/stage28y/host_preflight.py'),'--public',str(t/'extracted')],capture_output=True,text=True,check=True))
 for name,member,mode in [('traversal','../escape',0),('absolute','/escape',0),('backslash','a\\b',0),('symlink','linked',0o120777<<16)]:
  z=t/(name+'.zip')
  with zipfile.ZipFile(z,'w') as f:info=zipfile.ZipInfo(member);info.external_attr=mode;f.writestr(info,b'x')
  case('reject_'+name,lambda z=z,n=name:pkg.extract(z,t/(n+'-out')),True)
 # Private fixtures below are explicitly synthetic and never added to the archive.
 c={'ssid':'Synthetic-Y-NOT-OWNER','ap_password':'fixture-Y-ap-not-owner-9821','web_password':'fixture-Y-web-not-owner-6739'};cfg=t/'config.json';cfg.write_text(json.dumps(c));os.chmod(cfg,0o600)
 for name,config in [('missing',{}),('short',dict(c,ap_password='short')),('shortweb',dict(c,web_password='short')),('type',dict(c,web_password=42)),('autorun_input',dict(c,autorun_enabled=True)),('path_input',dict(c,autorun_script='x'))]:case('config_'+name,lambda config=config:priv.config(config),True)
 legacy=re.search(r'^#define\s+WIFI_PASSWORD\s+"([^"\\]*)"\s*$',(pkg.ROOT/'EvilDuckS3/config.h').read_text(),re.M)[1];case('legacy_password',lambda:priv.config(dict(c,ap_password=legacy)),True)
 case('private_inside_public_rejected',lambda:priv.prepare(a.public,cfg,a.public/'private',a.core,a.sdk,a.generator,a.mkspiffs),True)
 private=t/'private';case('real_fresh_generation_and_finalization',lambda:priv.prepare(a.public,cfg,private,a.core,a.sdk,a.generator,a.mkspiffs));case('recheck_complete_plan',lambda:priv.finalize(a.public,cfg,private,a.core,a.sdk,a.generator,a.mkspiffs))
 case('private_modes',lambda:require(private.stat().st_mode&0o077==0 and all(f.stat().st_mode&0o077==0 for f in private.rglob('*')),'private permissions'))
 for name,change in [('wrong_binding',lambda d: (d/'binding.json').write_text('{}')),('wrong_size',lambda d:(d/'images/fresh-nvs.bin').write_bytes(bytes(0x4000)))]:
  d=t/name;shutil.copytree(private,d);change(d);case(name,lambda d=d:priv.finalize(a.public,cfg,d,a.core,a.sdk,a.generator,a.mkspiffs),True)
 def mutate_nvs(name,kind):
  d=t/name;shutil.copytree(private,d)
  rows=[['duck','namespace','',''],['autorun_enabled','data','u8',0],['autorun_script','data','string',''],['ap_ssid','data','string',c['ssid']],['ap_password','data','string',c['ap_password']],['ap_channel','data','u8',1],['stealth','data','u8',0],['hidden_ap','data','u8',0],['disable_led','data','u8',0],['led_color','data','u32',0x28],['web_pw','data','string',c['web_password']],['ar_dly_min','data','u16',0],['ar_dly_max','data','u16',0]]
  if kind=='autorun':rows[1][3]=1
  elif kind=='path':rows[2][3]='not-executed.txt'
  elif kind=='type':rows[5][2:]=['string','1']
  elif kind=='missing':rows.pop(10)
  csvfile=d/'synthetic.csv'
  with csvfile.open('w',newline='') as f:w=csv.writer(f);w.writerow(['key','type','encoding','value']);w.writerows(rows)
  env=dict(os.environ,PYTHONPATH=str(a.generator),PYTHONDONTWRITEBYTECODE='1');cmd=[sys.executable,str(a.sdk/'components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py'),'generate',str(csvfile),str(d/'images/replacement.bin'),'0x5000'];r=subprocess.run(cmd,env=env,capture_output=True);require(r.returncode==0,'fixture generation failed');csvfile.unlink();(d/'images/replacement.bin').replace(d/'images/fresh-nvs.bin');inv=json.loads((d/'images/review-inventory.json').read_text());inv['artifacts'][0]['sha256']=pkg.sha(d/'images/fresh-nvs.bin');(d/'images/review-inventory.json').write_text(json.dumps(inv));priv.finalize(a.public,cfg,d,a.core,a.sdk,a.generator,a.mkspiffs)
 for kind in ['autorun','path','type','missing']:case('valid_nvs_wrong_'+kind,lambda kind=kind:mutate_nvs('nvs-'+kind,kind),True)
 def nonempty():
  d=t/'nonempty';shutil.copytree(private,d);src=t/'files';src.mkdir();(src/'benign.txt').write_text('test');pack_files(a.mkspiffs,src,t/'packed');shutil.copyfile(t/'packed/spiffs-new-0x160000.bin',d/'images/fresh-spiffs.bin');inv=json.loads((d/'images/review-inventory.json').read_text());inv['artifacts'][1]['sha256']=pkg.sha(d/'images/fresh-spiffs.bin');(d/'images/review-inventory.json').write_text(json.dumps(inv));priv.finalize(a.public,cfg,d,a.core,a.sdk,a.generator,a.mkspiffs)
 case('nonempty_private_filesystem',nonempty,True)
 def secret_free():
  with zipfile.ZipFile(archive) as z:
   for n in z.namelist():
    require(not any(x in n for x in ['fresh-nvs.bin','config.json','binding.json','settings.csv']), 'private filename in public')
    data=z.read(n);require(c['ap_password'].encode() not in data and c['web_password'].encode() not in data,'synthetic private credential leaked')
 case('public_archive_excludes_private_inputs',secret_free)
 # Generic CLI failure must not print credentials/config paths or traceback.
 bad=t/'bad.json';bad.write_text(json.dumps(dict(c,web_password='short')));os.chmod(bad,0o600)
 cmd=[sys.executable,str(pkg.ROOT/'tests/stage28y/private.py'),'prepare','--public',str(a.public),'--owner-config',str(bad),'--private',str(t/'cli-output'),'--core',str(a.core),'--sdk',str(a.sdk),'--generator',str(a.generator),'--mkspiffs',str(a.mkspiffs),'--receipt',str(t/'receipt.json')];r=subprocess.run(cmd,capture_output=True,text=True);case('sanitized_cli_error',lambda:require(r.returncode!=0 and str(bad) not in r.stderr and c['ap_password'] not in r.stderr and 'Traceback' not in r.stderr,'unsanitized CLI error'))
counts={s:sum(x['status']==s for x in results) for s in ['PASS','FAIL']};a.results.write_text(json.dumps(dict(counts=counts,assertions=len(results),results=results,fixtures='SYNTHETIC NON-OWNER; temporary files removed',asan_ubsan='NOT APPLICABLE: Python packaging; X native evidence unchanged and not rerun',physical=False),indent=2)+'\n');print(counts);raise SystemExit(bool(counts['FAIL']))
