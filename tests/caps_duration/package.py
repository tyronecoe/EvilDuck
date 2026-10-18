#!/usr/bin/env python3
"""Release existing verified public artifacts; no firmware build/device/network API."""
import argparse,hashlib,json,pathlib,shutil,stat,subprocess,sys,zipfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
from preflight import SOURCE,APP_BYTES,APP_SHA,TABLE_SHA,ROLLBACK_BYTES,ROLLBACK_SHA,rows,validate
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def prepare(out,build_root,core):
 out,build_root,core=map(pathlib.Path,[out,build_root,core]);assert not out.exists() and not out.is_symlink() and ROOT not in out.resolve().parents
 sys.path.insert(0,str(ROOT/'tools'));from feedback_core import check_sources
 receipt=json.loads((ROOT/'docs/caps-duration-build.json').read_text());assert check_sources(core,True)==receipt['core_pin']
 for name in ['docs/caps-duration-build.json','docs/caps-duration-dependency-pin.json','downloads/evilduck-caps-duration-review.bin','downloads/evilduck-led-feedback-review.bin','docs/led-feedback-build.json']:
  assert subprocess.check_output(['git','show',SOURCE+':'+name],cwd=ROOT)==(ROOT/name).read_bytes(),name
 build=build_root/'build'
 for row in receipt['artifacts']:
  f=build/row['file'];assert f.is_file() and not f.is_symlink() and f.stat().st_size==row['size'] and sha(f)==row['sha256']
 assert (ROOT/'downloads/evilduck-caps-duration-review.bin').read_bytes()==(build/'EvilDuckS3.ino.bin').read_bytes()
 rollback=ROOT/'downloads/evilduck-led-feedback-review.bin';assert rollback.stat().st_size==ROLLBACK_BYTES and sha(rollback)==ROLLBACK_SHA
 assert (build/'EvilDuckS3.ino.bin').stat().st_size==APP_BYTES and sha(build/'EvilDuckS3.ino.bin')==APP_SHA
 out.mkdir()
 copies={'test-results.json':ROOT/'docs/caps-duration-software-tests.json','feedback-analysis.md':ROOT/'docs/caps-duration-feedback-analysis.md','feedback-evidence.json':ROOT/'docs/caps-duration-feedback-evidence.json','OWNER-CHECK.md':ROOT/'docs/caps-duration-owner-check.md','application.bin':build/'EvilDuckS3.ino.bin','rollback-application.bin':rollback,'expected-partitions.bin':build/'EvilDuckS3.ino.partitions.bin','INSTALL-MAC.md':ROOT/'docs/caps-duration-install.md','ROLLBACK-MAC.md':ROOT/'docs/caps-duration-rollback.md','preflight.py':ROOT/'tests/caps_duration/preflight.py','gen_esp32part.py':core/'tools/gen_esp32part.py','APACHE-2.0.txt':pathlib.Path('/usr/share/common-licenses/Apache-2.0'),'source-LICENSE.txt':ROOT/'LICENSE','build-receipt.json':ROOT/'docs/caps-duration-build.json','rollback-build-receipt.json':ROOT/'docs/led-feedback-build.json','firmware-report.md':ROOT/'docs/caps-duration-design.md','tool-evidence.json':ROOT/'docs/caps-duration-tool-parser.json','dependency-pin.json':ROOT/'docs/caps-duration-dependency-pin.json','reproduction.md':ROOT/'docs/caps-duration-reproduction.md'}
 for name,f in copies.items():assert f.is_file() and not f.is_symlink();shutil.copyfile(f,out/name)
 (out/'README.md').write_text('Read INSTALL-MAC.md first. ROLLBACK-MAC.md returns to the owner-installed 2c657f0c application (installation receipt and observed buildId; not a new readback).\nSoftware/package review only; no physical installation authorization. Caps Lock and LED feedback remain physically unverified.\n')
 original=(ROOT/'tests/mac_install/installer.py').read_text();assert original.count('RELEASE_BINDING=None')==1
 original=original.replace("ROLLBACK_SHA='c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4'","ROLLBACK_SHA='2c657f0c74f1d12c88aa1e6fa6daf5cc76de36e8e68bc41a325f39b19c9045a7'").replace('ROLLBACK_BYTES=1376576','ROLLBACK_BYTES=1386176')
 original=original.replace(' result=subprocess.run(command,capture_output=True,text=True,timeout=3600)', " operation=next((part for part in command[3:] if part in ['version','flash_id','get_security_info','read_flash','write_flash','verify_flash']),None)\n require(operation is not None,'UNSUPPORTED_OPERATION')\n tool_process.step=getattr(tool_process,'step',0)+1\n print('Step %d: %s'%(tool_process.step,operation),flush=True)\n result=subprocess.run(command,capture_output=True,text=True,timeout=3600)\n print('Step %d: %s %s'%(tool_process.step,operation,'PASS' if result.returncode==0 else 'FAIL'),flush=True)")

 bound=original.replace('RELEASE_BINDING=None','RELEASE_BINDING='+repr(dict(preflight_sha256=sha(out/'preflight.py'))))
 bound=bound.replace('PREPARATION ONLY: no approved release binding. CLI fails before device access.','Bound app-only Mac installer. Defaults to read-only; no automatic reboot.').replace('A reviewed build/package must bind this in a later review before installation.','Use only after checking the published ZIP; physical writes need owner authorization.')
 (out/'installer.py').write_text(bound)
 for name in ['install-macos.sh','rollback-macos.sh']:
  s=(ROOT/'tests/mac_install'/name).read_text().replace('# PREPARATION ONLY. No release binding; Python exits before any hardware access.','# Bound package launcher; check is the default action.').replace('# PREPARATION ONLY. A separate deliberate rollback action; no implicit retry.','# Bound package launcher; deliberate rollback only, no implicit retry.')
  (out/name).write_text(s)
 support={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir()) if p.name not in ['application.bin','rollback-application.bin','expected-partitions.bin']}
 m=dict(package_id='evilduck-caps-duration-macos-install-v1',label='OWNER REVIEW APP-ONLY MAC PACKAGE; CAPS/LED PHYSICALLY UNVERIFIED',source_commit=SOURCE,source_url='https://github.com/tyronecoe/EvilDuck/tree/'+SOURCE,composition_commit=SOURCE,application_bytes=APP_BYTES,application_sha256=APP_SHA,application_elf_sha256=receipt['provenance']['elf_sha256'],table_sha256=TABLE_SHA,update_method='FUTURE_ROM_APP_ONLY_BOTH_SLOTS',installation_authorized=False,hardware=False,proposed_writes=rows(),rollback_writes=rows('rollback'),rollback_bytes=ROLLBACK_BYTES,rollback_sha256=ROLLBACK_SHA,rollback_source_commit='43aa0c7a2fe0fc8a571ea856d511ae70494ce2ae',rollback_package_commit='75e50b5856f6df5974e4e663fb0e51546ff81dc2',support_files=support,protected_nonapplication_regions='all; bootloader/table/NVS/otadata/SPIFFS/coredump untouched by plan',required_installed_otadata_sha256='f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0',unsigned_integrity_only=True)
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');validate(out);return m

def archive(directory,destination):
 d=pathlib.Path(directory);validate(d);dest=pathlib.Path(destination);assert not dest.exists() and not dest.is_symlink()
 with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(d.iterdir()):
   i=zipfile.ZipInfo(p.name,(2026,10,18,0,0,0));i.external_attr=(stat.S_IFREG|0o644)<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 return dict(file=dest.name,bytes=dest.stat().st_size,sha256=sha(dest),files=[p.name for p in sorted(d.iterdir())])
if __name__=='__main__':
 p=argparse.ArgumentParser();
 for name in ['directory','build-root','core','archive']:p.add_argument('--'+name,type=pathlib.Path,required=True)
 a=p.parse_args();prepare(a.directory,a.build_root,a.core);print(json.dumps(archive(a.directory,a.archive),indent=2))
