# Additive right-side modifier package tests; parent SHA256 da21a7ac6c880c6cbe3a2e1a04a467dd7c279e8dcd061ed00cd845acf94ed2e5
# Additive H1 experimental packaging checks. Historical suites remain unchanged.
# Parent SHA-256: c2000e5cf3458744f2e11229b0e65e3c7099720686366ca27b052cc955669a27
# Additive bounded-lock-wait adaptation of tests/source_text_v2/test_package.py
# Parent SHA-256: 25dcf7417c1ae7c700b0c77f308e7f988e181efbdf74523274fd80914548c5d5
# Additive source/text-portability adaptation of tests/payload_restart/test_package.py
# Parent SHA-256: 96fcf97d856f0d3519bebbe6f12d68b2d036c5d0d9e116c7c00a082b22092418
# Additive payload-restart adaptation of tests/text_keyboard/test_package.py
# Parent SHA-256: 188d52ac9cf504cd1223055cf7b5172169faf3daae828a285747e1be87f340ac
# Adapted for this release from unchanged tests/caps_stop/test_package.py.
# Original SHA-256: c7bce27b9c6b30cd3ca79357ac9ee489973cb61e208861dbfb6d214c58b58d27
#!/usr/bin/env python3
"""Fault-injection on disposable PUBLIC copies only. No owner files/device calls."""
import argparse,ast,copy,hashlib,importlib.util,json,pathlib,re,shutil,stat,subprocess,sys,tempfile,zipfile
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--archive',type=pathlib.Path,required=True);p.add_argument('--ota-template',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists();cases=[]
spec=importlib.util.spec_from_file_location('keyboard_bound_preflight',a.directory/'preflight.py');release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
validate,Rejected,rows,check_rows,ota=release.validate,release.Rejected,release.rows,release.check_rows,release.ota
def case(name,fn):
 try:fn();cases.append(dict(name=name,status='PASS'));print('PASS',name)
 except Exception as e:cases.append(dict(name=name,status='FAIL',diagnostic=type(e).__name__));print('FAIL',name,type(e).__name__)
def reject(fn):
 try:fn()
 except (Rejected,ValueError,KeyError):return
 raise AssertionError('unsafe input accepted')
def need(c):
 if not c:raise AssertionError('wrong result')
