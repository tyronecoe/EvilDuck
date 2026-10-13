#!/usr/bin/env python3
"""Offline final-link provenance checks; compilation is not physical USB validation."""
import argparse,json,subprocess,tempfile,sys,re
sys.dont_write_bytecode = True
from pathlib import Path
from patched_core import check_sources,sha
from s3_validation import ROOT,require,validate_build

def verify(core,build):
 core,build=Path(core).resolve(),Path(build).resolve();pin=check_sources(core,True)
 validated_build=validate_build(core,build)
 props=json.loads((build/'s3-build-properties.json').read_text());require(Path(props['runtime.platform.path']).resolve()==core,'Final build selected a different platform')
 entries=json.loads((build/'compile_commands.json').read_text())
 routes=[e for e in entries if Path(e['file']).name=='USBHID.cpp'];require(len(routes)==1,'Expected exactly one compiled USBHID translation unit')
 entry=routes[0];require(Path(entry['file']).resolve()==core/'libraries/USB/src/USBHID.cpp','Compiled routing is not from verified isolated core')
 obj=Path(entry['arguments'][entry['arguments'].index('-o')+1]);require(obj.exists(),'Routing object missing')
 backends=[e for e in entries if Path(e['file']).name=='hid_backend.cpp'];require(len(backends)==1,'Expected one production backend')
 require('-DEVILDUCK_VERIFIED_HID_ROUTING=1' in backends[0]['arguments'],'Production dependency guard not enabled')
 compiled_backend=Path(backends[0]['file']).read_bytes()
 prefix_line=('#line 1 '+json.dumps(str(ROOT/'EvilDuckS3/hid_backend.cpp'))+'\n').encode()
 require(compiled_backend==prefix_line+(ROOT/'EvilDuckS3/hid_backend.cpp').read_bytes(),'Compiled backend differs from current production source (after Arduino line directive)')
 build_report=json.loads((build/'s3-build-report.json').read_text())
 sketch_entries=[e for e in entries if Path(e['file']).name=='EvilDuckS3.ino.cpp']
 require(len(sketch_entries)==1,'Expected one actual startup translation unit')
 require('-DEVILDUCK_VERIFIED_NVS_PRESERVATION=1' in sketch_entries[0]['arguments'],'NVS dependency guard not enabled')
 misc=[e for e in entries if Path(e['file']).name=='esp32-hal-misc.c']
 require(len(misc)==1 and Path(misc[0]['file']).resolve()==core/pin['nvs_source'],'Early startup is not from the verified isolated core')
 safe_flag='-DEVILDUCK_DEPLOYMENT_SAFE_START=1' in sketch_entries[0]['arguments']
 controlled_flag='-DEVILDUCK_CONTROLLED_START=1' in sketch_entries[0]['arguments']
 require(not(safe_flag and controlled_flag),'Conflicting startup profiles')
 require(controlled_flag is build_report.get('controlled_normal_start',False),'Controlled profile metadata/flags mismatch')
 require(safe_flag is build_report.get('deployment_safe_start',False),'Startup profile metadata differs from actual compiler flags')
 if (ROOT/'EvilDuckS3/deployment_boot.h').exists():
  header=ROOT/'EvilDuckS3/deployment_boot.h'
  require((build/'sketch/deployment_boot.h').read_bytes()==('#line 1 '+json.dumps(str(header))+'\n').encode()+header.read_bytes(),'Compiled deployment policy differs from source')
  startup=(ROOT/'EvilDuckS3/EvilDuckS3.ino').read_text()
  require(startup[startup.index('void setup() {'):] in Path(sketch_entries[0]['file']).read_text(),'Compiled startup bodies differ from current source')
 compiler=Path(entry['arguments'][0]);prefix=str(compiler).rsplit('g++',1)[0];nm=prefix+'nm';objdump=prefix+'objdump'
 elf=build/'EvilDuckS3.ino.elf'
 require(build_report['application_sha256']==sha(build/'EvilDuckS3.ino.bin'),'Application differs from clean-build hash')
 # Regenerate using the exact pinned Arduino elf2image settings, never a port API.
 esptool=Path(props['runtime.tools.esptool_py.path'])/'esptool'
 with tempfile.TemporaryDirectory(prefix='evilduck-elf-image-proof-') as t:
  regenerated=Path(t)/'application.bin'
  subprocess.run([str(esptool),'--chip','esp32s3','elf2image','--flash-mode','dio','--flash-freq','80m','--flash-size','16MB','--elf-sha256-offset','0xb0','-o',str(regenerated),str(elf)],capture_output=True,text=True,check=True)
  require(regenerated.read_bytes()==(build/'EvilDuckS3.ino.bin').read_bytes(),'Application is not the image generated from the verified ELF')
  rodata=Path(t)/'rodata.bin'
  subprocess.run([prefix+'objcopy','--dump-section','.flash.rodata='+str(rodata),str(elf),str(Path(t)/'inspection-only.elf')],capture_output=True,text=True,check=True)
  marker=b'DEPLOYMENT SAFE START: application services and payload execution disabled'
  require((marker in rodata.read_bytes())==safe_flag,'Linked application startup profile differs from build flags')
  controlled_marker=b'CONTROLLED NORMAL START: strict credentials, no format, no examples, no autorun'
  require((controlled_marker in rodata.read_bytes())==controlled_flag,'Linked controlled startup identity mismatch')
 symbols=subprocess.run([nm,'-C','--defined-only',str(elf)],capture_output=True,text=True,check=True).stdout
 callback=[l for l in symbols.splitlines() if l.endswith(' T tud_hid_set_report_cb')];require(len(callback)==1,'Final ELF must contain exactly one strong SET_REPORT callback')
 require('FeedbackKeyboard::_onOutput(' in symbols,'Production OUTPUT override missing from linked ELF')
 require('FeedbackKeyboard::_onSetFeature(' not in symbols,'Legacy FEATURE-as-LED workaround still linked')
 require(sum(l.endswith(' T evilduck_nvs_startup_error') for l in symbols.splitlines())==1,'Protected NVS status hook missing/duplicated')
 require('startupNvsError' in symbols,'Application failure latch absent')
 if controlled_flag:
  for module in ['spiffs.cpp','storage.cpp']:
   matches=[e for e in entries if Path(e['file']).name==module];original=ROOT/'EvilDuckS3'/module
   require(len(matches)==1 and '-DEVILDUCK_CONTROLLED_START=1' in matches[0]['arguments'],'Controlled storage flag absent')
   require(Path(matches[0]['file']).read_bytes()==('#line 1 '+json.dumps(str(original))+'\n').encode()+original.read_bytes(),'Compiled controlled storage differs from source')
  header=ROOT/'EvilDuckS3/controlled_layout.h'
  require((build/'sketch/controlled_layout.h').read_bytes()==('#line 1 '+json.dumps(str(header))+'\n').encode()+header.read_bytes(),'Compiled controlled layout differs from source')
  for latch in ['startupStorageFailed','startupControlledAttempted','startupControlledReady']:require(latch in symbols,'Controlled startup latch absent: '+latch)
 nvs_header=ROOT/'EvilDuckS3/nvs_startup.h'
 require((build/'sketch/nvs_startup.h').read_bytes()==('#line 1 '+json.dumps(str(nvs_header))+'\n').encode()+nvs_header.read_bytes(),'Compiled NVS contract header differs from source')
 setup_disasm=subprocess.run([objdump,'-d','--disassemble=_Z5setupv',str(elf)],capture_output=True,text=True,check=True).stdout
 # Xtensa sequential disassembly can lose alignment at unreachable linker padding.
 # Re-decode bounded explicit branch targets to verify the final linked call.
 if 'evilduck_nvs_startup_error' not in setup_disasm:
  targets=list(dict.fromkeys(re.findall(r'([0-9a-f]+) <_Z5setupv\+0x[0-9a-f]+>',setup_disasm)))[:16]
  for target in targets:
   address=int(target,16)
   block=subprocess.run([objdump,'-d','--start-address='+hex(address),'--stop-address='+hex(address+96),str(elf)],capture_output=True,text=True,check=True).stdout
   setup_disasm += block
   if 'evilduck_nvs_startup_error' in block:break
 require('evilduck_nvs_startup_error' in setup_disasm,'Actual setup does not read protected core status')
 if (ROOT/'EvilDuckS3/settings.h').read_text().find('bool ready();') >= 0:
  setting_entries=[e for e in entries if Path(e['file']).name=='settings.cpp']
  require(len(setting_entries)==1,'Expected one production settings translation unit')
  settings_header=ROOT/'EvilDuckS3/settings.h'
  require((build/'sketch/settings.h').read_bytes()==('#line 1 '+json.dumps(str(settings_header))+'\n').encode()+settings_header.read_bytes(),'Compiled settings contract differs from source')
  settings_source=ROOT/'EvilDuckS3/settings.cpp'
  require(Path(setting_entries[0]['file']).read_bytes()==('#line 1 '+json.dumps(str(settings_source))+'\n').encode()+settings_source.read_bytes(),'Compiled settings safety policy differs from source')
  if not safe_flag:
   require('startupSettingsFailed' in symbols,'Settings failure latch absent')
   require('_ZN8settings5readyEv' in setup_disasm and '_ZN8settings9loadErrorEv' in setup_disasm,'Actual setup settings readiness/error checks absent')
   require(setup_disasm.index('_ZN8settings5readyEv')<setup_disasm.index('_ZN11hid_backend5beginEv'),'Settings validation must precede HID activation')
  if 'bool saveChecked();' in settings_header.read_text():
   for module in ['cli.cpp','webserver.cpp']:
    found=[e for e in entries if Path(e['file']).name==module]
    original=ROOT/'EvilDuckS3'/module
    require(len(found)==1 and Path(found[0]['file']).read_bytes()==('#line 1 '+json.dumps(str(original))+'\n').encode()+original.read_bytes(),'Compiled checked-persistence caller differs from source')
   if not safe_flag:
    require('settings::saveChecked()' in symbols and 'settings::resetChecked()' in symbols,'Checked persistence API absent from final normal ELF')
  if controlled_flag:
   require('_ZN7storage5beginEv' in setup_disasm,'Controlled mount check not linked')
   require(setup_disasm.index('_ZN7storage5beginEv')<setup_disasm.index('_ZN11hid_backend5beginEv'),'Storage must precede HID activation')
   require('_ZN14script_library15installIfNeededEv' not in setup_disasm and '_ZN10duckscript3run' not in setup_disasm,'Controlled startup injects examples or payloads')
  (build/'stage19-linked-startup.txt').write_text(setup_disasm)
 (build/'stage18-linked-startup.txt').write_text(setup_disasm)
 nvs_disasm=subprocess.run([objdump,'-d','--disassemble=initArduino',str(elf)],capture_output=True,text=True,check=True).stdout
 require('<initArduino>:' in nvs_disasm and 'nvs_flash_init' in nvs_disasm,'Real NVS startup call missing')
 require('esp_partition_erase_range' not in nvs_disasm and 'nvs_flash_erase' not in nvs_disasm,'Automatic erase still linked in Arduino initialization')
 (build/'stage18-linked-nvs.txt').write_text(nvs_disasm)
 for symbol in ['tud_hid_get_report_cb','tud_cdc_rx_cb','tud_msc_read10_cb','tud_msc_write10_cb']:
  require(symbol in symbols,'Expected HID/CDC/MSC integration symbol absent: '+symbol)
 maptext=(build/'EvilDuckS3.ino.map').read_text();require(str(obj) in maptext,'Link map lacks verified routing object')
 disasm=subprocess.run([objdump,'-d','--disassemble=tud_hid_set_report_cb',str(elf)],capture_output=True,text=True,check=True).stdout
 require('<tud_hid_set_report_cb>:' in disasm,'Linked callback disassembly missing')
 (build/'stage16-linked-routing.txt').write_text(disasm)
 report=dict(patched_core_pin=pin,core=str(core),compiled_routing=str(entry['file']),routing_object_sha256=sha(obj),elf_sha256=sha(elf),application_sha256=sha(build/'EvilDuckS3.ino.bin'),backend_sha256=sha(ROOT/'EvilDuckS3/hid_backend.cpp'),compiler_sha256=sha(compiler),compiler_version=subprocess.run([str(compiler),'--version'],capture_output=True,text=True,check=True).stdout,cli_settings=props['build.fqbn'],single_strong_callback=True,feature_workaround_absent=True,hid_cdc_msc_linked=True,deployment_safe_start=safe_flag,controlled_normal_start=controlled_flag,elf_to_image_verified=True,esptool_sha256=sha(esptool),checked_settings_persistence=True,settings_failure_quiescent=True,settings_source_sha256=sha(ROOT/'EvilDuckS3/settings.cpp'),sdk_nvs_immutable=False,nvs_preservation_policy=True,nvs_source_sha256=sha(core/pin['nvs_source']),hardware_access=False)
 (build/'stage16-link-provenance.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);a=p.parse_args();print(json.dumps(verify(a.core_dir,a.build_dir),indent=2))
