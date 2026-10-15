#!/usr/bin/env python3
"""Preparation fault controls; synthetic copies only, no compiler or device."""
import hashlib,json,pathlib,shutil,subprocess,sys,tempfile
sys.dont_write_bytecode=True
import prepare_sources as prep
ROOT=prep.ROOT
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 results=[]
 with tempfile.TemporaryDirectory(prefix='stage28t-preparation-') as tmp:
  t=pathlib.Path(tmp)
  for case in ['healthy','wrong_input','wrong_patch','wrong_output','reused_destination','combined_review_patch']:
   fixture=t/case/'repo';fixture.mkdir(parents=True)
   m=json.loads((ROOT/'docs/stage28t-source-and-patch-manifest.json').read_text())
   paths=[x['file'] for x in m['inputs']]+[m[k]['file'] for k in ['stage28s_patch','patch']]
   for path in paths:
    dst=fixture/path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dst)
   if case=='wrong_input':(fixture/m['inputs'][0]['file']).write_text('altered')
   if case=='wrong_patch':(fixture/m['patch']['file']).write_text('altered')
   if case=='wrong_output':m['outputs'][0]['sha256']='0'*64
   dst=fixture/'docs/stage28t-source-and-patch-manifest.json';dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(m))
   out=t/case/'scratch'
   if case=='reused_destination':out.mkdir()
   prep.ROOT=fixture
   if case=='combined_review_patch':
    out.mkdir()
    for n in ['com.cpp','com.h','hid_backend.cpp','hid_backend.h']:shutil.copyfile(ROOT/'EvilDuckS3'/n,out/n)
    subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(ROOT/'tests/stage28t/production-review-only.patch')],cwd=out,check=True,capture_output=True)
    assert all(digest(out/x['file'])==x['sha256'] for x in m['outputs'])
   else:
    rejected=False
    try:prep.prepare(out)
    except (AssertionError,FileExistsError):rejected=True
    assert rejected==(case!='healthy'),case
   results.append(dict(case=case,status='PASS'))
 prep.ROOT=ROOT
 print(json.dumps(dict(PASS=len(results),FAIL=0,results=results,hardware=False),indent=2))
if __name__=='__main__':main()
