#!/usr/bin/env python3
"""Exact T composition then portable U delta, fresh external trees only."""
import pathlib,hashlib,json,subprocess,sys,importlib.util
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(out):
 out=pathlib.Path(out);assert not out.resolve().is_relative_to(ROOT)
 spec=importlib.util.spec_from_file_location('stage_t_prepare',ROOT/'tests/stage28t/prepare_sources.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
 m=json.loads((ROOT/'docs/stage28u-source-and-patch-manifest.json').read_text())
 for row in m['inputs']+[m['patch']]+m['candidate_files']:assert sha(ROOT/row['file'])==row['sha256'],row['file']
 t.prepare(out)
 for row in m['inputs']:
  name=pathlib.Path(row['file']).name
  if not (out/name).exists():(out/name).write_bytes((ROOT/row['file']).read_bytes())
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(ROOT/m['patch']['file'])],cwd=out,check=True,capture_output=True)
 for row in m['outputs']:assert sha(out/row['file'])==row['sha256'],row['file']
 return out
if __name__=='__main__':prepare(sys.argv[1])
