#!/usr/bin/env python3
"""Read-only historical/freeze/dependency/input/receipt checks. Never patch/build."""
import argparse,hashlib,json,pathlib,stat,subprocess,sys,zipfile
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];BASE='300c8dc649efce448d931d0b7bbfdba2a46d4e97'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--original',type=pathlib.Path,required=True);p.add_argument('--prototype',type=pathlib.Path,required=True);p.add_argument('--protected-core',type=pathlib.Path);p.add_argument('--package',type=pathlib.Path);p.add_argument('--remote-before',type=pathlib.Path);p.add_argument('--remote-after',type=pathlib.Path);a=p.parse_args()
assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
old=[]
for e in git('ls-tree','-rz',BASE).split(b'\0'):
 if not e:continue
 m,name=e.split(b'\t');mode,kind,oid=m.split();f=ROOT/name.decode()
 assert kind==b'blob' and f.read_bytes()==git('cat-file','blob',oid.decode()),name
 assert bool(f.stat().st_mode&stat.S_IXUSR)==(mode==b'100755'),name
 old.append(name.decode())
assert len(old)==1096
assert not set(git('diff',BASE,'--name-only').decode().splitlines())&set(old)
added=sorted(set(git('ls-files','--cached','--others','--exclude-standard').decode().splitlines())-set(old))
assert all(f.startswith(('docs/stage28o-','tests/stage28o/')) for f in added)
subprocess.run([sys.executable,'tests/stage28h/verify_freeze.py'],cwd=ROOT,check=True)
n=json.loads((ROOT/'docs/stage28n-source-manifest.json').read_text());m=json.loads((ROOT/'docs/stage28o-input-and-patch-manifest.json').read_text());changed={r['file']:r['output_sha256'] for r in m['patched_files']}
assert sha(ROOT/'docs/stage28n-source-manifest.json')==m['original_manifest_sha256']
assert sha(ROOT/'tests/stage28o/tinyusb-native.patch')==m['patch_sha256']
for row in n['vendor_inputs']:
 assert sha(a.original/row['file'])==row['sha256']
 assert sha(a.prototype/row['file'])==changed.get(row['file'],row['sha256'])
for row in m['patched_files']:assert sha(a.prototype/row['file'])==row['output_sha256']
dependency='NOT REQUESTED'
if a.protected_core:
 sys.path.insert(0,str(ROOT/'tools'));import patched_core
 patched_core.check_sources(a.protected_core,patched=True);dependency='PASS unchanged pinned protected core/SDK'
package='NOT REQUESTED'
if a.package:
 assert a.package.stat().st_size==n['artifact_verification']['package_size']
 assert sha(a.package)==n['artifact_verification']['package_sha256']
 with zipfile.ZipFile(a.package) as z:
  member=z.read('esp32-arduino-libs/esp32s3/lib/libarduino_tinyusb.a')
  assert hashlib.sha256(member).hexdigest()==n['artifact_verification']['sdk_archive_sha256']
  revisions=z.read('esp32-arduino-libs/versions.txt')
  assert hashlib.sha256(revisions).hexdigest()==n['artifact_verification']['versions_sha256']
  for label,key in [('tinyusb','tinyusb'),('lib-builder','builder'),('esp-idf','idf')]:
   line=next(v for v in revisions.decode().splitlines() if v.startswith(label+':'));prefix=line.split()[-1]
   assert len(prefix)>=7 and m[key].startswith(prefix), (label,prefix)
  if a.protected_core:
   archive=a.protected_core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3/lib/libarduino_tinyusb.a'
   assert sha(archive)==n['artifact_verification']['sdk_archive_sha256']
 package='PASS package/member and publisher-recorded revisions; no whole source-to-object attestation'
receipt='NOT AVAILABLE'
r=ROOT/'docs/stage28o-test-results.json'
if r.exists():
 report=json.loads(r.read_text());assert sha(ROOT/'docs/stage28o-input-and-patch-manifest.json')==report['patch_manifest_sha256']
 rows=report['primary']['results'];assert [v['id'] for v in rows]==['O%02d'%i for i in range(1,47)]
 assert report['primary']['counts']=={'PASS':46,'FAIL':0}
 assert sum(v['assertions'] for v in rows)==report['primary']['assertions']
 assert report['opt_in_disabled']['observations_match_baseline']
 assert report['unchanged_baseline']['assertions']==report['opt_in_disabled']['assertions']==131
 for row in report['inputs']:
  if row['file'].startswith('<project-root>/'):assert sha(ROOT/row['file'].removeprefix('<project-root>/'))==row['sha256'],row['file']
 receipt='PASS unique cases, exact tested source/config/patch, separate accounting'
remote='NOT REQUESTED'
if a.remote_before and a.remote_after:
 def refs(p):return dict(line.split()[::-1] for line in p.read_text().splitlines())
 before,after=refs(a.remote_before),refs(a.remote_after);assert len(before)==39
 assert all(after.get(k)==v for k,v in before.items())
 added_refs=set(after)-set(before)
 assert added_refs=={'refs/heads/stage28o-native-tagged-transfer-prototype'}
 assert after[next(iter(added_refs))]==git('rev-parse','HEAD').decode().strip()
 remote='PASS all39 previous refs unchanged; only new Stage28O branch added'
report={'status':'PASS','baseline':BASE,'historical_files_paths_modes':len(old),'frozen_stage26_files':235,'dependency':dependency,'package':package,'receipt':receipt,'remote':remote,'new_file_count':len(added),'new_files':[dict(file=f,size=(ROOT/f).stat().st_size,sha256=sha(ROOT/f)) for f in added if f!='docs/stage28o-integrity.json'],'integrity_self_excluded':True,'runtime_assertions':0}
a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='new_files'}))
