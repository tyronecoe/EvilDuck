#!/usr/bin/env python3
"""Post-link read-only evidence closure, including linker response/archive inputs."""
import pathlib,json,argparse,subprocess,shlex,re,sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'caps_stop'))
from prepare_sources import ROOT,sha,frameworks,manifest
sys.path.insert(0,str(ROOT/'tools'))
from feedback_core import check_sources
from s3_validation import validate_build
p=argparse.ArgumentParser();p.add_argument('--build-root',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();assert not a.output.exists();r=json.loads((a.build_root/'report.json').read_text());assert r['status']=='PASS';build=a.build_root/'build';elf=build/'EvilDuckS3.ino.elf';core=pathlib.Path(r['provenance']['core']);assert check_sources(core,True)==r['core_pin'];assert sha(elf)==r['provenance']['elf_sha256'];assert sha(build/'EvilDuckS3.ino.bin')==r['report']['application_sha256']
for x in r['source_inventory']:assert sha(a.build_root/'candidate'/x['file'])==x['sha256'],x['file']
pin=json.loads((ROOT/'docs/keyboard-shortcuts-source-manifest.json').read_text());after={x['file']:x['sha256'] for x in pin['after']}
http_pin=json.loads((ROOT/'docs/http-snapshot-source-manifest.json').read_text());after.update({x['file']:x['sha256'] for x in http_pin['after']})
for newpin in ['stop-ui-source-manifest.json','led-return-source-manifest.json','caps-queue-source-manifest.json','led-feedback-source-manifest.json','caps-duration-source-manifest.json','mac-caps-source-manifest.json','caps-stop-source-manifest.json']:
 extra=json.loads((ROOT/'docs'/newpin).read_text());after.update({x['file']:x['sha256'] for x in extra['after']+extra.get('additions',[])})
for x in manifest()['outputs']:
 if x['file']!='platform.cpp':assert sha(a.build_root/'candidate/EvilDuckS3'/x['file'])==after.get(x['file'],x['sha256'])
for file,digest in after.items():assert sha(a.build_root/'candidate/EvilDuckS3'/file)==digest
assert frameworks(pathlib.Path(json.loads((a.build_root/'arduino-cli.json').read_text())['directories']['user']))==r['framework_pins']
link=r['link_command'];response=[];expanded=[]
for x in link:
 if x.startswith('@'):
  f=pathlib.Path(x[1:]);response.append(dict(file=str(f),sha256=sha(f),text=f.read_text()));expanded.extend(shlex.split(f.read_text()))
 else:expanded.append(x)
maptext=(build/'EvilDuckS3.ino.map').read_text();inputs={x['file']:x for x in r['linked_input_hashes']}
for path in re.findall(r'^LOAD (.+)$',maptext,re.M):
 f=pathlib.Path(path.strip())
 if f.is_file():inputs[str(f)]=dict(file=str(f),size=f.stat().st_size,sha256=sha(f))
sdk=core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3';assert sdk.is_dir()
for f in sorted(sdk.rglob('*.a')):
 if str(f) in maptext or '-l'+f.stem[3:] in expanded:inputs[str(f)]=dict(file=str(f),size=f.stat().st_size,sha256=sha(f))
compiler=pathlib.Path(link[0]);linker=pathlib.Path(subprocess.check_output([str(compiler),'-print-prog-name=ld'],text=True).strip());assert linker.is_file()
# Linker scripts can be supplied through response files and -L search directories.
search=[pathlib.Path(x[2:]) for x in expanded if x.startswith('-L')]
scripts=[]
for i,x in enumerate(expanded):
 name=expanded[i+1] if x=='-T' else x[2:] if x.startswith('-T') else None
 if name:
  matches=[f for d in [build,*search] if (f:=d/name).is_file()]
  assert matches,'missing linker script '+name
  f=matches[0];scripts.append(dict(file=str(f),size=f.stat().st_size,sha256=sha(f)))
assert len([x for x in inputs if '/esp32-arduino-libs/' in x and x.endswith('.a')])>20
symbols=r['symbols'];off='selector-off' in r['profile'];prefix=str(compiler).rsplit('g++',1)[0]
for artifact in r['artifacts']:assert sha(build/artifact['file'])==artifact['sha256'],artifact['file']
if not off:
 assert 'AsyncFileResponse' not in symbols and 'activeWsClient' not in symbols and 'wsOut(' not in symbols
 assert 'serialBuffer' in symbols and 'lineBuffer' not in symbols
else:assert 'AsyncFileResponse' in symbols and 'activeWsClient' in symbols and 'lineBuffer' in symbols

# Independently dump linked data: marker and immutable profile identity are retained.
rodata=a.output.parent/(a.output.stem+'-rodata.tmp');subprocess.run([prefix+'objcopy','--dump-section','.flash.rodata='+str(rodata),str(elf),str(a.output.parent/(a.output.stem+'-inspection-only.elf'))],check=True,capture_output=True)
marker=b'STAGE28W CONTROLLED ROUTE B REVIEW ONLY; explicit selection required';assert (marker in rodata.read_bytes())==(not off);rodata.unlink();(a.output.parent/(a.output.stem+'-inspection-only.elf')).unlink();assert sha(elf)==r['provenance']['elf_sha256']
for symbol in ['cli::update()','route_u::tick','route_u::requestStart','ds_preview::CompileSession::step','native_b::Adapter::step']:
 if symbol.startswith('cli'):assert symbol in symbols
 else:assert (symbol in symbols)==(not off)
loop_disasm=subprocess.check_output([prefix+'objdump','-d','--disassemble=_Z4loopv',str(elf)],text=True)
assert '_ZN7route_u9bindOwnerEv' in loop_disasm if not off else '_ZN7route_u9bindOwnerEv' not in loop_disasm
assert '_ZN10duckscript6updateEv' in loop_disasm and '_ZN3cli6updateEv' in loop_disasm
assert loop_disasm.index('_ZN10duckscript6updateEv')<loop_disasm.index('_ZN3cli6updateEv')
update_disasm=subprocess.check_output([prefix+'objdump','-d','--disassemble=_ZN10duckscript6updateEv',str(elf)],text=True)
assert ('_ZN7route_u4tickEm' in update_disasm)==(not off)
compiled_source_checks=[]
for original in (a.build_root/'candidate/EvilDuckS3').iterdir():
 if original.suffix not in ['.cpp','.h','.inc']:continue
 copy=build/'sketch'/original.name
 if copy.exists():
  expected=('#line 1 '+json.dumps(str(original))+'\n').encode()+original.read_bytes()
  assert copy.read_bytes() in [expected,original.read_bytes()],str(copy)
  compiled_source_checks.append(dict(file=str(copy),sha256=sha(copy),original_sha256=sha(original)))

stack_disasm=subprocess.check_output([prefix+'objdump','-d','--disassemble=_Z28getArduinoLoopTaskStackSizev',str(elf)],text=True)
# GCC mangling count is checked by the human-readable nm inventory if tool has no function match.
if '<_Z28getArduinoLoopTaskStackSizev>:' not in stack_disasm:
 stack_disasm=subprocess.check_output([prefix+'objdump','-d','-C',str(elf)],text=True);start=stack_disasm.index('<getArduinoLoopTaskStackSize()>:');stack_disasm=stack_disasm[start:stack_disasm.index('\n\n',start)]
# Compare every consumed installed SDK archive with immutable W, not just NVS.
w=json.loads((ROOT/'docs/stage28w-linked-enabled.json').read_text())
w_sdk={x['file'].split('/esp32s3/',1)[1]:x['sha256'] for x in w['linked_input_hashes'] if '/esp32-arduino-libs/' in x['file'] and x['file'].endswith('.a')}
x_sdk={x['file'].split('/esp32s3/',1)[1]:x['sha256'] for x in inputs.values() if '/esp32-arduino-libs/' in x['file'] and x['file'].endswith('.a')}
assert x_sdk==w_sdk,'SDK archive identity differs from W'
r['sdk_archives_identical_to_w']=len(x_sdk)
r['linked_input_hashes']=list(inputs.values());r['link_response_files']=response;r['linker']=dict(file=str(linker),sha256=sha(linker));r['linker_scripts']=scripts;r['verified_w_marker']=not off;r['loop_disassembly']=loop_disasm;r['loop_stack_selection_disassembly']=stack_disasm;r['verification_scope']='actual linked ELF/BIN and pinned source/archive identity; not FreeRTOS, AsyncTCP or physical execution';r['compiled_source_checks']=compiled_source_checks;r['duckscript_update_disassembly']=update_disasm;r['post_link_verifier_sha256']=sha(pathlib.Path(__file__))
# Actual linked default-off/instrumented identity, no hardware claim.
diag=r['diagnostics_enabled']
for name in ['route_x::beginTurn','route_x::endTurn','route_x::format','route_x::snapshot','heap_caps_get_largest_free_block','uxTaskGetStackHighWaterMark']:
 assert (name in symbols) if diag else (not name.startswith('route_x::') or name not in symbols),name
xmarker=b'STAGE28X OBSERVATIONAL DIAGNOSTICS REVIEW ONLY; no deployment authorization'
before=sha(elf);tmp=a.output.parent/(a.output.stem+'-xdata');tmpelf=a.output.parent/(a.output.stem+'-xinspection.elf')
subprocess.run([prefix+'objcopy','--dump-section','.flash.rodata='+str(tmp),str(elf),str(tmpelf)],check=True,capture_output=True)
assert (xmarker in tmp.read_bytes())==diag;tmp.unlink();tmpelf.unlink();assert sha(elf)==before
r['verified_x_marker']=diag
entries=json.loads((build/'compile_commands.json').read_text())
sys.path.insert(0,str(ROOT/'tests/mac_install'))
from core_inventory import inventory
neo=json.loads((ROOT/'docs/mac-release-neopixel-pin.json').read_text())
user=pathlib.Path(json.loads((a.build_root/'arduino-cli.json').read_text())['directories']['user'])
assert json.loads(json.dumps(inventory(user/'libraries/Adafruit_NeoPixel')))==neo['inventory']
neo_entries=[e for e in entries if '/libraries/Adafruit_NeoPixel/' in e['file']]
assert len(neo_entries)==6
for e in neo_entries:
 f=pathlib.Path(e['file']);assert sha(f)==dict(neo['inventory']['files'])[str(f.relative_to(user/'libraries/Adafruit_NeoPixel'))]
r['supplementary_library_pin']=neo

for e in entries:
 if pathlib.Path(e['file']).is_relative_to(build/'sketch'):
  assert ('-DEVILDUCK_ROUTE_B_DIAGNOSTICS' in e['arguments'])==diag
  assert '-DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1' in e['arguments']
  assert '-DEVILDUCK_ROUTE_B_STATUS_HARDENING=1' in e['arguments']
assert 'slli' in stack_disasm and ', 13' in stack_disasm # linked getter selects 1<<13 bytes
if diag:
 body=subprocess.check_output([prefix+'objdump','-d','--disassemble=_ZN7route_x7endTurnEm',str(elf)],text=True)
 for name in ['heap_caps_get_free_size','heap_caps_get_minimum_free_size','heap_caps_get_largest_free_block','uxTaskGetStackHighWaterMark','esp_timer_get_time']:
  assert name in body,name
 tickbody=subprocess.check_output([prefix+'objdump','-d','--disassemble=_ZN7route_u4tickEm',str(elf)],text=True)
 assert '_ZN7route_x9beginTurnEv' in tickbody and '_ZN7route_x7endTurnEm' in tickbody
 r['measurement_disassembly']=body;r['instrumented_tick_disassembly']=tickbody

assert 'route_b::key(unsigned long long, unsigned short, route_b::Id&, unsigned char)' in symbols
r['shortcut_delta_pin']=pin
r['http_delta_pin']=http_pin
assert 'execution::BoundedGuard::BoundedGuard(execution::Owner)' in symbols
assert 'execution::detail::statsMux' in symbols
assert 'led_return::service' in symbols and 'led_return::observe' in symbols and 'route_u::stopWithStatus' in symbols
assert '_ZN10led_return7serviceEy' in loop_disasm or '_ZN10led_return7serviceEx' in loop_disasm
r['stop_led_source_pins']=[json.loads((ROOT/'docs'/p).read_text()) for p in ['stop-ui-source-manifest.json','led-return-source-manifest.json','caps-queue-source-manifest.json','led-feedback-source-manifest.json','caps-duration-source-manifest.json','mac-caps-source-manifest.json','caps-stop-source-manifest.json']]
wait_body=subprocess.check_output([prefix+'objdump','-d','--disassemble=_ZN9execution4takeEb',str(elf)],text=True)
assert 'xQueueTakeMutexRecursive' in wait_body and re.search(r'movi(?:\.n)?\s+a11, 0',wait_body) and re.search(r'movi(?:\.n)?\s+a11, 5',wait_body)
assert wait_body.index('vPortExitCritical')<wait_body.index('a11, 5')
r['bounded_wait_disassembly']=wait_body;r['verified_http_wait_ticks']=5
assert 'statusCapturedForTest' not in symbols
assert 'contendedForTest' not in symbols
r['diagnostic_symbols']=[line for line in symbols.splitlines() if any(x in line for x in ['route_x::','heap_caps_get_','uxTaskGetStackHighWaterMark','esp_timer_get_time'])]
r['compiled_selector']='EVILDUCK_ROUTE_B_DIAGNOSTICS' if diag else 'default off'
for name in ['evilduck_hid_route_diagnostic','evilduck_hid_keyboard_identity','evilduck_hid_input_diagnostic','evilduck_usb_feedback_lifecycle']:
 assert sum(line.endswith(' T '+name) for line in symbols.splitlines())==1,name
r['feedback_boundary_disassembly']={}
for name,hook in [('tud_hid_set_report_cb','evilduck_hid_route_diagnostic'),('tud_hid_report_complete_cb','evilduck_hid_input_diagnostic'),('tud_mount_cb','evilduck_usb_feedback_lifecycle'),('tud_umount_cb','evilduck_usb_feedback_lifecycle'),('tud_suspend_cb','evilduck_usb_feedback_lifecycle'),('tud_resume_cb','evilduck_usb_feedback_lifecycle')]:
 body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+name,str(elf)],text=True)
 if name=='tud_hid_set_report_cb':
  outlined='_ZZ21tud_hid_set_report_cbENKUlhhE_clEhh'
  assert outlined in body
  helper=subprocess.check_output([prefix+'objdump','-d','--disassemble='+outlined,str(elf)],text=True)
  assert hook in helper
  body+='\nVerified direct call to the pinned compiler outlined diagnostic helper:\n'+helper
 else:assert hook in body,(name,hook)
 r['feedback_boundary_disassembly'][name]=body
