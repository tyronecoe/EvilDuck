"""Deterministic source-only future-owner LED fixture; never compiles or runs IOKit."""
import argparse,hashlib,json,pathlib,stat,subprocess,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
def package(destination,commit):
 files={}
 for name in ('led_action.py','led_action.c'):
  path='tests/lock_feedback/'+name
  data=subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)
  assert data==(ROOT/path).read_bytes(), 'Uncommitted host fixture source'
  files[name]=data
 guide='docs/lock-feedback-owner-check.md'
 files['README.md']=subprocess.check_output(['git','show',commit+':'+guide],cwd=ROOT)
 assert files['README.md']==(ROOT/guide).read_bytes()
 manifest=dict(label='REVIEW ONLY; NOT AUTHORIZED FOR HARDWARE EXECUTION',source_commit=commit,build_id='ROUTEB-LOCK-FEEDBACK-20261023-v1',native_Apple_compilation='UNVERIFIED',hardware_tested=False,files={n:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in files.items()})
 files['manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
 with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(files.items()):
   info=zipfile.ZipInfo(name,(2026,10,23,0,0,0));info.external_attr=(stat.S_IFREG|0o644)<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 with zipfile.ZipFile(destination)as z:
  assert z.testzip() is None and set(z.namelist())==set(files)
  for n,b in files.items():assert z.read(n)==b
 p=pathlib.Path(destination)
 return dict(file=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_commit=commit,members=sorted(files))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--source-commit',required=True);a=p.parse_args();print(json.dumps(package(a.archive,a.source_commit),indent=2))
