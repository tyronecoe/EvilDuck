#!/usr/bin/env python3
import pathlib,sys,json,subprocess
sys.dont_write_bytecode=True
import importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[2]
def load(p,n):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
K=load(ROOT/'tests/keyboard_shortcuts/prepare_sources.py','http_keyboard_prepare')
sha=K.sha;frameworks=K.frameworks;native_sources=K.native_sources;manifest=K.manifest;prepare=K.prepare

def delta(s):
 p=json.loads((ROOT/'docs/http-snapshot-source-manifest.json').read_text());patch=ROOT/'tests/http_snapshot/contention.patch';assert sha(patch)==p['patch_sha256']
 for r in p['before']:assert sha(s/r['file'])==r['sha256'],r['file']
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(patch)],cwd=s,check=True,capture_output=True)
 for r in p['after']:assert sha(s/r['file'])==r['sha256'],r['file']
 return s

def overlay(s):
 K.overlay(s)
 (s/'execution_guard.h').write_bytes((ROOT/'EvilDuckS3/execution_guard.h').read_bytes())
 return delta(s)
