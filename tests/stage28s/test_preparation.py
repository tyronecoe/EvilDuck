#!/usr/bin/env python3
"""Fail-closed preparation fault checks; synthetic source trees, no installed files."""
import hashlib,json,pathlib,shutil,sys,tempfile
sys.dont_write_bytecode=True
from run_tests import ROOT,load
m=load(ROOT/'tests/stage28s/prepare_sources.py','prepare');rows=[]
with tempfile.TemporaryDirectory(prefix='stage28s-prepare-') as d:
 p=pathlib.Path(d);m.prepare(p/'valid');rows.append(dict(name='exact_patch_output',status='PASS'))
 try:m.prepare(p/'valid');raise RuntimeError('overwrote output')
 except FileExistsError:rows.append(dict(name='existing_output_refused',status='PASS'))
 for case in ['wrong_source','wrong_patch','wrong_output_hash']:
  fake=p/case;fake.mkdir();pins=json.loads((ROOT/'docs/stage28s-source-and-patch-manifest.json').read_text())
  for row in pins['inputs']:
   dst=fake/row['file'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['file'],dst)
  dst=fake/pins['patch']['file'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/pins['patch']['file'],dst)
  if case=='wrong_source':
   f=fake/'EvilDuckS3/com.cpp';f.write_bytes(f.read_bytes()+b'\n// synthetic source mismatch\n')
  elif case=='wrong_patch':dst.write_bytes(dst.read_bytes()+b'\nsynthetic drift\n')
  else:pins['outputs'][0]['sha256']='0'*64
  manifest=fake/'docs/stage28s-source-and-patch-manifest.json';manifest.parent.mkdir(exist_ok=True);manifest.write_text(json.dumps(pins))
  m.ROOT=fake
  try:m.prepare(fake/'output');raise RuntimeError('unsafe preparation accepted')
  except AssertionError:rows.append(dict(name=case+'_rejected',status='PASS'))
 m.ROOT=ROOT
print(json.dumps(dict(preparation_checks=rows,counts={'PASS':len(rows),'FAIL':0},runtime_assertions=0,hardware=False),indent=2))
