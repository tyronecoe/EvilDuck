#!/usr/bin/env python3
"""Reproduce immutable S/T/U/V composition, then W delta in fresh scratch only."""
import pathlib,sys,json,hashlib,subprocess,importlib.util
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,n):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def manifest():return json.loads((ROOT/'docs/stage28w-source-manifest.json').read_text())
def prepare(out):
 out=pathlib.Path(out);assert not out.exists() and not out.resolve().is_relative_to(ROOT)
 m=manifest()
 for x in [m['patch']]+m['runtime_inputs']+m.get('test_inputs',[]):assert sha(ROOT/x['file'])==x['sha256'],x['file']
 load(ROOT/'tests/stage28v/prepare_sources.py','v_prep').prepare(out)
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(ROOT/m['patch']['file'])],cwd=out,check=True,capture_output=True)
 for x in m['outputs']:assert sha(out/x['file'])==x['sha256'],x['file']
 return out
def native_sources(out):return load(ROOT/'tests/stage28v/prepare_sources.py','v_native').native_sources(out)
def frameworks(user):
 m=manifest();rows=[]
 for lib in m['framework_libraries']:
  p=pathlib.Path(user)/'libraries'/lib['directory'];files=[dict(file=str(f.relative_to(p)),sha256=sha(f),size=f.stat().st_size) for f in sorted(p.rglob('*')) if f.is_file() and '.git' not in f.parts]
  assert files==lib['files'],lib['directory']
  rows.append(dict(directory=lib['directory'],tree_sha256=lib['tree_sha256']))
 return rows
if __name__=='__main__':prepare(pathlib.Path(sys.argv[1]))
