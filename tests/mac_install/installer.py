#!/usr/bin/env python3
"""PREPARATION ONLY: no approved release binding. CLI fails before device access.
The session engine is unit tested with injected memory-only esptool responses.
A reviewed build/package must bind this in a later review before installation.
"""
import argparse,hashlib,importlib.util,json,pathlib,re,subprocess,sys,tempfile
sys.dont_write_bytecode=True
RELEASE_BINDING=None
ROLLBACK_SHA='c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4'
ROLLBACK_BYTES=1376576
class Stopped(ValueError):pass
def require(ok,code):
 if not ok:raise Stopped(code)
def safe_port(port):
 require(isinstance(port,str) and bool(re.fullmatch(r'/dev/cu\.[A-Za-z0-9_.-]+',port)),'INVALID_PORT_NAME')
 p=pathlib.Path(port);require(p.exists() and p.is_char_device(),'PORT_NOT_PRESENT_OR_NOT_CHARACTER_DEVICE')
def identity(flash,security):
 require(len(re.findall(r'^Chip is ESP32-S3(?:[ (].*)?$',flash,re.M))==1,'WRONG_OR_UNCONFIRMED_CHIP')
 require(re.findall(r'Detected flash size:\s*(\S+)',flash)==['16MB'],'FLASH_SIZE')
 mac=re.findall(r'^MAC:\s*((?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})\s*$',flash,re.M);require(len(mac)==1,'CHIP_IDENTITY_MISSING_OR_AMBIGUOUS')
 for name in ['Secure Boot','Flash Encryption']:
  require(re.findall(r'^'+name+r':\s*(\S+)\s*$',security,re.M)==['Disabled'],'SECURITY_STATE')
 require(re.findall(r'SPI Boot Crypt Count \(SPI_BOOT_CRYPT_CNT\):\s*(\S+)',security)==['0x0'],'CRYPT_COUNT')
 chip=re.findall(r'^Chip ID:\s*(\S+)\s*$',security,re.M);require(chip==['9'],'SECURITY_CHIP_ID')
 return mac[0].lower()

