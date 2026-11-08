#!/usr/bin/env python3
"""Fresh preserved native and browser cases over the USB-observer composition.

Original drivers, case bodies, expectations, SDK mocks and sanitizer flags stay
hash-pinned. The reviewed backend and web deltas apply to disposable native
snapshots; the separately bound SDK-shaped DCD mock supplies the original-handler
symbol. No target compiler, hardware, payload, installer or external request.
"""
import argparse
import ast
from collections import Counter
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
BUILD_ID = 'ROUTEB-USB-ENUM-OBSERVER-H1-v1'
PARENTS = {
 'native': ('/workspace/scratch/define-labels-release/regressions-v1/native.json',
            '2ad98c56cd42c48e70458be99d8f7575216908ae51cc6802081f953097316edb',
            'previous_command_repeat_driver.cpp', 636, 27376),
 'del': ('/workspace/scratch/define-labels-release/regressions-v1/del.json',
         '27b5f3e1936ff1a5afd458221e4cfd7bea794ba317476675ff953b4c376f37c8',
         'del_alias_driver.cpp', 27, 797),
 'define': ('/workspace/scratch/define-labels-release/focused-v1.json',
            'b391c771232948cd5e60c81f86f3db7e4f623d443ebd11e526bd431284fc0db3',
            'define_labels_driver.cpp', 28, 374),
}
WEB_PINS = {
 'tests/dashboard_response_safety/test_native.py': '0cfc05c580b430ccea6489a4ad7b4e38fc466331165dd5766e37229688d4b78e',
 'tests/dashboard_response_safety/test_browser.py': '8d0bff34655580c40d8528b187a171b2b4401792c3f9478cfbfcfb8ef7c1d3ea',
 'tests/dashboard_cleanup/test_browser.py': '3713fa15a9d5ca9fa1bfe1fbfe4fde337af1b662c67c79921efe74aa05ce6166',
 'tests/editor_load_safety/test_browser.py': 'a5915a0b2a617f9090eab994e8a50eeeb1863d402cd2194aa9d783e0c5d617ef',
}
BASELINE = pathlib.Path('/workspace/scratch/define-labels-release/build-v1/candidate/EvilDuckS3')


def sha(path):
 return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
 spec = importlib.util.spec_from_file_location(name, path)
 value = importlib.util.module_from_spec(spec)
 spec.loader.exec_module(value)
 return value


def final_preparer(source):
 module = load(HERE / 'prepare_sources.py', 'usb_observer_regression_final')
 rows = module.verify_final(source)
 assert len(rows) == 201
 assert (pathlib.Path(source) / 'caps_trial.h').read_bytes().count(BUILD_ID.encode()) == 1
 return module, rows


def replace(text, before, after, changes, count=1):
 assert text.count(before) == count, (before, text.count(before))
 changes.append(dict(before=before, after=after, occurrences=count))
 return text.replace(before, after)


