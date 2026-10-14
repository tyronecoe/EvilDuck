#!/usr/bin/env python3
"""Opt-in genuine native C; opt-out historical fixtures; coverage and negative control."""
import argparse,gzip,hashlib,json,os,pathlib,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);p.add_argument('--original-root',type=pathlib.Path,required=True);p.add_argument('--baseline-results',type=pathlib.Path,required=True);a=p.parse_args()
for f in (a.build_dir,a.results):
 if f.exists() or f.resolve().is_relative_to(ROOT):raise ValueError('Fresh external outputs required')
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
m=json.loads((ROOT/'docs/stage28o-input-and-patch-manifest.json').read_text());n=json.loads((ROOT/'docs/stage28n-source-manifest.json').read_text());s=a.source_root.resolve();changed={r['file']:r['output_sha256'] for r in m['patched_files']}
assert sha(ROOT/'tests/stage28o/tinyusb-native.patch')==m['patch_sha256']
for row in n['vendor_inputs']:assert sha(s/row['file'])==changed.get(row['file'],row['sha256']),row['file']
for row in m['patched_files']:assert sha(s/row['file'])==row['output_sha256']
base=json.loads(a.baseline_results.read_text());assert base['counts']=={'PASS':20,'FAIL':0} and base['assertions']==131 and base['vendor_sources_modified'] is False
cc=shutil.which('gcc');gc=shutil.which('gcov');assert cc and gc
a.build_dir.mkdir();env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1');commands=[]
flags=['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','--coverage']
units=[s/'src'/v for v in n['compiled_translation_units']]
def build(name,fixture,defines):
 exe=a.build_dir/name;source=units+[ROOT/'tests'/fixture/'boundary.c',ROOT/'tests'/fixture/'test_components.c']
 cmd=[cc]+flags+defines+['-I',str(ROOT/'tests'/fixture),'-I',str(s/'src')]+list(map(str,source))+['-o',str(exe)];commands.append(cmd);subprocess.run(cmd,env=env,check=True,timeout=180);return exe
exe=build('prototype','stage28o',['-DCFG_TUD_TAGGED_NATIVE=1','-DTAG_ID_MAX=8'])
maximum=build('maximum-ids','stage28o',['-DCFG_TUD_TAGGED_NATIVE=1','-DTAG_TEST_ID_START=(UINT64_MAX-1)'])
optout=build('optout','stage28n',['-DCFG_TUD_TAGGED_NATIVE=0'])
def execute(exe,arg,label):
 directory=a.build_dir/label;directory.mkdir();e=dict(env,GCOV_PREFIX=str(directory),GCOV_PREFIX_STRIP=str(len(a.build_dir.resolve().parts)-1))
 cmd=[str(exe),arg];commands.append(cmd);r=subprocess.run(cmd,env=e,capture_output=True,text=True,timeout=30)
 if r.returncode or r.stderr:raise AssertionError(label+' failed: '+r.stderr)
 row=json.loads(r.stdout);functions=[]
 for note in a.build_dir.glob(exe.name+'-*.gcno'):
  shutil.copyfile(note,directory/note.name);c=[gc,'-j','-f',str(directory/note.name)];commands.append(c);cov=subprocess.run(c,cwd=directory,capture_output=True,text=True,timeout=30);assert cov.returncode==0,cov.stderr
 for f in directory.glob('*.gcov.json.gz'):
  report=json.loads(gzip.decompress(f.read_bytes()))
  for file in report['files']:
   path=pathlib.Path(file['file'])
   if path.is_relative_to(s):functions.extend(dict(file=str(path.relative_to(s)),name=v['name'],count=v['execution_count'],start_line=v['start_line'],end_line=v['end_line']) for v in file['functions'] if v['execution_count']>0)
 row.update(exit=r.returncode,stderr=r.stderr,executed_vendor_functions=functions)
 return row
