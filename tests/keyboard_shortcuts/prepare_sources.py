#!/usr/bin/env python3
"""Compose immutable X then hash-checked shortcut delta in external scratch only."""
import pathlib,sys,json,subprocess
sys.dont_write_bytecode=True
import importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[2]
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
X=load(ROOT/'tests/stage28x/prepare_sources.py','shortcut_x_sources')
sha=X.sha;frameworks=X.frameworks;native_sources=X.native_sources;manifest=X.manifest
prepare=X.prepare

def overlay(s):
 pin=json.loads((ROOT/'docs/keyboard-shortcuts-source-manifest.json').read_text())
 for row in pin['before']:assert sha(s/row['file'])==row['sha256'],row['file']
 p=ROOT/'tests/keyboard_shortcuts/shortcuts.patch';assert sha(p)==pin['patch_sha256']
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(p)],cwd=s,check=True,capture_output=True)
 for row in pin['after']:assert sha(s/row['file'])==row['sha256'],row['file']
 return s
