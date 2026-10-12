#!/usr/bin/env python3
"""Offline final-link provenance checks; compilation is not physical USB validation."""
import argparse,json,subprocess
from pathlib import Path
from patched_core import check_sources,sha
from s3_validation import ROOT,require

def verify(core,build):
 core,build=Path(core).resolve(),Path(build).resolve();pin=check_sources(core,True)
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
 compiler=Path(entry['arguments'][0]);prefix=str(compiler).rsplit('g++',1)[0];nm=prefix+'nm';objdump=prefix+'objdump'
 elf=build/'EvilDuckS3.ino.elf';symbols=subprocess.run([nm,'-C','--defined-only',str(elf)],capture_output=True,text=True,check=True).stdout
 callback=[l for l in symbols.splitlines() if l.endswith(' T tud_hid_set_report_cb')];require(len(callback)==1,'Final ELF must contain exactly one strong SET_REPORT callback')
 require('FeedbackKeyboard::_onOutput(' in symbols,'Production OUTPUT override missing from linked ELF')
 require('FeedbackKeyboard::_onSetFeature(' not in symbols,'Legacy FEATURE-as-LED workaround still linked')
 for symbol in ['tud_hid_get_report_cb','tud_cdc_rx_cb','tud_msc_read10_cb','tud_msc_write10_cb']:
  require(symbol in symbols,'Expected HID/CDC/MSC integration symbol absent: '+symbol)
 maptext=(build/'EvilDuckS3.ino.map').read_text();require(str(obj) in maptext,'Link map lacks verified routing object')
 disasm=subprocess.run([objdump,'-d','--disassemble=tud_hid_set_report_cb',str(elf)],capture_output=True,text=True,check=True).stdout
 require('<tud_hid_set_report_cb>:' in disasm,'Linked callback disassembly missing')
 (build/'stage16-linked-routing.txt').write_text(disasm)
 report=dict(patched_core_pin=pin,core=str(core),compiled_routing=str(entry['file']),routing_object_sha256=sha(obj),elf_sha256=sha(elf),application_sha256=sha(build/'EvilDuckS3.ino.bin'),backend_sha256=sha(ROOT/'EvilDuckS3/hid_backend.cpp'),compiler_sha256=sha(compiler),compiler_version=subprocess.run([str(compiler),'--version'],capture_output=True,text=True,check=True).stdout,cli_settings=props['build.fqbn'],single_strong_callback=True,feature_workaround_absent=True,hid_cdc_msc_linked=True,hardware_access=False)
 (build/'stage16-link-provenance.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);a=p.parse_args();print(json.dumps(verify(a.core_dir,a.build_dir),indent=2))
