#!/usr/bin/env python3
"""Read-only historical freeze, native fixture and publication verification."""
import argparse,hashlib,json,pathlib,stat,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE='6c186219c9ef7037f3ecab9bae44179421fd1278'
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--remote-before',type=pathlib.Path);p.add_argument('--remote-after',type=pathlib.Path);a=p.parse_args()
assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
def git(*v):return subprocess.check_output(['git',*v],cwd=ROOT)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
old=[]
for row in git('ls-tree','-rz',BASE).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode()
 assert kind==b'blob' and f.read_bytes()==git('cat-file','blob',oid.decode())
 assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755');old.append(name.decode())
assert len(old)==1164
new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old))
assert all(f.startswith(('tests/stage28s/','docs/stage28s-')) for f in new)
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
m=json.loads((ROOT/'docs/stage28s-source-and-patch-manifest.json').read_text())
for row in m['inputs']:assert sha(ROOT/row['file'])==row['sha256']
assert sha(ROOT/m['patch']['file'])==m['patch']['sha256']
for row in m['native_seam_files']:assert sha(ROOT/row['file'])==row['sha256']
r=json.loads((ROOT/'docs/stage28s-test-results.json').read_text())
assert r['primary']['counts']=={'PASS':56,'FAIL':0} and r['primary']['assertions']==512
assert [x['id'] for x in r['primary']['results']]==['S%02d'%i for i in range(1,57)]
for row in r['tested_fixtures']:assert sha(ROOT/row['file'])==row['sha256'],row['file']
for row in r['primary']['results']:
 tr=row['trace'];calls=[]
 for run in tr['calls_rle']:
  for i in range(run['count']):calls.append(dict(run['call'],at=(run['first_time']+i*run['stride'])&0xffffffff))
 restored=dict(tr);del restored['calls_rle'];del restored['calls_sha256'];restored['calls']=calls
 assert hashlib.sha256(json.dumps(calls,sort_keys=True,separators=(',',':')).encode()).hexdigest()==tr['calls_sha256']
 assert row['assertions']>0
remote='NOT REQUESTED'
if a.remote_before or a.remote_after:
 assert a.remote_before and a.remote_after
 def refs(f):return dict(line.split()[::-1] for line in f.read_text().splitlines())
 before,after=refs(a.remote_before),refs(a.remote_after);assert len(before)==43 and all(after.get(k)==v for k,v in before.items());extra=set(after)-set(before);assert extra=={'refs/heads/stage28s-native-runtime-scheduler'} and after[next(iter(extra))]==git('rev-parse','HEAD').decode().strip();remote='PASS43 prior refs unchanged; new S only'
# A unified diff's empty context line MUST contain its one leading space.
# Validate that narrow format exception; preserve the exact runtime-tested patch.
for line in (ROOT/'tests/stage28s/scheduler.patch').read_text().splitlines():
 if line.endswith((' ','\t')):assert line==' '
for staged in [[],['--cached']]:
 subprocess.run(['git','diff',*staged,'--check','--','.',':(exclude)tests/stage28s/scheduler.patch'],cwd=ROOT,check=True)
x=dict(status='PASS',baseline=BASE,historical_files_paths_modes=len(old),frozen_stage26_files=235,source_patch_hashes='PASS',primary_receipt='PASS56/512; exact RLE backend-call reconstruction',remote=remote,new_files=[dict(file=f,size=(ROOT/f).stat().st_size,sha256=sha(ROOT/f)) for f in new if f!='docs/stage28s-integrity.json'],self_excluded=True,hardware=False,firmware=False)
a.output.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({k:v for k,v in x.items() if k!='new_files'}))