rows=[]
for i in range(1,47):
 row=execute(maximum if i==41 else exe,str(i),'O%02d'%i);assert row['id']=='O%02d'%i and row['status']=='PASS'
 names={v['name'] for v in row['executed_vendor_functions']};assert {'dcd_event_handler','tud_task_ext','usbd_tagged_bind'}.issubset(names)
 if i!=29:assert 'usbd_tagged_try' in names
 if row['tagged_callbacks']:assert {'hidd_xfer_cb','usbd_tagged_observe'}.issubset(names)
 assert row['tagged_callbacks']==len(row['tagged_receipts'])
 if i==6:assert row['tagged_receipts'][0]['at']<row['records'][0]['returned_at']
 assert row['controller_records']==len(row['records']);assert len({(r['c'],r['q']) for r in row['records']})==len(row['records'])
 for r in row['records']:assert len(r['frame'])==r['length']*2 and r['length']==8+(r['id']!=0)
 # Fixture enumeration uses ordinary legacy claim before lease. It never waits in tested try path.
 assert row['mutex_wait_forever']==(2 if i==34 else 0), 'unexpected hidden wait'
 row['legacy_prelease_wait_forever_calls']=2 if i==34 else 0
 rows.append(row);print('PASS',row['id'],'assertions',row['assertions'])
legacy=[]
for i in range(1,21):
 row=execute(optout,'N%02d'%i,'optout-N%02d'%i);old=base['results'][i-1]
 # Compare complete functional observations, not just PASS/count. Ignore coverage and path receipts.
 for key,value in old.items():
  if key not in ('exit','stderr','executed_vendor_functions','coverage_commands','physical_behavior','boundary'):assert row[key]==value,(row['id'],key)
 legacy.append(row)
old_units=[a.original_root/'src'/v for v in n['compiled_translation_units']]
for row in n['vendor_inputs']:assert sha(a.original_root/row['file'])==row['sha256']
oldexe=a.build_dir/'old-contract';cmd=[cc]+flags+['-I',str(ROOT/'tests/stage28n'),'-I',str(a.original_root/'src')]+list(map(str,old_units))+[str(ROOT/'tests/stage28n/boundary.c'),str(ROOT/'tests/stage28o/old_contract_reproducer.c'),'-o',str(oldexe)]
commands.append(cmd);subprocess.run(cmd,env=env,check=True,timeout=180)
violations=[]
for case,expected in [('stale','usbd_edpt_busy(0,0x81)'),('refusal','tud_hid_n_report(0,1,a,8)')]:
 cmd=[str(oldexe),case];commands.append(cmd);oldrun=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=30)
 assert oldrun.returncode==1 and oldrun.stderr.strip()=='EXPECTED OLD CONTRACT VIOLATION: '+expected
 violations.append({'scenario':case,'exit':oldrun.returncode,'diagnostic':oldrun.stderr,'classification':'expected original contract violation; excluded from PASS/assertions'})
negative=build('negative','stage28o',['-DCFG_TUD_TAGGED_NATIVE=1','-DTAG_ID_MAX=8','-DSTAGE28O_NEGATIVE_CONTROL=1'])
cmd=[str(negative),'1'];commands.append(cmd);bad=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=30)
assert bad.returncode==1 and 'CHECK' not in bad.stderr and 'FAIL line=' in bad.stderr,bad.stderr
inputs=[dict(file=str(v).replace(str(ROOT),'<project-root>'),sha256=sha(v)) for v in units]
inputs.extend(dict(file=str(v).replace(str(ROOT),'<project-root>'),sha256=sha(v)) for v in sorted((ROOT/'tests/stage28o').glob('*')) if v.is_file())
report={'primary':{'counts':{'PASS':len(rows),'FAIL':0},'assertions':sum(v['assertions'] for v in rows),'results':rows},'expected_old_contract_violations':violations,'unchanged_baseline':base,'opt_in_disabled':{'counts':{'PASS':20,'FAIL':0},'assertions':sum(v['assertions'] for v in legacy),'observations_match_baseline':True,'results':legacy},'negative_control':{'exit':bad.returncode,'stderr':bad.stderr,'excluded_from_counts':True},'flags':flags,'commands':commands,'compiler':subprocess.check_output([cc,'--version'],text=True),'compiler_sha256':sha(pathlib.Path(cc)),'gcov':subprocess.check_output([gc,'--version'],text=True),'inputs':inputs,'patch_manifest_sha256':sha(ROOT/'docs/stage28o-input-and-patch-manifest.json'),'sanitizers':{'ASan':'clean','UBSan':'clean','leak_detection':'detect_leaks=1; clean'},'boundary':'native fake controller/OS only; vendor submission/dispatch/HID executes; no target build/hardware/core integration'}
a.results.write_text(json.dumps(report,indent=2).replace(str(ROOT),'<project-root>')+'\n');print(json.dumps({'primary':report['primary']['counts'],'assertions':report['primary']['assertions'],'optout_assertions':report['opt_in_disabled']['assertions'],'negative_exit':bad.returncode}))
