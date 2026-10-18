"""Additive profile and historical rejection checks; disposable input copies only."""
import argparse,json,pathlib,sys,shutil,tempfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import archive_core,patched_core
p=argparse.ArgumentParser();p.add_argument('--core',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists();cases=[]
def case(name,fn):
 try:fn();cases.append(dict(name=name,status='PASS'))
 except Exception as e:cases.append(dict(name=name,status='FAIL',error=str(e)))
def need(v):assert v
def reject(fn):
 try:fn()
 except (ValueError,OSError,AssertionError):return
 raise AssertionError('unsafe dependency accepted')
case('approved_archive_patched_tree_accepted',lambda:need(archive_core.check_sources(a.core,True)['profile']=='arduino-3.3.0-publisher-archive-hid-nvs-v1'))
case('archive_patched_tree_rejected_as_raw',lambda:reject(lambda:archive_core.check_sources(a.core,False)))
case('historical_guard_still_rejects_new_profile',lambda:reject(lambda:patched_core.check_sources(a.core,True)))
with tempfile.TemporaryDirectory(prefix='new-profile-') as tmp:
 t=pathlib.Path(tmp);clone=t/'data/packages/esp32/hardware/esp32/3.3.0';clone.parent.mkdir(parents=True);shutil.copytree(a.core,clone);tools=clone.parents[2]/'tools';tools.symlink_to(a.core.parents[2]/'tools',target_is_directory=True)
 for name in ['libraries/USB/src/USBHID.cpp','cores/esp32/esp32-hal-misc.c','platform.txt','cores/esp32/Arduino.h']:
  f=clone/name;old=f.read_bytes();f.write_bytes(old+b'\n/* alteration */\n');case('changed_'+name,lambda:reject(lambda:archive_core.check_sources(clone,True)));f.write_bytes(old)
 f=clone/'unknown';f.write_bytes(b'unknown');case('added_source_rejected',lambda:reject(lambda:archive_core.check_sources(clone,True)));f.unlink()
 f.symlink_to('missing');case('broken_link_rejected',lambda:reject(lambda:archive_core.check_sources(clone,True)));f.unlink()
 case('missing_core_rejected',lambda:reject(lambda:archive_core.check_sources(t/'absent',True)))
# Exact source of old verifier is pinned by the additive adapter before adaptation.
sys.path.insert(0,str(ROOT/'tests/mac_release'));from startup_decode import load_verifier
case('adapted_verifier_retains_base_identity',lambda:need(load_verifier(ROOT).__name__=='archive_profile_guard_preserving_verifier'))
out=dict(counts={x:sum(r['status']==x for r in cases) for x in ['PASS','FAIL']},results=cases,hardware=False);a.results.write_text(json.dumps(out,indent=2)+'\n');print(out['counts']);raise SystemExit(bool(out['counts']['FAIL']))
