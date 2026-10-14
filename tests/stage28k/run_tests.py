#!/usr/bin/env python3
"""Linux host-only Stage28K runner; fresh external outputs, no devices/network."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build-dir',type=Path,required=True)
parser.add_argument('--results',type=Path,required=True)
args=parser.parse_args()
for path in (args.build_dir,args.results):
    if path.exists() or path.resolve().is_relative_to(ROOT):
        raise ValueError('Fresh external build/results required')
compiler=shutil.which('g++')
if not compiler:
    raise RuntimeError('SKIP_ENVIRONMENT: mandatory Linux GCC missing; gate stopped')
args.build_dir.mkdir()
flags=['-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',
       '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
sources=[ROOT/'language_preview'/name for name in ('core.cpp','keyboard.cpp','bridge.cpp')]+[ROOT/'tests/stage28k/journal_driver.cpp']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1')
version=subprocess.run([compiler,'--version'],capture_output=True,text=True,check=True).stdout
commands=[]


def build(name,main,extra=(),sanitized=True):
    selected=flags if sanitized else [x for x in flags if x not in ('-fsanitize=address,undefined',)]
    cmd=[compiler]+selected+list(extra)+[str(s) for s in sources]+[str(ROOT/'tests/stage28k'/main),'-o',str(args.build_dir/name)]
    commands.append(cmd)
    subprocess.run(cmd,env=env,check=True,timeout=180)
    return args.build_dir/name


def run(exe):
    result=subprocess.run([str(exe)],env=env,capture_output=True,text=True,timeout=180)
    return result,json.loads(result.stdout)


exe=build('journal-tests','test_journal.cpp')
normal,report=run(exe)
required=['T%02d'%n for n in range(1,19)]+['B%02d'%n for n in range(1,20)]
if [r['name'].split('_')[0] for r in report['results']]!=required:
    raise AssertionError('Missing/duplicate/incorrect trace coverage')
if normal.returncode or normal.stderr or report['counts']!={'PASS':37,'FAIL':0}:
    raise AssertionError('Unexpected C++ failure/sanitizer diagnostic: '+normal.stderr)
if sum(r['assertions'] for r in report['results'])!=report['assertions']:
    raise AssertionError('Malformed assertion receipt')
for row in report['results']:
    needed=('attempts','acceptances','source_intents','source_acks','delay_acks','receipts','intents','state','fault')
    if any(key not in row for key in needed):
        raise AssertionError('Missing per-case outcome evidence')
    accepted=sum(r['receipt_state']==1 for r in row['receipts'])
    if accepted!=row['acceptances'] or sum(i['acks'] for i in row['intents'])!=row['source_acks']:
        raise AssertionError('Receipt/ack total mismatch')
    ids=[(r['S'],r['R']) for r in row['receipts']]
    if len(ids)!=len(set(ids)) or any(len(r['snapshot'])!=16 for r in row['receipts']):
        raise AssertionError('Aliased action or wrong snapshot size')
    if any(i['acks']>1 for i in row['intents']):
        raise AssertionError('Duplicate source acknowledgement')
    intents={(i['S'],i['E']):i for i in row['intents']}
    if len(intents)!=len(row['intents']):
        raise AssertionError('Reused source identity')
    for r in row['receipts']:
        if r['E'] and (r['S'],r['E']) not in intents:
            raise AssertionError('Report action has no admitted source intent')
    for key,i in intents.items():
        receipts=sum(r['receipt_state']==1 and (r['S'],r['E'])==key for r in row['receipts'])
        if receipts!=i['reports_accepted'] or (i['kind']==1 and receipts) or (i['state']==2 and i['acks']):
            raise AssertionError('Invalid source/report or cancellation association')
    row['evidence_level']='executed unchanged preview/Bridge/Planner plus synthetic wrapper'
    row['sanitizers']='Linux ASan/UBSan; ASAN detect_leaks=1; UBSAN halt_on_error=1'
    row['state_name']=['Idle','Syncing','Prepared','Running','TerminalUndrained','DrainPending','Drained'][row['state']]
    row['keyboard_source_acks']=row['source_acks']-row['delay_acks']

# Deliberate failing build is separate and its repeated normal-case assertions are excluded.
bad=build('negative-control','test_journal.cpp',['-DSTAGE28K_NEGATIVE_CONTROL=1'])
negative,neg=run(bad)
if negative.returncode!=1 or neg['counts']!={'PASS':36,'FAIL':1} or neg['results'][0]['status']!='FAIL':
    raise AssertionError('Negative control did not fail as intended')
if 'FAIL line=' not in negative.stderr:
    raise AssertionError('Negative control missing assertion diagnostic')
probe=build('allocation-probe','allocation_probe.cpp',sanitized=False)
allocation,alloc=run(probe)
if allocation.returncode or allocation.stderr or alloc['new_calls']!=0:
    raise AssertionError('Unexpected allocation-probe result')
report.update(compiler_version=version,commands=commands,build_flags=flags,
              runner_exit=normal.returncode,required_traces='T01–T18 all executed',
              negative_control=dict(exit=negative.returncode,counts=neg['counts'],counted_in_primary_assertions=False),
              allocation_probe=alloc,allocation_probe_sanitized=False,
              physical_testing=False,network_from_tests=False,legacy_assertions_not_included=579622,
              scopes=dict(primary='37 new C++ groups',legacy='separate fresh published runners',owner_mac='owner-reported earlier runs; not executed here'))
text=json.dumps(report,indent=2).replace(str(ROOT),'<project-root>')+'\n'
args.results.write_text(text)
print(json.dumps(dict(status='PASS',counts=report['counts'],new_assertions=report['assertions'],sizes=report['sizes'],negative_control_exit=negative.returncode,new_calls=alloc['new_calls'])))
