#!/usr/bin/env python3
"""Real patched service bodies; lower File/network/NVS/USB are memory-only fakes."""
import pathlib,sys,argparse,json,subprocess,hashlib
sys.dont_write_bytecode=True
from prepare_sources import ROOT,load,prepare,native_sources,sha
U=load(ROOT/'tests/stage28u/run_tests.py','u_runner')
def command(exe,scratch,main,opt=True):
 cmd=U.command(exe,scratch,main,opt=opt)
 cmd=[x.replace(str(ROOT/'tests/stage28u'),str(ROOT/'tests/stage28v')) for x in cmd]
 if opt:
  cmd=[x.replace(str(ROOT/'tests/stage28t/allocations.cpp'),str(ROOT/'tests/stage28v/allocations.cpp')) for x in cmd if not x.endswith('/msc_platform.cpp')]
  cmd[1:1]=['-DEVILDUCK_CONTROLLED_START=1','-DCONFIG_TINYUSB_MSC_ENABLED=1','-DCONFIG_TINYUSB_MSC_BUFSIZE=512','-Wno-unused-function','-Wno-unused-variable','-I'+str(ROOT/'tests/stage28v/mocks'),'-I/workspace/tooling/stage19-sdk-source/components/nvs_flash/include','-I/workspace/tooling/stage19-sdk-source/components/esp_common/include','-I'+str(ROOT/'tests/stage19/mocks')]
  cmd[cmd.index('-o'):cmd.index('-o')]=[str(scratch/n) for n in ['settings.cpp','storage.cpp','spiffs.cpp','sd_card.cpp','usb_msc.cpp','led.cpp','script_library.cpp']]+[str(ROOT/'tests/stage28v/nvs_fixture.cpp')]
 return cmd
def main():
 p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists() and not a.build_dir.resolve().is_relative_to(ROOT);a.build_dir.mkdir()
 s=prepare(a.build_dir/'sources');extract=native_sources(s);cmd=command(a.build_dir/'native',s,ROOT/'tests/stage28v/test_main.cpp');subprocess.run(cmd,check=True)
 rows=[]
 for i in range(1,57):
  row=U.execute(a.build_dir/'native','V%02d'%i);rows.append(row);print(row['id'],row['status'],row['stderr'],flush=True)
 neg=list(cmd);neg.insert(1,'-DSTAGE28V_NEGATIVE_CONTROL');neg[neg.index('-o')+1]=str(a.build_dir/'negative');subprocess.run(neg,check=True);nr=U.execute(a.build_dir/'negative','V01');assert nr['exit']==1 and 'deliberate negative control' in nr['stderr']
 report=dict(counts={x:sum(r['status']==x for r in rows) for x in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,negative_control=nr,commands=[cmd,neg],web_actual_body_extractions=extract,sanitizers=U.T.ENV['ASAN_OPTIONS']+'; '+U.T.ENV['UBSAN_OPTIONS'],hardware=False,firmware=False)
 a.results.write_text(json.dumps(report,indent=2)+'\n');print(report['counts'],report['assertions']);return bool(report['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