def adapt_mock_apis(command, work):
 """Add missing SDK-shaped APIs in disposable mocks, never original fixtures."""
 sdk_headers={
  pathlib.Path('/workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/cores/esp32/WString.h'):
   '4ae882b44440656ef99c685087e03e5102b36c217f15b1c8c4954c926bad100e',
  pathlib.Path('/workspace/tooling/arduino/user/libraries/ESP_Async_WebServer/src/ESPAsyncWebServer.h'):
   '25db7c8fb30943307b28b181722187a65576f6ee778eeb99e29b1ef8db7915ba'}
 for path,expected in sdk_headers.items():assert sha(path)==expected,'SDK API reference changed: '+str(path)
 includes = [pathlib.Path(v[2:]) for v in command if v.startswith('-I')]
 selected = next(p for p in includes if (p/'Arduino.h').is_file())
 original = selected/'Arduino.h'
 assert sha(original) == '01afd2b39213cc6abc92db9d26f4ebf7f774360c3e352c69f36a116698c962cb'
 copy = work/'observer-arduino-api-mocks'
 shutil.copytree(selected,copy)
 text, changes = original.read_text(), []
 text = replace(text,'  void reserve(size_t n) { value.reserve(n); }',
  '  bool reserve(unsigned int n) { try { value.reserve(n); return true; } catch (const std::bad_alloc&) { return false; } }\n'
  '  bool concat(const char *s, unsigned int n) { if (!s) return false; try { value.append(s,n); return true; } catch (const std::bad_alloc&) { return false; } }\n'
  '  bool concat(const char *s) { return s && concat(s,static_cast<unsigned int>(std::strlen(s))); }',changes)
 text = replace(text,'#include <string>','#include <string>\n#include <new>',changes)
 (copy/'Arduino.h').write_text(text)
 command = ['-I'+str(copy) if v=='-I'+str(selected) else v for v in command]
 # The pre-existing generated HTTP mock is already outside the repository.
 # Preserve its old send path and give beginResponse ownership to pointer-send.
 original_network = next(p/'network.h' for p in includes if (p/'network.h').is_file())
 assert sha(original_network) == 'ba2ec28f13f98516fab39114cb7bb6625ffc8565d2b7e03b7b991b1246604cfa'
 network_copy=work/'observer-http-api-mocks'
 shutil.copytree(original_network.parent,network_copy)
 network=network_copy/'network.h'
 command=['-I'+str(network_copy) if v=='-I'+str(original_network.parent) else v for v in command]
 network_before = sha(original_network)
 net, net_changes = original_network.read_text(), []
 net = replace(net,'#include <map>','#include <map>\n#include <memory>',net_changes)
 net = replace(net,'class AsyncWebServerRequest {',
  'struct AsyncWebServerResponse {\n'
  ' int code; String content; std::map<std::string,String> headers;\n'
  ' AsyncWebServerResponse(int c,const String&s):code(c),content(s){}\n'
  ' bool addHeader(const char*k,const char*v,bool=true){headers[k]=v;return true;}\n'
  '};\nclass AsyncWebServerRequest {',net_changes)
 net = replace(net,' void send_P(int c,const char*t,const char*s){send(c,t,s);}',
  ' AsyncWebServerResponse* beginResponse(int c,const char*,const String&s){return new AsyncWebServerResponse(c,s);}\n'
  ' void send(AsyncWebServerResponse*r){std::unique_ptr<AsyncWebServerResponse> owner(r);if(!r)throw std::runtime_error("null response");send(r->code,"application/json",r->content);}\n'
  ' void send_P(int c,const char*t,const char*s){send(c,t,s);}',net_changes)
 network.write_text(net)
 return command,dict(arduino=dict(original=str(original),original_sha256=sha(original),
  adapted=str(copy/'Arduino.h'),adapted_sha256=sha(copy/'Arduino.h'),edits=changes),
  http=dict(original=str(original_network),file=str(network),original_sha256=network_before,adapted_sha256=sha(network),edits=net_changes),
  sdk_header_pins={str(p):s for p,s in sdk_headers.items()},
  scope='Disposable API additions only; test bodies, previous send path and production sources unchanged; allocation/transport remain mocks')


def static_assertion_expectations(source):
 """Count the pinned probe's checks independently from resource byte lengths."""
 fixture=ROOT/'tests/dashboard_response_safety/native/probe.cpp'
 assert sha(fixture)=='aa95ccae06550cd11c4f7b87bcd3fb5406be81e7f64ab1e40d7e15737c03d8a8'
 probe=fixture.read_text()
 chunks=[int(n) for n in re.search(r'const size_t chunks\[\]=\{([^}]+)\}',probe)[1].split(',')]
 routes=re.findall(r'RESOURCE\("([^"]+)",([A-Z0-9_]+),"[^"]+",\d+\)',probe)
 assert len(routes)==12 and chunks==[0,1,7,0,1460,4096,23,0,8192]
 text=(pathlib.Path(source)/'webfiles.h').read_text()
 resources={n:len(v.encode()) for n,v in re.findall(r'static const char (\w+)\[\] PROGMEM = R"rawliteral\((.*?)\)rawliteral";',text,re.S)}
 def drains(length):
  turns=sent=0
  while sent<length:
   sent+=min(chunks[turns%len(chunks)],length-sent);turns+=1
  return 2*turns+3 # Chunk length/guard assertions and three stable EOF reads.
 rows={}
 for route,name in routes:rows['route_explicit_flash_'+route]=14+drains(resources[name])
 for route,_ in routes:rows['control_baseline_copy_'+route]=9
 for label in ['CSS_then_JS','JS_then_CSS']:rows['negative_old_'+label+'_50k']=12
 css,js=resources['STYLE_CSS'],resources['INDEX_JS']
 rows['concurrent_new_CSS_JS_same_50k']=24+drains(css)+drains(js)
 rows['new_JS_under_existing_old_CSS_pressure']=19+drains(js)
 rows['negative_old_largest_block_31935']=3
 rows['new_stream_largest_block_31935']=12+drains(js)
 rows['per_instance_cursor_cancel_independent']=10+drains(js-5)
 for route in ['/favicon.ico','/unrecognized.js']:rows['preserved_fallback_'+route]=6
 assert len(rows)==33
 # reset() checks lie outside reported rows: once per row and once at end,
 # plus the initial argc check. Every original check remains required.
 return dict(rows=rows,total_assertions=sum(rows.values())+len(rows)+2,
  probe_sha256=sha(fixture),resource_bytes=resources,chunks=chunks,unreported_checks=len(rows)+2)


