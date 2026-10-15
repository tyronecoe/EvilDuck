#!/usr/bin/env python3
"""Offline public X package only. No serial, USB, uploader or device APIs."""
import argparse,hashlib,importlib.util,json,os,pathlib,shutil,stat,struct,subprocess,sys,tempfile,zipfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from s3_validation import require,LAYOUT,check_table
from stage26_installation import ranges,row
from deployment_preflight import esp_image
from s3_write_plan import validate_ota_initializer
from s3_migration import checked_mkspiffs,source_listing
PIN=ROOT/'docs/stage28y-public-manifest.json'
ID='evilduck-stage28y-x134b295-public-v1'
BASE='134b295deaebcb93f94beb63f2d46f102a7d6555'
LABEL='REVIEW ONLY — NOT AUTHORIZED FOR FLASHING'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def ordinary(p):
 p=pathlib.Path(p);require(p.is_file() and not p.is_symlink(),'Ordinary file required');return p
def safe_name(name):
 require(isinstance(name,str) and name and '\\' not in name and ':' not in name,'Unsafe member')
 p=pathlib.PurePosixPath(name);require(not p.is_absolute() and all(x not in ('','..','.') for x in name.split('/')),'Unsafe path');return p

def validate(directory,mkspiffs=None):
 d=pathlib.Path(directory);require(d.is_dir() and not d.is_symlink(),'Ordinary package required');m=json.loads(ordinary(d/'manifest.json').read_text());require(m==json.loads(PIN.read_text()),'Wrong package identity or manifest')
 require(m['package_id']==ID and m['source_commit']==BASE and not m['migration_authorized'],'Wrong X profile')
 ranges(m['rows']);expected={'manifest.json'}|{r['file'] for r in m['rows']}|{r['file'] for r in m['support_files']}
 expected.add('source/docs/stage28y-public-manifest.json');require((d/'source/docs/stage28y-public-manifest.json').read_bytes()==PIN.read_bytes(),'Copied pin mismatch')
 actual={str(p.relative_to(d)) for p in d.rglob('*') if p.is_file() or p.is_symlink()};require(actual==expected,'Missing or extra package member')
 for r in m['rows']+m['support_files']:
  safe_name(r['file']);p=ordinary(d/r['file']);require(not any(q.is_symlink() for q in p.parents if q!=d.parent),'Linked package path');require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Artifact integrity mismatch')
 tool=d/'partition-tool/gen_esp32part.py';spec=importlib.util.spec_from_file_location('pinned_partition_tool',tool);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.offset_part_table=0x8000
 data=(d/'partitions.bin').read_bytes();table=mod.PartitionTable.from_binary(data);check_table(table,LAYOUT);require(table.to_binary()==data and all(not p.readonly and not p.encrypted for p in table),'Wrong table, flags or MD5')
 headers={}
 for r in m['rows']:
  if r['role'] in ('app0','app1','bootloader'):
   data=(d/r['file']).read_bytes();info=esp_image(data,r['region_end_exclusive']-r['offset'],True);require(info['image_bytes']==len(data) and data[3]==0x4f,'Image length/flash profile mismatch');require(data[2]==2,'Expected reviewed DIO-safe image header');entry=struct.unpack_from('<I',data,4)[0];require(0x40370000<=entry<0x403e0000,'Wrong entry point');headers[r['role']]=dict(info,entry=entry,flash_mode_code=data[2],flash_mhz=80)
 require(m['rows'][3]['sha256']==m['rows'][4]['sha256'],'Mixed app slots')
 validate_ota_initializer((d/'ota-app0.bin').read_bytes());require((d/'coredump-erased.bin').read_bytes()==b'\xff'*0x10000,'Wrong coredump initialization')
 fs='PINNED EMPTY IMAGE BYTE IDENTITY'
 if mkspiffs:
  checked_mkspiffs(mkspiffs);require(source_listing(str(mkspiffs),d/'empty-spiffs.bin',0x160000)=={},'Filesystem not empty');fs='DECODED EMPTY; 4096 block/256 page/0x160000'
 return dict(status='PASS',package_id=ID,manifest_sha256=sha(d/'manifest.json'),image_headers=headers,spiffs=fs,private_nvs_ready=False,migration_authorized=False,hardware=False)

