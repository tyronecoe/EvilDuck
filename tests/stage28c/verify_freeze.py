#!/usr/bin/env python3
"""Read-only source freeze and saved remote-ref verification; no device operations."""
import argparse, hashlib, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path);p.add_argument('--remote-before',type=Path);p.add_argument('--remote-after',type=Path);a=p.parse_args()
old=json.loads((ROOT/'docs/stage28b-stage26-freeze.json').read_text());baseline=old['baseline_commit'];rows=[]
inventory=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline],cwd=ROOT,text=True).splitlines()
protected=[name for name in inventory if name.startswith(('EvilDuckS3/','review/stage26-installation/','tools/','docs/stage26-','proposals/'))]
if sorted(protected)!=sorted(row['file'] for row in old['files']):raise ValueError('Freeze inventory differs from immutable Git scope')
for row in old['files']:
 data=(ROOT/row['file']).read_bytes();original=subprocess.check_output(['git','show',baseline+':'+row['file']],cwd=ROOT)
 if data!=original or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Frozen file mismatch: '+row['file'])
 rows.append(dict(file=row['file'],bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
if len(rows)!=235:raise ValueError('Unexpected freeze inventory')
receipt=dict(baseline_commit=baseline,stage28c_baseline='e184f2837d008d2d732b97dcd5aab839bec3f502',all_files_byte_identical=True,stage27a_must_use_stage26_only=True,scope=old['scope'],files=rows)
if a.receipt:
 with a.receipt.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
if a.remote_before or a.remote_after:
 if not (a.remote_before and a.remote_after):raise ValueError('Both saved remote snapshots required')
 def refs(path):return dict(reversed(line.split()) for line in path.read_text().splitlines())
 before,after=refs(a.remote_before),refs(a.remote_after)
 for ref,sha in before.items():
  if after.get(ref)!=sha:raise ValueError('Preexisting remote ref changed: '+ref)
 print('PASS',len(before),'preexisting remote refs unchanged')
print('PASS 235 protected Stage26 files byte-identical')