def native_group(label, source, work, output):
 release, inventory = final_preparer(source)
 path, expected_sha, driver_name, expected_cases, expected_assertions = PARENTS[label]
 original = pathlib.Path(path)
 assert sha(original) == expected_sha, 'PARENT_RECEIPT_CHANGED_' + label
 previous = json.loads(original.read_text())
 assert previous['counts'] == dict(PASS=expected_cases, FAIL=0)
 assert previous['assertions'] == expected_assertions
 command = list(previous['command'])
 drivers = [pathlib.Path(v) for v in command if v.endswith('/' + driver_name)]
 assert len(drivers) == 1 and sha(drivers[0]) == previous['driver_sha256']
 old_source, old_work = drivers[0].parent, drivers[0].parent.parent
 for row in previous['source_bindings']:
  assert sha(row['native']) == row['sha256'], 'PARENT_MODULE_CHANGED_' + row['file']
 assert not work.exists() and not output.exists()
 work.mkdir(parents=True)
 destination = work / 'sources'
 shutil.copytree(old_source, destination)
 before = {str(f.relative_to(destination)): sha(f) for f in destination.rglob('*') if f.is_file()}
 backend = load(ROOT / 'tests/usb_os_observer/prepare_sources.py', 'usb_backend_delta_' + label)
 web = load(ROOT / 'tests/usb_os_observer_web/prepare_sources.py', 'usb_web_delta_' + label)
 backend.delta(destination)
 web.delta(destination)
 after = {str(f.relative_to(destination)): sha(f) for f in destination.rglob('*') if f.is_file()}
 assert before.keys() == after.keys()
 assert {n for n in before if before[n] != after[n]} == {'hid_backend.cpp', 'hid_backend.h', 'webserver.cpp', 'webfiles.h'}
 for value in command:
  if value.startswith('-I'):
   old = pathlib.Path(value[2:])
   if old.is_relative_to(old_work) and not old.is_relative_to(old_source):
    selected = work / old.relative_to(old_work)
    if not selected.exists(): shutil.copytree(old, selected)
 command = [v.replace(str(old_work), str(work)) for v in command]
 command, api_adaptations = adapt_mock_apis(command,work)
 # The new wrapper remains compiled and linked in native tests. Its original
 # handler and pinned event declarations are mocks, never the device SDK.
 mock_source = ROOT / 'tests/usb_os_observer/mocks'
 mock_dest = work / 'observer-mocks'
 shutil.copytree(mock_source, mock_dest)
 mock_tu = mock_dest / 'mock_real.cpp'
 assert mock_tu.is_file() and (mock_dest / 'device/dcd.h').is_file()
 command[1:1] = ['-DEVILDUCK_USB_ENUM_OBSERVER=1', '-I' + str(mock_dest)]
 at = command.index('-o')
 command[at + 1] = str(work / 'native')
 command.insert(at, str(mock_tu))
 assert '-fsanitize=address,undefined' in command and '-fno-omit-frame-pointer' in command
 assert '-fno-pie' in command and '-no-pie' in command
 production, mocks = [], []
 for value in command:
  if not value.endswith('.cpp'): continue
  file = pathlib.Path(value)
  if file.name == driver_name:
   assert sha(file) == before[driver_name]
  elif (source / file.name).exists():
   assert file.read_bytes() == (source / file.name).read_bytes(), 'PRODUCTION_MODULE_' + file.name
   production.append(dict(file=file.name, native=str(file), sha256=sha(file)))
  else:
   assert file.name in {'platform.cpp','lower.cpp','allocations.cpp','nvs_fixture.cpp','boot_fixture.cpp','mock_real.cpp'}, file.name
   mocks.append(dict(file=str(file), sha256=sha(file)))
 for name in ['core.h','shortcut_keys.h','adapter.h','backend_lease.inc','seam.inc','hid_backend.h','webserver.cpp','webfiles.h','EvilDuckS3.ino']:
  file = destination / name
  assert file.read_bytes() == (source / name).read_bytes(), 'PRODUCTION_HEADER_OR_INCLUDE_' + name
  production.append(dict(file=name, native=str(file), sha256=sha(file)))
 mock_bindings = [dict(file=str(f.relative_to(mock_dest)), sha256=sha(f)) for f in sorted(mock_dest.rglob('*')) if f.is_file()]
 compiled = subprocess.run(command, capture_output=True, text=True, timeout=360)
 result = dict(status='FAIL', command=command, compile_exit=compiled.returncode,
  compile_stdout=compiled.stdout, compile_stderr=compiled.stderr, results=[],
  parent_receipt=str(original), parent_receipt_sha256=sha(original),
  source_bindings=production, generated_mock_bindings=mocks,
  parent_snapshot_hashes=before, executed_snapshot_hashes=after,
  observer_mock_bindings=mock_bindings, driver_sha256=sha(destination / driver_name),
  disposable_mock_api_adaptations=api_adaptations,
  original_case_bodies_or_expectations_changed=False, sanitizer_flags_changed=False,
  added_compile_inputs=['EVILDUCK_USB_ENUM_OBSERVER=1','SDK-shaped DCD mock header','mock original-handler TU'],
  sanitizers='ASan/UBSan/detect_leaks=1', fresh_execution=True,
  native_fixture_identity_policy='Historical mock caps identity retained; all actual production modules and included webserver equal the final201 candidate.',
  hardware=False, real_hid=False, target_firmware_built=False)
 env = dict(os.environ, ASAN_OPTIONS='detect_leaks=1:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1')
 if compiled.returncode == 0:
  cases = [row['id'] for row in previous['results']]
  assert len(cases) == len(set(cases)) == expected_cases
  for case in cases:
   run = subprocess.run([str(work / 'native'), case], capture_output=True, text=True, timeout=45, env=env)
   matched = re.search(r'PASS ' + re.escape(case) + r' \((\d+) assertions\)', run.stdout)
   result['results'].append(dict(id=case, exit=run.returncode, stdout=run.stdout, stderr=run.stderr,
    assertions=int(matched[1]) if matched else 0,
    status='PASS' if run.returncode == 0 and matched and not run.stderr else 'FAIL'))
 result['counts'] = {s: sum(row['status'] == s for row in result['results']) for s in ['PASS','FAIL']}
 result['assertions'] = sum(row['assertions'] for row in result['results'])
 result['status'] = 'PASS' if compiled.returncode == 0 and result['counts'] == dict(PASS=expected_cases, FAIL=0) and result['assertions'] == expected_assertions else 'FAIL'
 result['observer_regression_binding'] = dict(wrapper_sha256=sha(__file__), final_build_id=BUILD_ID,
  final_source=str(source), source_manifest_sha256=sha(HERE / 'source-manifest.json'),
  full_source_inventory=inventory, actual_production_delta=['hid_backend.cpp','hid_backend.h','webserver.cpp','webfiles.h'],
  target_build=False, hardware_access=False)
 assert release.verify_final(source) == inventory
 output.write_text(json.dumps(result, indent=2) + '\n')
 return int(result['status'] != 'PASS')


