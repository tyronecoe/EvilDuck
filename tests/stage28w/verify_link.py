#!/usr/bin/env python3
"""Post-link read-only evidence closure, including linker response/archive inputs."""
import pathlib,json,argparse,subprocess,shlex,re,sys
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha,frameworks,manifest
sys.path.insert(0,str(ROOT/'tools'))
from patched_core import check_sources
from s3_validation import validate_build
p=argparse.ArgumentParser();p.add_argument('--build-root',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();assert not a.output.exists();r=json.loads((a.build_root/'report.json').read_text());assert r['status']=='PASS';build=a.build_root/'build';elf=build/'EvilDuckS3.ino.elf';core=pathlib.Path(r['provenance']['core']);assert check_sources(core,True)==r['core_pin'];assert sha(elf)==r['provenance']['elf_sha256'];assert sha(build/'EvilDuckS3.ino.bin')==r['report']['application_sha256']
for x in r['source_inventory']:assert sha(a.build_root/'candidate'/x['file'])==x['sha256'],x['file']
for x in manifest()['outputs']:
 if x['file']!='platform.cpp':assert sha(a.build_root/'candidate/EvilDuckS3'/x['file'])==x['sha256']
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
r['linked_input_hashes']=list(inputs.values());r['link_response_files']=response;r['linker']=dict(file=str(linker),sha256=sha(linker));r['linker_scripts']=scripts;r['verified_w_marker']=not off;r['loop_disassembly']=loop_disasm;r['loop_stack_selection_disassembly']=stack_disasm;r['verification_scope']='actual linked ELF/BIN and pinned source/archive identity; not FreeRTOS, AsyncTCP or physical execution';r['compiled_source_checks']=compiled_source_checks;r['duckscript_update_disassembly']=update_disasm;r['post_link_verifier_sha256']=sha(pathlib.Path(__file__))
a.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS linked closure',len(inputs),'inputs',len(response),'response files',len(scripts),'scripts')
