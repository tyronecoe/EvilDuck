#!/usr/bin/env python3
"""Read-only historical scope/source verification; external receipt only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE='dce42b8664c2964019cf4b488388d08b2b7fc2d0'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--protected-core',type=Path,required=True)
parser.add_argument('--sdk',type=Path,required=True)
parser.add_argument('--results',type=Path,required=True)
args=parser.parse_args()
if args.results.exists() or args.results.resolve().is_relative_to(ROOT):
    raise ValueError('Fresh external receipt required')
def git(*cmd):return subprocess.check_output(['git',*cmd],cwd=ROOT)
old=git('ls-tree','-r','--name-only',BASE).decode().splitlines()
for name in old:
    if (ROOT/name).read_bytes()!=git('show',BASE+':'+name):
        raise ValueError('Historical file changed: '+name)
if set(git('diff',BASE,'--name-only').decode().splitlines()) & set(old):
    raise ValueError('Historical tracked mode/path/content changed')
current=set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())
added=sorted(current-set(old))
for name in added:
    if not(name.startswith('docs/stage28k-') or name.startswith('tests/stage28k/')):
        raise ValueError('Out-of-scope addition: '+name)
source=json.loads((ROOT/'docs/stage28k-source-evidence.json').read_text())
if source['baseline']!=BASE:raise ValueError('Wrong source baseline')
roots={'protected-core':args.protected_core,'sdk':args.sdk}
anchors=source['repo_anchors']+source['dependency_anchors']
for row in anchors:
    root=roots[row['root']] if 'root' in row else ROOT
    path=Path(row['file'])
    if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe evidence path')
    raw=(root/path).read_bytes();lines=raw.decode().splitlines()
    if not 1<=row['start']<=row['end']<=len(lines):raise ValueError('Invalid source range')
    span=('\n'.join(lines[row['start']-1:row['end']])+'\n').encode()
    if hashlib.sha256(raw).hexdigest()!=row['file_sha256'] or hashlib.sha256(span).hexdigest()!=row['span_sha256']:
        raise ValueError('Evidence drift: '+str(path))
subprocess.run(['python3','tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
report=json.loads((ROOT/'docs/stage28k-test-results.json').read_text())
if report['counts']!={'PASS':37,'FAIL':0}:raise ValueError('Current harness failures')
if [r['name'].split('_')[0] for r in report['results'][:18]]!=['T%02d'%i for i in range(1,19)]:raise ValueError('Trace coverage missing')
legacy=json.loads((ROOT/'docs/stage28k-legacy-results.json').read_text())
if legacy['aggregate']!={'PASS':187,'FAIL':0,'assertions':579622}:raise ValueError('Legacy results disagree')
result=dict(status='PASS',baseline=BASE,byte_identical_historical_files=len(old),source_spans=len(anchors),protected_stage26_files=235,added_files=added,kind='static integrity evidence, not runtime assertion totals',physical_testing=False)
args.results.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
