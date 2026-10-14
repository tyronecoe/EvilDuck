#!/usr/bin/env python3
"""Linux-only runner fault audit; local owner smoke needs no Python. Synthetic files only."""
import argparse,hashlib,json,os,re,shlex,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
if a.build_dir.exists() or a.results.exists():raise ValueError('Fresh external outputs required')
a.build_dir.mkdir();gxx=shutil.which('g++')
if not gxx:raise RuntimeError('Mandatory Linux GCC unavailable')
flags=['-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1')
base=[gxx]+flags+[str(ROOT/'language_preview'/f) for f in ['core.cpp','keyboard.cpp','bridge.cpp']]+[str(ROOT/'tests/stage28h/test_host_validation.cpp')]
exe=a.build_dir/'trace-audit';subprocess.run(base+['-o',str(exe)],check=True)
rows=[];checks=0

def check(ok,message):
 global checks
 checks+=1
 if not ok:raise AssertionError(message)

def run(cmd,cwd=None,extra=None):return subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=90,env=dict(env,**(extra or {})))
def group(name,fn):
 global checks
 checks=0
 try:
  details=fn();rows.append(dict(name=name,status='PASS',assertions=checks,details=details));print('PASS',name)
 except Exception as error:rows.append(dict(name=name,status='FAIL',assertions=checks,error=str(error)));print('FAIL',name,str(error))

def fixture():
 r=run([str(exe)]);check(r.returncode==0,r.stdout+r.stderr);m=re.search(r'PASS host-validation traces=3 blocked_cases=4 assertions=(\d+)',r.stdout);check(bool(m),'Missing fixture count')
 global checks
 checks+=int(m[1])
 check(len(re.findall(r'^VECTOR ',r.stdout,re.M))==19,'19 fixed vector lines');check(len(re.findall(r'^PASS trace=',r.stdout,re.M))==3,'3 trace status lines')
 return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode,cpp_assertions=int(m[1]))
group('fixed_trace_vectors_and_blocked_preflight',fixture)

def manifest():
 r=run([str(exe),'--manifest']);check(r.returncode==0,r.stderr);expected=(ROOT/'tests/stage28h/expected-traces.json').read_text();check(r.stdout==expected,'Compiled expectations mismatch JSON');j=json.loads(r.stdout);check([len(x['reports']) for x in j['traces']]==[7,9,3],'Trace counts');check(all(len(v)==16 for x in j['traces'] for v in x['reports']),'8-byte hex snapshots');return dict(stdout=r.stdout,exit=r.returncode)
