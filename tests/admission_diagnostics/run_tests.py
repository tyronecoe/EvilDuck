#!/usr/bin/env python3
"""Actual composed admission adapter/coordinator probes and inherited native cases.

Only disposable RAM-mock sources outside the repository are compiled/executed.
No target build, USB device, payload execution, network or owner data is used.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = pathlib.Path('/workspace/scratch/usb-os-observer-v2-release/focused-v2.json')
REGRESSIONS = pathlib.Path('/workspace/scratch/usb-os-observer-release/regressions-v2/native.json')
FIXTURE_SHA = 'c409c52a31ca5c34b22fc7678f3ec61eff89589caa03a21ed66afbd67a0f0f37'

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target-composed', type=pathlib.Path, required=True)
    p.add_argument('--output-dir', type=pathlib.Path, required=True)
    p.add_argument('--results', type=pathlib.Path, required=True)
    p.add_argument('--include-regressions', action='store_true')
    p.add_argument('--negative-control', action='store_true')
    p.add_argument('--resume-results', type=pathlib.Path)
    a = p.parse_args()
    executed_runner_sha = sha(__file__)
    assert not a.output_dir.exists() and not a.results.exists()
    assert not a.output_dir.resolve().is_relative_to(ROOT)
    assert sha(FIXTURE) == FIXTURE_SHA, 'PINNED_NATIVE_FIXTURE_RECEIPT_CHANGED'
    fixture = json.loads(FIXTURE.read_text())
    original_driver = pathlib.Path(next(x for x in fixture['command'] if x.endswith('/observer_v2_driver.cpp')))
    assert sha(original_driver) == fixture['driver_sha256']
    old_work = original_driver.parent.parent
    for row in fixture['source_bindings']:
        assert sha(row['native']) == row['sha256'], row['file']
    baseline = json.loads((ROOT/'docs/usb-os-observer-v2-build.json').read_text())['source_inventory']
    if a.negative_control:
        inventory = baseline
    else:
        prep = load(ROOT/'tests/admission_diagnostics_release/prepare_sources.py', 'admission_target_composition')
        inventory = prep.verify_final(a.target_composed)
    for row in inventory:
        rel = row['file'].removeprefix('EvilDuckS3/')
        path = a.target_composed/rel
        assert path.stat().st_size == row.get('size', row.get('bytes')) and sha(path) == row['sha256'], rel
    a.output_dir.mkdir(parents=True)
    for name in ['sources', 'observer-mocks', 'observer-arduino-api-mocks', 'static-response-api-mocks']:
        shutil.copytree(old_work/name, a.output_dir/name)
    source = a.output_dir/'sources'
    # Preserve mocks, then copy the complete final201 production composition over
    # every matching source. The compiled adapter/coordinator/HTTP body is exact.
    shutil.copytree(a.target_composed, source, dirs_exist_ok=True)
    observer_body = (ROOT/'tests/usb_os_observer_v2/test_main.cpp').read_text()
    assert observer_body.count('int main(int argc,char**argv)') == 1
    (source/'observer_v2_parent.inc').write_text(observer_body.replace('int main(int argc,char**argv)', 'int observer_v2_parent_main(int argc,char**argv)', 1))
    # Two historical assertions name the old stage identity. Retain its complete
    # predicate and replace only that expected literal with this exact BuildId.
    fixture_edits = []
    for inc in source.glob('*.inc'):
        text = inc.read_text()
        before = 'r.response.indexOf("ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-")'
        if before in text:
            assert text.count(before) == 1
            text = text.replace(before, 'r.response.indexOf(caps_trial::BuildId)', 1)
            fixture_edits.append(dict(file=inc.name, before=before, after='r.response.indexOf(caps_trial::BuildId)', occurrences=1))
            inc.write_text(text)
    assert {row['file'] for row in fixture_edits} == {'duration_cases.inc','feedback_cases.inc'}
    selected = HERE/('negative_control.cpp' if a.negative_control else 'test_main.cpp')
    driver = source/'admission_diagnostics_driver.cpp'
    driver.write_bytes(selected.read_bytes())
    command = [x.replace(str(old_work), str(a.output_dir)) for x in fixture['command']]
    old_driver = str(source/original_driver.name)
    assert command.count(old_driver) == 1
    command[command.index(old_driver)] = str(driver)
    assert '-fsanitize=address,undefined' in command and '-fno-omit-frame-pointer' in command
    bindings = []
    for x in command:
        if x.endswith('.cpp') and pathlib.Path(x) != driver:
            path = pathlib.Path(x)
            production = a.target_composed/path.name
            if production.exists():
                assert path.read_bytes() == production.read_bytes(), path.name
                bindings.append(dict(file=path.name, native=str(path), sha256=sha(path)))
    for name in ['adapter.h','core.h','coordinator.h','hid_backend.h','caps_trial.h','webserver.cpp','webfiles.h','seam.inc','backend_lease.inc']:
        assert (source/name).read_bytes() == (a.target_composed/name).read_bytes(), name
        bindings.append(dict(file=name,native=str(source/name),sha256=sha(source/name)))
    cases = ['N01','N02'] if a.negative_control else ['ADM%02d'%n for n in range(1,41)]
    groups = {x:'negative_control' if a.negative_control else 'focused_admission' for x in cases}
    if a.include_regressions:
        assert not a.negative_control
        inherited = json.loads(REGRESSIONS.read_text())
        assert inherited['counts'] == {'PASS':636,'FAIL':0} and inherited['assertions'] == 27376
        for row in inherited['results']:
            cases.append(row['id']);groups[row['id']]='existing_native_regression'
        for row in fixture['results']:
            cases.append(row['id']);groups[row['id']]='existing_observer_v2'
        # DEFINE cases are not in the older636 receipt; the complete composition
        # already carries their original bodies. Execute those exact cases too.
        define_text = (source/'define_labels_parent_cases.inc').read_text()
        for case in sorted(set(re.findall(r'"(DL\d\d)"',define_text))):
            if case not in groups:cases.append(case);groups[case]='existing_define_regression'
    assert len(cases) == len(set(cases))
    resumed = []
    if a.resume_results:
        assert a.include_regressions and not a.negative_control
        previous = json.loads(a.resume_results.read_text())
        assert previous['source'] == str(a.target_composed) and previous['full_source_inventory'] == inventory
        old_driver_text = driver.read_text().replace('if(id.size()==4&&id.rfind("V2",0)==0)', 'if(id.rfind("V2",0)==0)', 1)
        assert hashlib.sha256(old_driver_text.encode()).hexdigest() == previous['driver_sha256'], 'RESUME_DRIVER_CHANGE_IS_NOT_EXACT_DISPATCH_FIX'
        for row in previous['source_bindings']:
            assert sha(row['native']) == row['sha256']
        expected_failures = {'V%02d'%n for n in range(20,30)}
        assert {r['id'] for r in previous['results'] if r['status']=='FAIL'} == expected_failures
        assert all('unknownV2case' in r['stderr'] for r in previous['results'] if r['status']=='FAIL')
        resumed = [dict(r, reused_from=str(a.resume_results)) for r in previous['results'] if r['status']=='PASS']
        cases = [case for case in cases if case in expected_failures]
    compiled = subprocess.run(command,capture_output=True,text=True,timeout=420)
    out = dict(status='FAIL',command=command,compile_exit=compiled.returncode,compile_stdout=compiled.stdout,compile_stderr=compiled.stderr,
        results=[],source=str(a.target_composed),full_source_inventory=inventory,source_bindings=bindings,
        driver_sha256=sha(driver),runner_sha256=executed_runner_sha,fixture_receipt=str(FIXTURE),fixture_receipt_sha256=sha(FIXTURE),
        fixture_identity_assertion_edits=fixture_edits,historical_assertions_removed=0,
        sanitizers='ASan/UBSan/detect_leaks=1',sanitizer_flags_changed=False,
        negative_control=a.negative_control,hardware=False,real_hid=False,target_firmware_built=False,
        resumed_results=str(a.resume_results) if a.resume_results else None, fresh_case_count=len(cases),resumed_case_count=len(resumed))
    out['results'].extend(resumed)
    env = dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
    if compiled.returncode == 0:
        for case in cases:
            r = subprocess.run([str(a.output_dir/'native'),case],capture_output=True,text=True,timeout=60,env=env)
            found = re.search(r'PASS '+case+r' \((\d+) assertions\)',r.stdout)
            observation = re.search(r'OBSERVATION (.+)',r.stdout)
            row = dict(id=case,group=groups[case],exit=r.returncode,stdout=r.stdout,stderr=r.stderr,
                status='PASS' if r.returncode==0 and found and not r.stderr else 'FAIL',assertions=int(found[1]) if found else 0)
            if observation:row['observation']=json.loads(observation[1])
            out['results'].append(row)
    out['counts'] = {x:sum(row['status']==x for row in out['results']) for x in ['PASS','FAIL']}
    out['assertions'] = sum(row['assertions'] for row in out['results'])
    out['groups'] = {g:dict(PASS=sum(r['status']=='PASS' for r in out['results'] if r['group']==g),FAIL=sum(r['status']=='FAIL' for r in out['results'] if r['group']==g),assertions=sum(r['assertions'] for r in out['results'] if r['group']==g)) for g in sorted(set(groups.values()))}
    out['status'] = 'PASS' if compiled.returncode==0 and len(out['results'])==len(cases)+len(resumed) and not out['counts']['FAIL'] else 'FAIL'
    a.results.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['status','compile_exit','counts','assertions','groups']},indent=2))
    if compiled.returncode:print(compiled.stderr)
    for row in out['results']:
        if row['status']!='PASS':print(row)
    return int(out['status']!='PASS')
if __name__=='__main__':raise SystemExit(main())
