#!/usr/bin/env python3
"""Disposable ELF symbol negative controls; never alter linked image bytes."""
import argparse,json,pathlib,subprocess,sys,tempfile,shutil
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
from startup_decode import load_verifier,allocated_sections
sys.path.insert(0,str(ROOT/'tools'))
import s3_validation
p=argparse.ArgumentParser();p.add_argument('--build-root',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
r=json.loads((a.build_root/'report.json').read_text());build=a.build_root/'build';source=a.build_root/'candidate';core=pathlib.Path(r['provenance']['core']);elf=build/'EvilDuckS3.ino.elf';before=sha(elf)
compiler=r['link_command'][0];prefix=compiler.rsplit('g++',1)[0];results=[]
for symbol,message in [('_ZN8settings5readyEv','Actual setup settings readiness/error checks absent'),('nvs_flash_init','Real NVS startup call missing')]:
 with tempfile.TemporaryDirectory(prefix='http-verifier-negative-') as d:
  scratch=pathlib.Path(d)
  for f in build.iterdir():
   if f.name=='EvilDuckS3.ino.elf':continue
   if f.is_dir():(scratch/f.name).symlink_to(f.resolve(),target_is_directory=True)
   else:shutil.copyfile(f,scratch/f.name)
  changed=scratch/elf.name
  subprocess.run([prefix+'objcopy','--redefine-sym',symbol+'=negative_control_missing',str(elf),str(changed)],check=True,capture_output=True)
  assert allocated_sections(elf)==allocated_sections(changed)
  props=json.loads((build/'s3-build-properties.json').read_text());esptool=pathlib.Path(props['runtime.tools.esptool_py.path'])/'esptool'
  image=scratch/'EvilDuckS3.ino.bin'
  subprocess.run([str(esptool),'--chip','esp32s3','elf2image','--flash-mode','dio','--flash-freq','80m','--flash-size','16MB','--elf-sha256-offset','0xb0','-o',str(image),str(changed)],check=True,capture_output=True)
  report=json.loads((scratch/'s3-build-report.json').read_text());report['application_sha256']=sha(image);(scratch/'s3-build-report.json').write_text(json.dumps(report))
  verifier=load_verifier(ROOT);verifier.ROOT=source;s3_validation.ROOT=source
  try:verifier.verify(core,scratch)
  except s3_validation.ValidationError as error:
   assert str(error)==message,str(error)
   results.append(dict(symbol=symbol,expected_rejection=message,observed=str(error),loaded_bytes_unchanged=True))
  else:raise AssertionError('negative control accepted')
assert sha(elf)==before
out=dict(status='PASS',controls=results,original_elf_unchanged=True,hardware=False)
a.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS two original safety predicates reject missing-symbol inspection controls')
