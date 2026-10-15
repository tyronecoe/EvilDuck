#!/usr/bin/env python3
"""Corrupt only disposable synthetic copies of the verified patch-chain inputs."""
import pathlib,tempfile,json,shutil,subprocess,sys
sys.dont_write_bytecode=True
import prepare_sources as prep
ROOT=prep.ROOT;rows=[]
with tempfile.TemporaryDirectory(prefix='stage28v-controls-') as td:
 for case in ['healthy','wrong_input','wrong_u_patch','wrong_v_patch','wrong_candidate','wrong_output','reused_destination']:
  root=pathlib.Path(td)/case/'repo';root.mkdir(parents=True)
  ms=[json.loads((ROOT/('docs/stage28'+n+'-source-and-patch-manifest.json')).read_text()) for n in ['t','u']]
  v=json.loads((ROOT/'docs/stage28v-source-manifest.json').read_text());paths={'tests/stage28u/prepare_sources.py','tests/stage28t/prepare_sources.py','docs/stage28t-source-and-patch-manifest.json','docs/stage28u-source-and-patch-manifest.json'}
  for m in ms+[v]:
   for key in ['inputs','candidate_files']:
    paths.update(x['file'] for x in m.get(key,[]))
   for key in ['patch','stage28s_patch']:
    if key in m:paths.add(m[key]['file'])
  for name in paths:
   dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
  corrupt={'wrong_input':v['inputs'][0]['file'],'wrong_u_patch':ms[1]['patch']['file'],'wrong_v_patch':v['patch']['file'],'wrong_candidate':'tests/stage28v/mutation_guard.h'}.get(case)
  if corrupt:(root/corrupt).write_text('synthetic changed input')
  if case=='wrong_output':v['outputs'][0]['sha256']='0'*64
  path=root/'docs/stage28v-source-manifest.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(v))
  out=pathlib.Path(td)/case/'scratch'
  if case=='reused_destination':out.mkdir()
  prep.ROOT=root;rejected=False
  try:prep.prepare(out)
  except (AssertionError,FileExistsError,subprocess.CalledProcessError):rejected=True
  assert rejected==(case!='healthy'),case
  rows.append(dict(case=case,status='PASS',rejected=rejected))
prep.ROOT=ROOT
print(json.dumps(dict(PASS=len(rows),FAIL=0,results=rows,hardware=False),indent=2))
