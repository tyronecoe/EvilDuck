#!/usr/bin/env python3
"""Offline isolated one-object SDK rebuild with original runtime equivalence gate."""
import argparse,hashlib,json,shutil,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from s3_validation import ROOT,require
from patched_core import sha,tree_hash,check_sources
PATCH=ROOT/'proposals/esp-idf-5.5-stage24-failclosed-scanner.patch'
PIN=ROOT/'docs/stage24-sdk-pin.json'

def elf_object(path):
 d=Path(path).read_bytes();h=struct.unpack_from('<16sHHIIIIIHHHHHH',d)
 require(d[:6]==b'\x7fELF\x01\x01' and h[2]==94,'Expected Xtensa ELF32 object')
 raw=[struct.unpack_from('<10I',d,h[6]+i*h[11]) for i in range(h[12])];strings=raw[h[13]];names=d[strings[4]:strings[4]+strings[5]]
 sections=[dict(name=names[r[0]:].split(b'\0')[0].decode(),kind=r[1],flags=r[2],data=(b'' if r[1]==8 else d[r[4]:r[4]+r[5]]),address=r[3],link=r[6],info=r[7],size=r[5],entry=r[9]) for r in raw]
 symbols=[]
 for r in sections:
  if r['kind']==2:
   ns=sections[r['link']]['data']
   for off in range(0,len(r['data']),r['entry']):
    n,v,size,info,other,idx=struct.unpack_from('<IIIBBH',r['data'],off)
    name=ns[n:].split(b'\0')[0].decode();section=sections[idx]['name'] if idx<len(sections) else str(idx)
    symbols.append(dict(name=name,value=v,size=size,info=info,other=other,section=section))
 relocs={}
 for r in sections:
  if r['kind']==4 and sections[r['info']]['flags']&2:
   vals=[]
   for off in range(0,len(r['data']),r['entry']):
    address,info,addend=struct.unpack_from('<IIi',r['data'],off);s=symbols[info>>8]
    vals.append((address,info&255,s['name'],s['section'],addend))
   relocs[sections[r['info']]['name']]=vals
 return dict(abi=(h[1],h[2],h[7]),alloc_addresses={r['name']:r['address'] for r in sections if r['flags']&2},alloc={r['name']:r['data'] for r in sections if r['flags']&2},relocations=relocs,public={s['name']:s for s in symbols if s['info']>>4 in [1,2]})

def compare(original,rebuilt,patched=False):
 a,b=elf_object(original),elf_object(rebuilt)
 require(a['abi']==b['abi'] and a['alloc_addresses']==b['alloc_addresses'],'Target ABI/section address mismatch')
 require(set(a['alloc'])==set(b['alloc']),'Allocated section set changed')
 allowed={'.text.esp_partition_is_flash_region_writable','.literal.esp_partition_is_flash_region_writable'} if patched else set()
 different=[n for n in a['alloc'] if a['alloc'][n]!=b['alloc'][n]]
 require(set(different)<=allowed,'Unrelated runtime section changed: '+str(different))
 rd=[n for n in set(a['relocations'])|set(b['relocations']) if a['relocations'].get(n)!=b['relocations'].get(n)]
 require(set(rd)<=allowed,'Unrelated relocation changed: '+str(rd))
 names=set(a['public']);extra=set(b['public'])-names
 require(extra<=({'esp_partition_iterator_release'} if patched else set()) and not(names-set(b['public'])),'Public symbol set changed unexpectedly')
 for n in names:
  left,right=dict(a['public'][n]),dict(b['public'][n])
  if patched and n=='esp_partition_is_flash_region_writable':left.pop('size');right.pop('size')
  require(left==right,'Public ABI changed: '+n)
 return dict(allocated_sections=len(a['alloc']),changed_runtime_sections=different,changed_relocation_sections=rd,extra_undefined_symbols=sorted(extra),abi_verified=True,unrelated_runtime_sections_identical=True)