def prepare(output,core,mkspiffs):
 out=pathlib.Path(output);require(not out.exists() and not out.is_symlink() and ROOT not in out.resolve().parents,'Fresh external output required')
 plan=json.loads((ROOT/'docs/stage28x-artifact-plan.json').read_text());linked=json.loads((ROOT/'docs/stage28x-linked-enabled.json').read_text());require(linked['report']['application_sha256']=='a0cefdbb8ff9915e58b9142841b4c015dd738406c6861ef5f8e4c3f9105cffc4','Wrong X receipt')
 # Materialization is allowed; verify exact retained ELF identity without building a variant.
 elf=pathlib.Path(next(r['file'] for r in plan['rows'] if r['role']=='app0')).with_name('EvilDuckS3.ino.elf');ordinary(elf);require(sha(elf)==linked['provenance']['elf_sha256'],'X ELF not retained or mismatched')
 out.mkdir();names=dict(bootloader='bootloader.bin',partitions='partitions.bin',otadata='ota-app0.bin',app0='controlled-stage28x.bin',app1='controlled-stage28x.bin',spiffs='empty-spiffs.bin',coredump='coredump-erased.bin');rows=[]
 for r in plan['rows']:
  if r['role']=='nvs':continue
  src=ordinary(r['file']);require(src.stat().st_size==r['bytes'] and sha(src)==r['sha256'],'X source artifact mismatch');name=names[r['role']];shutil.copyfile(src,out/name);rows.append(dict(r,file=name))
 support=[]
 readme=out/'README.md';shutil.copyfile(ROOT/'docs/stage28y-package-readme.md',readme);support.append(dict(file='README.md',bytes=readme.stat().st_size,sha256=sha(readme)))
 # Public source only, no .git, backups, external outputs or private configuration.
 files=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
 files=[f for f in files if f.startswith(('tools/','EvilDuckS3/','docs/'))]
 files+=['tests/stage28y/'+name for name in ['package.py','private.py','host_preflight.py']]
 for name in files:
  src=ordinary(ROOT/name);target=out/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
  support.append(dict(file=str(target.relative_to(out)),bytes=target.stat().st_size,sha256=sha(target)))
 tool=pathlib.Path(core)/'tools/gen_esp32part.py';ordinary(tool)
 # Exact protected-core identity, not an inferred version string alone.
 from patched_core import check_sources
 require(check_sources(core,True)==linked['core_pin'],'Core pin mismatch')
 target=out/'partition-tool/gen_esp32part.py';target.parent.mkdir();shutil.copyfile(tool,target);support.append(dict(file=str(target.relative_to(out)),bytes=target.stat().st_size,sha256=sha(target)))
 m=dict(format_version=1,package_id=ID,label=LABEL,source_commit=BASE,profile='controlled-start Route B compiled; diagnostics enabled; legacy default; explicit selection',migration_authorized=False,hardware=False,flash_bytes=0x1000000,chip='ESP32-S3',flash_mode='QIO80 configured / DIO80 image header',psram=False,core_pin=linked['core_pin'],application_elf_sha256=linked['provenance']['elf_sha256'],application_bin_sha256=linked['report']['application_sha256'],rows=rows,support_files=support,private_nvs='ABSENT; owner-local fresh finalization required',unsigned_integrity_only=True)
 # Receipt/pin is the only new repository output; the historic Stage26 pin is untouched.
 PIN.write_text(json.dumps(m,indent=2)+'\n');(out/'manifest.json').write_bytes(PIN.read_bytes());(out/'source/docs/stage28y-public-manifest.json').write_bytes(PIN.read_bytes())
 return validate(out,mkspiffs)

def archive(directory,destination):
 validate(directory);dest=pathlib.Path(destination);require(not dest.exists() and not dest.is_symlink(),'Fresh archive required')
 with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(pathlib.Path(directory).rglob('*')):
   if p.is_file():
    info=zipfile.ZipInfo(str(p.relative_to(directory)),(2026,10,15,0,0,0));info.external_attr=(stat.S_IFREG|0o644)<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 return dict(file=dest.name,bytes=dest.stat().st_size,sha256=sha(dest))
def extract(archive_file,output):
 out=pathlib.Path(output);require(not out.exists() and not out.is_symlink(),'Fresh extraction required')
 with zipfile.ZipFile(ordinary(archive_file)) as z:
  seen=set();total=0
  for info in z.infolist():
   safe_name(info.filename);require(info.filename not in seen and stat.S_IFMT(info.external_attr>>16) in (0,stat.S_IFREG),'Linked/duplicate archive member');seen.add(info.filename);total+=info.file_size;require(total<=128*1024*1024 and info.file_size<=32*1024*1024,'Archive bound exceeded')
  out.mkdir()
  for info in z.infolist():
   p=out/info.filename;p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('xb') as f:f.write(z.read(info))
 return validate(out)

def main():
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['prepare','validate','archive','extract']);p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--archive',type=pathlib.Path);p.add_argument('--core',type=pathlib.Path);p.add_argument('--mkspiffs',type=pathlib.Path);a=p.parse_args()
 if a.operation=='prepare':r=prepare(a.directory,a.core,a.mkspiffs)
 elif a.operation=='validate':r=validate(a.directory,a.mkspiffs)
 elif a.operation=='archive':r=archive(a.directory,a.archive)
 else:r=extract(a.archive,a.directory)
 print(json.dumps(r,indent=2))
if __name__=='__main__':
 try:main()
 except Exception:sys.exit('FAIL: offline package rejected; no device operation')
