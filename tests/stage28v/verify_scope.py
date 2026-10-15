#!/usr/bin/env python3
"""Read-only exact baseline, scratch, source, freeze and optional publication check."""
import pathlib,sys,subprocess,json,hashlib,stat,argparse
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
BASE='967596476dfe0dde5e824c8f6d1b2ba543502443';BRANCH='stage28v-service-ownership-controlled-candidate'
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def refs(p):return dict(line.split()[::-1] for line in pathlib.Path(p).read_text().splitlines())
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--remote-before',type=pathlib.Path);p.add_argument('--remote-after',type=pathlib.Path);a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
assert git('branch','--show-current').decode().strip()==BRANCH
head=git('rev-parse','HEAD').decode().strip();assert head==BASE or git('rev-parse','HEAD^').decode().strip()==BASE
old=[]
for row in git('ls-tree','-rz',BASE).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode();assert kind==b'blob' and not f.is_symlink();b=f.read_bytes()
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==oid.decode(),name
 assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755'),name;old.append(name.decode())
assert len(old)==1254
new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old))
assert all(x.startswith(('tests/stage28v/','docs/stage28v-')) and pathlib.Path(x).suffix not in ['.o','.elf','.bin','.uf2'] for x in new)
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
m=json.loads((ROOT/'docs/stage28v-source-manifest.json').read_text())
for x in m['inputs']+[m['patch']]+m['candidate_files']:assert sha(ROOT/x['file'])==x['sha256'],x['file']
r=json.loads((ROOT/'docs/stage28v-native-results.json').read_text())
assert r['primary']['counts']=={'PASS':56,'FAIL':0} and r['primary']['assertions']==566
assert r['primary']['negative_control']['exit']==1
for name,count,assertions in [('stage28u',64,515),('stage28t',47,467)]:
 s=r[name];s=s.get('primary',s);assert s['counts']=={'PASS':count,'FAIL':0} and s['assertions']==assertions
for role,s in r['production_comparison']['suites'].items():assert s['counts']=={'PASS':77,'FAIL':0} and s['assertions']==67371
for role in ['startup_original','startup_candidate']:assert r[role]['counts']=={'PASS':30,'FAIL':0} and r[role]['assertions']==635
assert r['target_disabled']['status']=='PASS' and len(r['target_disabled']['sources'])==15 and not r['target_disabled']['forbidden_host_thread_symbols']
assert r['preparation']['PASS']==7 and r['preparation']['FAIL']==0
for x in r['tested_v_files']:assert sha(ROOT/x['file'])==x['sha256'],x['file']
t=json.loads((ROOT/'docs/stage28v-target-object-results.json').read_text());assert t['status']=='PASS' and len(t['sources'])==20 and not t['forbidden_host_thread_symbols']
assert t['compiler_sha256']=='d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3'
for x in t['sources']:
 name=pathlib.Path(x['source']).name
 if name in {x['file'] for x in m['outputs']}:assert x['source_sha256']==next(x['sha256'] for x in m['outputs'] if x['file']==name)
for line in (ROOT/'tests/stage28v/services.patch').read_text().splitlines():
 if line.endswith((' ','\t')):assert line==' '
for opts in [[],['--cached']]:subprocess.run(['git','diff',*opts,'--check','--','.',':(exclude)tests/stage28v/services.patch'],cwd=ROOT,check=True)
publication='NOT REQUESTED'
if a.remote_before or a.remote_after:
 assert a.remote_before and a.remote_after
 before,after=refs(a.remote_before),refs(a.remote_after);assert len(before)==46 and all(after.get(k)==v for k,v in before.items())
 extra=set(after)-set(before);assert extra=={'refs/heads/'+BRANCH} and after[next(iter(extra))]==head;publication='PASS: all 46 previous refs unchanged; only new Stage28V ref added'
out=dict(status='PASS',baseline=BASE,head=head,historical_files_paths_modes=len(old),frozen=235,publication=publication,scope='precommit unless remote comparison supplied; integrity receipt excludes itself',new_files=[dict(file=x,size=(ROOT/x).stat().st_size,sha256=sha(ROOT/x)) for x in new if x!='docs/stage28v-integrity.json'],hardware=False,firmware_link=False)
a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='new_files'}))
