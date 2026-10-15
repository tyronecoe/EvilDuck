#!/usr/bin/env python3
"""Read-only parent/freeze/input/receipt/publication verification. No devices."""
import argparse,hashlib,json,pathlib,stat,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE='5355b4dd76fe57884fb9036348f218dd28634958'
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--remote-before',type=pathlib.Path);p.add_argument('--remote-after',type=pathlib.Path);a=p.parse_args()
 assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
 assert git('branch','--show-current').decode().strip()=='stage28t-native-real-backend-route-b'
 head=git('rev-parse','HEAD').decode().strip()
 assert head==BASE or git('rev-parse','HEAD^').decode().strip()==BASE
 historical=[]
 for row in git('ls-tree','-rz',BASE).split(b'\0'):
  if not row:continue
  meta,name=row.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode()
  assert kind==b'blob' and f.read_bytes()==git('cat-file','blob',oid.decode()),name
  assert not f.is_symlink() and bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755'),name
  historical.append(name.decode())
 assert len(historical)==1186
 new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(historical))
 assert all(f.startswith(('tests/stage28t/','docs/stage28t-')) for f in new)
 subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
 m=json.loads((ROOT/'docs/stage28t-source-and-patch-manifest.json').read_text())
 for x in m['inputs']+m['native_seam_files']+[m[k] for k in ['patch','stage28s_patch','review_only_patch']]:assert sha(ROOT/x['file'])==x['sha256'],x['file']
 r=json.loads((ROOT/'docs/stage28t-test-results.json').read_text())
 assert r['primary']['counts']=={'PASS':47,'FAIL':0} and r['primary']['assertions']==467
 assert [x['id'] for x in r['primary']['results']]==['T%02d'%i for i in range(1,48)]
 for x in r['tested_runtime_fixtures']:assert sha(ROOT/x['file'])==x['sha256'],x['file']
 for x in r['primary']['results']:
  assert x['exit']==0 and not x['stderr'] and x['assertions']>0
  trace=json.loads(x['stdout'].split('TRACE ',1)[1]);assert trace['backend_shared_bytes']==136
  for call in trace['calls']:assert len(call['bytes'])==8 and call['id']==1 and call['instance']==0
 assert r['negative_control']['observed']['exit']==1
 s=r['unchanged_stage28s']['primary'];assert s['counts']=={'PASS':56,'FAIL':0} and s['assertions']==512
 suites=r['affected_actual_production_regressions']['suites']
 for s in suites.values():assert s['counts']=={'PASS':77,'FAIL':0} and s['assertions']==67371
 for x,y in zip(suites['unchanged_production']['results'],suites['candidate_optin_disabled']['results']):assert (x['id'],x['exit'],x['stdout'],x['stderr'])==(y['id'],y['exit'],y['stdout'],y['stderr'])
 assert r['preparation_controls']['PASS']==6 and r['preparation_controls']['FAIL']==0
 # Unified diff blank context requires a single leading space; no other exception.
 excluded=[]
 for name in ['candidate.patch','production-review-only.patch']:
  f='tests/stage28t/'+name;excluded.append(':(exclude)'+f)
  for line in (ROOT/f).read_text().splitlines():
   if line.endswith((' ','\t')):assert line==' '
 for staged in [[],['--cached']]:subprocess.run(['git','diff',*staged,'--check','--','.',*excluded],cwd=ROOT,check=True)
 remote='NOT REQUESTED'
 if a.remote_before or a.remote_after:
  assert a.remote_before and a.remote_after
  def refs(f):return dict(line.split()[::-1] for line in f.read_text().splitlines())
  before,after=refs(a.remote_before),refs(a.remote_after)
  assert len(before)==44 and all(after.get(k)==v for k,v in before.items())
  extra=set(after)-set(before);assert extra=={'refs/heads/stage28t-native-real-backend-route-b'} and after[next(iter(extra))]==git('rev-parse','HEAD').decode().strip()
  remote='PASS44 previous refs unchanged; only new Stage28T branch added'
 report=dict(status='PASS',baseline=BASE,historical_files_paths_modes=len(historical),frozen_stage26_files=235,tested_inputs='PASS',remote=remote,new_files=[dict(file=f,bytes=(ROOT/f).stat().st_size,sha256=sha(ROOT/f)) for f in new if f!='docs/stage28t-integrity.json'],self_excluded=True,hardware=False,firmware=False)
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='new_files'}))
if __name__=='__main__':main()
