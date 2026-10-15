#!/usr/bin/env python3
"""Read-only evidence/range/scope checks. No board or installation interface."""
import pathlib,sys,json,hashlib,subprocess,stat,argparse,re
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha,manifest
BASE='606098b1158c216f7c5e205cd81debcb9661e04d';BRANCH='stage28x-instrumented-validation-candidate'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def scope():
 assert git('branch','--show-current').decode().strip()==BRANCH
 head=git('rev-parse','HEAD').decode().strip();assert head==BASE or git('rev-parse','HEAD^').decode().strip()==BASE
 old=[]
 for row in git('ls-tree','-rz',BASE).split(b'\0'):
  if not row:continue
  meta,name=row.split(b'\t');mode,kind,oid=meta.split();f=ROOT/name.decode();assert kind==b'blob' and not f.is_symlink();d=f.read_bytes();assert hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()==oid.decode(),name;assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755'),name;old.append(name.decode())
 assert len(old)==1349
 subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
 new=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old))
 assert all(n.startswith(('docs/stage28x-','tests/stage28x/')) and pathlib.Path(n).suffix not in ['.elf','.o','.bin','.uf2','.pyc'] for n in new),new
 for r in [manifest()['patch']]+manifest()['runtime_inputs']+manifest().get('audit_inputs',[]):assert sha(ROOT/r['file'])==r['sha256'],r['file']
 return dict(parent=BASE,head=head,historical_files_bytes_modes=len(old),frozen_stage26=235,new_files=[dict(file=n,size=(ROOT/n).stat().st_size,sha256=sha(ROOT/n)) for n in new if n!='docs/stage28x-integrity.json'])
