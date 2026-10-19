#!/usr/bin/env python3
"""Download public immutable package and compare every byte; no device APIs."""
import argparse,pathlib,sys,re,urllib.request,hashlib,json,zipfile,io,tempfile,importlib.util,subprocess
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--commit',required=True);p.add_argument('--destination',type=pathlib.Path,required=True);p.add_argument('--receipt',type=pathlib.Path,required=True);a=p.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.commit) and not a.destination.exists() and not a.receipt.exists()
expected=json.loads((ROOT/'docs/caps-stop-integrity.json').read_text());name=expected['file'];url='https://raw.githubusercontent.com/tyronecoe/EvilDuck/'+a.commit+'/downloads/'+name
with urllib.request.urlopen(url,timeout=60) as r:
 assert r.status==200;data=r.read(expected['bytes']+1)
assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256'];assert data==(ROOT/'downloads'/name).read_bytes();a.destination.write_bytes(data)
with zipfile.ZipFile(io.BytesIO(data)) as z,zipfile.ZipFile(ROOT/'downloads'/name) as local,tempfile.TemporaryDirectory(prefix='verified-public-download-') as tmp:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist())) and sorted(z.namelist())==sorted(expected['files']);members=[];d=pathlib.Path(tmp)
 for n in z.namelist():
  assert '/' not in n and '\\' not in n and n not in ('.','..');b=z.read(n);assert b==local.read(n);(d/n).write_bytes(b);members.append(dict(file=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 for n,size,sha in [('application.bin',expected['application_bytes'],expected['application_sha256']),('rollback-application.bin',1397968,'5e10009fd3e5a0a862b4f7bed1f7f28ba8464f7bb1066fd8091c6e01b2ed4a59')]:
  b=(d/n).read_bytes();assert len(b)==size and hashlib.sha256(b).hexdigest()==sha
 # Only import the downloaded validator AFTER exact ZIP/member byte equality.
 spec=importlib.util.spec_from_file_location('verified_download_preflight',d/'preflight.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);result=v.validate(d);assert result['package_integrity']=='PASS' and not result['installation_authorized'] and not result['selected_write_ranges']
previous={ref:sha for sha,ref in (l.split() for l in (pathlib.Path('/workspace/scratch/caps-stop-refs-before.txt').read_text().splitlines()))};current={ref:sha for sha,ref in (l.split() for l in subprocess.check_output(['git','ls-remote','--heads','--tags','origin'],cwd=ROOT,text=True).splitlines())};assert all(current.get(ref)==sha for ref,sha in previous.items());assert set(current)-set(previous)=={'refs/heads/caps-stop-hid-trace'}
assert not subprocess.check_output(['git','diff','5e22569709f44bd4a6c429beb43a055d94d39257','--diff-filter=MDRT','--name-only'],cwd=ROOT,text=True).strip()
out=dict(status='PASS',url=url,package_commit=a.commit,source_commit=expected['source_commit'],bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),every_member_identical=True,members=members,downloaded_preflight=result,previous_remote_refs_unchanged=len(previous),new_remote_refs=sorted(set(current)-set(previous)),baseline_files_unchanged=len(subprocess.check_output(['git','ls-tree','-r','--name-only','5e22569709f44bd4a6c429beb43a055d94d39257'],cwd=ROOT,text=True).splitlines()),frozen_stage26_files=235,physical_hardware=False,installation_executed=False,host_caps_or_led_tested=False)
a.receipt.write_text(json.dumps(out,indent=2)+'\n');print('PASS actual published download,',len(data),'bytes;',len(members),'members;',len(previous),'previous refs unchanged')
