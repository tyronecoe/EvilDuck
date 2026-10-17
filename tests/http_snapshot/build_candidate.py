#!/usr/bin/env python3
"""Offline controlled link only. No upload, port, board, flash or OTA interface."""
import argparse,pathlib,sys,json,subprocess,shutil,re,hashlib,shlex
sys.dont_write_bytecode=True
from prepare_sources import ROOT,prepare,sha,frameworks,manifest,overlay
sys.path.insert(0,str(ROOT/'tools'))
import patched_core,s3_validation
from startup_decode import load_verifier
verify_patched_firmware=load_verifier(ROOT)

def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=pathlib.Path,required=True);p.add_argument('--config',type=pathlib.Path,required=True);p.add_argument('--baseline-build',type=pathlib.Path,required=True);p.add_argument('--arduino-cli',type=pathlib.Path,required=True);p.add_argument('--verify-existing',action='store_true',help='Resume only failed provenance verification of an already clean compiled build');p.add_argument('--selector-off',action='store_true');p.add_argument('--diagnostics-off',action='store_true');p.add_argument('--jobs',type=int,default=2);a=p.parse_args();assert a.jobs>0 and (a.verify_existing or not a.output_dir.exists()) and not a.output_dir.resolve().is_relative_to(ROOT);a.output_dir.mkdir(exist_ok=a.verify_existing)
 assert not a.selector_off, 'shortcut candidate requires explicit Route B build'
 old=json.loads((a.baseline_build/'stage16-link-provenance.json').read_text());core=pathlib.Path(old['core']);pin=patched_core.check_sources(core,True);assert pin==json.loads((ROOT/'docs/stage28v-target-object-results.json').read_text())['pin']
 cfg=json.loads(a.config.read_text());user=pathlib.Path(cfg['directories']['user']);library_pins=frameworks(user)
 cfg['build_cache']={'path':str(a.output_dir/'cache')};config=a.output_dir/'arduino-cli.json';config.write_text(json.dumps(cfg,indent=2)+'\n')
 # Copy only public reviewed source, never installed dependencies or owner data.
 candidate=a.output_dir/'candidate';sketch=candidate/'EvilDuckS3'
 if not a.verify_existing:
  scratch=prepare(a.output_dir/'prepared');candidate=a.output_dir/'candidate';sketch=candidate/'EvilDuckS3';shutil.copytree(ROOT/'EvilDuckS3',sketch)
  for row in manifest()['outputs']:
   if row['file']!='platform.cpp':shutil.copyfile(scratch/row['file'],sketch/row['file'])
  if not a.selector_off:
   for row in manifest()['runtime_inputs']:shutil.copyfile(ROOT/row['file'],sketch/pathlib.Path(row['file']).name)
   for name in ['bridge.cpp','bridge.h','keyboard.cpp','keyboard.h']:shutil.copyfile(ROOT/'language_preview'/name,sketch/name)
  overlay(sketch)
 source_inventory=[dict(file=str(f.relative_to(candidate)),size=f.stat().st_size,sha256=sha(f)) for f in sorted(candidate.rglob('*')) if f.is_file()]
 # Existing tool validators run against explicitly reviewed candidate source ROOT;
 # dependency verifier retains its original ROOT and exact protected-core hashes.
 s3_validation.ROOT=candidate;verify_patched_firmware.ROOT=candidate
 flags='-DEVILDUCK_ROUTE_B_STATUS_HARDENING=1 -DEVILDUCK_ROUTE_B_TRANSIENT_SHORTCUTS=1 -DEVILDUCK_VERIFIED_HID_ROUTING=1 -DEVILDUCK_VERIFIED_NVS_PRESERVATION=1 -DEVILDUCK_CONTROLLED_START=1 -fstack-usage'
 if not a.selector_off:flags+=' -DEVILDUCK_PORTABLE_ROUTE_B'
 if not a.diagnostics_off:
  assert not a.selector_off;flags+=' -DEVILDUCK_ROUTE_B_DIAGNOSTICS'
 flags+=' -I'+str(sketch)
 build=a.output_dir/'build';cli=[str(a.arduino_cli),'--config-file',str(config)];args=['compile','--fqbn',s3_validation.FQBN,'--build-path',str(build),'--jobs',str(a.jobs),'--build-property','upload.maximum_size='+str(s3_validation.APP_BYTES),'--build-property','recipe.hooks.objcopy.postobjcopy.3.pattern=','--build-property','compiler.cpp.extra_flags='+flags]
 r=subprocess.run(cli+args+['--show-properties=expanded',str(sketch)],capture_output=True,text=True,check=True);props=dict(x.split('=',1) for x in r.stdout.splitlines() if '=' in x);assert pathlib.Path(props['runtime.platform.path']).resolve()==core.resolve();s3_validation.validate_properties(props);s3_validation.validate_csv(core,sketch/'partitions.csv')
 command=cli+args+['--clean','--verbose',str(sketch)]
 if a.verify_existing:
  assert (build/'s3-build-properties.json').is_file() and not (a.output_dir/'report.json').exists()
  stored=json.loads((build/'s3-build-properties.json').read_text());volatile={'extra.time.local','extra.time.utc'}
  assert {k:v for k,v in stored.items() if k not in volatile}=={k:v for k,v in props.items() if k not in volatile}
  props=stored
  log=(build/'s3-build.log').read_text();run=subprocess.CompletedProcess(command,0)
 else:
  run=subprocess.run(command,capture_output=True,text=True);build.mkdir(parents=True,exist_ok=True);log=run.stdout+run.stderr;(build/'s3-build.log').write_text(log)
 print('Arduino compile exit',run.returncode,flush=True)
 if run.returncode:
  failure=dict(status='FAIL',command=command,exit=run.returncode,source_inventory=source_inventory,core_pin=pin,framework_pins=library_pins,log_sha256=sha(build/'s3-build.log'),hardware=False)
  (a.output_dir/'report.json').write_text(json.dumps(failure,indent=2)+'\n');print(log[-12000:]);return 1
 (build/'s3-build-properties.json').write_text(json.dumps(props,indent=2)+'\n');report=s3_validation.validate_build(core,build)
 program=re.search(r'Sketch uses (\d+) bytes .*Maximum is (\d+) bytes',log);ram=re.search(r'Global variables use (\d+) bytes .*Maximum is (\d+) bytes',log);assert program and ram and int(program[2])==s3_validation.APP_BYTES
 report.update(compiler_program_bytes=int(program[1]),static_ram_bytes=int(ram[1]),compiler_ram_maximum_bytes=int(ram[2]),deployment_safe_start=False,controlled_normal_start=True,verified_cpp_extra_flags=flags,merged_image_for_migration=False)
 (build/'s3-build-report.json').write_text(json.dumps(report,indent=2)+'\n')
 provenance=verify_patched_firmware.verify(core,build)
 entries=json.loads((build/'compile_commands.json').read_text());entry=next(e for e in entries if pathlib.Path(e['file']).name=='hid_backend.cpp');compiler=pathlib.Path(entry['arguments'][0]);assert sha(compiler)==old['compiler_sha256'];prefix=str(compiler).rsplit('g++',1)[0];elf=build/'EvilDuckS3.ino.elf'
 symbols=subprocess.check_output([prefix+'nm','-C','-S','--defined-only',str(elf)],text=True);(build/'stage28x-symbols.txt').write_text(symbols)
 required=['route_u::requestStart','route_u::tick','route_u::enterMutation','native_b::Adapter::step','ds_preview::CompileSession::step','route_b::drive','backend_b::acquire']
 for symbol in required:assert (symbol in symbols)==(not a.selector_off),symbol
 for symbol in ['route_x::beginTurn','route_x::endTurn','route_x::snapshot','route_x::format']:
  assert (symbol in symbols)==(not a.diagnostics_off),symbol
 for symbol in ['std::thread','__emutls']:assert symbol not in symbols,symbol
 # All selected application CPP commands must carry the same explicit profile.
 for e in entries:
  if pathlib.Path(e['file']).is_relative_to(build/'sketch'):
   assert '-DEVILDUCK_CONTROLLED_START=1' in e['arguments'];assert ('-DEVILDUCK_PORTABLE_ROUTE_B' in e['arguments'])==(not a.selector_off)
 # Existing verifier checked startup, exact candidate backend/settings/storage,
 # protected HID/NVS core, linked callbacks and regenerated BIN byte equality.
 maptext=(build/'EvilDuckS3.ino.map').read_text();assert 'USBHID.cpp.o' in maptext
 library_compiles=[]
 for e in entries:
  f=pathlib.Path(e['file'])
  if any('/libraries/'+x['directory']+'/' in str(f) for x in manifest()['framework_libraries']):library_compiles.append(dict(source=str(f),sha256=sha(f),object=str(e['arguments'][e['arguments'].index('-o')+1])))
 assert any('/ESP_Async_WebServer/' in x['source'] for x in library_compiles) and any('/Async_TCP/' in x['source'] for x in library_compiles)
 # Capture actual verbose link invocation, its inputs and identities.
 links=[shlex.split(line) for line in log.splitlines() if ' -o ' in line and '.ino.elf' in line and 'g++' in line and ' -c ' not in line];assert len(links)==1
 link=links[0];inputs=[]
 for arg in link:
  if pathlib.Path(arg).is_file() and (arg.endswith(('.a','.o','.ld')) or arg==link[0]):inputs.append(dict(file=arg,size=pathlib.Path(arg).stat().st_size,sha256=sha(pathlib.Path(arg))))
 for f in sorted(build.rglob('*.a')):
  if str(f) not in {x['file'] for x in inputs}:inputs.append(dict(file=str(f),size=f.stat().st_size,sha256=sha(f)))
 # -l libraries are located by exact SDK archive basename and map references.
 sdk=core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3'
 for f in sorted(sdk.rglob('*.a')):
  if str(f) in maptext or '-l'+f.stem[3:] in link:inputs.append(dict(file=str(f),size=f.stat().st_size,sha256=sha(f)))
 frames=[]
 for f in build.rglob('*.su'):
  for line in f.read_text().splitlines():
   try:name,n,kind=line.rsplit('\t',2);frames.append(dict(symbol=name,bytes=int(n),kind=kind))
   except ValueError:pass
 artifacts=[dict(file=str(f.relative_to(build)),size=f.stat().st_size,sha256=sha(f)) for f in sorted(build.iterdir()) if f.suffix in ['.elf','.map','.bin']]
 final=dict(verifier_adapter_sha256=sha(ROOT/'tests/http_snapshot/startup_decode.py'),base_verifier_sha256=sha(ROOT/'tools/verify_patched_firmware.py'),verification_resumed=a.verify_existing,status='PASS',profile='controlled legacy-default selector-off' if a.selector_off else 'HTTP SNAPSHOT HARDENING CONTROLLED ROUTE B REVIEW ONLY',diagnostics_enabled=not a.diagnostics_off,source_inventory=source_inventory,command=command,report=report,provenance=provenance,framework_pins=library_pins,framework_compiles=library_compiles,link_command=link,linked_input_hashes=inputs,artifacts=artifacts,frames=frames,symbols=symbols,compiler_sha256=sha(compiler),core_pin=pin,physical=False,review_only=True,production_integration_approved=False)
 (a.output_dir/'report.json').write_text(json.dumps(final,indent=2)+'\n');assert patched_core.check_sources(core,True)==pin;assert frameworks(user)==library_pins
 print(json.dumps(report,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
