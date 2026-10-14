#!/usr/bin/env python3
"""Fresh memory-only transport contract tests. No devices, network or target compilation."""
import argparse, hashlib, json, os, pathlib, shutil, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--build-dir',type=pathlib.Path,required=True)
p.add_argument('--results',type=pathlib.Path,required=True)
a=p.parse_args()
for x in (a.build_dir,a.results):
    if x.exists() or x.resolve().is_relative_to(ROOT):raise ValueError('Fresh external output required')
compiler=shutil.which('g++')
if not compiler:raise RuntimeError('Required GCC unavailable; stopped, not PASS')
a.build_dir.mkdir()
flags=['-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1')
commands=[]
preview=[ROOT/'language_preview'/n for n in ('core.cpp','keyboard.cpp','bridge.cpp')]
new=[ROOT/'tests/stage28m'/n for n in ('synthetic_transport.cpp','journal_driver.cpp')]
def build(name,main,extra=(),historical=False,sanitize=True):
    f=[v for v in flags if sanitize or v!='-fsanitize=address,undefined']
    sources=preview+([ROOT/'tests/stage28k/journal_driver.cpp'] if historical else new)
    cmd=[compiler]+f+list(extra)+[str(v) for v in sources]+[str(ROOT/'tests/stage28m'/main),'-o',str(a.build_dir/name)]
    commands.append(cmd);subprocess.run(cmd,env=env,check=True,timeout=180);return a.build_dir/name
def run(exe):
    r=subprocess.run([str(exe)],env=env,capture_output=True,text=True,timeout=180)
    return r,json.loads(r.stdout)
old,oldrow=run(build('historical-k01','k01_reproducer.cpp',['-DHISTORICAL_K01=1'],historical=True))
if old.returncode!=1 or not oldrow['start'] or oldrow['queued_after_start']!=1 or oldrow['queued_after_terminal']!=0 or oldrow['setup_held'] or 'K01 INTENDED BARRIER FAILED' not in old.stderr:raise AssertionError('K01 not reproduced for intended reason')
corrected,correctedrow=run(build('corrected-k01','k01_reproducer.cpp'))
if corrected.returncode or corrected.stderr or correctedrow['start'] or correctedrow['queued_after_start']!=1:raise AssertionError('Corrected barrier failed')
normal,report=run(build('transport-tests','test_transport.cpp'))
required=['L%02d'%v for v in range(1,25)]+['B%02d'%v for v in range(1,13)]
if normal.returncode or normal.stderr or report['counts']!={'PASS':36,'FAIL':0}:raise AssertionError('Primary failed: '+normal.stderr)
if [r['id'] for r in report['results']]!=required or sum(r['assertions'] for r in report['results'])!=report['assertions']:raise AssertionError('Trace/accounting mismatch')
for case in report['results']:
    if not case['fixtures']:raise AssertionError('Missing fixture evidence')
    case['mock_status']='EXECUTED';case['real_stack_and_hardware']='NOT EXECUTED'
    for row in case['fixtures']:
        ts=row['transfers'];receipts=row['receipts'];intents=row['intents']
        if len({(t['C'],t['Q']) for t in ts})!=len(ts):raise AssertionError('Reused C/Q')
        if len({(r['S'],r['R']) for r in receipts})!=len(receipts):raise AssertionError('Reused S/R')
        if sum(t['accepted'] for t in ts)!=row['Accepted'] or sum(r['receipt']==1 for r in receipts)!=row['Accepted']:raise AssertionError('Acceptance totals')
        if sum(i['acks'] for i in intents)!=row['source_acks'] or any(i['acks']>1 for i in intents):raise AssertionError('Source ack totals')
        if sum(t['outcome']==1 for t in ts)!=row['submissions'] or len(ts)!=row['submit_calls']:raise AssertionError('Submission totals')
        for t in ts:
            if len(t['wire'])!=2*t['length'] or t['length']!=(9 if t['report_id'] else 8):raise AssertionError('Wire shape')
            if t['accepted'] and (not t['success'] or not t['retired'] or t['cancelled'] or not t['acceptance_order']>max(t['success_order'],t['retirement_order'])):raise AssertionError('Unsafe acceptance')
            if not any((r['S'],r['E'],r['R'])==(t['S'],t['E'],t['R']) for r in receipts):raise AssertionError('Transfer not bound to report')
        for i in intents:
            count=sum(t['accepted'] and (t['S'],t['E'])==(i['S'],i['E']) for t in ts)
            if count!=i['reports_accepted'] or (i['kind']==1 and count) or (i['state']==2 and i['acks']):raise AssertionError('Invalid event association')
negative,neg=run(build('negative-control','test_transport.cpp',['-DSTAGE28M_NEGATIVE_CONTROL=1']))
if negative.returncode!=1 or neg['counts']!={'PASS':35,'FAIL':1} or neg['results'][0]['status']!='FAIL' or 'FAIL line=' not in negative.stderr:raise AssertionError('Negative control not meaningful')
allocation,alloc=run(build('allocation-probe','allocation_probe.cpp',sanitize=False))
if allocation.returncode or allocation.stderr or alloc['new_calls']!=0:raise AssertionError('Allocation probe failed')
report.update(compiler=subprocess.check_output([compiler,'--version'],text=True),compiler_sha256=hashlib.sha256(pathlib.Path(compiler).read_bytes()).hexdigest(),flags=flags,commands=commands,exit=normal.returncode,sanitizers={'ASan':'clean','UBSan':'clean','leak_detection':'detect_leaks=1; clean'},historical_K01={'classification':'CONTROLLED DEFECT REPRODUCTION; excluded primary','exit':old.returncode,'stdout':oldrow,'diagnostic':old.stderr},corrected_K01={'exit':corrected.returncode,'stdout':correctedrow,'counted_in_primary':False},negative_control={'exit':negative.returncode,'counts':neg['counts'],'counted_in_primary':False},allocation_probe=alloc,allocation_probe_sanitized=False,hardware=False,target_compilation=False,scopes={'primary':'36 groups, fresh executed counts only','L20_exact_non_event_progress':'BLOCKED/UNSELECTED pre-admission API variant','real_transport':'NOT EXECUTED'})
a.results.write_text(json.dumps(report,indent=2).replace(str(ROOT),'<project-root>')+'\n')
print(json.dumps({'counts':report['counts'],'assertions':report['assertions'],'K01_historical_exit':old.returncode,'K01_corrected_exit':corrected.returncode,'negative_exit':negative.returncode,'sizes':report['sizes'],'new_calls':alloc['new_calls']}))
