#!/usr/bin/env python3
"""Synthetic fault controls for exact scratch preparation; no compiler/device."""
import pathlib,json,sys,shutil,tempfile,importlib.util
sys.dont_write_bytecode=True
import prepare_sources as prep
ROOT=prep.ROOT
with tempfile.TemporaryDirectory(prefix='stage28u-prep-') as td:
 results=[]
 for case in ['healthy','wrong_input','wrong_t_patch','wrong_u_patch','wrong_candidate','wrong_output','reused_destination']:
  root=pathlib.Path(td)/case/'fixture';root.mkdir(parents=True)
  um=json.loads((ROOT/'docs/stage28u-source-and-patch-manifest.json').read_text());tm=json.loads((ROOT/'docs/stage28t-source-and-patch-manifest.json').read_text())
  paths={x['file'] for x in um['inputs']+um['candidate_files']+tm['inputs']+[um['patch'],tm['patch'],tm['stage28s_patch']]}
  paths.update(['tests/stage28t/prepare_sources.py','docs/stage28t-source-and-patch-manifest.json'])
  for name in paths:
   dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
  key={'wrong_input':um['inputs'][0]['file'],'wrong_t_patch':tm['patch']['file'],'wrong_u_patch':um['patch']['file'],'wrong_candidate':um['candidate_files'][0]['file']}.get(case)
  if key:(root/key).write_text('corrupt synthetic input')
  if case=='wrong_output':um['outputs'][0]['sha256']='0'*64
  manifest=root/'docs/stage28u-source-and-patch-manifest.json';manifest.parent.mkdir(parents=True,exist_ok=True);manifest.write_text(json.dumps(um))
  out=pathlib.Path(td)/case/'scratch'
  if case=='reused_destination':out.mkdir()
  prep.ROOT=root;rejected=False
  try:prep.prepare(out)
  except (AssertionError,FileExistsError):rejected=True
  assert rejected==(case!='healthy'),case
  results.append(dict(case=case,status='PASS'))
 prep.ROOT=ROOT
 print(json.dumps(dict(PASS=len(results),FAIL=0,results=results,hardware=False),indent=2))
