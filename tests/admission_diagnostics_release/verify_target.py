#!/usr/bin/env python3
"""Additive current-request diagnostic proof over the complete frozen v2 chain.

Only declared final source/identity expectations advance. All inherited require
and Assert nodes execute; the real source objects/header dependencies are bound
to the existing approved target compilation and actual link.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
from unittest.mock import patch
sys.dont_write_bytecode = True
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent
BUILD_ID='ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1'
OLD_BUILD_ID='ROUTEB-USB-ENUM-OBSERVER-H1-v2'
SELF_PATH='tests/admission_diagnostics_release/verify_target.py'
PARENT=ROOT/'tests/usb_os_observer_v2_release/verify_target.py'
PARENT_SHA='f74d07d88531acd14882260da5d2d4e61ba4a6b2f636438d06f85c117975e3a6'

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def require(value,message):
    if not value:raise ValueError(message)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
require(sha(PARENT)==PARENT_SHA,'Historical v2 target verifier changed')
P=load(PARENT,'admission_complete_frozen_v2_target')
P.__file__=str(pathlib.Path(__file__).resolve())
_seen=set()
def _context(module):
    if id(module) in _seen:return
    _seen.add(id(module))
    if hasattr(module,'BUILD_ID'):module.BUILD_ID=BUILD_ID
    if hasattr(module,'SELF_PATH'):module.SELF_PATH=SELF_PATH
    for name in ['D','S']:
        child=getattr(module,name,None)
        if child is not None:_context(child)
_context(P)
P.HERE=HERE
ORIGINAL_COMPILE=P.ORIGINAL_COMPILE
TARGET_EDITS=[
 ('tests/usb_os_observer_v2_release/','tests/admission_diagnostics_release/',3),
 ('tests/usb_os_observer_v2_web/prepare_sources.py','tests/admission_diagnostics/prepare_sources.py',1),
 ('evilduck-usb-os-observer-release-v2','evilduck-routeb-admission-diagnostics-release-v1',1),
 ('len(pin["after"]) == 7 and len(pin["unchanged"]) == 194','len(pin["after"]) == 9 and len(pin["unchanged"]) == 192',1),
 ('7/194','9/192',1),
 ('source_files=201, usb_observer_files=7, unchanged_files=194','source_files=201, admission_diagnostics_files=9, unchanged_files=192',1),
 ('cumulative_h1_changed_files=8, cumulative_h1_unchanged_files=193','cumulative_h1_changed_files=10, cumulative_h1_unchanged_files=191',1),
 ('len(pin["before"]) == 7','len(pin["before"]) == 9',1),
 ('len(pin["cumulative_h1_after"]) == 8','len(pin["cumulative_h1_after"]) == 10',1),
 ('{"core.cpp", "shortcut_keys.h", "webfiles.h", "caps_trial.h", "webserver.cpp", "hid_backend.cpp", "hid_backend.h"}',
  '{"core.cpp", "shortcut_keys.h", "webfiles.h", "caps_trial.h", "webserver.cpp", "hid_backend.cpp", "hid_backend.h", "adapter.cpp", "adapter.h"}',2),
 ('{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h", "hid_backend.cpp", "hid_backend.h"}',
  '{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h", "hid_backend.cpp", "hid_backend.h", "adapter.cpp", "adapter.h"}',1),
]

def predicate_counts(text):
    tree=ast.parse(text)
    return dict(asserts=sum(isinstance(n,ast.Assert) for n in ast.walk(tree)),
                require_calls=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' for n in ast.walk(tree)))

def adapt_text(text,edits):
    before=predicate_counts(text);changes=[]
    for old,new,count in edits:
        require(text.count(old)==count,'Admission target occurrence mismatch: '+old)
        text=text.replace(old,new);changes.append(dict(before=old,after=new,occurrences=count))
    require(predicate_counts(text)==before,'Admission target removed an inherited predicate')
    return text,dict(edits=changes,predicates_retained=before)

_P_ADAPTED=P.adapted_parent
def adapted_parent():
    events=[]
    def adapt(source,filename,mode,*args,**kwargs):
        if mode=='exec' and isinstance(source,str) and 'pin["format"] == "evilduck-usb-os-observer-release-v2"' in source:
            source,evidence=adapt_text(source,TARGET_EDITS);events.append(evidence)
        return ORIGINAL_COMPILE(source,filename,mode,*args,**kwargs)
    with patch.object(P,'ORIGINAL_COMPILE',adapt):namespace,inherited=_P_ADAPTED()
    require(len(events)==1,'Complete v2 target adaptation absent/ambiguous')
    return namespace,dict(observer_v2=inherited,admission_diagnostics=events[0],
        active_verifier_context=dict(file=SELF_PATH,build_id=BUILD_ID,parent_sha256=PARENT_SHA))
P.adapted_parent=adapted_parent

def verify_composed_source(source):
    source=pathlib.Path(source);M=load(HERE/'prepare_sources.py','admission_target_exact_source');rows=M.verify_final(source)
    prior=json.loads((ROOT/'tests/usb_os_observer_v2_release/source-manifest.json').read_text())
    before={r['file']:r['sha256'] for r in prior['after']+prior['unchanged']}
    final={r['file']:r['sha256'] for r in M.pin()['after']+M.pin()['unchanged']}
    changed={n for n in final if final[n]!=before[n]}
    require(len(final)==len(before)==201 and changed=={'adapter.cpp','adapter.h','caps_trial.h'},'Admission scope extends beyond request diagnostics and identity')
    caps=(source/'caps_trial.h').read_bytes()
    require(caps.count(BUILD_ID.encode())==1 and OLD_BUILD_ID.encode() not in caps,'Admission identity absent/ambiguous')
    require(hashlib.sha256(caps.replace(BUILD_ID.encode(),OLD_BUILD_ID.encode(),1)).hexdigest()==before['caps_trial.h'],'Admission identity changed beyond literal')
    for name in ['core.cpp','core.h','coordinator.cpp','shortcut_keys.h','hid_backend.cpp','hid_backend.h','webfiles.h','webserver.cpp','cli.cpp']:
        require(final[name]==before[name],'Unrelated retained source changed: '+name)
    return dict(status='PASS',source_files=201,source_manifest_sha256=sha(HERE/'source-manifest.json'),changed_sources=sorted(changed),
                core_sha256=final['core.cpp'],webfiles_sha256=final['webfiles.h'],webserver_sha256=final['webserver.cpp'],
                compiler_and_runtime_unchanged=True,build_id=BUILD_ID)
P.verify_composed_source=verify_composed_source

_P_INPUTS=P.verify_input_manifest
def verify_input_manifest(root):
    value=_P_INPUTS(root)
    pin=json.loads((pathlib.Path(root)/'build-inputs.json').read_text());names={r['file'] for r in pin['files']}
    needed={str(p.relative_to(ROOT)) for directory in ['tests/admission_diagnostics','tests/admission_diagnostics_release'] for p in (ROOT/directory).rglob('*') if p.is_file()}
    require(needed.issubset(names),'Admission committed inputs missing')
    require(value['post_compile_verifier_delta'] is None,'Admission has a post-build verifier exception')
    return dict(value,admission_required_inputs=sorted(needed))
P.verify_input_manifest=verify_input_manifest

def admission_binding(root):
    root=pathlib.Path(root);source=root/'candidate/EvilDuckS3'
    verify_composed_source(source)
    entries=json.loads((root/'build/compile_commands.json').read_text());report=json.loads((root/'report.json').read_text())
    namespace,_=adapted_parent();privacy,_=namespace['parent_namespace']()
    loaded={line.removeprefix('LOAD ').strip() for line in (root/'build/EvilDuckS3.ino.map').read_text().splitlines() if line.startswith('LOAD ')}
    linked={row['file']:row for row in report['linked_input_hashes']};units=[]
    for name in ['adapter.cpp','coordinator.cpp']:
        found=[row for row in entries if pathlib.Path(row['file']).name==name]
        require(len(found)==1,'Admission compile absent/ambiguous: '+name)
        entry=found[0];compiled=pathlib.Path(entry['file']);args=entry['arguments'];obj=pathlib.Path(args[args.index('-o')+1])
        require(compiled==root/'build/sketch'/name and privacy['source_matches']((source/name).read_bytes(),compiled.read_bytes(),source/name),'Actual admission source differs: '+name)
        target,deps=privacy['make_dependencies'](obj.with_suffix('.d').read_text())
        require(pathlib.Path(target)==obj and str(root/'build/sketch/adapter.h') in deps,'Admission diagnostic header absent from compile dependencies: '+name)
        require(privacy['source_matches']((source/'adapter.h').read_bytes(),(root/'build/sketch/adapter.h').read_bytes(),source/'adapter.h'),'Actual admission header differs')
        require(str(obj) in loaded and str(obj) in linked and linked[str(obj)]['sha256']==sha(obj),'Admission object absent/changed in link: '+name)
        units.append(dict(file=name,source_sha256=sha(source/name),compiled_source=str(compiled),compiled_sha256=sha(compiled),object=str(obj),object_sha256=sha(obj),header_dependency=True))
    entry=next(e for e in entries if pathlib.Path(e['file']).name=='adapter.cpp')
    prefix=str(entry['arguments'][0]).rsplit('g++',1)[0];elf=root/'build/EvilDuckS3.ino.elf'
    symbols=P.symbol_rows(subprocess.check_output([prefix+'nm','-C','-S','--defined-only',str(elf)],text=True))
    fail=[r for r in symbols if r['name']=='native_b::Adapter::fail(native_b::Fault, ds_preview::Error)' and r['size']>0]
    require(len(fail)==1,'Request-owned diagnostic fail handler absent/ambiguous in actual ELF')
    require(not any(r['name']=='native_b::Adapter::fail(native_b::Fault)' for r in symbols),'Old diagnostic handler remains linked')
    header=(source/'adapter.h').read_text();body=(source/'adapter.cpp').read_text()
    require('ds_preview::Error diagnostic_{};uint16_t admissionLine_=1;' in header and 'diagnostic()const{return diagnostic_;}' in header,'Request-owned diagnostic state missing')
    require('diagnostic_={};admissionLine_=1;' in body and body.count('ds_preview::ErrorCode::InvalidSource,admissionLine_,1')==3,'Admission source classification anchors changed')
    require('if(c==10)++admissionLine_;' in body,'LF/CRLF admission line accounting missing')
    return dict(status='PASS',compiled_units=units,first_fault_handler=fail[0],actual_elf_sha256=sha(elf),
                adapter_header_sha256=sha(source/'adapter.h'),coordinator_source_unchanged=True,
                existing_error_code=2,status_schema_unchanged=True,source_acceptance_unchanged=True,
                compiler_workspace_bytes=4096,physical_line_contract='LF increments; CRLF counts once; bare CR remains compiler validation',
                scope='Exact composed source, actual compilation dependencies and linked object/symbol identity; behavioral claims require native tests, not token anchors')

def verify(root):
    binding=P.verify(root)
    binding['admission_diagnostics']=admission_binding(root)
    binding['admission_diagnostics_source_manifest_sha256']=sha(ROOT/'tests/admission_diagnostics/source-manifest.json')
    binding['admission_diagnostics_release_manifest_sha256']=sha(HERE/'source-manifest.json')
    binding['actual_admission_verifier_sha256']=sha(__file__)
    return binding

# Re-export unchanged helpers used by inherited verifier controls and wrappers.
for _name in ['symbol_rows','elf_bytes','inspection_disassembly','observer_binding','web_binding','core_binding','alias_binding','define_binding']:
    globals()[_name]=getattr(P,_name)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build-root',type=pathlib.Path,required=True);parser.add_argument('--output',type=pathlib.Path,required=True);args=parser.parse_args()
    require(not args.output.exists(),'Use fresh target proof')
    args.output.write_text(json.dumps(verify(args.build_root),indent=2)+'\n')
    print('PASS admission diagnostic target and complete retained v2 source/USB/resource proofs')

if __name__=='__main__':raise SystemExit(main())