def completed_native_receipt(path,source,inventory,label='native'):
 """Reuse a completed current-source group after unrelated runner plumbing fixes."""
 path=pathlib.Path(path);r=json.loads(path.read_text())
 original,original_sha,driver_name,cases,assertions=PARENTS[label]
 assert r['status']=='PASS' and r['compile_exit']==0
 assert not r['compile_stderr'] and not r['compile_stdout']
 assert r['counts']==dict(PASS=cases,FAIL=0) and r['assertions']==assertions
 assert r['parent_receipt']==original and r['parent_receipt_sha256']==original_sha==sha(original)
 parent=json.loads(pathlib.Path(original).read_text())
 assert [row['id'] for row in r['results']]==[row['id'] for row in parent['results']]
 drivers=[pathlib.Path(v) for v in r['command'] if v.endswith('/'+driver_name)]
 assert len(drivers)==1 and sha(drivers[0])==r['driver_sha256']==parent['driver_sha256']
 before,after=r['parent_snapshot_hashes'],r['executed_snapshot_hashes']
 assert before.keys()==after.keys() and {n for n in before if before[n]!=after[n]}=={'hid_backend.cpp','hid_backend.h','webserver.cpp','webfiles.h'}
 for name,expected in after.items():assert sha(drivers[0].parent/name)==expected
 assert r['fresh_execution'] and not r['original_case_bodies_or_expectations_changed'] and not r['sanitizer_flags_changed']
 assert r['sanitizers']=='ASan/UBSan/detect_leaks=1' and '-fsanitize=address,undefined' in r['command']
 assert '-fno-omit-frame-pointer' in r['command'] and '-fno-pie' in r['command'] and '-no-pie' in r['command']
 binding=r['observer_regression_binding']
 assert binding['full_source_inventory']==inventory and binding['source_manifest_sha256']==sha(HERE/'source-manifest.json')
 assert binding['final_source']==str(source) and binding['final_build_id']==BUILD_ID
 assert not r['hardware'] and not r['real_hid'] and not r['target_firmware_built']
 assert len(r['results'])==cases and len({row['id'] for row in r['results']})==cases
 for row in r['results']:
  assert row['status']=='PASS' and row['exit']==0 and not row['stderr']
  assert re.search(r'PASS '+re.escape(row['id'])+r' \('+str(row['assertions'])+r' assertions\)',row['stdout'])
 assert sum(row['assertions'] for row in r['results'])==assertions
 for row in r['source_bindings']:
  assert sha(row['native'])==row['sha256']==sha(source/row['file'])
 for row in r['generated_mock_bindings']:assert sha(row['file'])==row['sha256']
 api=r['disposable_mock_api_adaptations']
 assert sha(api['arduino']['original'])==api['arduino']['original_sha256']
 assert sha(api['arduino']['adapted'])==api['arduino']['adapted_sha256']
 assert sha(api['http']['file'])==api['http']['adapted_sha256']
 for name,expected in api['sdk_header_pins'].items():assert sha(name)==expected
 return r


