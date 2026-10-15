#!/usr/bin/env python3
"""Native proposed semantic model only; no USB/driver/firmware operation."""
import argparse,gzip,hashlib,json,os,pathlib,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args()
for x in (a.build_dir,a.results):assert not x.exists() and not x.resolve().is_relative_to(ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cc=shutil.which('g++');gc=shutil.which('gcov');assert cc and gc
a.build_dir.mkdir();commands=[];flags=['-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','--coverage'];env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1')
def build(name,negative=False,reproducer=False):
 sources=[ROOT/'tests/stage28q/model.cpp',ROOT/'tests/stage28q'/('receipt_reproducer.cpp' if reproducer else 'test_model.cpp')]
 cmd=[cc]+flags+(['-DSTAGE28Q_NEGATIVE_CONTROL=1'] if negative else [])+list(map(str,sources))+['-o',str(a.build_dir/name)];commands.append(cmd);subprocess.run(cmd,check=True,env=env,timeout=180);return a.build_dir/name
exe=build('model');rows=[]
for i in range(1,38):
 d=a.build_dir/('Q%02d'%i);d.mkdir();e=dict(env,GCOV_PREFIX=str(d),GCOV_PREFIX_STRIP=str(len(a.build_dir.resolve().parts)-1));cmd=[str(exe),str(i)];commands.append(cmd);r=subprocess.run(cmd,env=e,capture_output=True,text=True,timeout=3)
 assert r.returncode==0 and not r.stderr,(i,r.stderr);row=json.loads(r.stdout);assert row['id']=='Q%02d'%i and row['PASS'] and not row['physical_certificate'];functions=[]
 for note in a.build_dir.glob('model-*.gcno'):
  shutil.copyfile(note,d/note.name);cmd=[gc,'-j','-f',str(d/note.name)];commands.append(cmd);cov=subprocess.run(cmd,cwd=d,capture_output=True,text=True,timeout=30);assert cov.returncode==0,cov.stderr
 for f in d.glob('*.gcov.json.gz'):
  for file in json.loads(gzip.decompress(f.read_bytes()))['files']:
   path=pathlib.Path(file['file'])
   if path==ROOT/'tests/stage28q/model.cpp':functions.extend(dict(name=v['demangled_name'],count=v['execution_count'],start_line=v['start_line'],end_line=v['end_line']) for v in file['functions'] if v['execution_count']>0)
 if i not in [4,34]:assert any('Sequencer::step' in v['name'] for v in functions)
 row.update(exit=r.returncode,stderr=r.stderr,executed_proposed_model_functions=functions,vendor_execution=False)
 rows.append(row);print('PASS model',row['id'],row['assertions'])
neg=build('negative',True);cmd=[str(neg),'1'];commands.append(cmd);n=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=3);assert n.returncode==1 and 'FAIL line=' in n.stderr
rep=build('receipt-reproducer',reproducer=True);cmd=[str(rep)];commands.append(cmd);r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=3);assert r.returncode==0 and r.stdout.startswith('PASS:') and not r.stderr
report={'primary':{'counts':{'PASS':len(rows),'FAIL':0},'assertions':sum(v['assertions'] for v in rows),'results':rows},'negative_control':{'exit':n.returncode,'stderr':n.stderr,'excluded_from_counts':True},'fixed_development_reproducer':{'exit':r.returncode,'stdout':r.stdout,'excluded_from_primary':True},'flags':flags,'commands':commands,'compiler':subprocess.check_output([cc,'--version'],text=True),'compiler_sha256':sha(pathlib.Path(cc)),'gcov':subprocess.check_output([gc,'--version'],text=True),'fixtures':[dict(file=str(f.relative_to(ROOT)),sha256=sha(f)) for f in sorted((ROOT/'tests/stage28q').glob('*')) if f.is_file()],'manifest_sha256':sha(ROOT/'docs/stage28q-source-and-model-manifest.json'),'sanitizers':{'ASan':'clean','UBSan':'clean','leak_detection':'detect_leaks=1 clean completed cases'},'vendor_execution':'NONE in new Q sequencer/model; P real driver rerun separately','physical':'NOT TESTED','production_profile':'UNRESOLVED; missing premises refuse without register writes'}
a.results.write_text(json.dumps(report,indent=2).replace(str(ROOT),'<project-root>')+'\n');print(json.dumps({'counts':report['primary']['counts'],'assertions':report['primary']['assertions'],'negative_exit':n.returncode,'reproducer_exit':r.returncode}))
