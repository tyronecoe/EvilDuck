#!/usr/bin/env python3
"""Apply deterministic default-off opt-in diff to fresh scratch copies only."""
import argparse,pathlib,hashlib,json,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(dest):
 dest=pathlib.Path(dest);dest.mkdir(exist_ok=False,parents=True)
 pins=json.loads((ROOT/'docs/stage28s-source-and-patch-manifest.json').read_text())
 assert sha(ROOT/pins['patch']['file'])==pins['patch']['sha256']
 for row in pins['inputs']:
  src=ROOT/row['file'];assert sha(src)==row['sha256'],row['file']
 for name in ['com.cpp','com.h']:(dest/name).write_bytes((ROOT/'EvilDuckS3'/name).read_bytes())
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(ROOT/'tests/stage28s/scheduler.patch')],cwd=dest,check=True,capture_output=True)
 for row in pins['outputs']:assert sha(dest/row['file'])==row['sha256'],row['file']
 return dest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('destination',type=pathlib.Path);a=p.parse_args();prepare(a.destination)
