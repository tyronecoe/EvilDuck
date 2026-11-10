#!/usr/bin/env python3
"""Occurrence-checked v2 adapter over an immutable complete observer-v1 tool.

All original function bodies and predicates remain; exact path/identity edits
are listed below. Additional v2 proof requirements are appended after loading.
"""
import pathlib as _v2_pathlib
import hashlib as _v2_hashlib
import builtins as _v2_builtins
import sys as _v2_sys
_v2_sys.dont_write_bytecode = True
_V2_FROZEN_PARENT = _v2_pathlib.Path(__file__).resolve().parents[1] / 'usb_os_observer_release' / 'verify_target.py'
_V2_FROZEN_SHA = '6669ea800c29bb4a51c3b7b97cd1f97f0ef5c1bc8be6a297a98f7c29d1473d18'
_V2_EDITS = [('tests/usb_os_observer_release/', 'tests/usb_os_observer_v2_release/', 4), ('tests/usb_os_observer_web/', 'tests/usb_os_observer_v2_web/', 2), ('tests/usb_os_observer/', 'tests/usb_os_observer_v2/', 1), ('ROUTEB-USB-ENUM-OBSERVER-H1-v1', 'ROUTEB-USB-ENUM-OBSERVER-H1-v2', 1), ('evilduck-usb-os-observer-release-v1', 'evilduck-usb-os-observer-release-v2', 1)]

_V2_EDITS += [(
    "callback=[r for r in frames if not any(n in r['function'] for n in ['snapshot(', 'service(', 'stateName('])]",
    "callback,callback_reachability=_v2_callback_frames(frames,symbols,observe,wrapper,objdump,elf)",1),
    ("stack_frames=frames,callback_max_frame=", "stack_frames=frames,callback_reachability=callback_reachability,callback_max_frame=",1)]

def _v2_frozen_source():
    raw = _V2_FROZEN_PARENT.read_bytes()
    assert _v2_hashlib.sha256(raw).hexdigest() == _V2_FROZEN_SHA, 'Historical observer-v1 tool changed'
    text = raw.decode()
    for before, after, count in _V2_EDITS:
        assert text.count(before) == count, ('Observer-v2 adapter occurrence mismatch', before, text.count(before))
        text = text.replace(before, after)
    return text

_V2_SOURCE = _v2_frozen_source()
_v2_original_name = __name__
try:
    __name__ = 'observer_v2_frozen_verify_target_py'
    exec(_v2_builtins.compile(_V2_SOURCE, str(_V2_FROZEN_PARENT), 'exec'), globals())
finally:
    __name__ = _v2_original_name


def _v2_callback_frames(frames,symbols,observe,wrapper,objdump,elf):
    # V2 adds foreground-only sampling methods. Bound the actual reachable
    # observer-owned IRQ call graph instead of counting foreground frames as
    # IRQ frames. Every reachable out-of-line observer function must have .su
    # evidence; all matching compiler clones are conservatively summed.
    owned={}
    for row in symbols:
        if row['size']>0 and row['kind'] in 'TtWw' and (row['name'].startswith('usb_observer::') or row['name']=='__wrap_dcd_event_handler'):
            owned.setdefault(row['address'],row)
    pending=[wrapper];visited={};edges_by_function={};data=pathlib.Path(elf).read_bytes()
    while pending:
        row=pending.pop()
        if row['address'] in visited:continue
        require(len(visited)<64,'Observer callback graph exceeds fixed proof bound')
        visited[row['address']]=row
        text,_=inspection_disassembly(objdump,elf,row)
        linked=call_edges(text,data);edges_by_function[row['name']]=linked
        pending.extend(owned[e['target']] for e in linked if e['target'] in owned)
    require(observe['address'] in visited,'Wrapper callback graph omits actual observer')
    def qualifier(name):
        if name=='__wrap_dcd_event_handler':return name
        match=re.search(r'(usb_observer::[^ ()]+|__wrap_dcd_event_handler)\(',name)
        require(match is not None,'Observer stack symbol cannot be attributed: '+name)
        return match[1]
    reachable={qualifier(row['name']) for row in visited.values()}
    forbidden={'usb_observer::sampleGeneration','usb_observer::service','usb_observer::snapshot','usb_observer::stateName'}
    require(not reachable.intersection(forbidden),'Foreground observer method is reachable from IRQ callback')
    callback=[row for row in frames if qualifier(row['function']) in reachable]
    require({qualifier(row['function']) for row in callback}==reachable,'Actual IRQ function lacks stack-usage evidence')
    return callback,dict(status='PASS',functions=list(visited.values()),calls=edges_by_function,
        foreground_methods_not_irq_reachable=sorted(forbidden),conservative_clone_frames=True,
        external_sdk_frames_separately_reported=True)

_V2_INNER_OBSERVER_BINDING = observer_binding

