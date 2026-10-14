#!/usr/bin/env python3
"""Read-only Git/source/mode/freeze and optional protected dependency verification."""
import argparse, hashlib, json, pathlib, stat, subprocess, sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE='9b8c2b0e76ac37c63f86a51f1a573a8466ca5669'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',type=pathlib.Path,required=True);p.add_argument('--protected-core',type=pathlib.Path);a=p.parse_args()
if a.results.exists() or a.results.resolve().is_relative_to(ROOT):raise ValueError('Fresh external receipt required')
def git(*cmd):return subprocess.check_output(['git',*cmd],cwd=ROOT)
old=[]
for e in git('ls-tree','-rz',BASE).split(b'\0'):
    if not e:continue
    meta,name=e.split(b'\t');mode,kind,oid=meta.split();path=ROOT/name.decode()
    if kind!=b'blob' or path.read_bytes()!=git('cat-file','blob',oid.decode()):raise ValueError('Historical content mismatch: '+name.decode())
    if bool(path.stat().st_mode & stat.S_IXUSR)!=(mode==b'100755'):raise ValueError('Historical mode mismatch')
    old.append(name.decode())
if set(git('diff',BASE,'--name-only').decode().splitlines())&set(old):raise ValueError('Historical path/mode changed')
current=set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())
added=sorted(current-set(old))
if not all(v.startswith(('tests/stage28m/','docs/stage28m-')) for v in added):raise ValueError('Out-of-scope new path')
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
dependency='NOT REQUESTED'
if a.protected_core:
    sys.path.insert(0,str(ROOT/'tools'));import patched_core
    patched_core.check_sources(a.protected_core,patched=True);dependency='PASS exact existing protected core and SDK pins; no patch/build'
rows=[{'file':v,'bytes':(ROOT/v).stat().st_size,'sha256':hashlib.sha256((ROOT/v).read_bytes()).hexdigest()} for v in added]
report={'status':'PASS','baseline':BASE,'historical_files_paths_modes':len(old),'stage26_frozen_files':235,'dependency':dependency,'new_files':rows,'runtime_assertions':0}
a.results.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='new_files'}))
