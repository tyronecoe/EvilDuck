#!/usr/bin/env python3
"""Flag serialization, source pins and actual archive/ELF evidence; no firmware candidate."""
import argparse, hashlib, json, re, struct, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from patched_core import check_sources,sha
from s3_validation import partition_tool,validate_csv,check_table
from verify_patched_firmware import verify as verify_firmware
from startup_reference_prepare import verify as verify_reference
from inspect_startup_elf import inventory
ROWS=[];ASSERTIONS=0
def check(v,m):
 global ASSERTIONS
 ASSERTIONS+=1
 if not v:raise AssertionError(m)
def case(n,fn):
 before=ASSERTIONS
 try:fn();s='PASS';e=''
 except Exception as ex:s='FAIL';e=str(ex)
 ROWS.append(dict(name=n,status=s,assertions=ASSERTIONS-before,error=e));print(s,n,e,flush=True)
def rejects(fn):
 try:fn()
 except (ValueError,OSError):check(True,'rejected');return
 raise AssertionError('unexpected acceptance')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['original-core','normal-core','safe-core','normal-build','safe-build','reference-source','results']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();check_sources(a.original_core);references=verify_reference(a.reference_source)
 tool=partition_tool(a.original_core);tools=a.original_core.resolve().parents[2]/'tools';sdk=tools/'esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3';objdump=tools/'esp-x32/2411/bin/xtensa-esp32s3-elf-objdump'
 evidence=dict(archives=[],source_reference_pin='docs/stage21-reference-pin.json',source_binary_equivalence_verified=False,experimental_firmware_created=False,hardware_access=False)
 def flags():
  original=(ROOT/'EvilDuckS3/partitions.csv').read_text();table=tool.PartitionTable.from_csv(original);check_table(table)
  lines=[]
  for line in original.splitlines():
   if line.startswith('nvs,'):fields=line.split(',');fields[-1]='readonly';line=','.join(fields)
   lines.append(line)
  experiment=tool.PartitionTable.from_csv('\n'.join(lines));experiment.verify();data=experiment.to_binary();decoded=tool.PartitionTable.from_binary(data)
  check(decoded[0].readonly is True and not decoded[0].encrypted,'official tool encodes readonly NVS')
  check(struct.unpack_from('<I',data,28)[0]==2,'native table readonly flag bit1')
  check(all((x.name,x.type,x.subtype,x.offset,x.size)==(y.name,y.type,y.subtype,y.offset,y.size) for x,y in zip(table,decoded)),'experimental flag preserves all approved geometry')
  check(all(not x.readonly for x in decoded[1:]),'only NVS flagged')
  rejects(lambda:check_table(decoded))
  with tempfile.TemporaryDirectory(prefix='stage21-test-table-') as t:
   path=Path(t)/'EXPERIMENTAL-NOT-FOR-DEPLOYMENT.csv';path.write_text('\n'.join(lines));rejects(lambda:validate_csv(a.original_core,path))
  check((ROOT/'EvilDuckS3/partitions.csv').read_text()==original,'approved CSV untouched')
  evidence['experimental_table_sha256']=hashlib.sha256(data).hexdigest();evidence['experimental_table_published']=False
 case('readonly_flag_binary_roundtrip_and_production_rejection',flags)
 def header():
  text=(a.reference_source/'components/bootloader_support/include/esp_flash_partitions.h').read_text()
  check('#define PART_FLAG_READONLY (1<<1)' in text,'immutable source defines flag bit1')
 case('readonly_flag_official_source_identity',header)
 def native():
  build=json.loads((a.normal_build/'compile_commands.json').read_text());entry=next(e for e in build if Path(e['file']).name=='settings.cpp');cmd=list(entry['arguments'])
  with tempfile.TemporaryDirectory(prefix='stage21-native-abi-') as t:
   t=Path(t);src=t/'check.cpp';src.write_text('#include <stddef.h>\n#include <esp_partition.h>\nstatic_assert(offsetof(esp_partition_t,readonly)==42,"readonly ABI");\n')
   cmd[cmd.index(entry['file'])]=str(src);cmd[cmd.index('-o')+1]=str(t/'out.o');subprocess.run(cmd,cwd=entry['directory'],capture_output=True,check=True);check((t/'out.o').exists(),'actual target header/ABI compiled')
 case('actual_native_readonly_descriptor_abi',native)
 def archive():
  selected=[(sdk/'lib/libesp_partition.a',['esp_partition_write','esp_partition_write_raw','esp_partition_erase_range','ensure_partitions_loaded$part$0','esp_partition_is_flash_region_writable']), (sdk/'lib/libnvs_flash.a',['_ZN3nvs12NVSPartition12get_readonlyEv','nvs_flash_init','nvs_flash_init_partition','_ZN3nvs11PageManager4loadEPNS_9PartitionEmm']), (sdk/'qio_qspi/libesp_system.a',['start_cpu0']), (sdk/'lib/libapp_update.a',['esp_ota_mark_app_valid_cancel_rollback']), (sdk/'qio_qspi/libspi_flash.a',['main_flash_region_protected','esp_flash_write','esp_flash_erase_region','esp_flash_app_enable_os_functions','esp_flash_set_dangerous_write_protection'])]
  for path,symbols in selected:
   row=dict(path=str(path.relative_to(sdk)),sha256=sha(path),functions=[])
   for symbol in symbols:
    r=subprocess.run([str(objdump),'-dr','--disassemble='+symbol,str(path)],capture_output=True,text=True,check=True)
    # Symbol may be local/mangled differently: record absence, never fabricate body.
    present=('<'+symbol+'>:') in r.stdout
    row['functions'].append(dict(symbol=symbol,present=present,disassembly_sha256=hashlib.sha256(r.stdout.encode()).hexdigest()))
    if symbol in ('esp_partition_write','esp_partition_write_raw','esp_partition_erase_range'):
     check(present and re.search(r'l8ui\s+a9, a2, 42',r.stdout) and '0x10d' in r.stdout,'actual archive has readonly byte/NOT_ALLOWED guard')
    if symbol=='_ZN3nvs12NVSPartition12get_readonlyEv':check(present and re.search(r'l32i.n\s+a8, a2, 12',r.stdout) and re.search(r'l8ui\s+a2, a8, 42',r.stdout),'actual NVS getter reads descriptor pointer then native readonly flag')
    if symbol=='ensure_partitions_loaded$part$0':check(present and re.search(r'extui\s+a10, a10, 1, 1',r.stdout) and re.search(r's8i\s+a10, a5, 42',r.stdout),'actual loader extracts readonly table bit into descriptor byte42')
    if symbol in ('start_cpu0','_ZN3nvs11PageManager4loadEPNS_9PartitionEmm'):check(present,'actual startup/manager entry found with native symbol spelling')
    if symbol=='main_flash_region_protected':check(present and 'esp_partition_is_flash_region_writable' in r.stdout and '0x10d' in r.stdout,'actual main driver callback has global readonly check')
    if symbol in ('esp_flash_write','esp_flash_erase_region','esp_flash_app_enable_os_functions'):check(present,'actual lower API/OS installation entry inspected')
   evidence['archives'].append(row)
  check(sha(objdump)==json.loads((ROOT/'docs/stage20-partition-archive.json').read_text())['objdump_sha256'],'pinned native inspector')
 case('actual_target_archive_readonly_guards_and_startup_evidence',archive)
 def boot():
  path=sdk/'bin/bootloader_qio_80m.elf';r=subprocess.run([str(objdump),'-dr','--disassemble=call_start_cpu0',str(path)],capture_output=True,text=True,check=True)
  check('<call_start_cpu0>:' in r.stdout,'actual supplied bootloader entry inspected')
  evidence['bootloader_elf']=dict(sha256=sha(path),entry_disassembly_sha256=hashlib.sha256(r.stdout.encode()).hexdigest(),complete_early_flash_audit=False)
 case('supplied_bootloader_entry_identity',boot)
 def ordering():
  core=(a.original_core/'cores/esp32/main.cpp').read_text();check(core.index('  USB.begin();')<core.index('  initArduino();')<core.index('  xTaskCreateUniversal(loopTask'),'source USB before NVS before app setup task')
  source=(a.reference_source/'components/esp_system/startup.c').read_text();tail=source[source.index('static void start_cpu0_default(void)\n{'):]
  check(tail.index('do_core_init();')<tail.index('do_global_ctors();'),'SDK source system init precedes global constructors')
 case('early_startup_source_ordering',ordering)
 def final():
  evidence['firmware']=[]
  for core,build,safe in [(a.normal_core,a.normal_build,False),(a.safe_core,a.safe_build,True)]:
   j=verify_firmware(core,build);check(j['deployment_safe_start'] is safe and j['sdk_nvs_immutable'] is False,'actual final profile/protection boundary explicit');check(j['settings_failure_quiescent'] is True and j['nvs_preservation_policy'] is True,'previous final guards remain')
   evidence['firmware'].append(j)
 case('both_clean_linked_profiles_and_prior_guards',final)
 def linked_arrays():
  nm=tools/'esp-x32/2411/bin/xtensa-esp32s3-elf-nm'
  for build in [a.normal_build,a.safe_build]:
   elf=build/'EvilDuckS3.ino.elf';before=sha(elf);j=inventory(elf,nm,objdump)
   arrays={row['start_symbol']:row for row in j['arrays']}
   check(len(arrays['__init_array_start']['entries'])==36,'all36 linked constructor array entries inventoried')
   check(len(arrays['_esp_system_init_fn_array_start']['entries'])==24,'all24 linked system-init entries inventoried')
   check(all(e['symbols'] for row in j['arrays'] if row['present'] for e in row['entries']),'linked startup addresses resolve to actual symbols')
   check(j['transitive_flash_write_audit_complete'] is False and sha(elf)==before,'no boot-proof inference or ELF mutation')
  with tempfile.TemporaryDirectory(prefix='stage21-invalid-elf-') as t:
   bad=Path(t)/'not-an-elf';bad.write_bytes(b'bad');rejects(lambda:inventory(bad,nm,objdump))
 case('both_linked_startup_array_inventories_and_invalid_elf',linked_arrays)
 def owner():
  j=json.loads((ROOT/'docs/stage20-owner-extended-preflight-evidence.json').read_text());check(j['reported_results']['nvs_classification']=='compatible-within-verified-checks' and j['reported_results']['nvs_issue_count']==0,'reported owner structural result retained');check(j['codex_independently_inspected'] is False and j['sdk_runtime_nvs_preservation_established'] is False and j['migration_status']=='NO-GO','no owner/immutability/authorization invention')
 case('owner_evidence_and_no_go_boundaries',owner)
 def reference_tamper():
  with tempfile.TemporaryDirectory(prefix='stage21-reference-fault-') as t:
   import shutil
   shutil.copytree(a.reference_source,Path(t)/'reference');target=Path(t)/'reference'/references['files'][0]['path'];target.write_bytes(target.read_bytes()+b'\n');rejects(lambda:verify_reference(Path(t)/'reference'))
 case('modified_startup_reference_rejected',reference_tamper)
 out=dict(results=ROWS,counts={s:sum(r['status']==s for r in ROWS) for s in ['PASS','FAIL']},assertions=ASSERTIONS,evidence=evidence,owner_files_inspected=False,hardware_access=False)
 with a.results.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
