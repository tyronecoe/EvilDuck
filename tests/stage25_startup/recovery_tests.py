#!/usr/bin/env python3
"""Recovery structure/range faults using compiled artifacts and synthetic stock format.
No actual owner recovery image or known-good physical operation is represented.
"""
import argparse,copy,hashlib,json,shutil,struct,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from stage25_recovery_check import verify_recovery
from stage25_fresh_config import controlled_config
from s3_validation import partition_tool,LAYOUT,LEGACY_LAYOUT
from verify_patched_firmware import verify
p=argparse.ArgumentParser()
for n in ['core-dir','controlled-core','controlled-build','normal-core','normal-build','safe-core','safe-build','results']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();rows=[];assertions=0

def case(name,fn,deny=False):
 global assertions
 try:
  fn()
  if deny:raise AssertionError('Unsafe input accepted')
  status='PASS';error=''
 except (ValueError,OSError,RuntimeError,KeyError) as e:
  status='PASS' if deny else 'FAIL';error='' if deny else str(e)
 except Exception as e:status='FAIL';error=str(e)
 assertions+=1;rows.append(dict(name=name,status=status,assertions=1,error=error));print(status,name,error)

def synthetic_image(size_code=2,minimum=0,maximum=65535,mode=2,frequency=15):
 d=bytearray(24);d[:4]=bytes([0xe9,1,mode,size_code<<4|frequency]);struct.pack_into('<I',d,4,0x40370000);struct.pack_into('<H',d,12,9);struct.pack_into('<H',d,15,minimum);struct.pack_into('<H',d,17,maximum);d[23]=1
 payload=b'non-executable-format-vector';d+=struct.pack('<II',0x3fc88000,len(payload))+payload;checksum=0xef
 for byte in payload:checksum^=byte
 d+=b'\0'*((15-len(d)%16)%16)+bytes([checksum]);return bytes(d)+hashlib.sha256(d).digest()

