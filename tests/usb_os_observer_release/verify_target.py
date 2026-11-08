#!/usr/bin/env python3
"""Actual source, archive, ISR forwarding and ELF capture-only target proof."""
import argparse
import builtins
import hashlib
import importlib.util
import json
import pathlib
import re
import shlex
import subprocess
import sys
from unittest.mock import patch
sys.dont_write_bytecode = True
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent
BUILD_ID='ROUTEB-USB-ENUM-OBSERVER-H1-v1'
OLD_BUILD_ID='ROUTEB-DEFINE-LABELS-H1-v1'
SELF_PATH='tests/usb_os_observer_release/verify_target.py'
PARENT=ROOT/'tests/define_labels_release/verify_target.py'
PARENT_SHA='1c288f259b7ae646e3740d4e71db1f9aebdf8668ef4e7b6626bfda47cd7cd397'
ORIGINAL_COMPILE=builtins.compile

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def require(condition,message):
    if not condition:raise ValueError(message)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
require(sha(PARENT)==PARENT_SHA,'Historical DEFINE target verifier changed')
D=load(PARENT,'usb_observer_complete_define_target')
D.BUILD_ID=D.S.BUILD_ID=BUILD_ID
D.SELF_PATH=D.S.SELF_PATH=SELF_PATH
S=D.S

def adapted_parent():
    captured=[]
    def capture(source,filename,mode,*args,**kwargs):
        if mode=='exec' and isinstance(source,str) and 'pin["format"] == "evilduck-define-labels-release-v1"' in source:captured.append(source)
        return ORIGINAL_COMPILE(source,filename,mode,*args,**kwargs)
    with patch.object(D,'ORIGINAL_COMPILE',capture):_,inherited=D.adapted_parent()
    require(len(captured)==1,'Complete DEFINE target source capture ambiguous')
    text=captured[0];changes=[]
    def replace(old,new,count=1):
        nonlocal text
        require(text.count(old)==count,'Observer target occurrence mismatch: '+old)
        text=text.replace(old,new);changes.append(dict(before=old,after=new,occurrences=count))
    replace('tests/define_labels_release/source-manifest.json','tests/usb_os_observer_release/source-manifest.json',2)
    replace('tests/define_labels_release/identity.patch','tests/usb_os_observer_release/identity.patch')
    replace('tests/define_labels/prepare_sources.py','tests/usb_os_observer_web/prepare_sources.py')
    replace('pin["format"] == "evilduck-define-labels-release-v1"','pin["format"] == "evilduck-usb-os-observer-release-v1"')
    replace('len(pin["after"]) == 5 and len(pin["unchanged"]) == 196','len(pin["after"]) == 7 and len(pin["unchanged"]) == 194')
    replace('DEL release manifest is not the reviewed 5/196 source delta','USB observer release manifest is not the reviewed 7/194 source delta')
    replace('{"core.cpp", "shortcut_keys.h", "webfiles.h", "caps_trial.h", "webserver.cpp"}',
            '{"core.cpp", "shortcut_keys.h", "webfiles.h", "caps_trial.h", "webserver.cpp", "hid_backend.cpp", "hid_backend.h"}',2)
    replace('source_files=201, del_alias_files=5, unchanged_files=196','source_files=201, usb_observer_files=7, unchanged_files=194')
    replace('len(pin["before"]) == 5','len(pin["before"]) == 7')
    replace('len(pin["cumulative_h1_after"]) == 6','len(pin["cumulative_h1_after"]) == 8')
    replace('{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h"}',
            '{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h", "hid_backend.cpp", "hid_backend.h"}')
    replace('cumulative_h1_changed_files=6, cumulative_h1_unchanged_files=195','cumulative_h1_changed_files=8, cumulative_h1_unchanged_files=193')
    ns=dict(__name__='usb_observer_frozen_target_chain',__file__=str(__file__))
    exec(ORIGINAL_COMPILE(text,str(S.PARENT),'exec'),ns)
    return ns,dict(define_labels=inherited,usb_observer=changes)

