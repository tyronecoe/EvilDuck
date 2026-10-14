#!/usr/bin/env python3
"""Native actual selected DCD + actual stack; explicitly simulated registers/OS."""
import argparse,gzip,hashlib,json,os,pathlib,shutil,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',type=pathlib.Path,required=True);p.add_argument('--plain-root',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args()
for v in (a.build_dir,a.results):assert not v.exists() and not v.resolve().is_relative_to(ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((ROOT/'docs/stage28p-source-and-boundary-manifest.json').read_text());altered={r['file']:r['output_sha256'] for r in m['adapted_files']}
assert sha(ROOT/'tests/stage28p/native-io-adaptation.patch')==m['patch_sha256']
for row in m['original_tinyusb_inputs']+m['new_inputs']:
 f=row.get('tree_file',row['file']);assert sha(a.source_root/f)==altered.get(f,row['sha256']),f
 if f!='src/portable/synopsys/dwc2/dwc2_common.h':assert sha(a.plain_root/f)==row['sha256']
assert sha(a.plain_root/'src/portable/synopsys/dwc2/dwc2_common.h')==m['plain_platform_header_sha256']
cc=shutil.which('gcc');gc=shutil.which('gcov');assert cc and gc
a.build_dir.mkdir();commands=[];env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1');flags=['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','--coverage']
def build(name,source,negative=False):
 files=[source/'src'/f for f in ('portable/synopsys/dwc2/dwc2_common.c','tusb.c','device/usbd.c','device/usbd_control.c','class/hid/hid_device.c','common/tusb_fifo.c')]+[ROOT/'tests/stage28p'/f for f in ('driver_unit.c','boundary.c','platform.c','test_controller.c')]
 cmd=[cc]+flags+(['-DSTAGE28P_NEGATIVE_CONTROL=1'] if negative else [])+['-I',str(ROOT/'tests/stage28p'),'-I',str(source/'builder'),'-I',str(source/'src'),'-I',str(source/'src/portable/synopsys/dwc2')]+list(map(str,files))+['-o',str(a.build_dir/name)];commands.append(cmd);subprocess.run(cmd,env=env,check=True,timeout=180);return a.build_dir/name
exe=build('controller',a.source_root);plain=build('plain-controller',a.plain_root);rows=[]
for i in list(range(1,27))+list(range(30,37)):
 case='P%02d'%i;d=a.build_dir/case;d.mkdir();e=dict(env,GCOV_PREFIX=str(d),GCOV_PREFIX_STRIP=str(len(a.build_dir.resolve().parts)-1));cmd=[str(exe),str(i)];commands.append(cmd);r=subprocess.run(cmd,env=e,capture_output=True,text=True,timeout=3)
 if r.returncode or r.stderr:raise AssertionError(case+' failed '+r.stderr)
 row=json.loads(r.stdout);assert row['id']==case and row['status']=='PASS';functions=[]
 for note in a.build_dir.glob('controller-*.gcno'):
  shutil.copyfile(note,d/note.name);cmd=[gc,'-j','-f',str(d/note.name)];commands.append(cmd);cov=subprocess.run(cmd,cwd=d,capture_output=True,text=True,timeout=30);assert cov.returncode==0,cov.stderr
 for f in d.glob('*.gcov.json.gz'):
  report=json.loads(gzip.decompress(f.read_bytes()))
  for file in report['files']:
   path=pathlib.Path(file['file'])
   if path.is_relative_to(a.source_root):functions.extend(dict(file=str(path.relative_to(a.source_root)),name=v['name'],count=v['execution_count'],start_line=v['start_line'],end_line=v['end_line']) for v in file['functions'] if v['execution_count']>0)
 names={v['name'] for v in functions};assert {'dcd_init','dcd_int_handler','handle_bus_reset','handle_enum_done','dcd_edpt_open','dwc2_core_init','dfifo_alloc'}.issubset(names),names
 if i not in [23,25,26,31]:assert 'dcd_edpt_xfer' in names
 if row['callback_count']:assert 'hidd_xfer_cb' in names
 if i==30:assert 'tu_fifo_read_n_const_addr_full_words' in names
 if i in [1,4,5,7,8,10,11,20,21,22,24,35]:assert 'handle_epin_slave' in names
 row['driver_call_counts']={v['name']:v['count'] for v in functions if v['file']=='builder/dcd_dwc2.c'}
 row.update(exit=r.returncode,stderr=r.stderr,executed_vendor_functions=functions,classification='software observation PASS; strict success-plus-retirement contract NOT SATISFIED')
 rows.append(row);print('PASS observation',case,row['assertions'])
watchdogs=[]
for i,program,expected in [(27,exe,'WATCHDOG entered original dcd_edpt_stall with INEPNE=0'),(28,exe,'WATCHDOG entered original close_all with TXFFLSH held'),(29,plain,'WATCHDOG genuine common phy reached before reset loop')]:
 cmd=[str(program),str(i)];commands.append(cmd)
 try:subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=1);raise AssertionError('Expected unresolved original wait did not timeout')
 except subprocess.TimeoutExpired as ex:
  out=ex.stdout.decode() if isinstance(ex.stdout,bytes) else ex.stdout or '';err=ex.stderr.decode() if isinstance(ex.stderr,bytes) else ex.stderr or '';assert expected in out and not err
  watchdogs.append(dict(id='P%02d'%i,classification='EXPECTED WATCHDOG observation; not a contract PASS; assertions excluded',timeout_seconds=1,stdout=out,stderr=err,coverage='unavailable after forced process termination; call marker/source evidence only',sanitizers='no diagnostics before kill; leak cleanup not performed/claimed'))
