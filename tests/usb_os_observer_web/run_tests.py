#!/usr/bin/env python3
"""Actual capture HTTP/auth handlers + SDK WString; RAM-only lower APIs and JS mocks.

No device, target compiler, installer, payload, network request or private data.
The full composed source remains manifest-bound; extracted function bodies are
hashed verbatim and compiled, rather than reimplemented as test expectations.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
CORE = pathlib.Path('/workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/cores/esp32')
FIXTURES = ROOT / 'tests/dashboard_response_safety/native'
PINS = {'WString.cpp':'26d0f9519e50e7a78b66fc46be4cf4f6b8d7ed825ce70c1596bd424d975d8107',
        'WString.h':'4ae882b44440656ef99c685087e03e5102b36c217f15b1c8c4954c926bad100e'}


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def function(text, signature):
    assert text.count(signature) == 1, signature
    start = text.index(signature)
    opening = text.index('{', start)
    depth, state, escaped, i = 1, 'normal', False, opening + 1
    while depth:
        ch, nxt = text[i], text[i:i+2]
        if state in ('string', 'char'):
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == ('"' if state == 'string' else "'"):
                state = 'normal'
        elif state == 'line':
            if ch == '\n':
                state = 'normal'
        elif state == 'block':
            if nxt == '*/':
                state = 'normal'
                i += 1
        elif ch == '"':
            state = 'string'
        elif ch == "'":
            state = 'char'
        elif nxt == '//':
            state = 'line'
            i += 1
        elif nxt == '/*':
            state = 'block'
            i += 1
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        i += 1
    return text[start:i]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=pathlib.Path, required=True)
    p.add_argument('--output', type=pathlib.Path, required=True)
    p.add_argument('--results', type=pathlib.Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and not a.results.exists(), 'PRESERVE_PREVIOUS_RESULTS'
    assert not a.output.resolve().is_relative_to(ROOT)
    spec = importlib.util.spec_from_file_location('observer_web_native_source', HERE/'prepare_sources.py')
    layer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(layer)
    inventory = layer.verify_final(a.source)
    a.output.mkdir(parents=True)
    for n in ['Arduino.h', 'pgmspace.h', 'stdlib_noniso.h', 'esp32-hal-log.h', 'hooks.h']:
        shutil.copyfile(FIXTURES/n, a.output/n)
    for n, expected in PINS.items():
        assert sha(CORE/n) == expected, n
        shutil.copyfile(CORE/n, a.output/n)
    for n in ['hid_backend.h','backend_lease.h','feedback_diag.h']:
        shutil.copyfile(a.source/n, a.output/n)
    for n in ['http_fixture.h','test_integration.cpp']:
        shutil.copyfile(HERE/n, a.output/n)
    dcd_mocks=ROOT/'tests/usb_os_observer/mocks'
    shutil.copytree(dcd_mocks,a.output/'observer-mocks')
    web = (a.source/'webserver.cpp').read_text()
    signatures = ['static bool checkAuth(AsyncWebServerRequest *req)',
                  'static void sendAuthRequired(AsyncWebServerRequest *req)',
                  'static bool authorize(AsyncWebServerRequest* req, bool headerOnly=false)',
                  'static void handleUsbObservations(AsyncWebServerRequest* req)']
    bodies = [function(web, s) for s in signatures]
    (a.output/'actual_handlers.inc').write_text('\n\n'.join(bodies)+'\n')
    backend = (a.source/'hid_backend.cpp').read_text()
    state = function(backend, 'const char* stateName(State state)')
    (a.output/'actual_state_name.inc').write_text(state+'\n')
    observer = function(backend,'namespace usb_observer {')
    wrapper = function(backend,'extern "C" __attribute__((noinline)) void __wrap_dcd_event_handler(dcd_event_t const* event,bool inIsr)')
    (a.output/'actual_observer.inc').write_text(observer+'\nextern "C" void __real_dcd_event_handler(dcd_event_t const*,bool);\n'+wrapper+'\n')
    shutil.copyfile(HERE/'test_http.cpp', a.output/'probe.cpp')
    flags = ['-std=c++17','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',
             '-fno-pie','-ffunction-sections','-fdata-sections','-DEVILDUCK_PORTABLE_ROUTE_B=1',
             '-DEVILDUCK_USB_ENUM_OBSERVER=1','-I'+str(a.output)]
    commands = [['g++']+flags+['-include',str(a.output/'hooks.h'),'-c',str(a.output/'WString.cpp'),'-o',str(a.output/'WString.o')],
                ['g++']+flags+[str(a.output/'probe.cpp'),str(a.output/'WString.o'),'-Wl,--gc-sections','-no-pie','-o',str(a.output/'native')],
                ['g++']+flags+['-DEVILDUCK_HOST_TEST=1','-I'+str(a.output/'observer-mocks'),str(a.output/'test_integration.cpp'),str(a.output/'observer-mocks/mock_real.cpp'),str(a.output/'WString.o'),'-Wl,--gc-sections','-no-pie','-pthread','-o',str(a.output/'integration')]]
    compilation = []
    for index, command in enumerate(commands):
        run = subprocess.run(command,capture_output=True,text=True,timeout=120)
        (a.output/('compile-%d.stdout.txt'%index)).write_text(run.stdout)
        (a.output/('compile-%d.stderr.txt'%index)).write_text(run.stderr)
        compilation.append(dict(command=command,exit=run.returncode,stdout=run.stdout,stderr=run.stderr))
        assert run.returncode == 0, run.stderr
    env = dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    native = subprocess.run([str(a.output/'native'),str(a.output)],capture_output=True,text=True,timeout=60,env=env)
    (a.output/'native.stdout.txt').write_text(native.stdout)
    (a.output/'native.stderr.txt').write_text(native.stderr)
    assert native.returncode == 0 and not native.stderr, native.stderr
    parsed = [json.loads(l) for l in native.stdout.splitlines()]
    cases, summary = parsed[:-1], parsed[-1]
    assert len(cases) == 20 and summary['groups'] == 20 and summary['status'] == 'PASS'
    assert sum(row['assertions'] for row in cases) == summary['assertions']
    integration=subprocess.run([str(a.output/'integration'),str(a.output)],capture_output=True,text=True,timeout=60,env=env)
    (a.output/'integration.stdout.txt').write_text(integration.stdout)
    (a.output/'integration.stderr.txt').write_text(integration.stderr)
    assert integration.returncode==0 and not integration.stderr, integration.stderr
    integrated=[json.loads(line) for line in integration.stdout.splitlines()]
    integration_cases,integration_summary=integrated[:-1],integrated[-1]
    assert len(integration_cases)==8 and integration_summary['groups']==8 and integration_summary['status']=='PASS'
    assert sum(row['assertions'] for row in integration_cases)==integration_summary['assertions']
    fieldset = {'order','port','bmRequestType','bRequest','wValue','wIndex','wLength'}
    outputs = {}
    for name in ['empty','complete','maximum','coherent','integration-complete','integration-unsupported']:
        f = a.output/(name+'.json')
        data = json.loads(f.read_text())
        assert data['schema'] == 'evilduck-usb-observer-v1'
        assert data['classification'] == 'UNKNOWN' and data['classificationReason'] == 'NO_VALIDATED_RULE'
        assert data['count'] == len(data['records']) <= 64
        assert all(set(record)==fieldset for record in data['records'])
        assert not (set(data) & {'password','payload','body','keys','report','strings','hostname','file'})
        outputs[name] = dict(bytes=f.stat().st_size,sha256=sha(f),records=data['count'])
    ui = subprocess.run(['node',str(HERE/'test_ui.cjs'),str(a.source/'webfiles.h'),str(a.output)],capture_output=True,text=True,timeout=30)
    (a.output/'ui.stdout.txt').write_text(ui.stdout)
    (a.output/'ui.stderr.txt').write_text(ui.stderr)
    assert ui.returncode==0 and not ui.stderr, ui.stderr
    js = json.loads(ui.stdout)
    assert js['counts'] == dict(PASS=12,FAIL=0)
    assert layer.verify_final(a.source) == inventory
    value = dict(status='PASS',counts=dict(PASS=len(cases)+len(integration_cases)+js['counts']['PASS'],FAIL=0),
                 assertions=summary['assertions']+integration_summary['assertions']+js['assertions'],http=dict(counts=dict(PASS=20,FAIL=0),assertions=summary['assertions'],cases=cases),
                 integration=dict(counts=dict(PASS=8,FAIL=0),assertions=integration_summary['assertions'],cases=integration_cases,exit=integration.returncode,stdout=integration.stdout,stderr=integration.stderr,observer_namespace_sha256=hashlib.sha256(observer.encode()).hexdigest(),wrapper_sha256=hashlib.sha256(wrapper.encode()).hexdigest(),driver_sha256=sha(HERE/'test_integration.cpp'),mock_bindings=[dict(file=str(p.relative_to(dcd_mocks)),sha256=sha(p)) for p in sorted(dcd_mocks.rglob('*')) if p.is_file()]),
                 ui=js,source=str(a.source),full_source_inventory=inventory,
                 source_manifest_sha256=sha(HERE/'source-manifest.json'),source_bindings=[dict(file=n,sha256=sha(a.source/n)) for n in ['webserver.cpp','webfiles.h','hid_backend.h','hid_backend.cpp','feedback_diag.h']],
                 extracted_functions=[dict(signature=s,sha256=hashlib.sha256(b.encode()).hexdigest()) for s,b in zip(signatures,bodies)],
                 state_name_sha256=hashlib.sha256(state.encode()).hexdigest(),framework_pins=PINS,generated_outputs=outputs,
                 compilation=compilation,native=dict(exit=native.returncode,stdout=native.stdout,stderr=native.stderr),
                 sanitizers=['ASan','UBSan','leak detection'],runner_sha256=sha(__file__),driver_sha256=sha(HERE/'test_http.cpp'),
                 boundary='Actual HTTP/auth functions and SDK WString; isolated HTTP cases mock capture snapshots. Integrated cases compile the verbatim actual capture namespace and DCD wrapper, with mocked event delivery, original handler, request transport, execution locks, boot context and settings. UI manual-export code uses inert DOM/fetch/download mocks and actual integrated JSON outputs.',
                 firmware_built=False,hardware_access=False,real_hid=False,network=False)
    a.results.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({k:value[k] for k in ['status','counts','assertions','source']},indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