def verify_composed_source(source):
    source=pathlib.Path(source);m=load(HERE/'prepare_sources.py','observer_verify_sources');rows=m.verify_final(source)
    old=json.loads((ROOT/'tests/define_labels_release/source-manifest.json').read_text())
    before={r['file']:r['sha256'] for r in old['after']+old['unchanged']}
    after={r['file']:r['sha256'] for r in m.pin()['after']+m.pin()['unchanged']}
    require(len(rows)==len(after)==len(before)==201,'Observer source inventory size differs')
    changed={n for n in after if after[n]!=before[n]}
    require(changed=={'hid_backend.cpp','hid_backend.h','webserver.cpp','webfiles.h','caps_trial.h'},'Observer source scope differs')
    caps=(source/'caps_trial.h').read_bytes()
    require(caps.count(BUILD_ID.encode())==1 and OLD_BUILD_ID.encode() not in caps,'Observer identity absent/ambiguous')
    require(hashlib.sha256(caps.replace(BUILD_ID.encode(),OLD_BUILD_ID.encode(),1)).hexdigest()==before['caps_trial.h'],'Observer identity extends beyond label')
    require(after['core.cpp']==before['core.cpp'] and after['core.h']==before['core.h'] and
            after['shortcut_keys.h']==before['shortcut_keys.h'],'Compiler/DEFINE/DEL capacity changed')
    return dict(status='PASS',source_files=201,source_manifest_sha256=sha(HERE/'source-manifest.json'),
        changed_sources=sorted(changed),core_sha256=after['core.cpp'],webfiles_sha256=after['webfiles.h'],
        webserver_sha256=after['webserver.cpp'],compiler_and_runtime_unchanged=True,build_id=BUILD_ID)

def verify_input_manifest(build_root):
    inherited=D.verify_input_manifest(build_root)
    require(inherited['post_compile_verifier_delta'] is None,'Observer has a post-build verifier delta')
    value=json.loads((pathlib.Path(build_root)/'build-inputs.json').read_text());names={r['file'] for r in value['files']}
    required={'tests/usb_os_observer_release/'+n for n in ['build_candidate.py','prepare_sources.py','source-manifest.json','identity.patch','verify_target.py','verify_release.py','startup_decode.py','test_verify_controls.py']}
    required|={'tests/usb_os_observer/'+n for n in ['application.patch','source-manifest.json','prepare_sources.py','test_main.cpp','run_tests.py']}
    required|={'tests/usb_os_observer_web/'+n for n in ['application.patch','source-manifest.json','prepare_sources.py']}
    require(required.issubset(names),'Observer committed inputs missing')
    return dict(inherited,usb_observer_required_inputs=sorted(required))

# Reuse unchanged compiled core, DEL and DEFINE proofs rather than clone them.
core_binding=D.core_binding
alias_binding=D.alias_binding
define_binding=D.define_binding
elf_bytes=D.elf_bytes

def symbol_rows(nm_text):
    rows=[]
    for line in nm_text.splitlines():
        m=re.match(r'^([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+(\w)\s+(.+)$',line)
        if m:rows.append(dict(address=int(m[1],16),size=int(m[2],16),kind=m[3],name=m[4]))
    return rows

def call_edges(text,data=None):
    """Decode direct calls or actual literal-loaded Xtensa indirect targets."""
    rows=[];registers={}
    for line in text.splitlines():
        m=re.match(r'^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F]+\s+(\S+)\s*(.*)$',line)
        if not m:continue
        at,op,args=int(m[1],16),m[2],m[3]
        if op.startswith('callx'):
            reg=args.split(',')[0].strip()
            if reg in registers:rows.append(dict(address=at,opcode=op,target=registers[reg],literal_loaded=True))
        elif re.fullmatch(r'call\w*|j',op):
            direct=re.search(r'^([0-9a-fA-F]+)\s*<([^>]+)>',args)
            if direct:rows.append(dict(address=at,opcode=op,target=int(direct[1],16),name=re.sub(r'\+0x[0-9a-fA-F]+$','',direct[2])))
        if op=='l32r':
            lit=re.match(r'(a\d+),\s*([0-9a-fA-F]+)',args)
            if lit and data is not None:registers[lit[1]]=int.from_bytes(elf_bytes(data,int(lit[2],16),4),'little')
        elif op.startswith(('mov','addi','l8','l16','l32','movi')):
            reg=args.split(',')[0].strip()
            registers.pop(reg,None)
    return rows