neg=build('negative',a.source_root,True);cmd=[str(neg),'1'];commands.append(cmd);r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=3);assert r.returncode==1 and 'FAIL line=' in r.stderr
inputs=[dict(file=str(f).replace(str(ROOT),'<project-root>'),sha256=sha(f)) for f in sorted((ROOT/'tests/stage28p').glob('*')) if f.is_file()]
report={'primary':{'counts':{'PASS':len(rows),'FAIL':0},'assertions':sum(v['assertions'] for v in rows),'results':rows},'watchdogs':watchdogs,'negative_control':{'exit':r.returncode,'stderr':r.stderr,'excluded':True},'manifest_sha256':sha(ROOT/'docs/stage28p-source-and-boundary-manifest.json'),'fixtures':inputs,'flags':flags,'commands':commands,'compiler':subprocess.check_output([cc,'--version'],text=True),'compiler_sha256':sha(pathlib.Path(cc)),'gcov':subprocess.check_output([gc,'--version'],text=True),'sanitizers':{'ASan':'clean completed cases','UBSan':'clean completed cases','leak_detection':'detect_leaks=1 clean completed cases; watchdog cleanup unmeasured'},'driver_body':'byte-identical selected builder C; diagnostic wrapper reads private state without changing it or static declarations','native_adaptation':'two pinned common files; fake platform/OS; no physical MMIO','prototype':'DEFERRED no safe original IRQ identity or validated retirement before descriptor reuse','blocked':['authentic completion C/Q and ID exhaustion in actual DCD','bounded real spinlock/ISR/concurrency','per-endpoint hardware retire and event-publication fence','RXFLVL/OUT payload/FIFO-pop/W1C/DMA/full hardware semantics','full Arduino core/FreeRTOS/CDC/MSC integration','target ABI/build and all physical host/controller behavior']}
a.results.write_text(json.dumps(report,indent=2).replace(str(ROOT),'<project-root>')+'\n');print(json.dumps({'primary':report['primary']['counts'],'assertions':report['primary']['assertions'],'expected_watchdogs':len(watchdogs),'negative_exit':r.returncode}))
