#!/usr/bin/env python3
"""Fault-injection on disposable PUBLIC copies only. No owner files/device calls."""
import argparse,copy,hashlib,json,pathlib,shutil,sys,tempfile,zipfile
sys.dont_write_bytecode=True
from preflight import validate,Rejected,rows,check_rows,ota
p=argparse.ArgumentParser();p.add_argument('--directory',type=pathlib.Path,required=True);p.add_argument('--archive',type=pathlib.Path,required=True);p.add_argument('--ota-template',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists();cases=[]
def case(name,fn):
 try:fn();cases.append(dict(name=name,status='PASS'));print('PASS',name)
 except Exception as e:cases.append(dict(name=name,status='FAIL',diagnostic=type(e).__name__));print('FAIL',name,type(e).__name__)
def reject(fn):
 try:fn()
 except (Rejected,ValueError,KeyError):return
 raise AssertionError('unsafe input accepted')
def need(c):
 if not c:raise AssertionError('wrong result')
with tempfile.TemporaryDirectory(prefix='public-shortcut-package-') as td:
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
 mutations=[('old_source_identity',lambda m:m.update(source_commit='134b295deaebcb93f94beb63f2d46f102a7d6555')),('authorization_flag',lambda m:m.update(installation_authorized=True)),('nvs_range',lambda m:m['proposed_writes'][0].update(offset=0x9000)),('full_slot_erase',lambda m:m['proposed_writes'][0].update(erase_end_exclusive=0x750000)),('only_one_slot',lambda m:m['proposed_writes'].pop()),('oversize_app',lambda m:m['proposed_writes'][1].update(bytes=0x740001)),('path_injection',lambda m:m['support_files'].update({'../owner.bin':dict(bytes=1,sha256='0'*64)}))]
 for name,mutate in mutations:
  def run(mutate=mutate):m=json.loads(manifest);mutate(m);(d/'manifest.json').write_text(json.dumps(m));reject(lambda:validate(d));(d/'manifest.json').write_bytes(manifest)
  case(name,run)
 def extra():(d/'private.json').write_text('{}');reject(lambda:validate(d));(d/'private.json').unlink()
 case('unexpected_private_member_rejected',extra)
 def support():p=d/'editor-only.duck';old=p.read_bytes();p.write_bytes(old+b' ');reject(lambda:validate(d));p.write_bytes(old)
 case('fixture_integrity',support)
 def zipcheck():
  with zipfile.ZipFile(a.archive) as z:
   need(z.testzip() is None);need(set(z.namelist())=={p.name for p in d.iterdir()});need(all('/' not in i.filename and '\\' not in i.filename for i in z.infolist()))
   for n in z.namelist():need(z.read(n)==(d/n).read_bytes())
 case('archive_crc_members_and_exact_bytes',zipcheck)
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [table,ot]};validate(d,table,ot);after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [table,ot]}
 case('input_files_readonly',lambda:need(before==after))
 case('all_plan_ranges_inside_apps_no_nonapplication_overlap',lambda:check_rows(rows()))
out=dict(counts={k:sum(r['status']==k for r in cases) for k in ['PASS','FAIL']},results=cases,fixtures='disposable public copies and pinned OTA initializer; no actual owner metadata supplied',hardware=False,native_macos_tested=False,sanitizers='N/A Python packaging/preflight only; no new C++',installation_authorized=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