def observer_binding(root):
    root=pathlib.Path(root);build=root/'build';source=root/'candidate/EvilDuckS3'
    report=json.loads((root/'report.json').read_text());entries=json.loads((build/'compile_commands.json').read_text())
    rows=[r for r in entries if pathlib.Path(r['file']).name=='hid_backend.cpp'];require(len(rows)==1,'Observer backend compilation absent/ambiguous')
    entry=rows[0];args=entry['arguments'];compiler=pathlib.Path(args[0]);prefix=str(compiler).rsplit('g++',1)[0]
    nm,objdump,ar=prefix+'nm',prefix+'objdump',prefix+'ar'
    obj=pathlib.Path(args[args.index('-o')+1]);elf=build/'EvilDuckS3.ino.elf';data=elf.read_bytes()
    E=S.load(ROOT/'tests/privacy_fix1/verify_target.py','observer_exact_source_binding')
    require(E.source_matches((source/'hid_backend.cpp').read_bytes(),pathlib.Path(entry['file']).read_bytes(),source/'hid_backend.cpp'),'Compiled observer backend differs')
    require(args.count('-DEVILDUCK_USB_ENUM_OBSERVER=1')==1,'Explicit observer compile selector missing/duplicated')
    linked={r['file']:r for r in report['linked_input_hashes']};loads={l[5:].strip() for l in (build/'EvilDuckS3.ino.map').read_text().splitlines() if l.startswith('LOAD ')}
    require(str(obj) in linked and str(obj) in loads and linked[str(obj)]['sha256']==sha(obj),'Observer object is not actual linked input')
    link=report['link_command'];link=shlex.split(link) if isinstance(link,str) else link
    require(link.count('-Wl,--wrap=dcd_event_handler')==1,'Actual link lacks one exact observer wrap flag')
    require(link.count('-Wl,--wrap=esp_panic_handler')==1,'Original panic wrapper missing/duplicated')
    require('-DEVILDUCK_USB_ENUM_OBSERVER=1' in report['report']['verified_cpp_extra_flags'],'Build profile does not record observer selector')
    symbols=symbol_rows(subprocess.check_output([nm,'-C','-S','--defined-only',str(elf)],text=True))
    def exact(name):
        rs=[r for r in symbols if r['name']==name];require(len(rs)==1 and rs[0]['size']>0,'Observer symbol absent/ambiguous: '+name);return rs[0]
    def disassemble(sym):return subprocess.check_output([objdump,'-C','-d','--start-address='+str(sym['address']),'--stop-address='+str(sym['address']+sym['size']),str(elf)],text=True)
    wrapper=exact('__wrap_dcd_event_handler');original=exact('dcd_event_handler');observe=exact('usb_observer::observe(dcd_event_t const*, bool)')
    text=disassemble(wrapper);edges=call_edges(text,data)
    require(sum(e['target']==original['address'] for e in edges)==1,'Wrapper must call original handler exactly once')
    require(sum(e['target']==observe['address'] for e in edges)==1,'Wrapper must call bounded observer exactly once')
    require(sum(e['target']==wrapper['address'] for e in edges)==0,'Observer wrapper recurses')
    dcd=exact('dcd_int_handler');dcd_text=disassemble(dcd);dcd_edges=call_edges(dcd_text,data)
    require(any(e['target']==wrapper['address'] for e in dcd_edges),'Actual DCD IRQ does not call observer wrapper')
    require(not any(e['target']==original['address'] for e in dcd_edges),'Actual DCD IRQ bypasses wrapper')
    state=exact('usb_observer::captureState');mux=exact('usb_observer::captureMux')
    require(state['kind'] in 'Bb','Early observer capture state is not zero-initialized BSS')
    require(state['size']+mux['size']<=2048,'Observer dedicated RAM budget exceeded')
    observer_ram=[r for r in symbols if r['kind'] in 'BbDd' and r['name'].startswith('usb_observer::')]
    require({r['name'] for r in observer_ram}=={state['name'],mux['name']},'Uncounted observer mutable state')
    object_dump=subprocess.check_output([objdump,'-C','-dr',str(obj)],text=True)
    chunks=object_dump.split('Disassembly of section ')
    initializers=[c for c in chunks if c.startswith(('.text.startup.','.literal.startup.','.text._GLOBAL__sub_I','.literal._GLOBAL__sub_I'))]
    require(initializers and all('usb_observer::captureState' not in c and 'usb_observer::captureMux' not in c for c in initializers),'Observer state has dynamic constructor initialization')
    # Bind the original linked SDK member and show the DCD call is originally
    # undefined, rather than a patched archive/private descriptor implementation.
    archives=[pathlib.Path(p) for p in linked if p.endswith('/libarduino_tinyusb.a')]
    require(len(archives)==1,'Actual linked TinyUSB archive missing/ambiguous')
    archive=archives[0];members=subprocess.check_output([ar,'t',str(archive)],text=True).splitlines()
    require('dcd_dwc2.c.obj' in members and 'usbd.c.obj' in members,'Pinned USB driver members missing')
    folder=root/'observer-proof-cache';folder.mkdir(exist_ok=True)
    driver=folder/'dcd_dwc2.c.obj';original_obj=folder/'usbd.c.obj'
    for name,path in [('dcd_dwc2.c.obj',driver),('usbd.c.obj',original_obj)]:
        content=subprocess.check_output([ar,'p',str(archive),name])
        if path.exists():require(path.read_bytes()==content,'Cached USB archive member changed')
        else:path.write_bytes(content)
    raw_nm=subprocess.check_output([nm,'-u',str(driver)],text=True)
    reloc=subprocess.check_output([objdump,'-r',str(driver)],text=True)
    require(re.search(r'\bU\s+dcd_event_handler\b',raw_nm) and 'dcd_event_handler' in reloc,'DCD archive lacks externally wrapped handler reference')
    orig_nm=symbol_rows(subprocess.check_output([nm,'-S','--defined-only',str(original_obj)],text=True))
    require(any(r['name']=='dcd_event_handler' and r['kind']=='T' for r in orig_nm),'Original SDK handler missing or weak')
    su=obj.with_suffix('.su');require(su.is_file(),'Observer stack-usage file missing')
    frames=[]
    for line in su.read_text().splitlines():
        cols=line.split('\t')
        if len(cols)>=3 and ('usb_observer::' in cols[0] or '__wrap_dcd_event_handler' in cols[0]):
            frames.append(dict(function=cols[0].split(':',3)[-1],bytes=int(cols[1]),kind=cols[2]))
    callback=[r for r in frames if not any(n in r['function'] for n in ['snapshot(', 'service(', 'stateName('])]
    require(callback and max(r['bytes'] for r in callback)<=256,'Observer callback frame budget exceeded')
    # Summing every observer-owned callback frame is deliberately conservative:
    # mutually exclusive and inlined paths cannot understate the bound.
    callback_sum=sum(r['bytes'] for r in callback)
    require(state['size']+mux['size']+callback_sum<=2048,'Observer state plus callback frames exceeds dedicated 2KiB budget')
    forbidden=['malloc','calloc','realloc','operator new','String::','execution::Guard','storage::','debug::','Serial']
    observe_text=disassemble(observe)
    require(not any(f in observe_text for f in forbidden),'Observer callback calls allocation/I/O/owner lock')
    return dict(status='PASS',capture_only=True,classification='UNKNOWN',reason='NO_VALIDATED_RULE',
        source_backend_sha256=sha(source/'hid_backend.cpp'),source_header_sha256=sha(source/'hid_backend.h'),
        actual_backend_object_sha256=sha(obj),actual_elf_sha256=sha(elf),explicit_compile_selector=True,
        actual_link_wrap_flag=True,wrapper=wrapper,original_handler=original,observer=observe,
        original_panic_wrap_preserved=True,
        wrapper_calls=edges,dcd_irq=dcd,dcd_calls=dcd_edges,original_handler_called_once=True,
        dcd_calls_wrapper=True,original_event_arguments_source_pinned=True,sdk_archive_sha256=sha(archive),
        original_sdk_members=dict(dcd=sha(driver),usbd=sha(original_obj)),sdk_sources_unchanged=True,
        mutable_state=observer_ram,dedicated_state_bytes=state['size']+mux['size'],state_budget_bytes=2048,
        early_bss_state=True,dynamic_observer_initialization_absent=True,max_records=64,window_ms=5000,
        stack_frames=frames,callback_max_frame=max(r['bytes'] for r in callback),callback_frame_budget=256,
        conservative_callback_frame_sum=callback_sum,state_plus_callback_bytes=state['size']+mux['size']+callback_sum,
        physical=False,installed=False,target_execution=False)

