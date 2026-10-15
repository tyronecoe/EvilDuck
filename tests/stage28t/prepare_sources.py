#!/usr/bin/env python3
"""Exact two-stage patches in fresh external scratch; no installed dependencies."""
import pathlib,json,hashlib,subprocess,argparse
ROOT=pathlib.Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(out):
 out=pathlib.Path(out);assert not out.resolve().is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 m=json.loads((ROOT/'docs/stage28t-source-and-patch-manifest.json').read_text())
 for row in m['inputs']:assert sha(ROOT/row['file'])==row['sha256']
 for role in ['stage28s_patch','patch']:assert sha(ROOT/m[role]['file'])==m[role]['sha256']
 (out/'platform.cpp').write_bytes((ROOT/'tests/stage1/mocks/host.cpp').read_bytes())
 for name in ['com.cpp','com.h','hid_backend.cpp','hid_backend.h']:(out/name).write_bytes((ROOT/'EvilDuckS3'/name).read_bytes())
 for role,rows in [('stage28s_patch',m['intermediate']),('patch',m['outputs'])]:
  subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(ROOT/m[role]['file'])],cwd=out,check=True,capture_output=True)
  for row in rows:assert sha(out/row['file'])==row['sha256']
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('destination',type=pathlib.Path);a=p.parse_args();prepare(a.destination)
