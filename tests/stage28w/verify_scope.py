#!/usr/bin/env python3
"""Read-only historical/freeze/source/result/publication receipts; never a writer."""
import pathlib,json,hashlib,subprocess,stat,sys,argparse
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha,manifest
BASE='3144c9bdf7b78a4f75d6861fdffa0707c755fffc';BRANCH='stage28w-framework-boundary-controlled-link'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--before',type=pathlib.Path);p.add_argument('--after',type=pathlib.Path);a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
head=git('rev-parse','HEAD').decode().strip();assert head==BASE or git('rev-parse','HEAD^').decode().strip()==BASE;assert git('branch','--show-current').decode().strip()==BRANCH
old=[]
for line in git('ls-tree','-rz',BASE).split(b'\0'):
 if not line:continue
 meta,name=line.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode();assert kind==b'blob' and not f.is_symlink();data=f.read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid.decode(),name;assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755'),name;old.append(name.decode())
assert len(old)==1307
new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old));assert all(x.startswith(('docs/stage28w-','tests/stage28w/')) and pathlib.Path(x).suffix not in ['.elf','.bin','.o','.uf2'] for x in new)
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
m=manifest()
for x in [m['patch']]+m['runtime_inputs']+m.get('test_inputs',[]):assert sha(ROOT/x['file'])==x['sha256'],x['file']
r=json.loads((ROOT/'docs/stage28w-test-results.json').read_text());assert r['primary']['counts']=={'PASS':34,'FAIL':0} and r['primary']['assertions']==380
assert r['primary']['negative_control']['result']['exit']==1 and 'serial budget' in r['primary']['negative_control']['result']['stderr']
assert r['framework_components']['counts']=={'PASS':5,'FAIL':0} and r['framework_components']['assertions']==116
for n,passes,count in [('stage28v',56,566),('stage28u',64,515),('stage28t',47,467)]:
 q=r[n].get('primary',r[n]);assert q['counts']=={'PASS':passes,'FAIL':0} and q['assertions']==count
for q in r['production_comparison']['suites'].values():assert q['counts']=={'PASS':77,'FAIL':0} and q['assertions']==67371
assert r['startup']['counts']=={'PASS':30,'FAIL':0} and r['startup']['assertions']==635
for x in r['primary']['tested_w_files']:assert sha(ROOT/x['file'])==x['sha256'],x['file']
for filename,off in [('docs/stage28w-linked-enabled.json',False),('docs/stage28w-linked-selector-off.json',True)]:
 q=json.loads((ROOT/filename).read_text());assert q['status']=='PASS' and q['provenance']['elf_to_image_verified'] and q['verified_w_marker']==(not off)
 assert q['core_pin']==json.loads((ROOT/'docs/stage28v-target-object-results.json').read_text())['pin'];assert q['report']['fqbn'].find('PSRAM=disabled')>=0;assert q['report']['ota_slot_bytes']==0x740000
 assert len(q['linker_scripts'])==13 and len(q['link_response_files'])==3 and len(q['compiled_source_checks'])==(60 if off else 72)
 assert ('AsyncFileResponse' in q['symbols'])==off;assert len(q['framework_compiles'])==14
for line in (ROOT/'tests/stage28w/boundary.patch').read_text().splitlines():
 if line.endswith((' ','\t')):assert line==' '
for args in [[],['--cached']]:subprocess.run(['git','diff',*args,'--check','--','.',':(exclude)tests/stage28w/boundary.patch'],cwd=ROOT,check=True)
publication='NOT REQUESTED'
if a.before or a.after:
 assert a.before and a.after
 read=lambda f:dict(x.split()[::-1] for x in f.read_text().splitlines())
 before,after=read(a.before),read(a.after);assert len(before)==47 and all(after.get(k)==v for k,v in before.items());extra=set(after)-set(before);assert extra=={'refs/heads/'+BRANCH} and after[next(iter(extra))]==head;publication='PASS:47 previous refs unchanged; only new Stage28W ref added'
out=dict(status='PASS',baseline=BASE,head=head,historical_paths_bytes_modes=len(old),frozen_stage26=235,publication=publication,phase='precommit unless publication compared; own receipt excluded',new_files=[dict(file=x,size=(ROOT/x).stat().st_size,sha256=sha(ROOT/x)) for x in new if x!='docs/stage28w-integrity.json'],hardware=False)
a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='new_files'}))
