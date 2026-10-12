#!/usr/bin/env python3
"""Offline bounded native call inspection; not complete transitive or physical proof."""
import argparse,hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from inspect_startup_elf import inventory
ROOT=Path(__file__).resolve().parents[1]
def audit(build,output,elf_override=None):
 build,output=Path(build),Path(output)
 if output.exists():raise ValueError('Fresh audit output required')
 entries=json.loads((build/'compile_commands.json').read_text());compiler=next(e['arguments'][0] for e in entries if Path(e['file']).name=='esp32-hal-misc.c');prefix=compiler.rsplit('gcc',1)[0];nm=prefix+'nm';objdump=prefix+'objdump';elf=Path(elf_override) if elf_override else build/'EvilDuckS3.ino.elf'
 inv=inventory(elf,nm,objdump)
 # Xtensa property metadata can classify genuine function bytes as data.
 # Inspection copy only: prove every file-backed ALLOC byte/address unchanged.
 from stage23_sdk_cleanup import elf_object
 inspection_dir=tempfile.TemporaryDirectory(prefix='stage23-inspection-only-')
 inspection=Path(inspection_dir.name)/'not-for-loading.elf'
 subprocess.run([prefix+'objcopy','--remove-section=.xt.prop',str(elf),str(inspection)],check=True,capture_output=True)
 original_runtime,inspection_runtime=elf_object(elf),elf_object(inspection)
 assert original_runtime['alloc']==inspection_runtime['alloc'] and original_runtime['alloc_addresses']==inspection_runtime['alloc_addresses']
 disassembly_elf=inspection
 symbols=subprocess.run([nm,'-n',str(elf)],capture_output=True,text=True,check=True).stdout
 functions={m[3] for line in symbols.splitlines() if (m:=re.match(r'^([0-9a-f]+) ([TtWw]) (.+)$',line))}
 roots=[]
 for a in inv['arrays']:
  for r in a.get('entries',[]):roots+=r['symbols'][:1]
 roots+='app_main initArduino start_cpu0 esp_flash_init_default_chip esp_flash_init_main esp_flash_app_init esp_flash_app_enable_os_functions main_flash_region_protected esp_partition_is_flash_region_writable esp_partition_find esp_partition_next esp_partition_iterator_release esp_partition_verify esp_core_dump_init esp_core_dump_image_check esp_core_dump_image_erase esp_ota_mark_app_valid_cancel_rollback esp_ota_mark_app_invalid_rollback_and_reboot bootloader_flash_write bootloader_flash_erase_range bootloader_flash_read evilduck_nvs_preinit_gate'.split()
 if elf_override:roots+='call_start_cpu0 bootloader_init bootloader_utility_load_boot_image bootloader_load_partition_table bootloader_common_erase_part_type_data bootloader_flash_write bootloader_flash_erase_sector bootloader_flash_erase_range'.split()
 queue=[(s,0) for s in dict.fromkeys(roots)];records={};missing=[]
 while queue and len(records)<400:
  s,depth=queue.pop(0)
  if s in records:continue
  if s not in functions:missing.append(s);continue
  d=subprocess.run([objdump,'-d','--disassemble='+s,str(disassembly_elf)],capture_output=True,text=True,check=True).stdout
  marker='<'+s+'>:';body=d.split(marker,1)[1].split('\n\n',1)[0] if marker in d else ''
  calls=[];unresolved=0;regs={}
  for line in body.splitlines():
   direct=re.search(r'\bcall[04812]+\s+[0-9a-f]+ <([^>]+)>',line)
   if direct:calls.append(direct[1]);continue
   literal=re.search(r'\bl32r\s+(a\d+),.*\([0-9a-f]+ <([^>]+)>\)',line)
   if literal:regs[literal[1]]=literal[2] if literal[2] in functions else None;continue
   indirect=re.search(r'\bcallx[04812]+\s+(a\d+)',line)
   if indirect:
    if regs.get(indirect[1]):calls.append(regs[indirect[1]])
    else:unresolved+=1
    regs.clear();continue
   destination=re.search(r'\b(?:l32i(?:\.n)?|mov(?:\.n)?|movi(?:\.n)?|addi(?:\.n)?)\s+(a\d+),',line)
   if destination:regs.pop(destination[1],None)
  calls=list(dict.fromkeys(calls));records[s]=dict(depth=depth,body_found=bool(body),body_sha256=hashlib.sha256(body.encode()).hexdigest(),named_calls=calls,unresolved_indirect_calls=unresolved)
  if depth<3:queue.extend((c,depth+1) for c in calls if c in functions)
 for a in inv['arrays']:
  if 'system_init' in a['start_symbol']:
   for r in a.get('entries',[]):r['stage']=r['cores_mask']>>16;r['core_bits']=r['cores_mask']&65535
 out=dict(inventory=inv,records=records,missing_roots=sorted(set(missing)),maximum_depth=3,maximum_functions=400,truncated=bool(queue),unresolved_indirect_calls=sum(r['unresolved_indirect_calls'] for r in records.values()),inspection_copy_only=True,inspection_runtime_bytes_verified=True,original_elf_modified=False,complete_transitive_audit=False,source_binary_equivalence=False,xtensa_execution=False,hardware_access=False)
 inspection_dir.cleanup()
 output.write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--elf-override',type=Path);a=p.parse_args();x=audit(a.build_dir,a.output,a.elf_override);print(len(x['records']),'inspected; unresolved indirect calls',x['unresolved_indirect_calls'])
