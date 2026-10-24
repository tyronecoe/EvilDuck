# Adapted for this release from unchanged tests/caps_stop/test_bound_installer.py.
# Original SHA-256: a0cc1ab3a5b94ed1b2d4f218ae380d5b83e2f78187202f983e15730a912f5bb2
"""Real extracted release validator + bound engine; only injected USB/tool data.
No esptool dispatcher, serial endpoint or hardware operation is executed.
"""
import argparse,ast,hashlib,importlib.util,json,pathlib,re,shutil,subprocess,sys,tempfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--ota-template',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists();cases=[]
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
installer=load(a.directory/'installer.py','bound_release');preflight=load(a.directory/'preflight.py','release_preflight')
# Reuse only the hash-pinned historical fake class, never its CLI or dispatcher.
oldbytes=(ROOT/'tests/mac_install/test_installer.py').read_bytes();assert hashlib.sha256(oldbytes).hexdigest()=='6299b965ddfaebea7f3317086980c94b10fcc9152fb78c2d1752e80ec959c10f';old=ast.parse(oldbytes);node=next(n for n in old.body if isinstance(n,ast.ClassDef) and n.name=='Fake');ns=dict(installer=installer,pathlib=pathlib,hashlib=hashlib);exec(compile(ast.Module(body=[node],type_ignores=[]),'historical-mock-class-only','exec'),ns);Fake=ns['Fake']
def need(v):assert v
def case(name,fn):
 try:fn();cases.append(dict(name=name,status='PASS'))
 except Exception as e:cases.append(dict(name=name,status='FAIL',diagnostic=type(e).__name__+': '+str(e)))
with tempfile.TemporaryDirectory(prefix='actual-public-release-mocks-') as tmp:
 t=pathlib.Path(tmp)
 def run(kind='healthy',action='check',choice=None):
  d=pathlib.Path(tempfile.mkdtemp(dir=t))/ 'package with spaces';shutil.copytree(a.directory,d);parent=d.parent/'private evidence';parent.mkdir();(parent/'existing-backup.bin').write_bytes(b'UNCHANGED')
  f=Fake(d,kind);f.table=(d/'expected-partitions.bin').read_bytes()+b'\xff'*1024;f.ota=a.ota_template.read_bytes()
  if kind=='wrong_layout':f.table=b'\xff'*4096
  if kind=='wrong_ota':f.ota=b'\xff'*8192
  if kind=='bad_package':(d/'application.bin').write_bytes(b'bad')
  def confirm(_):
   if kind=='changed_image':(d/'application.bin').write_bytes(b'changed')
   if kind=='interrupt':raise KeyboardInterrupt()
   return choice if choice is not None else ('ROLLBACK' if action=='rollback' else 'INSTALL')
  try:result=installer.session(d,'/dev/cu.SYNTHETIC-NOT-A-DEVICE',action,f.run,preflight.validate,confirm,parent,port_check=lambda _:None,emit=lambda _:None)
  except (installer.Stopped,preflight.Rejected,OSError,KeyboardInterrupt) as e:result=e
  need((parent/'existing-backup.bin').read_bytes()==b'UNCHANGED')
  return f,result
 case('release_binding_matches_exact_preflight',lambda:need(installer.RELEASE_BINDING==dict(preflight_sha256=hashlib.sha256((a.directory/'preflight.py').read_bytes()).hexdigest())))
 def check():
  f,r=run();need(r['result']=='READ_ONLY_CHECK_PASS' and r['writes']==0 and not f.writes());need(not any('0x1000000' in c for c in f.calls));need(len([c for c in f.calls if 'read_flash' in c])==2)
 case('actual_release_default_check_no_write_no_full_backup',check)
 for action in ['install','rollback']:
  def accepted(action=action):
   f,r=run(action=action);need(r['result']=='BOTH_APPLICATION_COMPARISONS_PASS' and not r['automatic_reboot']);need(len(f.writes())==1);v=[c for c in f.calls if 'verify_flash' in c];need([c[-2] for c in v]==['0x10000','0x750000']);name='rollback-application.bin' if action=='rollback' else 'application.bin';need(all(c[-1].endswith(name) for c in v));need(all('hard_reset' not in c and 'erase_flash' not in c and 'erase_region' not in c for c in f.calls));need(len([c for c in f.calls if 'read_flash' in c])==5)
  case('actual_release_'+action+'_fresh_gates_and_two_compares',accepted)
 for kind in ['bad_package','wrong_tool','wrong_chip','small_flash','secure_boot','encrypted','crypt_count','missing_security','duplicate_security','wrong_layout','wrong_ota','short_table','missing_readback','backup_failure','short_backup','wrong_backup','changed_chip','changed_metadata','changed_image','interrupt']:
  def denied(kind=kind):
   f,r=run(kind,action='install');need(isinstance(r,BaseException) and not f.writes())
   if kind=='bad_package':need(not f.calls)
  case('real_validator_denies_'+kind,denied)
 def cancelled():
  f,r=run(action='install',choice='NO');need(isinstance(r,installer.Stopped) and str(r)=='OWNER_CANCELLED' and not f.writes())
 case('deliberate_cancellation_before_write',cancelled)
 for kind,n in [('write_failure',0),('verify_failure',1),('second_verify_failure',2)]:
  def fail(kind=kind,n=n):
   f,r=run(kind,action='install');need(isinstance(r,installer.Stopped) and 'Stay in ROM' in str(r));need(len(f.writes())==1 and len([c for c in f.calls if 'verify_flash' in c])==n);need(all('hard_reset' not in c for c in f.calls))
  case('real_release_'+kind+'_no_retry_or_reboot',fail)
 def binding_reject():
  d=t/'changed-helper';shutil.copytree(a.directory,d);(d/'preflight.py').write_text('raise RuntimeError("MUST NOT IMPORT")\n');r=subprocess.run([sys.executable,str(d/'installer.py')],capture_output=True,text=True);need(r.returncode==1 and 'RELEASE_PREFLIGHT_IDENTITY' in r.stdout and 'MUST NOT IMPORT' not in r.stderr)
 case('changed_helper_rejected_before_import_or_device_access',binding_reject)
 def no_port():
  r=subprocess.run(['bash',str(a.directory/'install-macos.sh')],capture_output=True,text=True);need(r.returncode==1 and 'INVALID_PORT_NAME' in r.stdout)
 case('bound_default_launcher_requires_explicit_fresh_port',no_port)
 def rollback_override():
  r=subprocess.run(['bash',str(a.directory/'rollback-macos.sh'),'--action','install'],capture_output=True,text=True);need(r.returncode==2 and 'cannot be overridden' in r.stderr)
 case('bound_rollback_cannot_be_overridden',rollback_override)
 for name in ['preflight.py','installer.py','gen_esp32part.py']:case('bound_python38_'+name,lambda name=name:ast.parse((a.directory/name).read_text(),feature_version=(3,8)))
 for name in ['install-macos.sh','rollback-macos.sh']:case('bound_shell_'+name,lambda name=name:subprocess.run(['bash','-n',str(a.directory/name)],check=True))
