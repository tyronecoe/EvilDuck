"""Additive receipt-bound admission packaging. No verifier/build execution."""
import argparse,ast,hashlib,importlib.util,json,pathlib,re,shutil,stat,subprocess,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
EVIDENCE=pathlib.Path('/workspace/artifacts/DEFINE-CANDIDATE-INDEPENDENT-v1-PROVENANCE-v2')
BUILD=pathlib.Path('/workspace/scratch/define-statements-target-build-v1')
FIRMWARE='de683669135fe5ccc5922f9883709194400672e5';BUILD_ID='ROUTEB-DEFINE-STATEMENTS-H1-v1'
PACKAGE='evilduck-routeb-define-statements-h1-v1-independent-owner-review-v1'
PARENT_ZIP=ROOT/'downloads/evilduck-routeb-admission-diagnostics-h1-macos-review-v1.zip';PARENT_SHA='05fdff0cdb7a0d4336f8dc219c3a501cc7349c9200f95c2f54a36bb9cccffd81'
APP_SHA='524805fbde1af49b908b156e0eb50de48393b8e2810efcf0eaddba931408012e';ELF_SHA='cd82758717bf0e6e78aa8a582dff7b01de99ac14a62923b12cd104de8c56f490'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def parent():
 assert sha(PARENT_ZIP)==PARENT_SHA
 return load(ROOT/'tests/admission_diagnostics_package/package.py','frozen_admission_packaging')
def fixture_bytes():
 return {'DS01_STATEMENTS.txt':b'DELAY 5000\nDEFINE #STEP $count = ($count + 1)\nDEFINE #MARK STRINGLN ROUTEB_DEFINE_PASS\nVAR $count = 0\n#STEP\nIF ($count == 1) THEN\n#MARK\nEND_IF\n',
 'DS02_DELAY_STOP.txt':b'DELAY 5000\nDEFINE #WAIT DELAY 10000\n#WAIT\nSTRINGLN UNEXPECTED\n',
 'DS03_RECOVERY.txt':b'DELAY 5000\nSTRINGLN recovery_ok\n',
 'DS04_REJECT.txt':b'DELAY 5000\nDEFINE #BAD VAR $x = 1\n#BAD\n'}
def template(bound):
 old=(ROOT/'tests/admission_diagnostics_package/package_preflight.py').read_text()
 prefix=old.split('def validate(',1)[0].replace('RELEASE=None','RELEASE='+repr(bound),1).replace("ACTUAL_BUILD_ID='ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1'","ACTUAL_BUILD_ID='"+BUILD_ID+"'",1)
 prefix+='\nSUPPORT=set('+repr(sorted(bound['support']))+')\n'
 original=old[old.index('def validate('):old.index('def main():')]
 initial=original[:original.index(' receipt=json.loads')].replace("'evilduck-routeb-admission-diagnostics-h1-macos-review-v1'",repr(PACKAGE))
 working=original[original.index(' # Working return is an exact'):original.index(' admission_tests_data=')]
 tail=original[original.index(' rollback_receipt='):]
 provider=(HERE/'package_preflight.py').read_text()
 # Original safety prefix, nested-return validation, rollback and installed-state
 # tail retain byte-identical conditions. Only evidence-provider validation changes.
 return prefix+'\n'+provider+'\n'+initial+' validate_evidence(d,m)\n'+working+tail+old[old.index('def main():'):]