def dashboard_browser_group(source,output):
 """Keep every historical check and add the fourth observer panel explicitly."""
 test=ROOT/'tests/dashboard_cleanup/test_browser.py'
 assert sha(test)==WEB_PINS['tests/dashboard_cleanup/test_browser.py']
 original=test.read_text();text=original;changes=[]
 text=replace(text,'            details = page.locator("#tab-diagnostics details")',
  '            self.check(await page.locator("#tab-diagnostics #usbObserverDiagnostic").count() == 1, "Expected one added capture-only panel")\n'
  '            details = page.locator("#tab-diagnostics details:not(#usbObserverDiagnostic)")',changes)
 text=replace(text,'            for button in await page.locator("#tab-diagnostics button").all():',
  '            await page.locator("#usbObserverDiagnostic > summary").click()\n'
  '            for button in await page.locator("#tab-diagnostics button").all():',changes)
 def checks(value):
  return Counter(ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(value))
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name)
   and n.func.value.id=='self' and n.func.attr=='check')
 before,after=checks(original),checks(text)
 assert not before-after and sum((after-before).values())==1
 assert 'self.check(await details.count() == 3, "Expected three collapsible diagnostic panels")' in text
 adapted=output.parent/(output.name+'-fixture.py');assert not adapted.exists();adapted.write_text(text)
 stdout=io.StringIO();argv=sys.argv;status=0
 try:
  sys.argv=[str(test),'--source',str(source/'webfiles.h'),'--output-dir',str(output)]
  with contextlib.redirect_stdout(stdout):
   try:exec(compile(text,str(test),'exec'),dict(__name__='__main__',__file__=str(test)))
   except SystemExit as error:status=int(error.code or 0)
 finally:
  sys.argv=argv
  (output.parent/(output.name+'.stdout.txt')).write_text(stdout.getvalue())
 result=output/'results.json';value=json.loads(result.read_text())
 value['observer_fixture_adapter']=dict(original_test_sha256=sha(test),adapted_test_sha256=sha(adapted),
  adapted_file=str(adapted),exact_adaptations=changes,all_original_check_calls_preserved=True,
  original_three_panel_expectation_preserved=True,added_fourth_panel_assertion=True,all_four_panels_expanded=True,
  original_check_call_count=sum(before.values()),adapted_check_call_count=sum(after.values()))
 result.write_text(json.dumps(value,indent=2)+'\n')
 return status,value,result


