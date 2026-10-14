#!/usr/bin/env python3
"""Execute genuine publisher-pinned TinyUSB C with fake controller/custom OS only."""
import argparse,gzip,hashlib,json,os,pathlib,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args()
for output in (a.build_dir,a.results):
    if output.exists() or output.resolve().is_relative_to(ROOT):raise ValueError('Fresh external outputs required')
source=a.source_root.resolve();manifest=json.loads((ROOT/'docs/stage28n-source-manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for row in manifest['vendor_inputs']:
    if sha(source/row['file'])!=row['sha256']:raise ValueError('Source mismatch: '+row['file'])
compiler=shutil.which('gcc');gcov=shutil.which('gcov')
if not compiler or not gcov:raise RuntimeError('Required native GCC/gcov unavailable; not PASS')
a.build_dir.mkdir();sources=[source/'src'/v for v in manifest['compiled_translation_units']]+[ROOT/'tests/stage28n/boundary.c',ROOT/'tests/stage28n/test_components.c']
flags=['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','--coverage']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1')
commands=[]
def build(name,negative=False):
    exe=a.build_dir/name;cmd=[compiler]+flags+(['-DSTAGE28N_NEGATIVE_CONTROL=1'] if negative else [])+['-I',str(ROOT/'tests/stage28n'),'-I',str(source/'src')]+[str(v) for v in sources]+['-o',str(exe)];commands.append(cmd);subprocess.run(cmd,check=True,env=env,timeout=180);return exe
exe=build('component-tests');rows=[]
for i in range(1,21):
    case='N%02d'%i;directory=a.build_dir/case;directory.mkdir();strip=len(a.build_dir.resolve().parts)-1
    case_env=dict(env,GCOV_PREFIX=str(directory.resolve()),GCOV_PREFIX_STRIP=str(strip))
    cmd=[str(exe.resolve()),case];commands.append(cmd);run=subprocess.run(cmd,env=case_env,capture_output=True,text=True,timeout=30)
    if run.returncode or run.stderr:raise AssertionError(case+' unexpected failure: '+run.stderr)
    row=json.loads(run.stdout)
    if row['id']!=case or row['observation_status']!='PASS' or row['contract_status']!='NOT SATISFIED':raise AssertionError('Incorrect receipt')
    if len(row['callbacks'])!=row['callback_count'] or any(c['submission_identity_exposed'] for c in row['callbacks']):raise AssertionError('Fabricated callback identity/count')
    if sum(s['ep']==129 for s in row['submissions'])!=row['hid_submits']:raise AssertionError('Submission count mismatch')
    for s in row['submissions']:
        if len(s['frame'])!=2*s['length'] or s['entered_at']>=s['returned_at']:raise AssertionError('Bad frame/order receipt')
    for event in row['events']:
        if event['queue_after']>4:raise AssertionError('Unbounded queue')
    functions=[];coverage_commands=[]
    for note in sorted(a.build_dir.glob('component-tests-*.gcno')):
        copied=directory/note.name;shutil.copyfile(note,copied)
        command=[gcov,'-j','-f',str(copied.resolve())];coverage_commands.append(command)
        covered=subprocess.run(command,cwd=directory,capture_output=True,text=True,timeout=30)
        if covered.returncode:raise AssertionError('Coverage failed: '+covered.stderr)
    for report in sorted(directory.glob('*.gcov.json.gz')):
        data=json.loads(gzip.decompress(report.read_bytes()))
        for file in data['files']:
            path=pathlib.Path(file['file'])
            if path.is_relative_to(source):
                functions += [dict(file=str(path.relative_to(source)),name=f['name'],count=f['execution_count'],start_line=f['start_line'],end_line=f['end_line']) for f in file['functions'] if f['execution_count']>0]
    executed={v['name'] for v in functions};required={'dcd_event_handler','tud_task_ext','tud_hid_n_report','usbd_edpt_xfer'}
    if i<19:required.add('hidd_xfer_cb')
    if i==18:required.add('hidd_control_xfer_cb')
    if i==20:required.update(('tud_deinit','hidd_deinit'))
    if not required.issubset(executed):raise AssertionError(case+' missing actual vendor execution: '+str(required-executed))
    row.update(exit=run.returncode,stderr=run.stderr,executed_vendor_functions=functions,coverage_commands=coverage_commands,physical_behavior='NOT TESTED',boundary='fake DCD/controller; supported custom OS; no actual FreeRTOS/controller')
    rows.append(row);print('PASS observation',case,'assertions',row['assertions'])
negative=build('negative-control',True);nr=subprocess.run([str(negative.resolve()),'N01'],capture_output=True,text=True,env=env,timeout=30);neg=json.loads(nr.stdout)
if nr.returncode!=1 or neg['observation_status']!='FAIL' or 'FAIL line=' not in nr.stderr:raise AssertionError('Negative control not detected')
input_hashes=[{'file':str(v),'sha256':sha(v)} for v in sources]+[{'file':str(ROOT/'tests/stage28n'/v),'sha256':sha(ROOT/'tests/stage28n'/v)} for v in ('boundary.h','tusb_config.h','tusb_os_custom.h')]
report={'results':rows,'counts':{'PASS':len(rows),'FAIL':0},'assertions':sum(r['assertions'] for r in rows),'sanitizers':{'ASan':'clean','UBSan':'clean','leak_detection':'detect_leaks=1; clean'},'compiler_version':subprocess.check_output([compiler,'--version'],text=True),'gcov_version':subprocess.check_output([gcov,'--version'],text=True),'compiler_sha256':sha(pathlib.Path(compiler)),'gcov_sha256':sha(pathlib.Path(gcov)),'commands':commands,'flags':flags,'compiled_inputs':input_hashes,'manifest_sha256':sha(ROOT/'docs/stage28n-source-manifest.json'),'negative_control':{'exit':nr.returncode,'status':neg['observation_status'],'diagnostic':nr.stderr,'assertions_excluded':True},'blocked':[{'id':'N21','path':'builder-selected DCD runtime','status':'BLOCKED native register/interrupt/FIFO/platform implementation; source/static only'},{'id':'N22','path':'protected Arduino USBHID runtime','status':'BLOCKED actual Arduino/FreeRTOS/ESP-IDF integration missing from this custom-OS host build; source/static only'}],'contract_status':'NOT SATISFIED; passing observation tests are not contract passes','hardware':False,'target_build':False,'vendor_sources_modified':False}
a.results.write_text(json.dumps(report,indent=2).replace(str(ROOT),'<project-root>')+'\n')
print(json.dumps({'counts':report['counts'],'assertions':report['assertions'],'negative_control_exit':nr.returncode,'blocked_paths':2,'contract_status':report['contract_status']}))
