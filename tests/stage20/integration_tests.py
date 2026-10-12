#!/usr/bin/env python3
"""Native descriptor ABI/candidate archive evidence and final production guards, offline."""
import argparse,hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from patched_core import check_sources,sha
from verify_patched_firmware import verify
from s3_validation import validate_csv
ROWS=[];ASSERTIONS=0
def check(x,m):
 global ASSERTIONS
 ASSERTIONS+=1
 if not x:raise AssertionError(m)
def case(n,fn):
 before=ASSERTIONS
 try:fn();s='PASS';e=''
 except Exception as ex:s='FAIL';e=str(ex)
 ROWS.append(dict(name=n,status=s,assertions=ASSERTIONS-before,error=e));print(s,n,e,flush=True)
def main():
 p=argparse.ArgumentParser()
 for name in ['original-core','normal-core','safe-core','normal-build','safe-build','results']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();check_sources(a.original_core)
 def layout():
  entries=json.loads((a.normal_build/'compile_commands.json').read_text());e=next(e for e in entries if Path(e['file']).name=='settings.cpp');cmd=list(e['arguments'])
  with tempfile.TemporaryDirectory(prefix='evilduck-native-abi-') as t:
   t=Path(t);source=t/'abi.cpp';source.write_text('#include <stddef.h>\n#include <esp_partition.h>\nstatic_assert(offsetof(esp_partition_t, readonly)==42,"SDK descriptor ABI changed");\n')
   cmd[cmd.index(e['file'])]=str(source);cmd[cmd.index('-o')+1]=str(t/'abi.o');subprocess.run(cmd,cwd=e['directory'],capture_output=True,text=True,check=True);check((t/'abi.o').exists(),'native installed descriptor compiled')
 case('native_readonly_descriptor_offset',layout)
 def binary():
  tools=a.original_core.resolve().parents[2]/'tools';archive=tools/'esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3/lib/libesp_partition.a';pin=json.loads((ROOT/'docs/stage20-partition-archive.json').read_text());check(sha(archive)==pin['archive_sha256'],'actual partition archive hash')
  objdump=tools/'esp-x32/2411/bin/xtensa-esp32s3-elf-objdump';check(sha(objdump)==pin['objdump_sha256'],'inspector identity')
  for row in pin['functions']:
   text=subprocess.run([str(objdump),'-drC','--disassemble='+row['symbol'],str(archive)],capture_output=True,text=True,check=True).stdout
   check(hashlib.sha256(text.encode()).hexdigest()==row['disassembly_sha256'],'actual archive disassembly unchanged')
   body=text.split('<'+row['symbol']+'>:',1)[1];check(re.search(r'l8ui\s+a9, a2, 42',body) and 'movi\ta2, 0x10d' in body and 'bnez.n\ta9' in body,'compiled readonly test/NOT_ALLOWED branch present')
 case('pinned_archive_readonly_guard_evidence',binary)
 def final():
  for core,build in [(a.normal_core,a.normal_build),(a.safe_core,a.safe_build)]:j=verify(core,build);check(j['checked_settings_persistence'] is True and j['sdk_nvs_immutable'] is False,'source+ELF checked API, no fake immutability')
 case('final_checked_persistence_provenance',final)
 def table():
  validate_csv(a.original_core)
  original=subprocess.run(['git','show','524d643a12af05e4efd9da509eae274ec43959a6:EvilDuckS3/partitions.csv'],cwd=ROOT,capture_output=True,check=True).stdout;check(original==(ROOT/'EvilDuckS3/partitions.csv').read_bytes(),'no readonly flag/table changes')
 case('partition_policy_unchanged',table)
 out=dict(results=ROWS,counts={s:sum(r['status']==s for r in ROWS) for s in ['PASS','FAIL']},assertions=ASSERTIONS,sdk_binary_executed=False,hardware_access=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
