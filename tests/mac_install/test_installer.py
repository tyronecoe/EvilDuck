"""Temporary-fixture installer-engine tests. Every esptool response is mocked.
The synthetic application fixture is NOT an ESP image or a deployment artifact.
"""
import argparse,ast,hashlib,json,pathlib,re,shutil,subprocess,sys,tempfile
sys.dont_write_bytecode=True
import installer
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists();cases=[]
class Fake:
 def __init__(self,root,kind='healthy'):self.root=root;self.kind=kind;self.calls=[];self.flash_reads=0;self.table=b'T'*4096;self.ota=b'O'*8192;self.identifications=0
 def run(self,args):
  self.calls.append(args)
  if args[-1]=='version':return '4.12.0\n' if self.kind!='wrong_tool' else '5.0.0\n'
  if args[-1]=='flash_id':
   self.identifications+=1;mac='11:22:33:44:55:66' if not(self.kind=='changed_chip' and self.identifications>1) else '22:22:33:44:55:66'
   return 'Chip is '+('ESP32' if self.kind=='wrong_chip' else 'ESP32-S3')+'\nMAC: '+mac+'\nDetected flash size: '+('4MB' if self.kind=='small_flash' else '16MB')+'\n'
  if args[-1]=='get_security_info':
   out='Chip ID: 9\nSecure Boot: Disabled\nFlash Encryption: Disabled\nSPI Boot Crypt Count (SPI_BOOT_CRYPT_CNT): 0x0\n'
   if self.kind=='secure_boot':out=out.replace('Secure Boot: Disabled','Secure Boot: Enabled')
   if self.kind=='encrypted':out=out.replace('Flash Encryption: Disabled','Flash Encryption: Enabled')
   if self.kind=='crypt_count':out=out.replace('0x0','0x2')
   if self.kind=='missing_security':out='Unknown\n'
   if self.kind=='duplicate_security':out+='Secure Boot: Disabled\n'
   return out
  if 'read_flash' in args:
   i=args.index('read_flash');address,size=int(args[i+1],0),int(args[i+2],0);dest=pathlib.Path(args[i+3]);assert not dest.exists()
   if address==0x8000:
    data=self.table
    if self.kind=='changed_metadata' and dest.name.startswith('fresh'):data=b'X'*4096
    if self.kind=='short_table':data=data[:-1]
   elif address==0xe000:data=self.ota
   else:
    assert address==0 and size==0x1000000
    if self.kind=='backup_failure':raise installer.Stopped('MOCK_READ_FAILURE')
    data=bytearray(b'\xff'*size);data[0x8000:0x9000]=self.table;data[0xe000:0x10000]=self.ota
    if self.kind=='short_backup':data=data[:-1]
    if self.kind=='wrong_backup':data[0x8000]^=1
   if self.kind=='missing_readback':return 'Read complete but fixture intentionally missing'
   dest.write_bytes(data);return 'Read complete'
  if 'write_flash' in args:
   if self.kind=='write_failure':raise installer.Stopped('MOCK_WRITE_FAILURE')
   return 'Mock write returned'
  if 'verify_flash' in args:
   if self.kind=='verify_failure':raise installer.Stopped('MOCK_VERIFY_FAILURE')
   if self.kind=='second_verify_failure' and args[-2]=='0x750000':raise installer.Stopped('MOCK_SECOND_VERIFY_FAILURE')
   return 'Mock compare passed'
  raise AssertionError('unexpected operation')
 def validate(self,d,table,ota,required,selected):
  if self.kind=='bad_package':raise installer.Stopped('MOCK_PACKAGE_HASH')
  if required:
   assert table and ota
   if self.kind in ['wrong_layout','wrong_ota']:raise installer.Stopped('MOCK_LAYOUT_OR_OTA')
  file='application.bin' if selected=='application' else 'rollback-application.bin';b=(d/file).read_bytes();sha=hashlib.sha256(b).hexdigest();rows=[dict(file=file,offset=o,bytes=len(b),sha256=sha,erase_start=o,erase_end_exclusive=o+((len(b)+4095)//4096)*4096) for o in [0x10000,0x750000]]
  if self.kind=='unsafe_range':rows[0]['offset']=0x9000
  if self.kind=='one_slot':rows.pop()
  return dict(plan_ready=required,selected_write_ranges=rows)
 def writes(self):return [x for x in self.calls if 'write_flash' in x]
def case(name,fn):
 try:fn();cases.append(dict(name=name,status='PASS'))
 except Exception as e:cases.append(dict(name=name,status='FAIL',diagnostic=type(e).__name__+': '+str(e)))
with tempfile.TemporaryDirectory(prefix='mac-installer-mocks-') as tmp:
 t=pathlib.Path(tmp);pkg=t/'package with spaces';pkg.mkdir();(pkg/'application.bin').write_bytes(b'UNVALIDATED-SYNTHETIC-APP'*4);shutil.copyfile(ROOT/'downloads/evilduck-stop-led-review.bin',pkg/'rollback-application.bin');parent=t/'private evidence';parent.mkdir();(parent/'existing-backup.bin').write_bytes(b'KEEP')
 def run(kind='healthy',action='check',choice='INSTALL',port='/dev/cu.SYNTHETIC'):
  (pkg/'application.bin').write_bytes(b'UNVALIDATED-SYNTHETIC-APP'*4)
  f=Fake(pkg,kind)
  def confirm(prompt):
   if kind=='changed_image':(pkg/'application.bin').write_bytes(b'CHANGED'*20)
   return choice
  try:r=installer.session(pkg,port,action,f.run,f.validate,confirm,parent,port_check=lambda x:installer.require(bool(re.fullmatch(r'/dev/cu\.[A-Za-z0-9_.-]+',x)),'INVALID_PORT_NAME'),emit=lambda _:None);return f,r
  except (installer.Stopped,OSError,KeyError) as e:return f,e
 def need(v):assert v
 def rejection(kind,action='install',choice='INSTALL',port='/dev/cu.SYNTHETIC'):
  f,r=run(kind,action,choice,port);need(isinstance(r,Exception));expected={'bad_package':'MOCK_PACKAGE_HASH','wrong_tool':'ESPTOOL_VERSION','wrong_chip':'WRONG_OR_UNCONFIRMED_CHIP','small_flash':'FLASH_SIZE','secure_boot':'SECURITY_STATE','encrypted':'SECURITY_STATE','crypt_count':'CRYPT_COUNT','missing_security':'SECURITY_STATE','duplicate_security':'SECURITY_STATE','short_table':'READBACK_MISSING_OR_SHORT','missing_readback':'READBACK_MISSING_OR_SHORT','wrong_layout':'MOCK_LAYOUT_OR_OTA','wrong_ota':'MOCK_LAYOUT_OR_OTA','unsafe_range':'UNSAFE_PLAN_RANGE','one_slot':'TWO_SLOTS_REQUIRED','backup_failure':'MOCK_READ_FAILURE','short_backup':'READBACK_MISSING_OR_SHORT','wrong_backup':'BACKUP_METADATA_MISMATCH','changed_chip':'CHIP_CHANGED','changed_metadata':'METADATA_CHANGED','changed_image':'PLAN_CHANGED'}.get(kind)
  if port!='/dev/cu.SYNTHETIC':expected='INVALID_PORT_NAME'
  if choice=='NO':expected='OWNER_CANCELLED'
  need(str(r)==expected);need(not f.writes());
  if kind=='bad_package' or port!='/dev/cu.SYNTHETIC':need(f.calls==[])
  need((parent/'existing-backup.bin').read_bytes()==b'KEEP')
 case('default_check_only_reads_no_flash_mutation',lambda:need(run()[1]['writes']==0 and not run()[0].writes()))
 for kind in ['bad_package','wrong_tool','wrong_chip','small_flash','secure_boot','encrypted','crypt_count','missing_security','duplicate_security','short_table','missing_readback','wrong_layout','wrong_ota','unsafe_range','one_slot','backup_failure','short_backup','wrong_backup','changed_chip','changed_metadata','changed_image']:
  case(kind,lambda kind=kind:rejection(kind))
 case('invalid_port_injection',lambda:rejection(port='/dev/cu.x;touchBAD',kind='healthy'))
 case('cancel_before_write',lambda:rejection('healthy',choice='NO'))
 def valid_install():
  f,r=run(action='install');need(isinstance(r,dict));need(len(f.writes())==1);verifies=[x for x in f.calls if 'verify_flash' in x];need(len(verifies)==2 and {x[-2] for x in verifies}=={'0x10000','0x750000'});need(not r['automatic_reboot']);need(all('--after' not in x or x[x.index('--after')+1]=='no_reset' for x in f.calls))
 case('explicit_install_and_two_independent_compares',valid_install)
 def rollback():
  f,r=run(action='rollback',choice='ROLLBACK');need(isinstance(r,dict) and len(f.writes())==1 and f.writes()[0][-1].endswith('rollback-application.bin'))
 case('rollback_is_current_c20_not_old_shortcuts',rollback)
 def wrong_rollback():
  path=pkg/'rollback-application.bin';old=path.read_bytes();path.write_bytes(old[:-1]+bytes([old[-1]^1]))
  try:
   f,r=run(action='rollback',choice='ROLLBACK');need(isinstance(r,installer.Stopped) and str(r)=='ROLLBACK_IDENTITY' and not f.writes())
  finally:path.write_bytes(old)
 case('wrong_rollback_bytes_fail_before_write',wrong_rollback)
 def missing_image():
  (pkg/'application.bin').unlink();f=Fake(pkg)
  try:installer.session(pkg,'/dev/cu.SYNTHETIC','install',f.run,f.validate,lambda _: 'INSTALL',parent,port_check=lambda _:None,emit=lambda _:None)
  except FileNotFoundError:need(f.calls==[]);return
  raise AssertionError('missing image accepted')
 case('missing_image_prevents_even_tool_invocation',missing_image)

 def failed_operation(kind):
  f,r=run(kind,action='install');need(isinstance(r,Exception) and len(f.writes())==1);need('Stay in ROM' in str(r) and 'MOCK_' in str(r));need(len([x for x in f.calls if 'verify_flash' in x])=={'write_failure':0,'verify_failure':1,'second_verify_failure':2}[kind]);need(not any('hard_reset' in x or 'erase_flash' in x or 'erase_region' in x or '--erase-all' in x for x in f.calls))
 for kind in ['write_failure','verify_failure','second_verify_failure']:case(kind,lambda kind=kind:failed_operation(kind))
 for action in ['check','install','rollback']:
  def unbound(action=action):
   r=subprocess.run([sys.executable,str(ROOT/'tests/mac_install/installer.py'),'--action',action],capture_output=True,text=True);need(r.returncode==2 and 'RELEASE_NOT_BOUND' in r.stdout)
  case('unbound_cli_'+action+'_cannot_access_device',unbound)
 def rollback_override():
  r=subprocess.run(['bash',str(ROOT/'tests/mac_install/rollback-macos.sh'),'--action','install'],capture_output=True,text=True);need(r.returncode==2 and 'cannot be overridden' in r.stderr)
 case('rollback_launcher_rejects_action_override',rollback_override)
 def space_launchers():
  d=t/'launchers with spaces';d.mkdir()
  for name in ['installer.py','install-macos.sh','rollback-macos.sh']:
   shutil.copyfile(ROOT/'tests/mac_install'/name,d/name);(d/name).chmod(0o644)
  for name in ['install-macos.sh','rollback-macos.sh']:
   r=subprocess.run(['bash',str(d/name)],capture_output=True,text=True);need(r.returncode==2 and 'RELEASE_NOT_BOUND' in r.stdout)
 case('bash_launchers_work_in_spaced_path_without_execute_bits',space_launchers)
 for path in (ROOT/'tests/mac_install').glob('*.py'):case('python38_'+path.name,lambda path=path:ast.parse(path.read_text(),feature_version=(3,8)))
 case('launcher_bash_syntax',lambda:[subprocess.run(['bash','-n',str(ROOT/'tests/mac_install'/name)],check=True) for name in ['install-macos.sh','rollback-macos.sh']])
out=dict(counts={x:sum(r['status']==x for r in cases) for x in ['PASS','FAIL']},results=cases,scope='Injected esptool/package-check mocks, public rollback fixture and synthetic non-firmware application; no real device or hardware command executed',release_binding=None,native_high_sierra='NOT TESTED',hardware=False)
a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['counts']));
for r in cases:
 if r['status']=='FAIL':print(r)
raise SystemExit(bool(out['counts']['FAIL']))