def session(directory,port,action,run,validate,confirm,evidence_parent,port_check=safe_port,emit=print):
 """No auto retry/reset; every command is an argument list, never shell input.
 `validate` must be the final release's independently pinned package/layout checker.
 Default CLI cannot reach this engine without a reviewed release binding.
 """
 require(action in ['check','install','rollback'],'UNKNOWN_ACTION');port_check(port)
 root=pathlib.Path(directory).resolve();validate(root,None,None,False,'application' if action!='rollback' else 'rollback')
 version=run([sys.executable,'-m','esptool','version']);require(re.findall(r'^(4\.12\.0)[ \t]*$',version,re.M)==['4.12.0'],'ESPTOOL_VERSION')
 prefix=[sys.executable,'-m','esptool','--chip','esp32s3','--port',port,'--baud','115200','--before','no_reset','--after','no_reset','--no-stub']
 def call(*args):return run(prefix+list(args))
 def identify():return identity(call('flash_id'),call('get_security_info'))
 first=identify();parent=pathlib.Path(evidence_parent).resolve();require(parent!=root and root not in parent.parents,'EVIDENCE_INSIDE_PACKAGE');require(parent.is_dir(),'EVIDENCE_PARENT_MISSING')
 evidence=pathlib.Path(tempfile.mkdtemp(prefix='evilduck-before-caps-',dir=str(parent)))
 def read(address,size,name):
  dest=evidence/name;require(not dest.exists(),'EVIDENCE_FILE_EXISTS');call('read_flash',hex(address),hex(size),str(dest));require(dest.is_file() and not dest.is_symlink() and dest.stat().st_size==size,'READBACK_MISSING_OR_SHORT');return dest
 table=read(0x8000,4096,'partitions.bin');ota=read(0xe000,8192,'otadata.bin');selected='rollback' if action=='rollback' else 'application'
 plan=validate(root,table,ota,True,selected);require(plan.get('plan_ready') is True,'PLAN_NOT_READY');rows=plan['selected_write_ranges'];require(len(rows)==2,'TWO_SLOTS_REQUIRED')
 # Independently limit the installer's own command plan; never trust arbitrary offsets/files.
 file='rollback-application.bin' if action=='rollback' else 'application.bin';data=(root/file).read_bytes();digest=hashlib.sha256(data).hexdigest()
 require(len(data)>24 and len(data)<=0x740000,'IMAGE_SIZE')
 if selected=='rollback':require(len(data)==ROLLBACK_BYTES and digest==ROLLBACK_SHA,'ROLLBACK_IDENTITY')
 for row,offset in zip(rows,[0x10000,0x750000]):
  end=offset+((len(data)+4095)//4096)*4096
  require(row['offset']==offset and row['file']==file and row['bytes']==len(data) and row['sha256']==digest and row['erase_start']==offset and row['erase_end_exclusive']==end and end<=offset+0x740000,'UNSAFE_PLAN_RANGE')
 emit(json.dumps(dict(action=action,chip_identity=first,plan=rows,evidence=str(evidence),physical_installation_authorized=False),indent=2))
 if action=='check':return dict(result='READ_ONLY_CHECK_PASS',evidence=str(evidence),writes=0)
 backup=read(0,0x1000000,'current-flash.bin');full=backup.read_bytes();require(full[0x8000:0x9000]==table.read_bytes() and full[0xe000:0x10000]==ota.read_bytes(),'BACKUP_METADATA_MISMATCH')
 backup_hash=hashlib.sha256(full).hexdigest();(evidence/'backup-integrity.json').write_text(json.dumps(dict(bytes=len(full),sha256=backup_hash))+'\n')
 phrase='ROLLBACK' if action=='rollback' else 'INSTALL'
 require(confirm('Type '+phrase+' to write only these two application regions: ')==phrase,'OWNER_CANCELLED')
 require(identify()==first,'CHIP_CHANGED')
 fresh_table=read(0x8000,4096,'fresh-partitions.bin');fresh_ota=read(0xe000,8192,'fresh-otadata.bin');require(fresh_table.read_bytes()==table.read_bytes() and fresh_ota.read_bytes()==ota.read_bytes(),'METADATA_CHANGED')
 final=validate(root,fresh_table,fresh_ota,True,selected);require(final['selected_write_ranges']==rows,'PLAN_CHANGED')
 require(hashlib.sha256((root/file).read_bytes()).hexdigest()==digest,'IMAGE_CHANGED')
 # NOR programming erases only these image-rounded app sectors. No separate erase API.
 try:
  call('write_flash','--flash_mode','keep','--flash_freq','keep','--flash_size','keep','--no-compress','0x10000',str(root/file),'0x750000',str(root/file))
  for offset in ['0x10000','0x750000']:call('verify_flash','--flash_mode','keep','--flash_freq','keep','--flash_size','keep',offset,str(root/file))
 except (Stopped,OSError,subprocess.SubprocessError) as e:
  raise Stopped('WRITE_OR_VERIFY_FAILED: '+str(e)+'. Stay in ROM; no reboot or retry was attempted. Rediscover the port and use a separately deliberate released rollback with fresh evidence. Private backup: '+str(evidence))
 return dict(result='BOTH_APPLICATION_COMPARISONS_PASS',evidence=str(evidence),backup_sha256=backup_hash,boot_tested=False,automatic_reboot=False)

def tool_process(command):
 # Called only by a separately bound release, never during this unbound CLI.
 require(command[:3]==[sys.executable,'-m','esptool'],'INVALID_TOOL_PROCESS')
 result=subprocess.run(command,capture_output=True,text=True,timeout=3600)
 require(result.returncode==0,'ESPTOOL_EXIT_'+str(result.returncode)+': '+(result.stderr or result.stdout)[-1000:])
 return result.stdout+'\n'+result.stderr

def main():
 try:
  require(sys.version_info>=(3,8),'PYTHON_38_OR_NEWER_REQUIRED')
  p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['check','install','rollback'],default='check');p.add_argument('--port');args=p.parse_args()
  if RELEASE_BINDING is None:
   print('BLOCKED: RELEASE_NOT_BOUND. This is tested installer preparation, not a released installation package. No device access occurred.');return 2
  root=pathlib.Path(__file__).resolve().parent
  # A future reviewed package binds the actual offline helper bytes, not a user flag.
  helper=root/'preflight.py';require(helper.is_file() and not helper.is_symlink(),'MISSING_RELEASE_PREFLIGHT')
  require(hashlib.sha256(helper.read_bytes()).hexdigest()==RELEASE_BINDING['preflight_sha256'],'RELEASE_PREFLIGHT_IDENTITY')
  spec=importlib.util.spec_from_file_location('reviewed_package_preflight',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  result=session(root,args.port,args.action,tool_process,module.validate,input,pathlib.Path.home()/'Desktop');print(json.dumps(result,indent=2));return 0
 except KeyboardInterrupt:
  print('Interrupted. No automatic retry or reboot. If writing had begun, stay in ROM and use fresh evidence for a deliberate released rollback.');return 130
 except (Stopped,OSError,ValueError,KeyError,subprocess.SubprocessError) as e:
  print('STOPPED: '+str(e));return 1
if __name__=='__main__':raise SystemExit(main())
