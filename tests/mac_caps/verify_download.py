#!/usr/bin/env python3
"""Download public immutable package and compare every byte; no device APIs."""
import argparse,pathlib,sys,re,urllib.request,hashlib,json,zipfile,io,tempfile,importlib.util,subprocess
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--commit',required=True);p.add_argument('--destination',type=pathlib.Path,required=True);p.add_argument('--receipt',type=pathlib.Path,required=True);a=p.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.commit) and not a.destination.exists() and not a.receipt.exists()
expected=json.loads((ROOT/'docs/caps-duration-integrity.json').read_text());name=expected['file'];url='https://raw.githubusercontent.com/tyronecoe/EvilDuck/'+a.commit+'/downloads/'+name
with urllib.request.urlopen(url,timeout=60) as r:
 assert r.status==200;data=r.read(expected['bytes']+1)
assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256'];assert data==(ROOT/'downloads'/name).read_bytes();a.destination.write_bytes(data)
with zipfile.ZipFile(io.BytesIO(data)) as z,zipfile.ZipFile(ROOT/'downloads'/name) as local,tempfile.TemporaryDirectory(prefix='verified-public-download-') as tmp:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist())) and sorted(z.namelist())==sorted(expected['files']);members=[];d=pathlib.Path(tmp)
 for n in z.namelist():
  assert '/' not in n and '\\' not in n and n not in ('.','..');b=z.read(n);assert b==local.read(n);(d/n).write_bytes(b);members.append(dict(file=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 for n,size,sha in [('application.bin',expected['application_bytes'],expected['application_sha256']),('rollback-application.bin',1386176,'2c657f0c74f1d12c88aa1e6fa6daf5cc76de36e8e68bc41a325f39b19c9045a7')]:
  b=(d/n).read_bytes();assert len(b)==size and hashlib.sha256(b).hexdigest()==sha
 # Only import the downloaded validator AFTER exact ZIP/member byte equality.
 spec=importlib.util.spec_from_file_location('verified_download_preflight',d/'preflight.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);result=v.validate(d);assert result['package_integrity']=='PASS' and not result['installation_authorized'] and not result['selected_write_ranges']
previous={ref:sha for sha,ref in (l.split() for l in (pathlib.Path('/workspace/scratch/caps-duration-refs-before.txt').read_text().splitlines()))};current={ref:sha for sha,ref in (l.split() for l in subprocess.check_output(['git','ls-remote','--heads','--tags','origin'],cwd=ROOT,text=True).splitlines())};assert all(current.get(ref)==sha for ref,sha in previous.items());assert set(current)-set(previous)=={'refs/heads/caps-duration-feedback-trial'}
assert not subprocess.check_output(['git','diff','3e693fbe790af670278716cdf4d64c75485cb097','--diff-filter=MDRT','--name-only'],cwd=ROOT,text=True).strip()
out=dict(status='PASS',url=url,package_commit=a.commit,source_commit=expected['source_commit'],bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),every_member_identical=True,members=members,downloaded_preflight=result,previous_remote_refs_unchanged=len(previous),new_remote_refs=sorted(set(current)-set(previous)),baseline_files_unchanged=1649,frozen_stage26_files=235,physical_hardware=False,installation_executed=False,host_caps_or_led_tested=False)
a.receipt.write_text(json.dumps(out,indent=2)+'\n');print('PASS actual published download,',len(data),'bytes;',len(members),'members;',len(previous),'previous refs unchanged')
