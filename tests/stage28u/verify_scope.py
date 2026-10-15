#!/usr/bin/env python3
"""Read-only historical, frozen, tested source and publication verification."""
import pathlib,json,hashlib,subprocess,stat,argparse,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE='3e450127f7e6e1664a97be1107a18253844bfe35'
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--remote-before',type=pathlib.Path);p.add_argument('--remote-after',type=pathlib.Path);a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
assert git('branch','--show-current').decode().strip()=='stage28u-portable-coordinator-file-dispatch'
assert git('rev-parse','HEAD').decode().strip()==BASE or git('rev-parse','HEAD^').decode().strip()==BASE
old=[]
for row in git('ls-tree','-rz',BASE).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode()
 assert kind==b'blob' and not f.is_symlink() and f.read_bytes()==git('cat-file','blob',oid.decode()),name
 assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755'),name;old.append(name.decode())
assert len(old)==1217
new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old))
assert all(x.startswith(('tests/stage28u/','docs/stage28u-')) and pathlib.Path(x).suffix not in ['.o','.elf','.bin','.uf2'] for x in new)
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
m=json.loads((ROOT/'docs/stage28u-source-and-patch-manifest.json').read_text())
for x in m['inputs']+m['candidate_files']+[m['patch']]:assert sha(ROOT/x['file'])==x['sha256'],x['file']
r=json.loads((ROOT/'docs/stage28u-native-results.json').read_text());primary=r['primary']
assert primary['counts']=={'PASS':64,'FAIL':0} and [x['id'] for x in primary['results']]==['U%02d'%i for i in range(1,65)]
for x in primary['tested_fixtures']:assert sha(ROOT/x['file'])==x['sha256'],x['file']
assert primary['negative_control']['exit']==1
assert r['stage28t']['primary']['counts']=={'PASS':47,'FAIL':0} and r['stage28t']['primary']['assertions']==467
for suite in r['regressions']['suites'].values():assert suite['counts']=={'PASS':77,'FAIL':0} and suite['assertions']==67371
assert r['startup']['counts']=={'PASS':30,'FAIL':0}
assert r['preparation']['PASS']==7 and r['preparation']['FAIL']==0
t=json.loads((ROOT/'docs/stage28u-target-object-results.json').read_text());assert t['status']=='PASS' and t['forbidden_host_thread_symbols']==[]
assert t['compiler_sha256']=='d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3'
for line in (ROOT/'tests/stage28u/portable.patch').read_text().splitlines():
 if line.endswith((' ','\t')):assert line==' '
for stage in [[],['--cached']]:subprocess.run(['git','diff',*stage,'--check','--','.',':(exclude)tests/stage28u/portable.patch'],cwd=ROOT,check=True)
remote='NOT REQUESTED'
if a.remote_before or a.remote_after:
 assert a.remote_before and a.remote_after
 def refs(f):return dict(line.split()[::-1] for line in f.read_text().splitlines())
 before,after=refs(a.remote_before),refs(a.remote_after);assert len(before)==45 and all(after.get(k)==v for k,v in before.items())
 extra=set(after)-set(before);assert extra=={'refs/heads/stage28u-portable-coordinator-file-dispatch'} and after[next(iter(extra))]==git('rev-parse','HEAD').decode().strip();remote='PASS45 previous refs unchanged; only new Stage28U branch added'
report=dict(status='PASS',phase='PRECOMMIT unless publication checked; own hash excluded',baseline=BASE,historical_files_paths_modes=len(old),frozen_stage26_files=235,remote=remote,new_files=[dict(file=x,size=(ROOT/x).stat().st_size,sha256=sha(ROOT/x)) for x in new if x!='docs/stage28u-integrity.json'],self_excluded=True,hardware=False,firmware=False)
a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='new_files'}))
