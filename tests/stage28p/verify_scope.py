#!/usr/bin/env python3
"""Read-only historical/scope/pin/native-receipt/remote verification."""
import argparse,hashlib,json,pathlib,stat,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE='d57e9d1a2b7280f0b5f415d93ae9e7d23db54871'
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--source-root',type=pathlib.Path,required=True);p.add_argument('--protected-core',type=pathlib.Path);p.add_argument('--remote-before',type=pathlib.Path);p.add_argument('--remote-after',type=pathlib.Path);a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
def git(*v):return subprocess.check_output(['git',*v],cwd=ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=[]
for e in git('ls-tree','-rz',BASE).split(b'\0'):
 if not e:continue
 meta,name=e.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode()
 assert kind==b'blob' and f.read_bytes()==git('cat-file','blob',oid.decode()),name
 assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755'),name
 old.append(name.decode())
assert len(old)==1118 and not set(git('diff',BASE,'--name-only').decode().splitlines())&set(old)
added=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old));assert all(f.startswith(('docs/stage28p-','tests/stage28p/')) for f in added)
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
m=json.loads((ROOT/'docs/stage28p-source-and-boundary-manifest.json').read_text());altered={r['file']:r['output_sha256'] for r in m['adapted_files']};assert sha(ROOT/'tests/stage28p/native-io-adaptation.patch')==m['patch_sha256']
for row in m['original_tinyusb_inputs']+m['new_inputs']:
 f=row.get('tree_file',row['file']);assert sha(a.source_root/f)==altered.get(f,row['sha256']),f
core='NOT REQUESTED'
if a.protected_core:
 sys.path.insert(0,str(ROOT/'tools'));import patched_core
 patched_core.check_sources(a.protected_core,patched=True);core='PASS unchanged pinned protected core/SDK'
receipts='NOT PRESENT';f=ROOT/'docs/stage28p-test-results.json'
if f.exists():
 report=json.loads(f.read_text());assert report['manifest_sha256']==sha(ROOT/'docs/stage28p-source-and-boundary-manifest.json')
 rows=report['primary']['results'];assert [v['id'] for v in rows]==['P%02d'%i for i in list(range(1,27))+list(range(30,37))]
 assert report['primary']['counts']=={'PASS':33,'FAIL':0};assert sum(v['assertions'] for v in rows)==report['primary']['assertions']
 for row in report['fixtures']:
  assert row['file'].startswith('<project-root>/')
  assert sha(ROOT/row['file'].removeprefix('<project-root>/'))==row['sha256'],row['file']
 reg=report['separate_stage28o_regression'];assert reg['primary']['counts']=={'PASS':46,'FAIL':0} and reg['primary']['assertions']==931
 assert reg['unchanged_baseline']['counts']==reg['opt_in_disabled']['counts']=={'PASS':20,'FAIL':0}
 assert reg['unchanged_baseline']['assertions']==reg['opt_in_disabled']['assertions']==131
 receipts='PASS unique cases, tested fixture/manifest hashes; separate unchanged O/N counts'
remote='NOT REQUESTED'
if a.remote_before and a.remote_after:
 def refs(p):return dict(line.split()[::-1] for line in p.read_text().splitlines())
 before,after=refs(a.remote_before),refs(a.remote_after);assert len(before)==40 and all(after.get(k)==v for k,v in before.items());extra=set(after)-set(before)
 assert extra=={'refs/heads/stage28p-builder-dcd-lifecycle'} and after[next(iter(extra))]==git('rev-parse','HEAD').decode().strip()
 remote='PASS all40 previous refs unchanged; new Stage28P branch only'
x={'status':'PASS','baseline':BASE,'historical_files_paths_modes':len(old),'frozen_stage26_files':235,'core_sdk':core,'receipts':receipts,'remote':remote,'new_file_count':len(added),'new_files':[dict(file=f,size=(ROOT/f).stat().st_size,sha256=sha(ROOT/f)) for f in added if f!='docs/stage28p-integrity.json'],'integrity_self_excluded':True,'runtime_assertions':0};a.output.write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({k:v for k,v in x.items() if k!='new_files'}))
