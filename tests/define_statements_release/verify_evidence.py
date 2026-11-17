"""Verify the completed native/dependency evidence without re-execution."""
import pathlib,json,hashlib,sys,importlib.util
import argparse
parser=argparse.ArgumentParser(description='Read-only native/dependency evidence reuse; no tests or compiler')
parser.add_argument('--scratch-root',type=pathlib.Path,default=pathlib.Path('/workspace/scratch'))
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
R=pathlib.Path(__file__).resolve().parents[2];S=args.scratch_root
assert not args.output.exists(), 'Preserve evidence'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pins={
'define-statements-ds02-helper-include-fix-v1/gate-receipt.json':'4215ad8a58638e7b29c61215fc72627ff401a3749eeab98b09d85aebbc3ff5ef',
'define-statements-cli-init-recovery-v1/recovery-receipt.json':'98bfa3058389a247bc2472b1fa6abbfbfad1308c3f63ef275b1e71e4ca140505'}
for n,h in pins.items():assert sha(S/n)==h,n
D=json.loads((S/'define-statements-ds02-helper-include-fix-v1/gate-receipt.json').read_text())
assert D['status']=='PASS' and D['fresh_scenarios_executed']==13 and D['controls_executed']==D['controls_rejected']==10
for row in D['input_hashes']+D['evidence_files']:assert sha(row['file'])==row['sha256'],row
assert sha(S/'define-statements-ds02-helper-include-fix-v1/harness/native')==D['executable_sha256']
assert len(D['results'])==13 and all(r['exit']==0 and not r['stderr'] for r in D['results'])
old=json.loads((S/'define-statements-adapter-mock-repair-v1/repair-receipt.json').read_text());assert old['results'][0]==dict(case='DS01',exit=0,stdout='PASS DS01\n',stderr='')
assert old['results'][1]['stderr']=='delay cancellation emits no reports\n'
a=load(R/'tests/admission_diagnostics_release/prepare_sources.py','original_admission');f=load(R/'tests/define_statements/prepare_sources.py','original_define')
source=S/'define-statements-integration-v1/candidate/EvilDuckS3';native=S/'define-statements-ds02-helper-include-fix-v1/harness/sources'
p=a.pin();expected={r['file']:r['sha256'] for r in p['after']+p['unchanged']};expected['core.cpp']=f.parent()[1]['after_core_sha256'];expected['caps_trial.h']=sha(source/'caps_trial.h')
assert a.inventory(source)==expected and len(expected)==201
for n,h in expected.items():assert sha(native/n)==h,n
core=S/'define-statements-integration-v1/focused-core'
for name in ['core.cpp','core.h','shortcut_keys.h']:assert sha(core/name)==expected[name],name
assert (S/'define-statements-integration-v1/focused-core.log').read_text()=='PASS 34 focused scenarios\n'
provenance=json.loads((R/'tests/define_statements_release/native/provenance.json').read_text())
for row in provenance['inputs']:assert sha(R/'tests/define_statements_release/native'/row['file'])==row['sha256'],row
assert sha(S/'define-statements-ds02-helper-include-fix-v1/harness/static-response-api-mocks/network.h')==old['repaired_mock_sha256']
v=json.loads((S/'define-statements-dependency-recovery-v4/recovery-receipt.json').read_text());assert v['native_dependency_closure']==v['firmware_dependency_profile']=='PASS'
for r in v['recovered_native_file_inventory']:assert sha(r['destination'])==r['observed_sha256'],r['destination']
c=json.loads((S/'define-statements-cli-init-recovery-v1/recovery-receipt.json').read_text());assert c['status']=='PASS' and c['dependency_integrity']=='PASS'
assert c['no_network_check']==c['no_forbidden_process_check']==c['configuration_and_s3_properties']=='PASS'
for row in c['builtin_file_inventory']:assert sha(row['file'])==row['sha256'],row
cfg=pathlib.Path(c['configuration']);cv=json.loads(cfg.read_text())
firmware=S/'define-statements-dependency-recovery-v4/firmware'
assert cv==dict(directories=dict(data=str(firmware/'data'),downloads=str(firmware/'archives'),user=str(firmware/'user')),build_cache=dict(path=str(firmware/'unused-build-cache')),updater=dict(enable_notification=False))
for r in c['evidence_files']:assert sha(r['file'])==r['sha256'],r
sys.path.insert(0,str(R/'tools'));import feedback_core
pin=feedback_core.check_sources(pathlib.Path(v['isolated_core']),True)
props=dict(line.split('=',1) for line in (S/'define-statements-cli-init-recovery-v1/properties.stdout.txt').read_text().splitlines() if '=' in line)
import s3_validation
s3_validation.validate_properties(props)
assert pathlib.Path(props['runtime.platform.path']).resolve()==pathlib.Path(v['isolated_core']).resolve()
s3_validation.validate_csv(pathlib.Path(v['isolated_core']))
assert sha(props['compiler.path']+'xtensa-esp32s3-elf-g++')==v['compiler_sha256']
user=pathlib.Path(v['isolated_core']).parents[5]/'user'
framework=load(R/'tests/stage28w/prepare_sources.py','checkframework').frameworks(user)
neo=load(R/'tests/mac_install/core_inventory.py','checkneo').inventory(user/'libraries/Adafruit_NeoPixel')
assert neo['tree_sha256']==json.loads((R/'docs/mac-release-neopixel-pin.json').read_text())['inventory']['tree_sha256']
assert sha('/workspace/tooling/arduino/bin/arduino-cli')=='d2f96eddc84f76cae4148a9d8ed0fa8e203d70343970ae0b554220d0db462f46'
rows=[dict(file=str(S/n),sha256=sha(S/n)) for n in pins]
result=dict(status='PASS',receipt_pins=rows,adapter_fresh_prior=13,adapter_reused_DS01=1,negative_controls_rejected=10,ADM_assertions_emitted=121,DS_assertions='not emitted by these drivers',core_scenarios_reused=34,native_input_hashes_verified=len(D['input_hashes']),native_evidence_files_verified=len(D['evidence_files']),production_bindings_verified=201,v4_inventory_verified=len(v['recovered_native_file_inventory']),core_tree_sha256=pin['patched_tree_sha256'],framework=framework,neopixel_tree_sha256=neo['tree_sha256'],firmware_compilation_attempts=0,tests_rerun=0,configuration_sha256=sha(cfg),compiler_sha256=v['compiler_sha256'],FQBN=s3_validation.FQBN,application_slot_bytes=s3_validation.APP_BYTES,property_resolution='Reused verified CLI initialization recovery v1; not re-executed',v4_receipt_sha256=sha(S/'define-statements-dependency-recovery-v4/recovery-receipt.json'))
args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