with tempfile.TemporaryDirectory(prefix='public-keyboard-control-package-') as td:
 t=pathlib.Path(td);d=t/'public';shutil.copytree(a.directory,d);table=t/'synthetic-table.bin';table.write_bytes((d/'expected-partitions.bin').read_bytes()+b'\xff'*1024);ot=t/'synthetic-otadata.bin';ot.write_bytes(a.ota_template.read_bytes());ota(ot.read_bytes())
 case('package_only_no_ranges_no_authorization',lambda:need(validate(d)['selected_write_ranges']==[] and validate(d)['installation_authorized'] is False))
 case('supplied_supported_metadata_app0_both_slots_no_authorization',lambda:need(validate(d,table,ot)['boot_selection_from_supplied_metadata']=='app0' and len(validate(d,table,ot)['selected_write_ranges'])==2 and not validate(d,table,ot)['installation_authorized']))
 case('table_without_ota_rejected',lambda:reject(lambda:validate(d,table)))
 original=table.read_bytes()
 for name,data in [('legacy_or_changed_layout',b'\xff'*4096),('truncated_table',original[:-1]),('changed_table_flag',original[:28]+bytes([2])+original[29:]),('nonerased_trailer',original[:-1]+b'\x00')]:
  def run(data=data):table.write_bytes(data);reject(lambda:validate(d,table,ot));table.write_bytes(original)
  case(name,run)
 original_ota=ot.read_bytes()
 for name,data in [('missing_ota_record',original_ota[:-1]),('unreviewed_active_slot',b'\x02'+original_ota[1:]),('corrupt_ota_crc',original_ota[:28]+b'\0'*4+original_ota[32:])]:
  def run(data=data):ot.write_bytes(data);reject(lambda:validate(d,table,ot));ot.write_bytes(original_ota)
  case(name,run)
 original_app=(d/'application.bin').read_bytes()
 for name,data in [('wrong_bin_hash',original_app[:-1]+bytes([original_app[-1]^1])),('truncated_bin',original_app[:-1]),('wrong_chip_header',original_app[:12]+b'\x00\x00'+original_app[14:])]:
  def run(data=data):(d/'application.bin').write_bytes(data);reject(lambda:validate(d));(d/'application.bin').write_bytes(original_app)
  case(name,run)
 manifest=(d/'manifest.json').read_bytes()
 mutations=[('old_source_identity',lambda m:m.update(source_commit='134b295deaebcb93f94beb63f2d46f102a7d6555')),('authorization_flag',lambda m:m.update(installation_authorized=True)),('false_canonical_claim',lambda m:m.update(official_runtime_encoding_verified=True)),('false_physical_claim',lambda m:m.update(physical_candidate_tested=True)),('wrong_manifest_build_id',lambda m:m.update(firmware_build_id='ROUTEB-UNRELATED')),('nvs_range',lambda m:m['proposed_writes'][0].update(offset=0x9000)),('full_slot_erase',lambda m:m['proposed_writes'][0].update(erase_end_exclusive=0x750000)),('only_one_slot',lambda m:m['proposed_writes'].pop()),('oversize_app',lambda m:m['proposed_writes'][1].update(bytes=0x740001)),('path_injection',lambda m:m['support_files'].update({'../owner.bin':dict(bytes=1,sha256='0'*64)}))]
 for name,mutate in mutations:
  def run(mutate=mutate):m=json.loads(manifest);mutate(m);(d/'manifest.json').write_text(json.dumps(m));reject(lambda:validate(d));(d/'manifest.json').write_bytes(manifest)
  case(name,run)
 def extra():(d/'private.json').write_text('{}');reject(lambda:validate(d));(d/'private.json').unlink()
 case('unexpected_private_member_rejected',extra)
 def support():p=d/'README.md';old=p.read_bytes();p.write_bytes(old+b' ');reject(lambda:validate(d));p.write_bytes(old)
 case('fixture_integrity',support)
 def no_observer():
  need(not (d/'observe_wait.py').exists())
  (d/'observe_wait.py').write_text('# unrelated historical observer\n')
  reject(lambda:validate(d));(d/'observe_wait.py').unlink()
 case('unrelated_historical_observer_not_published',no_observer)
 source_sheet=pathlib.Path(__file__).resolve().parents[2]/'docs/h1-right-modifiers-acceptance.md'
 reference_fixtures=re.findall(r'```ducky\n(.*?)```',source_sheet.read_text(),re.S)
 need(len(reference_fixtures)==4)
 for fixture,index in [('rm-shift.txt',0),('rm-modifier-taps.txt',1),('rm-stop.txt',2),('rm-malformed.txt',3)]:
  case('fixture_matches_reviewed_source_'+fixture,lambda fixture=fixture,index=index:need((d/fixture).read_bytes()==reference_fixtures[index].encode('ascii')))
 for fixture in ['rm-shift.txt','rm-modifier-taps.txt','rm-stop.txt','rm-malformed.txt']:
  def changed_fixture(fixture=fixture):
   p=d/fixture;saved=p.read_bytes();p.write_bytes(saved+b'REM altered\n');reject(lambda:validate(d));p.write_bytes(saved)
  case('bound_fixture_tamper_'+fixture,changed_fixture)
  def missing_fixture(fixture=fixture):
   p=d/fixture;saved=p.read_bytes();p.unlink();reject(lambda:validate(d));p.write_bytes(saved)
  case('bound_fixture_missing_'+fixture,missing_fixture)
 def zipcheck():
  with zipfile.ZipFile(a.archive) as z:
   need(z.testzip() is None);need(set(z.namelist())=={p.name for p in d.iterdir()});need(len(z.namelist())==len(set(z.namelist())));need(all(stat.S_ISREG(i.external_attr >> 16) for i in z.infolist()));need(all('/' not in i.filename and '\\' not in i.filename for i in z.infolist()))
   for n in z.namelist():need(z.read(n)==(d/n).read_bytes())
 case('archive_crc_members_and_exact_bytes',zipcheck)
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [table,ot]};validate(d,table,ot);after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [table,ot]}
 case('input_files_readonly',lambda:need(before==after))
 def linked_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['lock_feedback_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('new_linked_keyboard_policy_required',linked_policy_missing)
 def source_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['text_keyboard_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('new_text_keyboard_policy_required',source_policy_missing)
 def restart_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['payload_restart_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('new_payload_restart_policy_required',restart_policy_missing)
 def portability_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['source_text_v2_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('new_source_text_v2_policy_required',portability_policy_missing)

 def parent_portability_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['source_text_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('inherited_source_text_v1_policy_required',parent_portability_policy_missing)

 def timeout_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['timeout_wait_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('new_lock_wait_timeout_policy_required',timeout_policy_missing)
 def inherited_v2_pin_mismatch():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['source_text_v2_source_pin']={};p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('inherited_source_text_v2_composition_pin_required',inherited_v2_pin_mismatch)



 def lowercase_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['random_lowercase_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('inherited_lowercase_policy_required',lowercase_policy_missing)
 def uppercase_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['random_uppercase_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('inherited_uppercase_policy_required',uppercase_policy_missing)
 def randomization_policy_missing():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['randomization_jitter_verified']=False;p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('inherited_randomization_jitter_policy_required',randomization_policy_missing)


 def source_pin_mismatch():
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  v=json.loads(saved);v['inject_var_experimental_source_pin']={};p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m))
  reject(lambda:validate(d));p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 case('new_linked_composition_pin_required',source_pin_mismatch)


 def receipt_mutation(mutator):
  p=d/'build-receipt.json';saved=p.read_bytes();m=json.loads(manifest)
  try:
   v=json.loads(saved);mutator(v);p.write_text(json.dumps(v));m['support_files']['build-receipt.json']=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m));reject(lambda:validate(d))
  finally:p.write_bytes(saved);(d/'manifest.json').write_bytes(manifest)
 for name,mutator in [
  ('h1_link_verification_required',lambda v:v.update(inject_var_experimental_verified=False)),
  ('canonical_runtime_claim_rejected',lambda v:v.update(official_runtime_encoding_verified=True)),
  ('h1_build_id_required',lambda v:v['inject_var_build_adapter'].update(build_id='ROUTEB-UNRELATED')),
  ('inherited_timeout_pin_required',lambda v:v.update(timeout_wait_source_pin={})),
  ('h1_build_adapter_identity_required',lambda v:v['inject_var_build_adapter'].update(adapter_sha256='0'*64)),
  ('h1_link_adapter_identity_required',lambda v:v['inject_var_link_adapter'].update(adapter_sha256='0'*64)),
  ('h1_build_guard_removal_rejected',lambda v:v['inject_var_build_adapter'].update(inherited_safety_predicates_removed=1)),
  ('h1_link_guard_removal_rejected',lambda v:v['inject_var_link_adapter'].update(inherited_safety_predicates_removed=1)),
  ('h1_opt_in_build_selector_required',lambda v:v['report'].update(verified_cpp_extra_flags=v['report']['verified_cpp_extra_flags'].replace('-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1',''))),
  ('right_modifiers_link_required',lambda v:v.update(right_modifiers_verified=False)),
  ('right_modifiers_source_pin_required',lambda v:v.update(right_modifiers_source_pin={})),
  ('right_modifiers_build_id_required',lambda v:v['right_modifiers_build_adapter'].update(build_id='ROUTEB-UNRELATED')),
  ('right_modifiers_build_wrapper_required',lambda v:v['right_modifiers_build_adapter'].update(adapter_sha256='0'*64)),
  ('right_modifiers_link_wrapper_required',lambda v:v['right_modifiers_link_adapter'].update(adapter_sha256='0'*64)),
  ('right_modifiers_build_guard_removal_rejected',lambda v:v['right_modifiers_build_adapter'].update(inherited_safety_predicates_removed=1)),
  ('right_modifiers_link_guard_removal_rejected',lambda v:v['right_modifiers_link_adapter'].update(inherited_safety_predicates_removed=1)),
  ('right_modifiers_optin_required',lambda v:v['report'].update(verified_cpp_extra_flags=v['report']['verified_cpp_extra_flags'].replace('-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1',''))),
 ]:case(name,lambda mutator=mutator:receipt_mutation(mutator))
 def swapped_images():
  app=d/'application.bin';back=d/'rollback-application.bin';ab=app.read_bytes();bb=back.read_bytes()
  try:app.write_bytes(bb);back.write_bytes(ab);reject(lambda:validate(d))
  finally:app.write_bytes(ab);back.write_bytes(bb)
 case('candidate_and_rollback_cannot_be_swapped',swapped_images)
 def offline_cli():
  # The CLI has no installed metadata or serial port and must not produce a write plan.
  r=subprocess.run([sys.executable,str(d/'preflight.py'),'--directory',str(d)],capture_output=True,text=True)
  need(r.returncode==0);v=json.loads(r.stdout);need(v['hardware_access'] is False and v['selected_write_ranges']==[] and v['plan_ready'] is False and v['installed_metadata']=='NOT_SUPPLIED')
 case('first_offline_command_no_hardware_or_write_plan',offline_cli)
 case('all_plan_ranges_inside_apps_no_nonapplication_overlap',lambda:check_rows(rows()))
 case('required_installed_metadata_missing_rejected',lambda:reject(lambda:validate(d,require_installed=True)))
 case('rollback_plan_requires_same_metadata_and_two_pinned_slots',lambda:need(validate(d,table,ot,True,'rollback')['selected_write_ranges']==rows('rollback')))
 case('rollback_without_metadata_has_no_plan',lambda:need(validate(d,selected='rollback')['selected_write_ranges']==[]))
 case('unknown_image_selection_rejected',lambda:reject(lambda:validate(d,selected='unknown')))
 def rollback_corrupt():
  p=d/'rollback-application.bin';old=p.read_bytes();p.write_bytes(old[:-1]);reject(lambda:validate(d,table,ot,True,'rollback'));p.write_bytes(old)
 case('corrupt_rollback_rejected',rollback_corrupt)
 def manifest_rollback():
  m=json.loads(manifest);m['rollback_writes'][0]['offset']=0x9000;(d/'manifest.json').write_text(json.dumps(m));reject(lambda:validate(d));(d/'manifest.json').write_bytes(manifest)
 case('rollback_nvs_range_rejected',manifest_rollback)
 case('rollback_erase_regions_inside_apps',lambda:check_rows(rows('rollback'),'rollback'))
 def cli():
  r=subprocess.run([sys.executable,str(d/'preflight.py'),'--directory',str(d),'--require-installed'],capture_output=True,text=True);need(r.returncode==1 and json.loads(r.stdout)['reason']=='CURRENT_INSTALLED_METADATA_REQUIRED')
  r=subprocess.run([sys.executable,str(d/'preflight.py'),'--directory',str(d),'--require-installed','--installed-table',str(table),'--installed-otadata',str(ot),'--image','rollback'],capture_output=True,text=True);need(r.returncode==0 and json.loads(r.stdout)['selected_write_ranges']==rows('rollback'))
 case('bundled_cli_required_metadata_and_rollback_exit_status',cli)
 def symlink():
  p=d/'application.bin';p.rename(d/'temporarily-saved.bin');p.symlink_to(d/'temporarily-saved.bin');reject(lambda:validate(d));p.unlink();(d/'temporarily-saved.bin').rename(p)
 case('symlink_member_rejected',symlink)
 def py38():
  for n in ['preflight.py','gen_esp32part.py','installer.py']:ast.parse((d/n).read_text(),feature_version=(3,8))
 case('bundled_python_38_grammar',py38)
 def guide():
  s=(d/'INSTALL-MAC.md').read_text();r=(d/'ROLLBACK-MAC.md').read_text()
  need('bash install-macos.sh --action install --port' in s and 'bash rollback-macos.sh --port' in r)
  for text in [s,r]:
   for block in text.split('```bash')[1:]:
    cmd=block.split('```')[0];need('erase_flash' not in cmd and 'erase_region' not in cmd and '--erase-all' not in cmd and '--force' not in cmd)
    subprocess.run(['bash','-n'],input=cmd,text=True,check=True)
  need('ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1' in s and 'OWNER-CHECK.md' in s and 'python3 preflight.py --directory .' in s)
 case('guide_shell_syntax_and_app_only_gates',guide)
 def deterministic_zip():
  from package import archive
  second=t/'second.zip';archive(d,second);need(second.read_bytes()==a.archive.read_bytes())
 case('deterministic_rearchive_exact_bytes',deterministic_zip)

out=dict(counts={k:sum(r['status']==k for r in cases) for k in ['PASS','FAIL']},results=cases,fixtures='disposable public copies and pinned OTA initializer; no actual owner metadata supplied',hardware=False,native_macos_tested=False,sanitizers='N/A Python package logic; sender cleanup checks reported separately',installation_authorized=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