def validate_output(output,core,build,source):
 output,core,build,source=map(lambda p:Path(p).resolve(),[output,core,build,source])
 sdk=(core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3').resolve()
 protected=[ROOT,core.parents[4],sdk.parents[5],build,source.parent]
 require(not output.exists(),'Rebuild destination must be fresh')
 require(all(output!=p and p not in output.parents for p in protected),'Rebuild output overlaps protected source/toolchain/build')
 return output


def rebuild(core,build,source,output):
 core,build,source,output=map(lambda p:Path(p).resolve(),[core,build,source,output])
 output=validate_output(output,core,build,source)
 from verify_patched_firmware import verify as verify_firmware
 verify_firmware(core,build)
 check_sources(core,True);require(not output.exists() and ROOT not in output.parents,'Fresh external rebuild directory required')
 ref=json.loads((ROOT/'docs/stage20-partition-reference.json').read_text())
 require(sha(source)==next(x['sha256'] for x in ref if x['url'].endswith('/partition_target.c')),'Unverified SDK target source')
 sdk=core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3';pin22=json.loads((ROOT/'docs/stage22-candidate-pin.json').read_text())
 for n,h in pin22['sdk_inputs'].items():require(sha(sdk/n)==h,'Baseline SDK input mismatch: '+n)
 output.mkdir(parents=True)
 entry=next(e for e in json.loads((build/'compile_commands.json').read_text()) if Path(e['file']).name=='esp32-hal-misc.c')
 require(Path(entry['file']).resolve()==core/'cores/esp32/esp32-hal-misc.c','Rebuild flags not from verified normal core')
 compiler=Path(entry['arguments'][0]);require(sha(compiler)==json.loads((ROOT/'docs/stage23-sdk-pin.json').read_text())['compiler_sha256'],'Compiler pin mismatch');prefix=str(compiler).rsplit('gcc',1)[0];ar=prefix+'ar';archive=sdk/'lib/libesp_partition.a'
 original=output/'original';original.mkdir()
 members=subprocess.run([ar,'t',str(archive)],check=True,capture_output=True,text=True).stdout.splitlines()
 require(members==['partition.c.obj','partition_target.c.obj'],'Unexpected SDK archive members')
 for m in members:(original/m).write_bytes(subprocess.run([ar,'p',str(archive),m],check=True,capture_output=True).stdout)
 commands=[];objects=[]
 for variant in ['reference','cleanup']:
  directory=output/variant/'components/esp_partition';directory.mkdir(parents=True);src=directory/'partition_target.c';shutil.copyfile(source,src)
  if variant=='cleanup':subprocess.run(['patch','--batch','--forward','--fuzz=0','-p1','-i',str(PATCH)],cwd=output/variant,check=True)
  obj=output/variant/'partition_target.c.obj';args=list(entry['arguments']);args[args.index('-o')+1]=str(obj);args[args.index(entry['file'])]=str(src)
  args+=['-ffile-prefix-map='+str(directory)+'=/IDF/components/esp_partition','-fdebug-prefix-map='+str(core.parents[4])+'=/ARDUINO_DATA','-fdebug-prefix-map='+str(output)+'=/SDK_REBUILD','-fdebug-prefix-map='+str(ROOT)+'=/EVILDUCK']
  subprocess.run(args,cwd=ROOT,check=True);commands.append(args);objects.append(obj)
 reference=compare(original/members[1],objects[0]);cleanup=compare(original/members[1],objects[1],True)
 newarchive=output/'libesp_partition.a';shutil.copyfile(archive,newarchive)
 subprocess.run([ar,'rD',str(newarchive),str(objects[1])],check=True)
 require(subprocess.run([ar,'p',str(newarchive),members[0]],check=True,capture_output=True).stdout==(original/members[0]).read_bytes(),'Unrelated archive member changed')
 require(subprocess.run([ar,'p',str(newarchive),members[1]],check=True,capture_output=True).stdout==objects[1].read_bytes(),'Replacement member mismatch')
 report=dict(label='EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING',source_sha256=sha(source),patched_source_sha256=sha(output/'cleanup/components/esp_partition/partition_target.c'),patch_sha256=sha(PATCH),compiler_sha256=sha(compiler),original_archive_sha256=sha(archive),patched_archive_sha256=sha(newarchive),original_target_sha256=sha(original/members[1]),reference_object_sha256=sha(objects[0]),patched_object_sha256=sha(objects[1]),unchanged_member_sha256=sha(original/members[0]),reference_equivalence=reference,cleanup_equivalence=cleanup,commands=commands,baseline_build=str(build),sdk_tree_sha256=tree_hash(sdk),sdk_inputs=pin22['sdk_inputs'],hardware_access=False,sdk_rebuilt_components=['partition_target.c'],complete_sdk_rebuild=False)
 (output/'EXPERIMENTAL-rebuild.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['core-dir','build-dir','source','output-dir']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();print(json.dumps(rebuild(a.core_dir,a.build_dir,a.source,a.output_dir),indent=2))