def progress_check():
 import contextlib,io
 from unittest.mock import patch
 output=io.StringIO();command=[sys.executable,'-m','esptool','version']
 with patch.object(installer.subprocess,'run',return_value=subprocess.CompletedProcess(command,0,'4.12.0','')) as mocked,contextlib.redirect_stdout(output):
  need('4.12.0' in installer.tool_process(command));need(mocked.call_count==1)
 need('Step 1: version' in output.getvalue() and 'version PASS' in output.getvalue())
case('numbered_tool_progress_success_without_device_dispatch',progress_check)
def progress_failure():
 import contextlib,io
 from unittest.mock import patch
 output=io.StringIO();command=[sys.executable,'-m','esptool','version']
 with patch.object(installer.subprocess,'run',return_value=subprocess.CompletedProcess(command,2,'','SIMULATED FAILURE')),contextlib.redirect_stdout(output):
  try:installer.tool_process(command)
  except installer.Stopped as e:need('ESPTOOL_EXIT_2' in str(e))
  else:raise AssertionError('tool failure hidden')
 need('version FAIL' in output.getvalue())
case('numbered_tool_progress_failure_not_hidden',progress_failure)
out=dict(counts={x:sum(r['status']==x for r in cases) for x in ['PASS','FAIL']},results=cases,scope='Actual public ELF-derived images, exact release preflight and bound installer with injected esptool responses. All device contents synthetic.',hardware=False,native_macos_tested=False);a.results.write_text(json.dumps(out,indent=2)+'\n');print(out['counts']);
for r in cases:
 if r['status']=='FAIL':print(r)
raise SystemExit(bool(out['counts']['FAIL']))