def prepare(directory,packaging_commit,verification_commit):
 assert not directory.exists();assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==packaging_commit
 for p in HERE.glob('*.py'):assert subprocess.check_output(['git','show',packaging_commit+':'+str(p.relative_to(ROOT))],cwd=ROOT)==p.read_bytes()
 summary=json.loads((EVIDENCE/'summary.json').read_text());assert summary['status']=='INDEPENDENT ARTIFACT GATE PASS / NOT INSTALLED'
 for row in json.loads((EVIDENCE/'MANIFEST.json').read_text())['files']:assert sha(EVIDENCE/row['file'])==row['sha256']
 for n,h in summary['identities']['independent_verifier_files'].items():assert hashlib.sha256(subprocess.check_output(['git','show',verification_commit+':'+n],cwd=ROOT)).hexdigest()==h
 assert sha(BUILD/'build/EvilDuckS3.ino.bin')==APP_SHA and sha(BUILD/'build/EvilDuckS3.ino.elf')==ELF_SHA
 p=parent();p.verify_working_kit();directory.mkdir(parents=True)
 with zipfile.ZipFile(PARENT_ZIP) as z:
  for n in ['rollback-application.bin','expected-partitions.bin','rollback-build-receipt.json','gen_esp32part.py','APACHE-2.0.txt','source-LICENSE.txt','working-define-labels-macos-review-v1.zip','install-macos.sh','rollback-macos.sh']:(directory/n).write_bytes(z.read(n))
  installer=z.read('installer.py').decode()
 copies={'application.bin':BUILD/'build/EvilDuckS3.ino.bin','original-build-report.json':BUILD/'report.json','build-inputs.json':BUILD/'build-inputs.json','independent-gate-summary.json':EVIDENCE/'summary.json','independent-gate-result.json':EVIDENCE/'gate/result.json','independent-release-receipt.json':EVIDENCE/'gate/release.json','independent-target-receipt.json':EVIDENCE/'gate/target.json','post-build-attestation.json':EVIDENCE/'gate/supplementary-attestation.json','independent-layout.json':EVIDENCE/'gate/layout.json','independent-stack.json':EVIDENCE/'gate/stack.json'}
 for n,src in copies.items():shutil.copyfile(src,directory/n)
 for n in ['README.md','OWNER-CHECK.md','INSTALL-MAC.md','ROLLBACK-MAC.md','RETURN-WORKING.md']:
  shutil.copyfile(ROOT/'docs/define-statements-review'/n,directory/n)
 for n,data in fixture_bytes().items():(directory/n).write_bytes(data)
 (directory/'FIXTURE-SHA256.txt').write_text(''.join(hashlib.sha256(b).hexdigest()+'  '+n+'\n' for n,b in fixture_bytes().items()))
 support={f.name for f in directory.iterdir()}-{'application.bin','rollback-application.bin','expected-partitions.bin'};support|={'preflight.py','installer.py'}
 pins={n:sha(directory/n) for n in support if n not in ['preflight.py','installer.py']}
 bound=dict(source_commit=packaging_commit,firmware_source_commit=FIRMWARE,verification_source_commit=verification_commit,application_bytes=1451184,application_sha256=APP_SHA,elf_sha256=ELF_SHA,build_inputs_sha256=summary['identities']['complete_build_inputs_file_sha256'],verifier_identity_sha256=summary['identities']['independent_verifier_identity_sha256'],core_sha256='b9c53bd3632e049e674ea66bf6c110bf22bb51c35f0d46ae75e0f5825d069d99',support=sorted(support),pins=pins)
 (directory/'preflight.py').write_text(template(bound))
 assert len(re.findall(r'^RELEASE_BINDING=.*$',installer,re.M))==1
 installer=re.sub(r'^RELEASE_BINDING=.*$',"RELEASE_BINDING="+repr(dict(preflight_sha256=sha(directory/'preflight.py'))),installer,flags=re.M)
 (directory/'installer.py').write_text(installer)
 v=load(directory/'preflight.py','new_package_preflight')
 m=dict(package_id=PACKAGE,status_label='REVIEW CANDIDATE / NOT INSTALLED',label='REVIEW CANDIDATE / NOT INSTALLED',source_commit=packaging_commit,firmware_source_commit=FIRMWARE,verification_source_commit=verification_commit,firmware_build_id=BUILD_ID,independent_gate='DEFINE-CANDIDATE-INDEPENDENT-v1',historical_gate='BLOCKED / EXACT HISTORICAL INPUT UNAVAILABLE',application_bytes=1451184,application_sha256=APP_SHA,application_elf_sha256=ELF_SHA,table_sha256=v.TABLE_SHA,rollback_bytes=v.ROLLBACK_BYTES,rollback_sha256=v.ROLLBACK_SHA,working_firmware_return=p.working_identity(),installation_authorized=False,hardware=False,physical_candidate_tested=False,official_runtime_encoding_verified=False,hardware_acceptance='PENDING',runtime_peak_stack_measured=False,update_method='FUTURE_ROM_APP_ONLY_BOTH_SLOTS',proposed_writes=v.rows(),rollback_writes=v.rows('rollback'),required_installed_otadata_sha256=v.OTA_SHA,protected_nonapplication_regions='all; bootloader/table/NVS/otadata/SPIFFS/coredump excluded',unsigned_integrity_only=True,support_files={n:dict(bytes=(directory/n).stat().st_size,sha256=sha(directory/n)) for n in sorted(support)})
 write(directory/'manifest.json',m)
 return v.validate(directory)
def archive(directory,destination):return parent().archive(directory,destination)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--directory',type=pathlib.Path,required=True);a.add_argument('--archive',type=pathlib.Path,required=True);a.add_argument('--packaging-commit',required=True);a.add_argument('--verification-commit',required=True);x=a.parse_args();print(json.dumps(prepare(x.directory,x.packaging_commit,x.verification_commit),indent=2));print(json.dumps(archive(x.directory,x.archive),indent=2))