def web_binding(root):
    """Prove the actual endpoint authenticates before the one snapshot call."""
    root=pathlib.Path(root);elf=root/'build/EvilDuckS3.ino.elf';data=elf.read_bytes()
    entries=json.loads((root/'build/compile_commands.json').read_text())
    entry=next(r for r in entries if pathlib.Path(r['file']).name=='webserver.cpp')
    prefix=str(entry['arguments'][0]).rsplit('g++',1)[0];nm=prefix+'nm';objdump=prefix+'objdump'
    symbols=symbol_rows(subprocess.check_output([nm,'-C','-S','--defined-only',str(elf)],text=True))
    def match(fragment):
        found=[r for r in symbols if r['name'].startswith(fragment) and r['size']>0]
        require(len(found)==1,'Observer export symbol absent/ambiguous: '+fragment);return found[0]
    handler=match('handleUsbObservations(');check=match('checkAuth(');snapshot=match('usb_observer::snapshot(')
    helpers=[r for r in symbols if r['name'].startswith(('authorizeUsbObservations(', 'authorize(')) and r['size']>0]
    def edges(row):
        text=subprocess.check_output([objdump,'-C','-d','--start-address='+str(row['address']),'--stop-address='+str(row['address']+row['size']),str(elf)],text=True)
        return call_edges(text,data)
    auth_nodes={r['address']:r for r in helpers+[check]}
    calls=edges(handler);authorized=[r for r in calls if r['target'] in auth_nodes];snapshots=[r for r in calls if r['target']==snapshot['address']]
    require(len(authorized)==len(snapshots)==1 and authorized[0]['address']<snapshots[0]['address'],'Observer export lacks auth-before-single-snapshot edge')
    auth=auth_nodes[authorized[0]['target']]
    pending=[auth];seen=set();auth_edges=[];reached=False
    while pending:
        node=pending.pop()
        if node['address'] in seen:continue
        seen.add(node['address'])
        if node['address']==check['address']:reached=True;continue
        linked=edges(node);auth_edges.extend(linked)
        pending.extend(auth_nodes[r['target']] for r in linked if r['target'] in auth_nodes)
    require(reached,'Observer export authorization does not reach original credential check')
    return dict(status='PASS',handler=handler,authorize=auth,check_auth=check,snapshot=snapshot,
        handler_calls=calls,auth_calls=auth_edges,authenticated_before_single_snapshot=True,
        header_only_source_pinned=True,no_store_source_pinned=True,actual_elf_sha256=sha(elf))

