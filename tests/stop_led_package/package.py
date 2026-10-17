#!/usr/bin/env python3
"""Package existing reviewed public bytes only; no firmware build or device API."""
import argparse,hashlib,json,pathlib,shutil,stat,subprocess,sys,zipfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
from preflight import SOURCE,APP_BYTES,APP_SHA,TABLE_SHA,ROLLBACK_BYTES,ROLLBACK_SHA,rows,validate

def prepare(out,build,core,rollback_build):
 out=pathlib.Path(out);assert not out.exists() and not out.is_symlink();assert ROOT not in out.resolve().parents
 assert subprocess.check_output(['git','show',SOURCE+':docs/stop-led-build.json'],cwd=ROOT)==(ROOT/'docs/stop-led-build.json').read_bytes()
 receipt=json.loads((ROOT/'docs/stop-led-build.json').read_text());build=pathlib.Path(build);core=pathlib.Path(core)
 sys.path.insert(0,str(ROOT/'tools'));from patched_core import check_sources
 assert check_sources(core,True)==receipt['core_pin']
 for n in ['EvilDuckS3.ino.bin','EvilDuckS3.ino.elf','EvilDuckS3.ino.partitions.bin','EvilDuckS3.ino.bootloader.bin']:
  r=next(x for x in receipt['artifacts'] if x['file']==n);f=build/n;assert not f.is_symlink() and f.stat().st_size==r['size'] and hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256']
 assert (ROOT/'downloads/evilduck-stop-led-review.bin').read_bytes()==(build/'EvilDuckS3.ino.bin').read_bytes()
 out.mkdir()
 rollback_build=pathlib.Path(rollback_build)
 rollback_receipt=json.loads((ROOT/'docs/keyboard-shortcuts-build.json').read_text())
 rollback=rollback_build/'EvilDuckS3.ino.bin'
 assert rollback.stat().st_size==ROLLBACK_BYTES and hashlib.sha256(rollback.read_bytes()).hexdigest()==ROLLBACK_SHA
 assert subprocess.check_output(['git','show',SOURCE+':docs/keyboard-shortcuts-build.json'],cwd=ROOT)==(ROOT/'docs/keyboard-shortcuts-build.json').read_bytes()
 copies={'application.bin':build/'EvilDuckS3.ino.bin','rollback-application.bin':rollback,'expected-partitions.bin':build/'EvilDuckS3.ino.partitions.bin','README.md':ROOT/'docs/stop-led-install.md','preflight.py':ROOT/'tests/stop_led_package/preflight.py','gen_esp32part.py':core/'tools/gen_esp32part.py','APACHE-2.0.txt':pathlib.Path('/usr/share/common-licenses/Apache-2.0'),'source-LICENSE.txt':ROOT/'LICENSE','build-receipt.json':ROOT/'docs/stop-led-build.json','rollback-build-receipt.json':ROOT/'docs/keyboard-shortcuts-build.json','firmware-report.md':ROOT/'docs/stop-led-report.md','tool-evidence.json':ROOT/'docs/stop-led-install-tool-evidence.json','host-cleanup-revision.json':ROOT/'docs/stop-led-install-host-cleanup.json'}
 for n,p in copies.items():assert p.is_file() and not p.is_symlink();shutil.copyfile(p,out/n)
 support={n:dict(bytes=(out/n).stat().st_size,sha256=hashlib.sha256((out/n).read_bytes()).hexdigest()) for n in copies if n not in ['application.bin','expected-partitions.bin','rollback-application.bin']}
 m=dict(package_id='evilduck-stop-led-install-v1',label='CONDITIONAL APP-ONLY OWNER INSTALLATION PACKAGE — NO AUTOMATIC HARDWARE ACCESS',source_commit=SOURCE,source_url='https://github.com/tyronecoe/EvilDuck/tree/'+SOURCE,application_bytes=APP_BYTES,application_sha256=APP_SHA,application_elf_sha256=receipt['provenance']['elf_sha256'],table_sha256=TABLE_SHA,update_method='FUTURE_ROM_APP_ONLY_BOTH_SLOTS',installation_authorized=False,hardware=False,proposed_writes=rows(),rollback_writes=rows("rollback"),rollback_bytes=ROLLBACK_BYTES,rollback_sha256=ROLLBACK_SHA,rollback_source_commit="5c19f0dacb25960bda36a97f4ff871937a3cc9e7",support_files=support,protected_nonapplication_regions='all; bootloader/table/NVS/otadata/SPIFFS/coredump untouched by this plan',required_installed_otadata_sha256='f94c5d786a7a8fab06ac5d10e33bf37711a6697636dc037559ea19cc410a17f0',rollback_zip_sha256='466edeac41cf33182136d5b4d02809a1f641fff5c17ae79e1a8fd3f46b314e0f',unsigned_integrity_only=True)
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');validate(out);return m

def archive(directory,destination):
 d=pathlib.Path(directory);validate(d);dest=pathlib.Path(destination);assert not dest.exists() and not dest.is_symlink()
 with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(d.iterdir()):
   i=zipfile.ZipInfo(p.name,(2026,10,17,0,0,0));i.external_attr=(stat.S_IFREG|0o644)<<16;i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 return dict(file=dest.name,bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),files=[p.name for p in sorted(d.iterdir())])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--build',type=pathlib.Path,required=True);p.add_argument('--core',type=pathlib.Path,required=True);p.add_argument('--rollback-build',type=pathlib.Path,required=True);p.add_argument('--archive',type=pathlib.Path,required=True);a=p.parse_args();prepare(a.directory,a.build,a.core,a.rollback_build);print(json.dumps(archive(a.directory,a.archive),indent=2))