with tempfile.TemporaryDirectory(prefix='stage25-recovery-vectors-') as t:
 t=Path(t)
 def bundle(layout,images):
  directory=t/('bundle-'+str(len(list(t.iterdir()))));directory.mkdir()
  table=partition_tool(a.core_dir).PartitionTable.from_csv('\n'.join(','.join([n,str(typ),str(sub),hex(o),hex(s),'']) for n,typ,sub,o,s in layout)).to_binary()
  payloads={'bootloader':images[0],'app0':images[1],'partitions':table,'otadata':(a.core_dir/'tools/partitions/boot_app0.bin').read_bytes()}
  offsets={'bootloader':0,'partitions':0x8000,'otadata':0xe000,'app0':0x10000}
  manifest=dict(kind='recovery-review',physical_flash_bytes=0x1000000,owner_reported_known_good=False,images=[])
  for role,data in payloads.items():
   file=role+'.bin';(directory/file).write_bytes(data);manifest['images'].append(dict(role=role,file=file,offset=offsets[role],bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
  (directory/'recovery-review.json').write_text(json.dumps(manifest));return directory,manifest
 build=a.controlled_build
 directory,manifest=bundle(LAYOUT,[(build/'EvilDuckS3.ino.bootloader.bin').read_bytes(),(build/'EvilDuckS3.ino.bin').read_bytes()])
 case('compiled_images_offline_structure_only',lambda:verify_recovery(a.core_dir,directory))
 original=json.loads(json.dumps(manifest))
 for name,change in [('wrong_hash',lambda m:m['images'][0].update(sha256='0'*64)),('wrong_offset',lambda m:m['images'][0].update(offset=0x9000)),('wrong_bytes',lambda m:m['images'][0].update(bytes=1)),('wrong_physical_size',lambda m:m.update(physical_flash_bytes=0x400000)),('missing_role',lambda m:m['images'].pop()),('duplicate_role',lambda m:m['images'].append(dict(m['images'][0])))]:
  bad=copy.deepcopy(original);change(bad);(directory/'recovery-review.json').write_text(json.dumps(bad));case(name,lambda:verify_recovery(a.core_dir,directory),True)
 (directory/'recovery-review.json').write_text(json.dumps(original))
 data=(directory/'partitions.bin').read_bytes();damaged=bytearray(data);damaged[0]^=1;(directory/'partitions.bin').write_bytes(damaged)
 bad=copy.deepcopy(original);next(r for r in bad['images'] if r['role']=='partitions')['sha256']=hashlib.sha256(damaged).hexdigest();(directory/'recovery-review.json').write_text(json.dumps(bad));case('corrupt_table_even_with_matching_hash',lambda:verify_recovery(a.core_dir,directory),True)
 # Synthetic legacy vectors validate format contracts, not executable recovery payloads.
 legacy,_=bundle(LEGACY_LAYOUT,[synthetic_image(),synthetic_image()]);case('synthetic_legacy_4m_header_on_16m_hardware_context',lambda:verify_recovery(a.core_dir,legacy))
 full,_=bundle(LEGACY_LAYOUT,[(build/'EvilDuckS3.ino.bootloader.bin').read_bytes(),(build/'EvilDuckS3.ino.bin').read_bytes()]);case('upgraded_application_does_not_fit_original_slot',lambda:verify_recovery(a.core_dir,full),True)
 for name,image in [('minimum_revision',synthetic_image(minimum=3)),('maximum_revision',synthetic_image(maximum=1)),('bad_flash_frequency',synthetic_image(frequency=1)),('excess_flash_capacity',synthetic_image(size_code=5)),('insufficient_flash_profile',synthetic_image(size_code=0)),('bad_chip',None)]:
  if image is None:
   d=bytearray(synthetic_image());d[12]=0;d[-32:]=hashlib.sha256(d[:-32]).digest();image=bytes(d)
  test,_=bundle(LEGACY_LAYOUT,[synthetic_image(),image]);case('reject_'+name,lambda d=test:verify_recovery(a.core_dir,d),True)
 invalid=bytearray(synthetic_image());struct.pack_into('<I',invalid,4,0);invalid[-32:]=hashlib.sha256(invalid[:-32]).digest()
 noentry,_=bundle(LEGACY_LAYOUT,[synthetic_image(),bytes(invalid)]);case('unsupported_entry_point_rejected',lambda:verify_recovery(a.core_dir,noentry),True)
 sentinel,_=bundle(LEGACY_LAYOUT,[synthetic_image(maximum=1),synthetic_image(maximum=0)]);case('sdk_max_revision_zero_sentinel_and_bootloader_max_exemption',lambda:verify_recovery(a.core_dir,sentinel))
 test,spec=bundle(LAYOUT,[synthetic_image(size_code=4),synthetic_image(size_code=4)]);row=next(r for r in spec['images'] if r['role']=='otadata');(test/row['file']).write_bytes(b'\xff'*0x2000);row['sha256']=hashlib.sha256((test/row['file']).read_bytes()).hexdigest();(test/'recovery-review.json').write_text(json.dumps(spec));case('nondeterministic_ota_initializer_rejected',lambda:verify_recovery(a.core_dir,test),True)
 for profile,core,target in [('normal',a.normal_core,a.normal_build),('safe',a.safe_core,a.safe_build),('controlled',a.controlled_core,a.controlled_build)]:case('linked_'+profile+'_profile',lambda c=core,b=target:verify(c,b))
 # Actual compiler diagnostics and public core property options prevent profile confusion.
 r=subprocess.run([sys.executable,str(ROOT/'tools/build_s3_patched.py'),'--core-dir','/unavailable-core','--user-dir','/unavailable-libraries','--isolation-dir','/tmp/unavailable-isolation','--build-dir','/tmp/unavailable-build','--arduino-cli','/unavailable-cli','--deployment-safe-start','--controlled-normal-start'],capture_output=True,text=True)
 case('conflicting_build_profile_rejected',lambda: (_ for _ in ()).throw(AssertionError()) if not r.returncode or 'not allowed with argument' not in r.stderr else None)
 config={'ssid':chr(115)*12,'ap_password':chr(112)*16,'web_password':chr(119)*16}
 case('explicit_private_config_contract',lambda:controlled_config(config))
 case('missing_private_config_rejected',lambda:controlled_config({}),True)
 import re
 legacy_password=re.search(r'^#define\s+WIFI_PASSWORD\s+"([^"\\]*)"\s*$',(ROOT/'EvilDuckS3/config.h').read_text(),re.M)[1]
 bad=dict(config,ap_password=legacy_password);case('legacy_provisioning_password_rejected',lambda:controlled_config(bad),True)
 # Native pinned header ABI proof; no target SDK execution is claimed.
 entries=json.load(open(build/'compile_commands.json'));entry=next(e for e in entries if Path(e['file']).name=='settings.cpp');cmd=list(entry['arguments']);source=t/'abi.cpp';source.write_text('#include <esp_app_format.h>\n#include <stddef.h>\n#include <soc/soc.h>\nstatic_assert(SOC_IRAM_LOW==0x40370000 && SOC_IRAM_HIGH==0x403E0000,"S3 memory ranges");\nstatic_assert(offsetof(esp_image_header_t,min_chip_rev_full)==15,"header ABI");\nstatic_assert(offsetof(esp_image_header_t,max_chip_rev_full)==17,"header ABI");\n')
 cmd[cmd.index(entry['file'])]=str(source);cmd[cmd.index('-o')+1]=str(t/'abi.o');case('pinned_native_image_header_revision_offsets',lambda:subprocess.run(cmd,cwd=entry['directory'],capture_output=True,check=True))
 for prop in ['recipe.hooks.objcopy.postobjcopy.3.pattern=']:
  case('merged_output_suppressed_by_real_compile_options',lambda: (_ for _ in ()).throw(AssertionError()) if prop not in json.load(open(build/'build.options.json'))['customBuildProperties'].split(',') or (build/'EvilDuckS3.ino.merged.bin').exists() else None)
a.results.write_text(json.dumps(dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=assertions,owner_recovery_files_inspected=False,hardware_access=False,known_good_recovery_independently_established=False),indent=2)+'\n');raise SystemExit(any(r['status']=='FAIL' for r in rows))
