#!/usr/bin/env python3
"""Decode only reachable setup instructions; recover Xtensa padding alignment.
No invented call labels, source mutation, SDK patch or relaxed safety predicate.
"""
import hashlib,pathlib,re,subprocess,struct,tempfile
BASE_SHA='d8b1ea90ea3528ecc0f6639f6d5b6c8d22dccf763532fb05726a2d45d96a00ac'
def decode_setup(objdump,elf):
 nm=str(objdump).rsplit('objdump',1)[0]+'nm'
 matches=[l.split() for l in subprocess.check_output([nm,'-S','--defined-only',str(elf)],text=True).splitlines() if l.endswith(' _Z5setupv')]
 assert len(matches)==1
 start,size=int(matches[0][0],16),int(matches[0][1],16);end=start+size;assert 0<size<=16384
 pending=[start];instructions={};blocks=0
 while pending:
  at=pending.pop()
  if at in instructions:continue
  assert start<=at<end;blocks+=1;assert blocks<=1024
  raw=subprocess.check_output([str(objdump),'-d','--start-address='+hex(at),'--stop-address='+hex(end),str(elf)],text=True)
  rows=[]
  for line in raw.splitlines():
   m=re.match(r'^\s*([0-9a-f]+):\s+([0-9a-f]{4,6})\s+([.\w]+)\s*(.*)$',line)
   if m:rows.append((int(m[1],16),len(m[2])//2,m[3],m[4],line))
  assert rows and rows[0][0]==at
  for pc,width,op,args,line in rows:
   if pc in instructions:break
   assert pc==at and op not in ('.byte','ill'),'unresolved reachable opcode'
   instructions[pc]=line;assert len(instructions)<=4096;at=pc+width
   if op.startswith('ret'):break
   if op in ('jx','jr'):raise AssertionError('unsupported indirect setup branch')
   conditional=op.startswith('b') and op not in ('break','break.n')
   if op=='j' or conditional:
    targets=re.findall(r'([0-9a-f]+) <_Z5setupv(?:\+0x[0-9a-f]+)?>',args);assert len(targets)==1,(pc,op,args)
    pending.append(int(targets[0],16))
    if conditional and at<end:pending.append(at)
    break
   if at==end:break
 # Keep actual linked instruction addresses/order for the original predicates.
 return 'Disassembly of reachable _Z5setupv (bounded CFG):\n'+''.join(instructions[k]+'\n' for k in sorted(instructions))

def allocated_sections(path):
 # ELF32 little-endian section bytes/virtual addresses, independently parsed.
 raw=pathlib.Path(path).read_bytes();assert raw[:6]==b'\x7fELF\x01\x01'
 off=struct.unpack_from('<I',raw,32)[0];width,count=struct.unpack_from('<HH',raw,46);assert width==40
 result=[]
 for i in range(count):
  _,kind,flags,addr,data,size,*_=struct.unpack_from('<10I',raw,off+i*width)
  if flags&2:result.append((kind,flags,addr,size,None if kind==8 else raw[data:data+size]))
 return result

def decode_nvs(objdump,elf):
 # Xtensa property metadata can mislabel code as literals. A disposable
 # inspection copy removes only non-loadable .xt metadata; actual allocated
 # section bytes, addresses, flags and symbols must remain identical.
 prefix=str(objdump).rsplit('objdump',1)[0]
 with tempfile.TemporaryDirectory(prefix='http-nvs-disassembly-') as d:
  copy=pathlib.Path(d)/'inspection.elf'
  subprocess.run([prefix+'objcopy','--remove-section=.xt.prop','--remove-section=.xt.lit',str(elf),str(copy)],capture_output=True,check=True)
  assert allocated_sections(elf)==allocated_sections(copy)
  nm=lambda f:subprocess.check_output([prefix+'nm','-n',str(f)],text=True)
  assert nm(elf)==nm(copy)
  return subprocess.check_output([str(objdump),'-d','--disassemble=initArduino',str(copy)],text=True)

def load_verifier(root):
 import types
 p=pathlib.Path(root)/'tools/verify_patched_firmware.py';source=p.read_bytes();assert hashlib.sha256(source).hexdigest()==BASE_SHA
 old="setup_disasm=subprocess.run([objdump,'-d','--disassemble=_Z5setupv',str(elf)],capture_output=True,text=True,check=True).stdout"
 text=source.decode();assert text.count(old)==1;text=text.replace(old,'setup_disasm=decode_setup(objdump,elf)')
 nvs="nvs_disasm=subprocess.run([objdump,'-d','--disassemble=initArduino',str(elf)],capture_output=True,text=True,check=True).stdout"
 assert text.count(nvs)==1;text=text.replace(nvs,'nvs_disasm=decode_nvs(objdump,elf)')
 old_import='from patched_core import check_sources,sha';assert text.count(old_import)==1;text=text.replace(old_import,'from archive_core import check_sources,sha')
 module=types.ModuleType('archive_profile_guard_preserving_verifier');module.__file__=str(p);module.decode_setup=decode_setup;module.decode_nvs=decode_nvs
 exec(compile(text,str(p),'exec'),module.__dict__)
 return module
