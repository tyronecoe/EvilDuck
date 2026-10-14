#!/usr/bin/env python3
"""Three external-only preparation checks; static utility checks, not C assertions."""
import argparse,hashlib,json,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--original',type=pathlib.Path,required=True);p.add_argument('--scratch',type=pathlib.Path,required=True);a=p.parse_args();assert not a.scratch.exists() and not a.scratch.resolve().is_relative_to(ROOT);a.scratch.mkdir()
def run(original,out):return subprocess.run([sys.executable,str(ROOT/'tests/stage28o/prepare_sources.py'),'--original',str(original),'--output',str(out)],capture_output=True,text=True)
valid=a.scratch/'valid';r=run(a.original,valid);assert r.returncode==0,r.stderr
before={str(v.relative_to(valid)):hashlib.sha256(v.read_bytes()).hexdigest() for v in valid.rglob('*') if v.is_file()}
r=run(a.original,valid);assert r.returncode!=0
assert before=={str(v.relative_to(valid)):hashlib.sha256(v.read_bytes()).hexdigest() for v in valid.rglob('*') if v.is_file()}
bad=a.scratch/'bad';shutil.copytree(a.original,bad);f=bad/'src/device/usbd.c';f.write_bytes(f.read_bytes()+b'\n/* synthetic hash fault */\n');r=run(bad,a.scratch/'rejected');assert r.returncode!=0 and not (a.scratch/'rejected').exists()
report={'static_utility_checks':3,'unexpected_failures':0,'checks':['fresh exact transform','existing output rejected unchanged','wrong source hash rejected before output'],'no_device':True}
(a.scratch/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
