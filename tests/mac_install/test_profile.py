"""Inventory semantics, proposal inputs and historical fail-closed preservation."""
import argparse,hashlib,json,pathlib,shutil,sys,tempfile
sys.dont_write_bytecode=True
from core_inventory import inventory,compare
import proposed_profile as proposal
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'));import patched_core
p=argparse.ArgumentParser();
for n in ['archive','raw','patched','sdk','compiler','results']:p.add_argument('--'+n,type=pathlib.Path,required=True)
a=p.parse_args();assert not a.results.exists();rows=[]
def case(n,fn):
 try:fn();rows.append(dict(name=n,status='PASS'))
 except Exception as e:rows.append(dict(name=n,status='FAIL',error=type(e).__name__+': '+str(e)))
def need(v):assert v
def reject(fn,code=None):
 try:fn()
 except (ValueError,OSError) as e:
  if code:need(str(e)==code)
  return
 raise AssertionError('accepted unexpected input')
def check(**kw):
 args=dict(archive=a.archive,raw=a.raw,patched=a.patched,sdk=a.sdk,compiler=a.compiler);args.update(kw);return proposal.inspect(**args)
case('verified_input_profile_still_requires_review',lambda:need(check()['approved_for_build'] is False and check()['approved_for_install'] is False and not check()['historical_reproduction']))
case('all_177_linked_sdk_archives_match_working_build',lambda:need(len(check()['sdk_archives'])==177))
case('historical_raw_guard_still_rejects_new_tree',lambda:reject(lambda:patched_core.check_sources(a.raw)))
case('historical_patched_guard_still_rejects_new_tree',lambda:reject(lambda:patched_core.check_sources(a.patched,True)))
case('raw_core_cannot_be_patched_profile',lambda:reject(lambda:check(patched=a.raw),'PROPOSAL_TREE_IDENTITY'))
case('patched_core_cannot_be_raw_profile',lambda:reject(lambda:check(raw=a.patched),'PROPOSAL_TREE_IDENTITY'))
with tempfile.TemporaryDirectory(prefix='archive-profile-tests-') as tmp:
 t=pathlib.Path(tmp);fake=t/'fake';fake.write_bytes(b'wrong')
 case('wrong_archive_rejected',lambda:reject(lambda:check(archive=fake),'ARCHIVE_IDENTITY'))
 case('wrong_compiler_rejected',lambda:reject(lambda:check(compiler=fake),'COMPILER_IDENTITY'))
 case('missing_sdk_not_accepted',lambda:reject(lambda:check(sdk=t/'missing')))
 small=t/'small';small.mkdir();(small/'a').mkdir();(small/'a/file').write_bytes(b'x');(small/'a.txt').write_bytes(b'y');(small/'installed.json').write_bytes(b'catalog');b=inventory(small)
 case('same_order_and_json_as_historical_hash',lambda:need(b['tree_sha256']==patched_core.tree_hash(small)))
 case('path_component_order_not_string_sort',lambda:need([r[0] for r in b['files']]==['a/file','a.txt']))
 (small/'installed.json').write_bytes(b'new metadata')
 case('only_root_installed_json_is_excluded',lambda:need(inventory(small)['tree_sha256']==b['tree_sha256']))
 (small/'a/installed.json').write_bytes(b'nested source')
 case('nested_catalog_name_is_not_ignored',lambda:need(inventory(small)['tree_sha256']!=b['tree_sha256']))
 before=inventory(small);(small/'a.txt').chmod(0o600)
 case('modes_not_hashed',lambda:need(inventory(small)['tree_sha256']==before['tree_sha256']))
 import os
 os.utime(small/'a.txt',(1,1))
 case('mtimes_not_hashed',lambda:need(inventory(small)['tree_sha256']==before['tree_sha256']))
 (small/'alias').symlink_to('a.txt');(small/'broken').symlink_to('absent');s=inventory(small)
 case('links_are_recorded_separately_and_file_links_followed',lambda:need(len(s['links'])==2 and 'alias' in dict(s['files']) and 'broken' not in dict(s['files'])))
 clone=t/'clone';shutil.copytree(a.raw,clone);(clone/'extra.generated').write_bytes(b'unknown')
 case('undeclared_generated_file_rejected',lambda:reject(lambda:check(raw=clone),'PROPOSAL_TREE_IDENTITY'))
 (clone/'extra.generated').unlink();(clone/'platform.txt').write_text((clone/'platform.txt').read_text().replace('version=3.3.0','version=2.0.17'))
 case('wrong_core_version_not_accepted',lambda:reject(lambda:check(raw=clone),'PROPOSAL_TREE_IDENTITY'))
 (clone/'platform.txt').write_bytes((a.raw/'platform.txt').read_bytes());(clone/'broken-unhashed-link').symlink_to('missing')
 case('unhashed_broken_symlink_is_still_rejected',lambda:reject(lambda:check(raw=clone),'UNREVIEWED_LINK'))
 clone2=t/'patched';shutil.copytree(a.patched,clone2);f=clone2/'libraries/USB/src/USBHID.cpp';f.write_bytes(f.read_bytes()+b'\n// tamper\n')
 case('patched_source_tamper_rejected',lambda:reject(lambda:check(patched=clone2),'PROPOSAL_TREE_IDENTITY'))
actual=compare(inventory(a.raw),inventory(a.patched))
case('patches_only_modify_two_declared_source_files',lambda:need(not actual['added'] and not actual['removed'] and len(actual['content_changed'])==2))
out=dict(counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},results=rows,hardware=False,source_images_modified=False,approved_for_build=False,approved_for_install=False);a.results.write_text(json.dumps(out,indent=2)+'\n');print(out['counts']);
for r in rows:
 if r['status']=='FAIL':print(r)
raise SystemExit(bool(out['counts']['FAIL']))