def artifacts(root):
 r=json.loads((root/'report.json').read_text());assert r['status']=='PASS' and r['diagnostics_enabled'];build=root/'build'
 public=json.loads((ROOT/'review/stage26-installation/manifest.json').read_text());rows=[]
 for old in public['rows']:
  item=dict(old)
  if old['role'].startswith('app'):
   f=build/'EvilDuckS3.ino.bin';item.update(file=str(f),bytes=f.stat().st_size,sha256=sha(f),purpose='Identical Stage28X instrumented controlled application; explicit Route B selection only')
  elif old['role']=='bootloader':
   f=build/'EvilDuckS3.ino.bootloader.bin';item.update(file=str(f),bytes=f.stat().st_size,sha256=sha(f))
  elif old['role']=='partitions':
   f=build/'EvilDuckS3.ino.partitions.bin';item.update(file=str(f),bytes=f.stat().st_size,sha256=sha(f));assert item['sha256']==old['sha256']
  else:
   f=ROOT/'review/stage26-installation'/old['file'];assert sha(f)==old['sha256'] and f.stat().st_size==old['bytes'];item['file']=str(f)
  item.update(erase_start=item['offset']//4096*4096,erase_end_exclusive=(item['offset']+item['bytes']+4095)//4096*4096,authorized_for_flashing=False)
  rows.append(item)
 assert len(rows)==7
 # Only planned NVS replacement, never an implicit preservation promise or generated credential.
 rows.append(dict(role='nvs',file='OWNER-LOCAL fresh-nvs.bin NOT SUPPLIED',offset=0x9000,bytes=0x5000,sha256=None,erase_start=0x9000,erase_end_exclusive=0xe000,region_end_exclusive=0xe000,initial_write_planned=True,authorized_for_flashing=False,purpose='Explicit fresh private credentials; later separately approved provisioning'))
 for item in rows:
  start,end=item['erase_start'],item['erase_end_exclusive'];assert start%4096==end%4096==0 and start<=item['offset']<item['offset']+item['bytes']<=end<=item['region_end_exclusive']<=0x1000000
  if item['role']!='nvs':assert end<=0x9000 or start>=0xe000,'unintended NVS overlap'
 ordered=sorted(rows,key=lambda x:x['erase_start']);assert all(a['erase_end_exclusive']<=b['erase_start'] for a,b in zip(ordered,ordered[1:]))
 assert r['report']['application_bytes']>0x140000 if 'application_bytes' in r['report'] else (build/'EvilDuckS3.ino.bin').stat().st_size>0x140000
 return dict(label='REVIEW ONLY — NOT AUTHORIZED FOR FLASHING',migration_authorized=False,hardware=False,rows=rows,original_firmware_availability='OWNER CONFIRMED: AVAILABLE EXTERNALLY',private_nvs_verified=False,complete_x_installation_package_verified=False)
def sources(root):
 p=root/'candidate/EvilDuckS3';core=pathlib.Path(json.loads((root/'report.json').read_text())['provenance']['core']);sdk=core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3'
 queries={p/'coordinator.cpp':['requestStartImpl','route_x::admissionLocked','void stop()','void tick(','route_x::endTurn'],p/'diagnostics.cpp':['void beginTurn','void endTurn','Snapshot snapshot','size_t format'],p/'diagnostic_platform.h':['heap_caps_get_free_size','static_assert','uxTaskGetStackHighWaterMark'],p/'webserver.cpp':['static bool checkAuth','static void handleDiagnostics','static void handleStatus','static void onWsEvent'],p/'cli.cpp':['void parse(','void update()'],p/'EvilDuckS3.ino':['void setup()','void loop()'],core/'cores/esp32/main.cpp':['size_t getArduinoLoopTaskStackSize','void loopTask(','xTaskCreateUniversal'],sdk/'include/freertos/FreeRTOS-Kernel/portable/xtensa/include/freertos/portmacro.h':['#define portSTACK_TYPE'],sdk/'include/freertos/FreeRTOS-Kernel/include/freertos/task.h':['UBaseType_t uxTaskGetStackHighWaterMark('],sdk/'include/heap/include/esp_heap_caps.h':['size_t heap_caps_get_free_size','size_t heap_caps_get_minimum_free_size','size_t heap_caps_get_largest_free_block'],sdk/'include/esp_timer/include/esp_timer.h':['int64_t esp_timer_get_time(']}
 libs=pathlib.Path('/workspace/tooling/arduino/user/libraries');queries.update({libs/'Async_TCP/src/AsyncTCP.cpp':['class queue_mutex_guard','static TaskHandle_t _async_service_task_handle','static void _async_service_task','static bool _start_async_task','void AsyncTCP_detail::handle_async_event'],libs/'ESP_Async_WebServer/src/WebResponses.cpp':['AsyncBasicResponse::AsyncBasicResponse','AsyncFileResponse::AsyncFileResponse','AsyncProgmemResponse::AsyncProgmemResponse'],libs/'ESP_Async_WebServer/src/WebRequest.cpp':['AsyncWebServerRequest::~AsyncWebServerRequest','void AsyncWebServerRequest::_onDisconnect','AsyncWebServerRequest::beginResponse(int code']})
 out=[]
 for f,needles in queries.items():
  text=f.read_text().splitlines();hits=[]
  for needle in needles:
   found=[dict(line=i+1,text=t.strip()) for i,t in enumerate(text) if needle in t];assert found,(str(f),needle);hits.extend(found)
  out.append(dict(file=str(f),sha256=sha(f),anchors=hits))
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--build-root',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--before',type=pathlib.Path);p.add_argument('--after',type=pathlib.Path);a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
 result=scope()
 if a.build_root:result.update(source_evidence=sources(a.build_root),artifact_plan=artifacts(a.build_root))
 if a.before or a.after:
  assert a.before and a.after
  read=lambda p:dict(x.split()[::-1] for x in p.read_text().splitlines());before,after=read(a.before),read(a.after);assert len(before)==48 and all(after.get(k)==v for k,v in before.items());extra=set(after)-set(before);assert extra=={'refs/heads/'+BRANCH} and after[next(iter(extra))]==git('rev-parse','HEAD').decode().strip();result['publication']='PASS:48 previous refs unchanged; only X added'
 result.update(status='PASS',physical=False);a.output.write_text(json.dumps(result,indent=2)+'\n');print('PASS scope/ranges/provenance; no hardware')
