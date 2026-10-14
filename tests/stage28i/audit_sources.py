#!/usr/bin/env python3
"""Read-only evidence/scope verification. No patching, compiler, device, network or adapter."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--protected-core',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
if a.results.exists():raise ValueError('Fresh external receipt required')
e=json.loads((ROOT/'docs/stage28i-source-evidence.json').read_text());checks=0
for row in e['repo_anchors']+e['dependency_anchors']:
 root=ROOT if 'root' not in row else (a.protected_core if row['root']=='protected-core' else a.sdk);file=root/row['file'];raw=file.read_bytes();lines=raw.decode().splitlines();span=('\n'.join(lines[row['start']-1:row['end']])+'\n').encode()
 if hashlib.sha256(raw).hexdigest()!=row['file_sha256'] or hashlib.sha256(span).hexdigest()!=row['span_sha256']:raise ValueError('Evidence drift: '+row['file'])
 checks+=2
# All preexisting tracked files stay unchanged; new files allowed only in stage audit scopes.
base=e['baseline'];old=subprocess.check_output(['git','ls-tree','-r','--name-only',base],cwd=ROOT,text=True).splitlines()
for name in old:
 original=subprocess.check_output(['git','show',base+':'+name],cwd=ROOT)
 if (ROOT/name).read_bytes()!=original:raise ValueError('Historical input changed: '+name)
 checks+=1
new=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
for name in set(new)-set(old):
 if not(name.startswith('docs/stage28i-') or name.startswith('tests/stage28i/')):raise ValueError('Out-of-scope new file: '+name)
 checks+=1
result=dict(status='PASS',source_spans=len(e['repo_anchors'])+len(e['dependency_anchors']),checked_historical_files=len(old),scope_checks=checks,kind='static integrity checks, NOT runtime compatibility tests/assertions',preview_unchanged=True,baseline=base,physical_testing=False,mac_native='PENDING OWNER / NOT TESTED')
a.results.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
