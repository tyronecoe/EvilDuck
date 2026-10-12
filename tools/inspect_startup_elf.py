#!/usr/bin/env python3
"""Inventory linked startup arrays/disassembly; not an execution or transitive audit."""
import argparse, hashlib, json, re, struct, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
def inventory(elf,nm,objdump):
 data=Path(elf).read_bytes()
 if data[:6]!=b'\x7fELF\x01\x01':raise ValueError('Expected little-endian ELF32')
 header=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
 if header[2]!=94:raise ValueError('Expected Xtensa ELF machine')
 phoff,phsize,phnum=header[5],header[9],header[10]
 segments=[struct.unpack_from('<IIIIIIII',data,phoff+i*phsize) for i in range(phnum)]
 def read(address,n):
  for kind,offset,virt,physical,filesize,memsize,flags,align in segments:
   if kind==1 and virt<=address and n<=filesize-(address-virt):return data[offset+address-virt:offset+address-virt+n]
  raise ValueError('Startup array not in file-backed load segment')
 result=subprocess.run([str(nm),'-n',str(elf)],capture_output=True,text=True,check=True).stdout
 names={};addresses={}
 for line in result.splitlines():
  match=re.fullmatch(r'([0-9a-fA-F]+) (\w) (.+)',line)
  if not match:continue
  address=int(match[1],16);names[match[3]]=address;addresses.setdefault(address,[]).append(match[3])
 arrays=[]
 for start,end,stride in [('__init_priority_array_start','__init_priority_array_end',4),('__init_array_start','__init_array_end',4),('_esp_system_init_fn_array_start','_esp_system_init_fn_array_end',8)]:
  if start not in names or end not in names:arrays.append(dict(start_symbol=start,present=False));continue
  first,last=names[start],names[end]
  if last<first or (last-first)%stride or last-first>4096:raise ValueError('Invalid/big startup array bounds')
  blob=read(first,last-first);entries=[]
  for pos in range(0,len(blob),stride):
   address=struct.unpack_from('<I',blob,pos)[0];row=dict(address=address,symbols=addresses.get(address,[]))
   if stride==8:row['cores_mask']=struct.unpack_from('<I',blob,pos+4)[0]
   entries.append(row)
  arrays.append(dict(start_symbol=start,end_symbol=end,present=True,stride=stride,entries=entries))
 selected=[]
 for symbol,address in sorted(names.items()):
  if symbol.startswith('_GLOBAL__sub_I') or symbol.startswith('__esp_system_init_fn_') or symbol in ('app_main','initArduino','setup','loop') or symbol in ('_Z5setupv','_Z4loopv'):
   r=subprocess.run([str(objdump),'-dr','--disassemble='+symbol,str(elf)],capture_output=True,text=True,check=True)
   marker='<'+symbol+'>:';body=r.stdout.split(marker,1)[1].split('\n\n',1)[0] if marker in r.stdout else ''
   selected.append(dict(symbol=symbol,address=address,body_found=bool(body),body_sha256=hashlib.sha256(body.encode()).hexdigest(),direct_named_calls=sorted(set(re.findall(r'call\w*\s+[0-9a-f]+ <([^>]+)>',body)))))
 return dict(elf_sha256=hashlib.sha256(data).hexdigest(),arrays=arrays,selected_entrypoints=selected,execution_performed=False,transitive_flash_write_audit_complete=False,rom_executed=False,hardware_access=False)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['elf','nm','objdump','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args()
 if a.output.exists():raise ValueError('Fresh inventory output required')
 report=inventory(a.elf,a.nm,a.objdump)
 with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print('PASS: linked startup inventory saved; complete boot/immutability not established')
if __name__=='__main__':raise SystemExit(main())