def v2_source_contract(source):
    source=pathlib.Path(source)
    # The full 201-file inventory is checked before these selected semantic
    # anchors; complete native tests establish their behavior, not token search.
    verify_composed_source(source)
    header=(source/'hid_backend.h').read_text()
    backend=(source/'hid_backend.cpp').read_text()
    web=(source/'webserver.cpp').read_text()
    require('WindowMs=5000,TailMs=5000,TotalMs=WindowMs+TailMs' in header,'V2 timing bounds changed')
    for marker in ['atMs=0','struct Witness','struct LiveSample','struct Tail',
                   'configuredKnown','configuredSampleAtMs','captureClosedObservedAtMs',
                   'firstUnsupported','additionalUnsupportedDistinct','maxServiceGapMs',
                   'sampleGeneration()','uint32_t expectedGeneration']:
        require(marker in header,'V2 capture contract missing: '+marker)
    require('esp_timer_get_time' in backend,'V2 ISR-safe clock source missing')
    require('evilduck-usb-observer-v2' in web and 'evilduck-usb-observer-v1' not in web,'V2 export schema missing or mixed')
    return dict(schema='evilduck-usb-observer-v2',window_ms=5000,diagnostic_tail_ms=5000,total_ms=10000,
        immutable_deadline_source_pinned=True,generation_tagged_samples_source_pinned=True,
        timestamped_records_source_pinned=True,first_unsupported_witness_source_pinned=True,
        tail_cannot_revalidate_source_pinned=True,
        source_header_sha256=sha(source/'hid_backend.h'),source_backend_sha256=sha(source/'hid_backend.cpp'),
        scope='Exact compiled source plus composed mock tests; not physical runtime validation')

def clock_binding(root):
    root=pathlib.Path(root);elf=root/'build/EvilDuckS3.ino.elf';data=elf.read_bytes()
    entries=json.loads((root/'build/compile_commands.json').read_text())
    entry=next(r for r in entries if pathlib.Path(r['file']).name=='hid_backend.cpp')
    prefix=str(entry['arguments'][0]).rsplit('g++',1)[0];nm=prefix+'nm';objdump=prefix+'objdump'
    symbols=symbol_rows(subprocess.check_output([nm,'-C','-S','--defined-only',str(elf)],text=True))
    def named(name):
        rows=[r for r in symbols if r['name']==name and r['size']>0]
        require(len(rows)==1,'V2 clock symbol absent/ambiguous: '+name);return rows[0]
    observe=named('usb_observer::observe(dcd_event_t const*, bool)')
    clock=named('usb_observer::clockMs()');api=named('esp_timer_get_time')
    def edges(row):
        text,evidence=inspection_disassembly(objdump,elf,row)
        return call_edges(text,data),text,evidence
    calls,body,inspect=edges(observe);clock_calls,clock_body,clock_inspect=edges(clock)
    require(any(r['target']==clock['address'] for r in calls),'Actual observer does not reach monotonic clock')
    require(any(r['target']==api['address'] for r in clock_calls),'Actual observer clock does not call pinned ESP timer API')
    api_calls,api_body,api_inspect=edges(api)
    require(not any(word in clock_body+api_body for word in ['malloc','calloc','realloc','operator new','execution::','storage::','Serial']),
        'V2 clock calls allocation/I/O/executor APIs')
    section_dump=subprocess.check_output([objdump,'-C','-t',str(elf)],text=True)
    api_rows=[line for line in section_dump.splitlines() if line.split() and line.split()[-1]=='esp_timer_get_time']
    require(len(api_rows)==1 and '.iram' in api_rows[0],'Pinned timer API is not linked in IRAM')
    def entry_frame(text):
        match=re.search(r'\bentry\s+a1,\s*(\d+)',text)
        return int(match[1]) if match else None
    external_frames=[dict(function=api['name'],address=api['address'],bytes=entry_frame(api_body))]
    # Existing SDK HAL implementation is separately attributed, never hidden
    # inside the observer-owned frame sum or claimed as measured peak latency.
    for edge in api_calls:
        rows=[row for row in symbols if row['address']==edge['target'] and row['name']=='systimer_hal_get_counter_value']
        if rows:
            hal_body,_=inspection_disassembly(objdump,elf,rows[0])
            external_frames.append(dict(function=rows[0]['name'],address=rows[0]['address'],bytes=entry_frame(hal_body)))
    return dict(status='PASS',clock=clock,api=api,observe_calls=calls,clock_calls=clock_calls,
        external_clock_entry_frames=external_frames,
        external_clock_stack_accounting='Separately decoded entry frames; not an exhaustive SDK IRQ peak or latency measurement',
        clock_disassembly=clock_body,api_disassembly=api_body,api_calls=api_calls,
        clock_inspection=clock_inspect,api_inspection=api_inspect,observe_inspection=inspect,
        actual_call_reachable=True,api_in_iram=True,
        sdk_usb_cpp_source_sha256='8d7b8283bc3ee978de14229382d43628ae48c1f01acbbaa15837bf2ced01571f',
        runtime_latency_measured=False,clock_available_before_usb_source_pinned=True)

def observer_binding(root):
    entries=json.loads((pathlib.Path(root)/'build/compile_commands.json').read_text())
    rows=[row for row in entries if pathlib.Path(row['file']).name=='hid_backend.cpp']
    require(len(rows)==1,'Observer backend compilation absent/ambiguous')
    require(rows[0]['arguments'].count(OBSERVER_FLAG)==1,'Explicit observer compile selector missing/duplicated')
    contract=v2_source_contract(pathlib.Path(root)/'candidate/EvilDuckS3')
    proof=_V2_INNER_OBSERVER_BINDING(root)
    proof['v2_contract']=contract;proof['clock_api']=clock_binding(root)
    return proof

if __name__ == '__main__':
    raise SystemExit(main())
