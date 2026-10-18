"""Inspection-only proposed archive profile. Never substitutes historical pins.
No build/upload API; review approval is deliberately absent.
"""
import hashlib,json,pathlib,sys,subprocess
sys.dont_write_bytecode=True
from core_inventory import inventory,compare
ROOT=pathlib.Path(__file__).resolve().parents[2]
ARCHIVE_SHA='c8525462e47b37b726c211b71afada0fca5859ba748963e4d967131355716ba2'
RAW_SHA='8d9ff37fa810d0338ed89bc87aa26523ea39add6ec8ce947ae59c4abeedeccc8'
PATCHED_SHA='edfa1c99cdb73dca1da7d2f0a9d1153e40a2ce196c7470872c9654f03093f530'
class Rejected(ValueError):pass
def require(v,code):
 if not v:raise Rejected(code)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def inspect(archive,raw,patched,sdk,compiler):
 for path in ['tools/patched_core.py','tools/verify_patched_firmware.py','docs/stage18-dependency-pin.json']:
  original=subprocess.check_output(['git','show','d32a60bd3fef73e38293f95905f5905eb41b32fd:'+path],cwd=ROOT)
  require((ROOT/path).read_bytes()==original,'HISTORICAL_GUARD_CHANGED')
 require(sha(archive)==ARCHIVE_SHA,'ARCHIVE_IDENTITY')
 a,b=inventory(raw),inventory(patched)
 require(a['tree_sha256']==RAW_SHA and b['tree_sha256']==PATCHED_SHA,'PROPOSAL_TREE_IDENTITY')
 pin=json.loads((ROOT/'docs/stage18-dependency-pin.json').read_text())
 for file,k in [('proposals/arduino-esp32-3.3.0-hid-routing.patch','patch_sha256'),('proposals/arduino-esp32-3.3.0-nvs-preservation.patch','nvs_patch_sha256')]:require(sha(ROOT/file)==pin[k],'PATCH_IDENTITY')
 require(not a['links'] and not b['links'],'UNREVIEWED_LINK')
 delta=compare(a,b);require(not delta['added'] and not delta['removed'] and {x['path'] for x in delta['content_changed']}=={'libraries/USB/src/USBHID.cpp','cores/esp32/esp32-hal-misc.c'},'PATCH_SCOPE')
 for file,k in [('libraries/USB/src/USBHID.cpp','patched_routing_sha256'),('cores/esp32/esp32-hal-misc.c','patched_nvs_source_sha256')]:require(dict(b['files'])[file]==pin[k],'PATCHED_SOURCE_IDENTITY')
 receipt=json.loads((ROOT/'docs/stop-led-build.json').read_text());require(sha(compiler)==receipt['compiler_sha256'],'COMPILER_IDENTITY')
 libraries={}
 for row in receipt['linked_input_hashes']:
  if '/esp32-arduino-libs/' in row['file'] and row['file'].endswith('.a'):
   relative=row['file'].split('/esp32s3/',1)[1];require(sha(pathlib.Path(sdk)/relative)==row['sha256'],'SDK_ARCHIVE_IDENTITY');libraries[relative]=row['sha256']
 require(len(libraries)==177,'SDK_ARCHIVE_INVENTORY')
 require(sha(pathlib.Path(sdk)/'qio_qspi/include/sdkconfig.h')==pin['sdk_config_sha256'],'SDK_CONFIG_IDENTITY')
 return dict(status='PROPOSED_PROFILE_INPUTS_VERIFIED',historical_reproduction=False,approved_for_build=False,approved_for_install=False,raw_tree=a['tree_sha256'],proposed_patched_tree=b['tree_sha256'],archive_sha256=ARCHIVE_SHA,compiler_sha256=sha(compiler),sdk_archives=libraries,patches=[dict(file=f,sha256=sha(ROOT/f)) for f in ['proposals/arduino-esp32-3.3.0-hid-routing.patch','proposals/arduino-esp32-3.3.0-nvs-preservation.patch']],historical_pin_file_sha256=sha(ROOT/'docs/stage18-dependency-pin.json'),historical_verifier_unchanged=True,gate='EXPLICIT_ADDITIVE_PROFILE_REVIEW_REQUIRED; alternatively supply a matching historical tree or complete original inventory')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();
 for flag in ['archive','raw','patched','sdk','compiler','output']:p.add_argument('--'+flag,type=pathlib.Path,required=True)
 a=p.parse_args();require(not a.output.exists(),'OUTPUT_EXISTS');a.output.write_text(json.dumps(inspect(a.archive,a.raw,a.patched,a.sdk,a.compiler),indent=2)+'\n')