def web_group(source, work, output):
 release, inventory = final_preparer(source)
 for path, expected in WEB_PINS.items(): assert sha(ROOT / path) == expected
 prior = load(ROOT / 'tests/define_labels_release/prepare_sources.py', 'observer_web_prior_source')
 prior.verify_final(BASELINE)
 assert (source / 'webfiles.h').read_bytes() != (BASELINE / 'webfiles.h').read_bytes()
 old_pin = json.loads((ROOT/'tests/dashboard_response_safety/source-manifest.json').read_text())
 static_deltas = {r['file'] for r in old_pin['after']+old_pin['unchanged'] if sha(source/r['file']) != r['sha256']}
 assert static_deltas == {'core.cpp','shortcut_keys.h','caps_trial.h','hid_backend.cpp','hid_backend.h','webserver.cpp','webfiles.h'}, static_deltas
 # Re-execute the static native test against the current extracted handler and
 # resources. Historical SDK/archive pins and all case bodies stay intact.
 # Only old whole-tree/candidate identity expectations advance; the old complete
 # streaming-parent comparison is still performed with its exact parent bytes.
 test = ROOT / 'tests/dashboard_response_safety/test_native.py'
 text, changes = test.read_text(), []
 text = replace(text, 'assert digest(source_bytes["webserver.cpp"]) == EXPECTED_FIXED',
  'assert digest(source_bytes["webserver.cpp"]) == CURRENT_WEB_SHA', changes)
 text = replace(text, 'assert digest(source_bytes["webfiles.h"]) == PINS[BASELINE/"webfiles.h"]',
  'assert digest(source_bytes["webfiles.h"]) == CURRENT_ASSET_SHA', changes)
 before = ('    for row in manifest["after"] + manifest["unchanged"]:\n'
           '        assert digest((args.source/row["file"]).read_bytes()) == row["sha256"], row["file"]\n')
 after = ('    FINAL_VERIFY(args.source)\n'
          '    for row in manifest["after"] + manifest["unchanged"]:\n'
          '        if row["file"] not in CURRENT_STATIC_DELTAS:\n'
          '            assert digest((args.source/row["file"]).read_bytes()) == row["sha256"], row["file"]\n')
 text = replace(text, before, after, changes)
 text = replace(text, '== source_bytes["webserver.cpp"], "Source outside static handler changed"',
  '== PRIOR_WEB_BYTES, "Source outside static handler changed"', changes)
 work.mkdir(parents=True)
 native_out, native_result = work / 'static-native', work / 'static-native.json'
 stdout = io.StringIO()
 argv = sys.argv
 try:
  sys.argv = [str(test), '--source', str(source), '--output', str(native_out), '--results', str(native_result)]
  with contextlib.redirect_stdout(stdout):
   exec(compile(text, str(test), 'exec'), dict(__name__='__main__', __file__=str(test),
    CURRENT_WEB_SHA=sha(source/'webserver.cpp'), CURRENT_ASSET_SHA=sha(source/'webfiles.h'),
    PRIOR_WEB_BYTES=(BASELINE/'webserver.cpp').read_bytes(), FINAL_VERIFY=release.verify_final,
    CURRENT_STATIC_DELTAS={'core.cpp','shortcut_keys.h','caps_trial.h','hid_backend.cpp','hid_backend.h','webserver.cpp','webfiles.h'}))
 finally:
  sys.argv = argv
  (work/'static-native.stdout.txt').write_text(stdout.getvalue())
 native = json.loads(native_result.read_text())
 expected=static_assertion_expectations(source)
 assert native['counts'] == dict(PASS=33, FAIL=0)
 assert {r['name']:r['assertions'] for r in native['results']}==expected['rows']
 assert native['assertions']==expected['total_assertions']
 native['observer_current_source_binding'] = dict(full_inventory=inventory,
  original_test_sha256=sha(test), adapted_test_sha256=hashlib.sha256(text.encode()).hexdigest(),
  exact_adaptations=changes, original_sdk_and_case_assertions_preserved=True,
  prior_streaming_source_comparison_retained=True, source_manifest_sha256=sha(HERE/'source-manifest.json'))
 native['observer_assertion_accounting']=expected
 native_result.write_text(json.dumps(native,indent=2)+'\n')
 commands = [
 ('streamed-browser',[sys.executable,'-B',str(ROOT/'tests/dashboard_response_safety/test_browser.py'),
  '--source',str(source),'--native-output',str(native_out),'--native-results',str(native_result),
  '--output',str(work/'streamed-browser'),'--results',str(work/'streamed-browser.json')],work/'streamed-browser.json'),
 ('dashboard-browser',[sys.executable,'-B',str(ROOT/'tests/dashboard_cleanup/test_browser.py'),
  '--source',str(source/'webfiles.h'),'--output-dir',str(work/'dashboard-browser')],work/'dashboard-browser/results.json'),
 ('editor-browser',[sys.executable,'-B',str(ROOT/'tests/editor_load_safety/test_browser.py'),
  '--source',str(source/'webfiles.h'),'--output-dir',str(work/'editor-browser')],work/'editor-browser/results.json')]
 groups={'static-native':dict(exit=0,stderr='',counts=native['counts'],assertions=native['assertions'],receipt=str(native_result),receipt_sha256=sha(native_result),fresh_execution=True)}
 code=0
 for label,command,path in commands:
  if label=='dashboard-browser':
   status,data,path=dashboard_browser_group(source,work/'dashboard-browser')
   groups[label]=dict(exit=status,stderr='',counts=data['counts'],assertions=data['assertions'],receipt=str(path),receipt_sha256=sha(path),fresh_execution=True)
   if status or data['counts']['FAIL']:code=1
   continue
  run=subprocess.run(command,capture_output=True,text=True,timeout=360)
  (work/(label+'.stdout.txt')).write_text(run.stdout);(work/(label+'.stderr.txt')).write_text(run.stderr)
  row=dict(command=command,exit=run.returncode,stderr=run.stderr,fresh_execution=True)
  if path.exists():
   data=json.loads(path.read_text());row.update(counts=data['counts'],assertions=data['assertions'],receipt=str(path),receipt_sha256=sha(path))
  if run.returncode or row.get('counts',{}).get('FAIL',0):code=1
  groups[label]=row
 assert release.verify_final(source)==inventory
 result=dict(status='PASS' if code==0 else 'FAIL',groups=groups,source=str(source),
  source_hashes={n:sha(source/n) for n in ['webserver.cpp','webfiles.h']},
  full_source_inventory=inventory,historical_test_pins=WEB_PINS,wrapper_sha256=sha(__file__),
  fresh_execution=True,all_original_check_calls_and_legacy_expectations_preserved=True,
  dashboard_fixture_scope='Legacy three-panel selector plus explicit fourth observer panel assertion and expansion; original fixture unmodified',
  hardware_access=False,target_build=False,real_hid=False,external_requests=False)
 result['counts']={s:sum(g.get('counts',{}).get(s,0) for g in groups.values()) for s in ['PASS','FAIL']}
 result['assertions']=sum(g.get('assertions',0) for g in groups.values())
 output.write_text(json.dumps(result,indent=2)+'\n')
 return code,result


