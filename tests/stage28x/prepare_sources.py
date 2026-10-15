#!/usr/bin/env python3
"""Exact W composition, X scratch-only delta, no installed source edits."""
import pathlib,sys,json,subprocess
sys.dont_write_bytecode=True
import importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[2]
def load(p,n):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
W=load(ROOT/'tests/stage28w/prepare_sources.py','immutable_w_prepare')
sha=W.sha;frameworks=W.frameworks;native_sources=W.native_sources
def manifest():return json.loads((ROOT/'docs/stage28x-source-manifest.json').read_text())
def prepare(out):
 m=manifest()
 for row in [m['patch']]+m['runtime_inputs']:
  assert sha(ROOT/row['file'])==row['sha256'],row['file']
 W.prepare(out)
 for name in ['coordinator.cpp','coordinator.h']:(out/name).write_bytes((ROOT/'tests/stage28v'/name).read_bytes())
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(ROOT/m['patch']['file'])],cwd=out,check=True,capture_output=True)
 for row in m['outputs']:assert sha(out/row['file'])==row['sha256'],row['file']
 return out