group('compiled_manifest_byte_identity',manifest)
# Isolate runner in a disposable project with spaces; no Git history, network or Python in shell runner.
with tempfile.TemporaryDirectory(prefix='stage28h runner ') as scratch:
 scratch=Path(scratch);project=scratch/'project with spaces';(project/'tests/stage28h').mkdir(parents=True);shutil.copytree(ROOT/'language_preview',project/'language_preview')
 for name in ['run_host_smoke.sh','test_host_validation.cpp','expected-traces.json']:shutil.copy2(ROOT/'tests/stage28h'/name,project/'tests/stage28h'/name)
 runner=project/'tests/stage28h/run_host_smoke.sh';work=scratch/'temporary work';work.mkdir();sentinel=work/'untouched-user-sentinel';sentinel.write_text('synthetic sentinel');source_hashes={str(f.relative_to(project)):hashlib.sha256(f.read_bytes()).hexdigest() for f in project.rglob('*') if f.is_file()}
 expected=(project/'tests/stage28h/expected-traces.json').read_text().strip()
 def compiler(mode):
  f=scratch/('fake compiler '+mode);output_script='#!/bin/sh\nif [ "${1:-}" = --manifest ]; then printf "%s\\n" '+shlex.quote(expected)+';exit 0;fi\n'
  if mode=='nonzero':output_script+='printf "%s\\n" "synthetic fixture failure";exit 7\n'
  else:output_script+='exit 0\n'
  script='#!/bin/sh\nif [ "${1:-}" = --version ]; then '+('exit 5' if mode=='version' else 'printf "%s\\n" "g++ synthetic sandbox wrapper";exit 0')+';fi\n'
  if mode=='probe':script+='case "$*" in *probe.cpp*) printf "%s\\n" "synthetic C++17 SDK failure";exit 66;;esac\n'
  else:script+='case "$*" in *probe.cpp*) exec '+shlex.quote(gxx)+' '+shlex.join(flags)+' "$@";;esac\n'
  if mode=='interrupt':script+='kill -TERM "$PPID";exit 0\n'
  elif mode=='badbuild':script+='printf "%s\\n" "synthetic fixture compile failure: $PWD/private-fixture $HOME/synthetic-private";exit 42\n'
  elif mode in ['nonzero','empty']:
   script+='out="";prev="";for arg in "$@";do if [ "$prev" = -o ];then out="$arg";fi;prev="$arg";done\nprintf "%s" '+shlex.quote(output_script)+' > "$out";chmod +x "$out";exit 0\n'
  elif mode=='mismatch':script+='exec '+shlex.quote(gxx)+' '+shlex.join(flags)+' -DSTAGE28H_TEST_MISMATCH=1 "$@"\n'
  else:script+='exec '+shlex.quote(gxx)+' '+shlex.join(flags)+' "$@"\n'
  f.write_text(script);f.chmod(0o755);return f
 def invoke(cxx,script=runner):return run(['bash',str(script)],cwd=project,extra={'CXX':str(cxx),'TMPDIR':str(work)})
 def intact():
  check(sentinel.read_text()=='synthetic sentinel','User sentinel changed');check(not list(work.glob('evilduck28h.*')),'Unique temporary directory retained')
 def success():
  r=invoke(compiler('normal'));check(r.returncode==0,r.stdout+r.stderr);check('PASS runner:' in r.stdout,'Missing runner PASS');check('<project-root>' in r.stdout,'Project label missing');check(str(project) not in r.stdout+r.stderr,'Project leaked');check(str(scratch) not in r.stdout+r.stderr,'Private temp path leaked');intact();return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode,duplicate_cpp_run_not_added_to_assertions=True)
 group('runner_quoted_paths_sdk_probe_privacy_and_cleanup',success)
 def relative_tmp():
  outside=scratch/'outside working directory';outside.mkdir();temp_parent=outside/'relative temp work';temp_parent.mkdir();marker=temp_parent/'user-sentinel';marker.write_text('synthetic')
  r=run(['bash',str(runner)],cwd=outside,extra={'CXX':str(compiler('normal')),'TMPDIR':'relative temp work'})
  check(r.returncode==0,r.stdout+r.stderr);check('PASS runner:' in r.stdout,'Missing PASS');check(marker.read_text()=='synthetic','Existing file changed');check(not list(temp_parent.glob('evilduck28h.*')),'Created temporary directory not cleaned');check(str(scratch) not in r.stdout+r.stderr,'Private temporary path leaked');return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode)
 group('relative_tmpdir_outside_project_is_normalized_and_cleaned',relative_tmp)
 def failure(mode,code,label,path=None):
  r=invoke(path if path is not None else compiler(mode));check(r.returncode==code,f'{mode}: wrong exit {r.returncode}\n{r.stdout}\n{r.stderr}');check(label in r.stdout,'Wrong classification');check('PASS runner:' not in r.stdout,'False PASS');check(str(project) not in r.stdout+r.stderr,'Project leaked');check(str(scratch) not in r.stdout+r.stderr,'Temporary path leaked');check((os.environ.get('HOME','')+'/synthetic-private') not in r.stdout+r.stderr,'Home path leaked');intact();return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode,simulated_outcome=label)
 group('missing_compiler_is_skip_not_pass',lambda:failure('missing',77,'SKIP_ENVIRONMENT',scratch/'missing compiler'))
 blocked=scratch/'nonexecutable compiler';blocked.write_text('synthetic');blocked.chmod(0o644)
 group('nonexecutable_compiler_is_skip',lambda:failure('blocked',77,'SKIP_ENVIRONMENT',blocked))
 group('compiler_version_failure_is_skip',lambda:failure('version',77,'SKIP_ENVIRONMENT'))
 group('unusable_cpp17_sdk_is_skip',lambda:failure('probe',77,'SKIP_ENVIRONMENT'))
 group('fixture_build_failure_preserves_exit_42',lambda:failure('badbuild',42,'FAIL fixture compile/link'))
 group('nonzero_fixture_preserves_exit_7',lambda:failure('nonzero',7,'FAIL fixture execution'))
 group('zero_exit_without_receipt_fails',lambda:failure('empty',1,'FAIL fixture receipt missing'))
 group('compiled_expectation_mismatch_fails_manifest_gate',lambda:failure('mismatch',1,'FAIL fixture manifest mismatch'))
 def wrongroot():
  fake=scratch/'wrong root/tests/stage28h';fake.mkdir(parents=True);shutil.copy2(runner,fake/'run_host_smoke.sh');r=invoke(scratch/'nonexistent',fake/'run_host_smoke.sh');check(r.returncode==2,'Wrong project must FAIL2');check('FAIL missing source fixture' in r.stdout,'Wrong root classification');check('SKIP_ENVIRONMENT' not in r.stdout,'Root error mislabeled');intact();return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode)
 group('wrong_project_root_fails_before_compiler',wrongroot)
 def missingfixture():
  f=project/'tests/stage28h/expected-traces.json';contents=f.read_bytes();f.unlink()
  try:r=invoke(compiler('normal'))
  finally:f.write_bytes(contents)
  check(r.returncode==2,'Missing fixture must fail');check('FAIL missing source fixture' in r.stdout,'Wrong classification');check('PASS runner:' not in r.stdout,'False PASS');intact();return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode)
 group('missing_manifest_fails_without_execution',missingfixture)
 def damagedmanifest():
  f=project/'tests/stage28h/expected-traces.json';raw=f.read_bytes();f.write_text('{}\n')
  try:r=invoke(compiler('normal'))
  finally:f.write_bytes(raw)
  check(r.returncode==1,'Damaged expectations must fail');check('FAIL fixture manifest mismatch' in r.stdout,'Missing manifest gate');check('PASS runner:' not in r.stdout,'False PASS');intact();return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode)
 group('altered_manifest_fails_identity_gate',damagedmanifest)
 def interrupted():
  r=invoke(compiler('interrupt'));check(r.returncode==143,'TERM must preserve signal exit143');check('PASS runner:' not in r.stdout,'False PASS on interrupt');intact();return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode)
 group('term_interrupt_cleans_only_created_temp_directory',interrupted)
 def warning():
  f=compiler('normal');raw=f.read_text();raw=raw.replace('exec '+shlex.quote(gxx)+' '+shlex.join(flags)+' "$@"\n','printf "%s\\n" "error: synthetic warning treated as error";exit 43\n');f.write_text(raw);return failure('warning',43,'FAIL fixture compile/link',f)
 group('fixture_warning_failure_not_environment_skip',warning)
 def mismatch():
  bad=a.build_dir/'mismatch-audit';subprocess.run(base+['-DSTAGE28H_TEST_MISMATCH=1','-o',str(bad)],check=True);r=run([str(bad)]);check(r.returncode==1,'Trace mismatch must fail');check('report=0 expected=01 00' in r.stdout,'No mismatched report index/expected bytes');check('actual=00 00' in r.stdout,'No actual bytes');check('PASS host-validation' not in r.stdout,'False fixture PASS');return dict(stdout=r.stdout,stderr=r.stderr,exit=r.returncode)
 group('actual_trace_byte_mismatch_has_report_diagnostic',mismatch)
 def untouched():
  check(all(hashlib.sha256((project/f).read_bytes()).hexdigest()==sha for f,sha in source_hashes.items()),'Source fixture modified');intact();return dict(synthetic_sources_unchanged=True)
 group('sandbox_sources_and_user_sentinel_unchanged',untouched)
report=dict(results=rows,counts={status:sum(r['status']==status for r in rows) for status in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),sanitizers='Linux GCC ASan/UBSan/leak enabled for actual C++ paths',command=base+['-o',str(exe)],compiler_version=run([gxx,'--version']).stdout,hardware_access=False,native_mac='SKIP_ENVIRONMENT',note='Simulated ENV skips / expected failures are runner behavior tests, not supported-language claims; repeat shell fixture runs not counted as extra C++ assertions')
report['paths_redacted']=True
receipt=json.dumps(report,indent=2).replace(str(ROOT),'<project-root>').replace(str(a.build_dir),'<build-dir>').replace(str(scratch),'<sandbox>')
if os.environ.get('HOME'):receipt=receipt.replace(os.environ['HOME'],'<home>')
with a.results.open('x') as f:f.write(receipt+'\n')
raise SystemExit(bool(report['counts']['FAIL']))
