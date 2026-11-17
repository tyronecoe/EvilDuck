"""Checksummed engineering evidence archive; never a build or installer."""
import argparse,hashlib,json,os,pathlib,posixpath,subprocess,tarfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
SCRATCH=pathlib.Path('/workspace/scratch');ART=pathlib.Path('/workspace/artifacts')
FIRMWARE='de683669135fe5ccc5922f9883709194400672e5'
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def package_records(directory):
 # Progress/error streams are still open while this writer captures inputs.
 # Preserve completed construction/control records here; archive-writer logs
 # are delivered separately after the writer exits, never sampled live.
 return [p for p in directory.iterdir() if p.is_file() and not p.name.startswith('evidence-preservation')]
def main(output,meta):
 assert not output.exists() and not meta.exists();meta.mkdir(parents=True)
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 subprocess.run(['git','bundle','create',str(meta/'source-history.bundle'),'--all'],cwd=ROOT,check=True,capture_output=True)
 subprocess.run(['git','bundle','verify',str(meta/'source-history.bundle')],cwd=ROOT,check=True,capture_output=True)
 subprocess.run(['git','archive','--format=tar','--output='+str(meta/'packaging-source.tar'),head],cwd=ROOT,check=True)
 recovery=SCRATCH/'define-statements-dependency-recovery-v4';firmware=recovery/'firmware';tools=firmware/'data/packages/esp32/tools';sdk=tools/'esp32-arduino-libs/idf-release_v5.5-b66b5448-v1'
 roots=[SCRATCH/'define-statements-target-build-v1',SCRATCH/'define-independent-v1-authenticated',SCRATCH/'define-independent-v1-verification',SCRATCH/'define-independent-provenance-v2',
  firmware/'data/packages/esp32/hardware/esp32/3.3.0',tools/'esp-x32/2411',tools/'esptool_py',sdk/'esp32s3',firmware/'user/libraries',firmware/'data/packages/builtin',
  recovery/'sdk-source',pathlib.Path('/workspace/tooling/arduino/bin/arduino-cli')]
 roots += [p for p in sdk.iterdir() if p.is_file()]
 # Original failed/blocked evidence remains in its original separate directory.
 roots += [p for p in ART.iterdir() if p.name.startswith(('ROUTEB-DEFINE','DEFINE-CANDIDATE','evilduck-routeb-define-statements')) and p!=output]
 roots += [SCRATCH/n for n in ['define-statements-integration-v1','define-statements-adapter-mock-repair-v1','define-statements-ds02-journal-v1','define-statements-ds02-expectation-repair-v1','define-statements-ds02-helper-include-fix-v1','define-statements-prebuild-v1','define-statements-verifier-signature-v1','del-baseline-input-recovery-v1','define-statements-single-target-build-v1','define-statements-dependency-recovery-v1','define-statements-dependency-recovery-v2','define-statements-dependency-recovery-v3','define-statements-cli-init-recovery-v1']]
 roots += [p for p in recovery.iterdir() if p.is_file()]
 roots += [p for p in (firmware/'data').iterdir() if p.is_file() and 'index' in p.name] # no CLI inventory installation secret
 roots += package_records(SCRATCH/'define-statements-packaging-v1')
 prior_capture=SCRATCH/'define-statements-packaging-v1/evidence-initial-failure'
 if prior_capture.exists():roots.append(prior_capture)
 candidates={}
 for root in roots:
  assert root.exists(),root
  for p in ([root] if root.is_file() else root.rglob('*')):
   if p.is_file() or p.is_symlink():candidates[p.as_posix().lstrip('/')]=p
 # Include every directly consumed link/response/dependency file, not just roots.
 report=json.loads((SCRATCH/'define-statements-target-build-v1/report.json').read_text());extra=[pathlib.Path(r['file']) for r in report['linked_input_hashes']]
 for r in report['linked_input_hashes']:assert sha(r['file'])==r['sha256']
 commands=[e['arguments'] for e in json.loads((SCRATCH/'define-statements-target-build-v1/build/compile_commands.json').read_text())]+[report['link_command']]
 for cmd in commands:extra.extend(pathlib.Path(x[1:]) for x in cmd if x.startswith('@'))
 for label in ['reference','candidate']:
  receipt=json.loads((SCRATCH/'define-independent-v1-authenticated'/label/'measurement.json').read_text())
  for n,h in receipt['dependencies'].items():assert sha(n)==h;extra.append(pathlib.Path(n))
 for p in extra:assert p.is_file();candidates[p.as_posix().lstrip('/')]=p
 records=[]
 for n,p in sorted(candidates.items()):
  assert not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts
  if p.is_symlink():
   target=os.readlink(p);resolved=posixpath.normpath(posixpath.join(posixpath.dirname(n),target))
   assert not target.startswith('/') and not resolved.startswith('../'),'Unsafe evidence symlink: '+str(p)
   records.append(dict(file=n,kind='symlink',target=target))
  else:records.append(dict(file=n,kind='file',bytes=p.stat().st_size,sha256=sha(p)))
 package=ART/'evilduck-routeb-define-statements-h1-v1-independent-owner-review-v1.zip'
 (meta/'RESUME.md').write_text('''# Engineering evidence resume guide

Temporary workspace storage is NOT persistent storage. Download both archives
and their external checksum receipts into owner-controlled persistent storage.
No remote upload or permanent preservation service has been used.

This is engineering evidence for Linux x86_64, not the High Sierra installer.
The separate Mac owner-review ZIP is the only owner kit. No restoration or
verification command authorizes compilation, linking, hardware or installation.

1. Check the externally supplied SHA-256/size of this tar.gz before extraction.
   Inspect EVIDENCE-MANIFEST.json and archive member names/types in a fresh
   isolated Linux container. Members use relative workspace/... paths. Do not
   overlay an existing owner workspace or private backups. Preserve internal
   relative toolchain symlinks; do not execute archive members while inspecting.
2. Regular-file SHA-256, lengths and symlink targets are recorded. The archive
   includes actual ELF/BIN, all linked objects/archives, .su/.d records, map,
   compile/log/response bytes, S3 SDK and patched core, libraries and complete
   pinned toolchain. Existing index metadata, CLI configuration and tool receipts
   are evidence only; do not repeat initialization or dependency recovery.
3. Restore workspace/... into /workspace ONLY in the empty isolated container.
   source-history.bundle contains the local source history without .git config
   or credentials. Clone it as /workspace/EvilDuck, check out detached firmware
   checkpoint de683669135fe5ccc5922f9883709194400672e5, and copy only the three
   independent verifier sources from the verification preservation commit named
   in ARCHIVE-IDENTITY.json into tests/define_statements_independent/. This keeps
   Git HEAD/source provenance at the original firmware checkpoint, while the
   supplementary verifier files keep their separately recorded hashes. Do not
   run a builder or measurement-creation command. packaging-source.tar is a
   separate review snapshot at the later local packaging/closeout checkpoint;
   it must never be described as the source of this existing firmware image.
4. Verification needs matching host Python/tool runtime libraries. The recorded
   compiler query -print-prog-name=ld is not compilation; nm/readelf/objdump and
   inspection-only objcopy are used by the frozen predicates. Runtime stack peak
   and physical host delivery are not measured by those tools.
5. For a separately authorized engineering replay, invoke the independent
   verify_existing.py with --measurements pointing to the restored original
   define-independent-v1-authenticated directory and a NEW --output directory.
   Verification-only mode rejects absent/stale caches; do not use authenticate
   or create modes to replace them. Original firmware attempts are ONE and
   auxiliary invocations TWO. No additional compiler allowance exists here.
6. Original failed/blocked results remain in their original separate paths:
   historical DEL recovery, failed signature gate and first independent-v1
   provenance failure. The later provenance-v2 gate is PASS for software/artifact
   scope only. Its supplementary attestation is not original builder metadata.
   Working DEFINE-return and older source/text-v2 rollback identities remain
   distinct, with original archives and pins in the source history/owner kit.

The immutable binary hashes and source/revision identities are recorded in
ARCHIVE-IDENTITY.json. No newly calculated file hash is relabelled as historical
proof. Original receipts supply original pins; this inventory adds preservation
integrity for the captured files. No exact historical DEL ELF was recovered.
''')
 verification_commit=subprocess.check_output(['git','log','--format=%H','--all','--grep=^Preserve independent DEFINE artifact verifier'],cwd=ROOT,text=True).splitlines()[0]
 dump(meta/'ARCHIVE-IDENTITY.json',dict(build_id='ROUTEB-DEFINE-STATEMENTS-H1-v1',firmware_source_commit=FIRMWARE,verification_preservation_commit=verification_commit,packaging_source_commit=json.loads((SCRATCH/'define-statements-packaging-v1/construction-command.json').read_text())['packaging_commit'],closeout_commit=head,package=dict(file=package.name,bytes=package.stat().st_size,sha256=sha(package)),firmware_compilation_attempts=1,auxiliary_compiler_invocations=2,storage='Temporary workspace; owner must download to persistent storage',historical_gate='BLOCKED / EXACT HISTORICAL INPUT UNAVAILABLE',exclusions=['unrelated architectures','CLI inventory installation secret','private owner backups','Git configuration/credentials']))
 for p in sorted(meta.iterdir()):
  if p.is_file():candidates[p.name]=p;records.append(dict(file=p.name,kind='file',bytes=p.stat().st_size,sha256=sha(p)))
 dump(meta/'EVIDENCE-MANIFEST.json',dict(files=records,excluded_self='EVIDENCE-MANIFEST.json'))
 candidates['EVIDENCE-MANIFEST.json']=meta/'EVIDENCE-MANIFEST.json'
 with tarfile.open(output,'w:gz',compresslevel=5) as tar:
  for i,(name,p) in enumerate(sorted(candidates.items()),1):
   info=tar.gettarinfo(str(p),arcname=name);info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
   if info.isfile():
    with p.open('rb') as f:tar.addfile(info,f)
   else:tar.addfile(info)
   if i%3000==0:print('Archived',i,'members',flush=True)
 # Hash every archived payload; no target/native verification is repeated.
 expected={r['file']:r for r in records};verified=0
 with tarfile.open(output,'r:gz') as tar:
  for entry in tar:
   if entry.name=='EVIDENCE-MANIFEST.json':continue
   r=expected.pop(entry.name)
   if r['kind']=='symlink':assert entry.issym() and entry.linkname==r['target']
   else:
    assert entry.isfile() or entry.islnk();h=hashlib.sha256();count=0
    with tar.extractfile(entry) as f:
     for b in iter(lambda:f.read(1024*1024),b''):h.update(b);count+=len(b)
    assert h.hexdigest()==r['sha256'] and count==r['bytes'],entry.name
   verified+=1
 assert not expected
 receipt=dict(status='PASS',file=str(output),bytes=output.stat().st_size,sha256=sha(output),members_verified=verified+1,firmware_compilations=0,links=0,scope='Preservation archive integrity only; not repeated firmware verification',source_checkpoint=head)
 dump(meta/'archive-receipt.json',receipt);output.with_name(output.name+'.sha256').write_text(receipt['sha256']+'  '+output.name+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--metadata',type=pathlib.Path,required=True);a=p.parse_args();main(a.output,a.metadata)