def resume_dashboard(previous,source,work,output):
 """Rerun only the three-panel fixture affected by the added observer panel."""
 _,inventory=final_preparer(source)
 old=json.loads(previous.read_text())
 assert old['status']=='FAIL' and old['full_inventory']==inventory
 assert old['source_manifest_sha256']==sha(HERE/'source-manifest.json')
 assert not old['target_build'] and not old['hardware_access'] and not old['real_hid']
 groups={}
 for label in ['native','del','define']:
  row=dict(old['groups'][label]);path=pathlib.Path(row['receipt'])
  assert sha(path)==row['receipt_sha256']
  result=completed_native_receipt(path,source,inventory,label)
  row.update(fresh_execution=False,current_stage_execution=True,reused_completed_current_stage=True,
   original_runner_sha256=result['observer_regression_binding']['wrapper_sha256'],current_runner_sha256=sha(__file__),
   reuse_reason='Already passed this frozen201-source candidate; only dashboard panel fixture changed')
  groups[label]=row
 prior_web=old['groups']['web'];path=pathlib.Path(prior_web['receipt'])
 assert sha(path)==prior_web['receipt_sha256']
 prior=json.loads(path.read_text());assert prior['full_source_inventory']==inventory
 assert prior['source_hashes']=={n:sha(source/n) for n in ['webserver.cpp','webfiles.h']}
 web={}
 for label in ['static-native','streamed-browser','editor-browser']:
  row=dict(prior['groups'][label]);path=pathlib.Path(row['receipt']);assert sha(path)==row['receipt_sha256']
  data=json.loads(path.read_text());assert row['exit']==0 and data['counts']['FAIL']==0
  if label=='static-native':
   expected=static_assertion_expectations(source)
   assert data['status']=='PASS' and data['source_hashes']==prior['source_hashes']
   assert {r['name']:r['assertions'] for r in data['results']}==expected['rows']
   assert data['assertions']==expected['total_assertions']
   for name,expected_sha in data['input_pins'].items():assert sha(name)==expected_sha
   for name,expected_sha in data['test_inputs'].items():assert sha(ROOT/name)==expected_sha
  else:assert data['source_sha256']==sha(source/'webfiles.h')
  assert all(r['status']=='PASS' for r in data['results'])
  row.update(fresh_execution=False,current_stage_execution=True,reused_completed_current_stage=True,
   reuse_reason='Passing exact-source receipt unaffected by dashboard panel selector adapter')
  web[label]=row
 failed=pathlib.Path(prior['groups']['dashboard-browser']['receipt'])
 assert sha(failed)==prior['groups']['dashboard-browser']['receipt_sha256']
 failure=json.loads(failed.read_text())
 assert failure['counts']==dict(PASS=6,FAIL=3)
 assert [(r['name'],r.get('diagnostic')) for r in failure['results'] if r['status']=='FAIL']==[
  ('layout-navigation-'+str(width),'AssertionError: Expected three collapsible diagnostic panels') for width in [1280,320,390]]
 status,data,path=dashboard_browser_group(source,work/'dashboard-browser')
 web['dashboard-browser']=dict(exit=status,stderr='',counts=data['counts'],assertions=data['assertions'],
  receipt=str(path),receipt_sha256=sha(path),fresh_execution=True)
 web_status='PASS' if status==0 and data['counts']==dict(PASS=9,FAIL=0) else 'FAIL'
 web_receipt=work/'web.json'
 web_result=dict(status=web_status,groups=web,source=str(source),full_source_inventory=inventory,
  source_hashes={n:sha(source/n) for n in ['webserver.cpp','webfiles.h']},wrapper_sha256=sha(__file__),
  assertions=sum(r['assertions'] for r in web.values()),counts={s:sum(r['counts'].get(s,0) for r in web.values()) for s in ['PASS','FAIL']},
  historical_test_pins=WEB_PINS,all_original_check_calls_and_legacy_expectations_preserved=True,
  resumed_from_receipt=str(previous),resumed_from_receipt_sha256=sha(previous),hardware_access=False,target_build=False,real_hid=False,external_requests=False)
 web_receipt.write_text(json.dumps(web_result,indent=2)+'\n')
 groups['web']=dict(exit=int(web_status!='PASS'),stderr='',receipt=str(web_receipt),receipt_sha256=sha(web_receipt),groups=web,fresh_execution=True)
 final_preparer(source)
 result=dict(status=web_status,groups=groups,wrapper_sha256=sha(__file__),source=str(source),full_inventory=inventory,
  source_manifest_sha256=sha(HERE/'source-manifest.json'),verified_native_cases=691,verified_native_assertions=28547,
  fresh_native_cases=0,fresh_native_assertions=0,resumed_native_cases=691,resumed_native_assertions=28547,
  verified_web_groups=web_result['counts']['PASS'],verified_web_assertions=web_result['assertions'],
  fresh_web_groups=data['counts']['PASS'],fresh_web_assertions=data['assertions'],
  resumed_web_groups=sum(r['counts']['PASS'] for name,r in web.items() if name!='dashboard-browser'),
  resumed_web_assertions=sum(r['assertions'] for name,r in web.items() if name!='dashboard-browser'),
  fresh_execution=True,fresh_execution_scope='All receipts executed on this frozen candidate in this stage; only dashboard9 rerun in final invocation; per-group flags disclose resumed checks',
  resumed_from_receipt=str(previous),resumed_from_receipt_sha256=sha(previous),target_build=False,hardware_access=False,real_hid=False,external_requests=False,
  limitations=old['limitations'])
 output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({n:result[n] for n in ['status','verified_native_cases','verified_native_assertions','verified_web_groups','verified_web_assertions','fresh_web_groups']},indent=2))
 return int(web_status!='PASS')


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--source',type=pathlib.Path,required=True)
 parser.add_argument('--core',type=pathlib.Path,required=True)
 parser.add_argument('--output-dir',type=pathlib.Path,required=True)
 parser.add_argument('--results',type=pathlib.Path,required=True)
 parser.add_argument('--completed-native-receipt',type=pathlib.Path,
  help='Preserve a passing636-case current-source receipt when resuming after runner-only changes')
 parser.add_argument('--completed-regressions-receipt',type=pathlib.Path,
  help='Verify and preserve passing groups; rerun only dashboard after additive observer-panel fixture adaptation')
 args=parser.parse_args()
 assert args.core.is_dir() and not args.output_dir.exists() and not args.results.exists()
 assert not args.output_dir.resolve().is_relative_to(ROOT)
 _,inventory=final_preparer(args.source)
 args.output_dir.mkdir(parents=True)
 if args.completed_regressions_receipt:
  assert not args.completed_native_receipt
  return resume_dashboard(args.completed_regressions_receipt,args.source,args.output_dir,args.results)
 groups,code={},0
 for label in ['native','del','define']:
  if label=='native' and args.completed_native_receipt:
   r=completed_native_receipt(args.completed_native_receipt,args.source,inventory)
   groups[label]=dict(exit=0,stderr='',receipt=str(args.completed_native_receipt),receipt_sha256=sha(args.completed_native_receipt),
    counts=r['counts'],assertions=r['assertions'],fresh_execution=False,current_stage_execution=True,reused_completed_current_stage=True,
    original_runner_sha256=r['observer_regression_binding']['wrapper_sha256'],current_runner_sha256=sha(__file__),
    arduino_api_mock_sha256=r['disposable_mock_api_adaptations']['arduino']['adapted_sha256'],
    http_api_mock_sha256=r['disposable_mock_api_adaptations']['http']['adapted_sha256'],
    reuse_reason='Completed on this exact frozen201-source candidate; verified original cases, all results, APIs, flags and hashes after runner-only HTTP mock path fix')
   continue
  output=args.output_dir/(label+'.json')
  status=native_group(label,args.source,args.output_dir/(label+'-build'),output)
  r=json.loads(output.read_text())
  groups[label]=dict(exit=status,stderr='',receipt=str(output),receipt_sha256=sha(output),counts=r['counts'],assertions=r['assertions'],fresh_execution=True)
  if status:code=1;break
 web=args.output_dir/'web.json'
 try:
  status,r=web_group(args.source,args.output_dir/'web-build',web)
  groups['web']=dict(exit=status,stderr='',receipt=str(web),receipt_sha256=sha(web),groups=r['groups'],fresh_execution=True)
  code=max(code,status)
 except Exception as error:
  groups['web']=dict(exit=1,error=type(error).__name__+': '+str(error),fresh_execution=True);code=1
 result=dict(status='PASS' if not code else 'FAIL',groups=groups,wrapper_sha256=sha(__file__),
  source=str(args.source),full_inventory=inventory,source_manifest_sha256=sha(HERE/'source-manifest.json'),
  verified_native_cases=sum(r.get('counts',{}).get('PASS',0) for r in groups.values()),
  verified_native_assertions=sum(r.get('assertions',0) for r in groups.values()),
  fresh_native_cases=sum(r.get('counts',{}).get('PASS',0) for r in groups.values() if not r.get('reused_completed_current_stage')),
  fresh_native_assertions=sum(r.get('assertions',0) for r in groups.values() if not r.get('reused_completed_current_stage')),
  resumed_native_cases=sum(r.get('counts',{}).get('PASS',0) for r in groups.values() if r.get('reused_completed_current_stage')),
  resumed_native_assertions=sum(r.get('assertions',0) for r in groups.values() if r.get('reused_completed_current_stage')),
  fresh_web_groups=sum(g.get('counts',{}).get('PASS',0) for g in groups.get('web',{}).get('groups',{}).values()),
  fresh_web_assertions=sum(g.get('assertions',0) for g in groups.get('web',{}).get('groups',{}).values()),
  reused_web_groups=0,target_build=False,hardware_access=False,real_hid=False,external_requests=False,
  fresh_execution_scope='All receipts executed on this frozen candidate in this stage; per-group fresh_execution distinguishes this invocation from a resumed completed group',
  limitations='Actual composed software with RAM-only mocks/Linux Chromium; not ESP32 runtime, real High Sierra HTTP or USB behavior.')
 args.results.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','fresh_native_cases','fresh_native_assertions','fresh_web_groups']},indent=2))
 return code


if __name__=='__main__':
 raise SystemExit(main())