for e in entries:
 if pathlib.Path(e['file']).is_relative_to(build/'sketch') or pathlib.Path(e['file']).name=='USBHID.cpp':
  assert '-DEVILDUCK_VERIFIED_LED_DIAGNOSTICS=1' in e['arguments']
assert 'route_u::requestCapsTrial' in symbols and 'caps_trial::submitted' in symbols and 'caps_trial::completed' in symbols
r['profile']='OPT-IN MAC CAPS TIMING; NEW APPLICATION PHYSICALLY UNVERIFIED'
r['caps_trial_source_pin']=json.loads((ROOT/'docs/caps-stop-source-manifest.json').read_text())
r['feedback_boundary_verified']=True
r['feedback_core_patch_sha256']=sha(ROOT/'tests/led_feedback/core-diagnostics.patch')
r['caps_trial_link_edges']={}
for name,target in [('_ZN7route_u4tickEm','caps_trial'),('_ZN13feedback_diag9submittedEbby','caps_trial'),('evilduck_hid_input_diagnostic','caps_trial'),('_ZN3com6updateEv','capsDwellMs')]:
 body=subprocess.check_output([prefix+'objdump','-d','-C','--disassemble='+name,str(elf)],text=True)
 # objdump --disassemble uses demangled symbol matching with -C; use raw names instead.
 body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+name,str(elf)],text=True)
 assert target in body,(name,target)
 r['caps_trial_link_edges'][name]=body
assert b'CAPS-STOP-TRACE-20261019-v1' in elf.read_bytes()
assert 'hid_trace::note' in symbols and 'hid_trace::read' in symbols
assert sum(line.endswith(' T tud_hid_report_failed_cb') for line in symbols.splitlines())==1
r['profile']='BOUNDED CAPS STOP TRACE; PHYSICAL CAUSE UNRESOLVED'
r['trace_failure_callback_disassembly']=subprocess.check_output([prefix+'objdump','-d','--disassemble=tud_hid_report_failed_cb',str(elf)],text=True)
assert 'hid_trace' in r['trace_failure_callback_disassembly']
a.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS linked closure',len(inputs),'inputs',len(response),'response files',len(scripts),'scripts')