def verify(build_root):
    root=pathlib.Path(build_root).resolve();source=verify_composed_source(root/'candidate/EvilDuckS3');committed=verify_input_manifest(root)
    ns,changes=adapted_parent();binding=ns['verify'](root)
    E=S.load(S.EDITOR,'observer_complete_resource_verifier');resources=E.literal_resources(root/'candidate/EvilDuckS3/webfiles.h')
    complete=E.verify_resource_bytes(resources,(root/'build/EvilDuckS3.ino.elf').read_bytes(),(root/'build/EvilDuckS3.ino.bin').read_bytes())
    streaming=S.streaming_binding(root,binding);core=core_binding(root);alias=alias_binding(root,core);capacity=define_binding(root);observer=observer_binding(root);web=web_binding(root)
    binding.update(status='PASS',build_id=BUILD_ID,source_commit=committed['source_commit'],
        build_inputs_sha256=committed['build_inputs_sha256'],committed_source_provenance=committed,
        verifier_context_commit=committed['verifier_context_commit'],post_compile_verifier_delta=None,
        static_response_source_composition=source,previous_repeat_source_composition=source,del_alias_source_composition=source,
        bundled_resources=complete,streaming_response=streaming,previous_command_repeat=core,del_alias=alias,
        define_labels=capacity,usb_observer=observer,usb_observer_web=web,actual_parent_verifier_sha256=PARENT_SHA,
        integration_verifier_adaptations=changes,physical=False,installed=False,package_created=False)
    return binding

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build-root',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True)
    a=p.parse_args();require(not a.output.exists(),'Use fresh target evidence');a.output.write_text(json.dumps(verify(a.build_root),indent=2)+'\n');print('PASS actual capture-only USB wrapper and complete inherited target proofs')
if __name__=='__main__':main()
