#!/usr/bin/env python3
"""Add exact payload-restart source/profile evidence to inherited link predicates."""
import hashlib
import json
import pathlib
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA='45d52ec2abdbc18cfcc03d24e672a8aa02088074efa119b638dc76e4af180d7d'
BUILD_ID='ROUTEB-PAYLOAD-RESTART-v1'

def change(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)

def main():
    p=ROOT/'tests/lock_feedback/verify_link.py'
    data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==PARENT_SHA
    text=data.decode()
    # Keep the lock-feedback pin itself intact. Only the final candidate's
    # explicit core/caps source identities override earlier reviewed layers.
    old='    text = text.replace(anchor, injection+anchor)'
    added=('    injection += "lower_pin=json.loads((ROOT/\'tests/random_lowercase/source-manifest.json\').read_text())\\n"\n'
           '    injection += "after.update({x[\'file\']:x[\'sha256\'] for x in lower_pin[\'after\']})\\n"\n'
           '    injection += "source_pin=json.loads((ROOT/\'tests/payload_restart/source-manifest.json\').read_text())\\n"\n'
           '    injection += "after.update({x[\'file\']:x[\'sha256\'] for x in source_pin[\'after\']})\\n"\n'
           +old)
    added=added.replace("    injection += \"source_pin=", "    injection += \"text_pin=json.loads((ROOT/'tests/text_keyboard/source-manifest.json').read_text())\\n\"\n    injection += \"after.update({x['file']:x['sha256'] for x in text_pin['after']})\\n\"\n    injection += \"source_pin=")
    text=change(text,old,added)
    text=change(text,'repr(BUILD_ID.encode())','repr(SOURCE_BUILD_ID.encode())')
    old='    for row in pin["after"]:\n        assert hashlib.sha256((sketch/row["file"]).read_bytes()).hexdigest() == row["sha256"]'
    new=('    source_after={x["file"]:x["sha256"] for x in json.loads((ROOT/"tests/random_lowercase/source-manifest.json").read_text())["after"]}\n'
         '    source_after.update({x["file"]:x["sha256"] for x in json.loads((ROOT/"tests/payload_restart/source-manifest.json").read_text())["after"]})\n'
         '    for row in pin["after"]:\n'
         '        assert hashlib.sha256((sketch/row["file"]).read_bytes()).hexdigest() == source_after.get(row["file"],row["sha256"])')
    new=new.replace('    source_after.update(', '    source_after.update({x["file"]:x["sha256"] for x in json.loads((ROOT/"tests/text_keyboard/source-manifest.json").read_text())["after"]})\n    source_after.update(',1)
    text=change(text,old,new)
    namespace={'__name__':'payload_restart_link_parent','__file__':str(__file__),'SOURCE_BUILD_ID':BUILD_ID}
    exec(compile(text,str(__file__),'exec'),namespace)
    assert namespace['main']()==0
    # The parent main's local namespace is intentionally not exported; parse only
    # this wrapper's known CLI arguments after the complete parent checks pass.
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--build-root',type=pathlib.Path,required=True);parser.add_argument('--output',type=pathlib.Path,required=True)
    args=parser.parse_args()
    report=json.loads(args.output.read_text())
    pin=json.loads((ROOT/'tests/payload_restart/source-manifest.json').read_text())
    assert pin['build_id']==BUILD_ID and pin['required_flag']=='EVILDUCK_ROUTE_B_PAYLOAD_RESTART=1'
    assert pin['parent_prepare_sha256']==hashlib.sha256((ROOT/'tests/text_keyboard/prepare_sources.py').read_bytes()).hexdigest()
    assert pin['patch_sha256']==hashlib.sha256((ROOT/'tests/payload_restart/application.patch').read_bytes()).hexdigest()
    previous=json.loads((ROOT/'docs/text-keyboard-build.json').read_text())
    before={x['file'].removeprefix('EvilDuckS3/'):x['sha256'] for x in previous['source_inventory']}

    assert {x['file'] for x in pin['before']}=={x['file'] for x in pin['after']}=={'core.cpp','core.h','caps_trial.h','adapter.cpp'}
    for row in pin['before']:assert before[row['file']]==row['sha256']
    for row in pin['after']:assert hashlib.sha256((args.build_root/'candidate/EvilDuckS3'/row['file']).read_bytes()).hexdigest()==row['sha256']
    entries=json.loads((args.build_root/'build/compile_commands.json').read_text())
    for entry in entries:
        if pathlib.Path(entry['file']).is_relative_to(args.build_root/'build/sketch'):
            assert '-DEVILDUCK_ROUTE_B_PAYLOAD_RESTART=1' in entry['arguments']
            assert '-DEVILDUCK_ROUTE_B_TEXT_KEYBOARD=1' in entry['arguments']
            assert '-DEVILDUCK_ROUTE_B_RANDOMIZATION_JITTER=1' in entry['arguments']
            assert '-DEVILDUCK_ROUTE_B_RANDOM_UPPERCASE=1' in entry['arguments']
            assert '-DEVILDUCK_ROUTE_B_RANDOM_LOWERCASE=1' in entry['arguments']
            assert '-DEVILDUCK_ROUTE_B_SOURCE_COMPAT=1' in entry['arguments']
            assert '-DEVILDUCK_ROUTE_B_KEYBOARD_CONTROL=1' in entry['arguments']
            assert '-DEVILDUCK_ROUTE_B_LOCK_FEEDBACK=1' in entry['arguments']
    elf=args.build_root/'build/EvilDuckS3.ino.elf'
    assert BUILD_ID.encode() in elf.read_bytes()
    for marker in (b'IF_DEFINED_TRUE',b'IF_NOT_DEFINED_TRUE',b'ELSE_DEFINED',b'END_IF_DEFINED',b'EXTENSION',b'END_EXTENSION',b'RANDOM_LOWERCASE_LETTER',b'RANDOM_UPPERCASE_LETTER',b'RANDOM_LETTER',b'RANDOM_NUMBER',b'RANDOM_SPECIAL',b'RANDOM_CHAR',b'$_RANDOM_INT',b'$_JITTER_ENABLED',b'REPEAT',b'RESTART_PAYLOAD',b'RESET',b'POWERSHELL',b'JAVASCRIPT'):
        assert marker in elf.read_bytes(),marker
    # Source/compiled-source equality and actual compiler object membership are
    # inherited. Require linked compiler implementation as well as source hashes.
    assert 'ds_preview::CompileSession::step()' in report['symbols']
    linkmap=(args.build_root/'build/EvilDuckS3.ino.map').read_text()
    assert 'core.cpp.o' in linkmap
    prefix=str(pathlib.Path(report['link_command'][0])).rsplit('g++',1)[0]
    raw=subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True)
    demangled=subprocess.check_output([prefix+'nm','-C','--defined-only',str(elf)],text=True)
    by_address={line.split()[0]:line.split(maxsplit=2)[2] for line in raw.splitlines() if len(line.split())==3}
    bodies={}
    for pattern in ('ds_preview::Compiler::line()', 'ds_preview::Compiler::preprocessing(char*, bool&)',
                    'ds_preview::Compiler::step(ds_preview::CompileWork&)', 'ds_preview::CompileSession::step()'):
        matches=[line for line in demangled.splitlines() if line.endswith(' '+pattern)]
        assert len(matches)==1,(pattern,matches)
        symbol=by_address[matches[0].split()[0]]
        body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+symbol,str(elf)],text=True)
        assert '<'+symbol+'>:' in body
        bodies[pattern]=subprocess.check_output([prefix+'c++filt'],input=body,text=True)
    assert 'ds_preview::Compiler::preprocessing(' in bodies['ds_preview::Compiler::line()']
    assert 'ds_preview::Compiler::line()' in bodies['ds_preview::Compiler::step(ds_preview::CompileWork&)']
    assert 'ds_preview::Compiler::step(' in bodies['ds_preview::CompileSession::step()']
    report['payload_restart_linked_functions']=bodies
    # The convenience synchronous compiler's 4224B object-file frame is not a
    # linked production path; record that distinction rather than hide it.
    report['synchronous_compile_linked']='ds_preview::Program::compile(' in demangled
    report['compiler_workspace_bytes']=4096

    providers=[line for line in demangled.splitlines() if 'native_b::deviceRandom(' in line]
    assert len(providers)==1,providers
    provider_symbol=by_address[providers[0].split()[0]]
    provider_body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+provider_symbol,str(elf)],text=True)
    assert '<esp_random>' in provider_body
    report['linked_random_provider']=provider_body
    assert 'esp_random' in demangled
    assert 'ds_preview::Runtime::tick(unsigned long)' in demangled or 'ds_preview::Runtime::tick(unsigned int)' in demangled
    linked_runtime={}
    for prefix_name in ('ds_preview::Runtime::sample(', 'ds_preview::Runtime::deliver(', 'ds_preview::Runtime::evaluationStep(', 'ds_preview::Runtime::tick('):
        matches=[line for line in demangled.splitlines() if len(line.split(maxsplit=2))==3 and line.split(maxsplit=2)[2].startswith(prefix_name)]
        assert len(matches)==1,(prefix_name,matches)
        mangled=by_address[matches[0].split()[0]]
        body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+mangled,str(elf)],text=True)
        assert '<'+mangled+'>:' in body
        linked_runtime[prefix_name]=subprocess.check_output([prefix+'c++filt'],input=body,text=True)
    for caller in ('ds_preview::Runtime::deliver(', 'ds_preview::Runtime::evaluationStep(', 'ds_preview::Runtime::tick('):
        assert 'ds_preview::Runtime::sample(' in linked_runtime[caller],caller
    report['linked_sampler_and_jitter_gate']=linked_runtime
    reset_edges={}
    for pattern in ('route_b::reset(', 'native_b::Adapter::receive(', 'ds_preview::Runtime::completeInstruction(', 'com::update('):
        matches=[line for line in demangled.splitlines() if len(line.split(maxsplit=2))==3 and line.split(maxsplit=2)[2].startswith(pattern)]
        assert len(matches)==1,(pattern,matches)
        symbol=by_address[matches[0].split()[0]]
        body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+symbol,str(elf)],text=True)
        assert '<'+symbol+'>:' in body
        reset_edges[pattern]=subprocess.check_output([prefix+'c++filt'],input=body,text=True)
    assert 'route_b::reset(' in reset_edges['native_b::Adapter::receive(']
    assert 'hid_backend::cancelReport()' in reset_edges['route_b::reset(']
    report['linked_reset_edges']=reset_edges
    report['text_keyboard_source_pin']=json.loads((ROOT/'tests/text_keyboard/source-manifest.json').read_text())
    report['text_keyboard_linked_functions']=bodies
    restart_functions={}
    for pattern in ('ds_preview::Runtime::rewindExecution()', 'ds_preview::Runtime::deliver(unsigned long)'):
        if pattern.endswith('deliver(unsigned long)'):
            restart_functions['deliver']=linked_runtime['ds_preview::Runtime::deliver('];continue
        matches=[line for line in demangled.splitlines() if line.endswith(' '+pattern)]
        assert len(matches)==1,(pattern,matches)
        symbol=by_address[matches[0].split()[0]]
        body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+symbol,str(elf)],text=True)
        restart_functions[pattern]=subprocess.check_output([prefix+'c++filt'],input=body,text=True)
    assert 'ds_preview::Runtime::rewindExecution()' in restart_functions['deliver']
    report['linked_restart_functions']=restart_functions
    report['random_lowercase_verified']=True
    report['random_uppercase_verified']=True
    report['randomization_jitter_verified']=True
    report['text_keyboard_verified']=True
    report['payload_restart_verified']=True
    report['payload_restart_source_pin']=pin
    report['profile']='ROUTE B PAYLOAD RESTART REVIEW ONLY; PHYSICAL VALIDATION PENDING'
    report['payload_restart_link_adapter']=dict(parent='tests/lock_feedback/verify_link.py',parent_sha256=PARENT_SHA,adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),inherited_safety_predicates_removed=0,build_id=BUILD_ID)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS exact composed restart source/profile, linked rewind/clear edges and inherited USB/NVS/ownership/feedback safeguards')
    return 0
if __name__=='__main__':raise SystemExit(main())
