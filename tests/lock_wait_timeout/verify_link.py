#!/usr/bin/env python3
"""Preserve pinned v2 link guards; add exact timeout source and linked-path proof."""
import argparse, hashlib, json, pathlib, subprocess, sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA='e155bf66e2c5892b49d7241d36f21dc4b10b6ac2cb1bbf95a96596b02bb07182'
BUILD_ID='ROUTEB-LOCK-WAIT-TIMEOUT-v1'

def change(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)

def main():
    parent=ROOT/'tests/source_text_v2/verify_link.py'
    assert hashlib.sha256(parent.read_bytes()).hexdigest()==PARENT_SHA
    text=parent.read_text()
    text=change(text,"BUILD_ID='ROUTEB-SOURCE-TEXT-PORTABILITY-v2'",'BUILD_ID='+repr(BUILD_ID))
    # Override final generated hashes only after every historical source layer.
    marker='    text=change(text,old,added)'
    inject=("    added=added.replace(old, \"    injection += \\\"timeout_pin=json.loads((ROOT/'tests/lock_wait_timeout/source-manifest.json').read_text())\\\\n\\\"\\n    injection += \\\"after.update({x['file']:x['sha256'] for x in timeout_pin['after']})\\\\n\\\"\\n\"+old)\n")
    text=change(text,marker,inject+marker)
    marker='    text=change(text,old,new)'
    # Insert the final override BEFORE the actual historical per-file loop.
    inject="    new=new.replace('    for row in pin[\"after\"]:', '    source_after.update({x[\"file\"]:x[\"sha256\"] for x in json.loads((ROOT/\"tests/lock_wait_timeout/source-manifest.json\").read_text())[\"after\"]})\\n    for row in pin[\"after\"]:')\n"
    text=change(text,marker,inject+marker)
    text=change(text,"assert pin['build_id']==BUILD_ID and pin['required_flag']=='EVILDUCK_ROUTE_B_SOURCE_TEXT_V2=1'","assert pin['build_id']=='ROUTEB-SOURCE-TEXT-PORTABILITY-v2' and pin['required_flag']=='EVILDUCK_ROUTE_B_SOURCE_TEXT_V2=1'")
    old="    for row in pin['after']:assert hashlib.sha256((args.build_root/'candidate/EvilDuckS3'/row['file']).read_bytes()).hexdigest()==row['sha256']"
    new="    timeout_after={x['file']:x['sha256'] for x in json.loads((ROOT/'tests/lock_wait_timeout/source-manifest.json').read_text())['after']}\n    for row in pin['after']:assert hashlib.sha256((args.build_root/'candidate/EvilDuckS3'/row['file']).read_bytes()).hexdigest()==timeout_after.get(row['file'],row['sha256'])"
    text=change(text,old,new)
    namespace={'__name__':'timeout_wait_parent','__file__':str(__file__)}
    exec(compile(text,str(parent),'exec'),namespace)
    assert namespace['main']()==0
    p=argparse.ArgumentParser();p.add_argument('--build-root',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
    report=json.loads(a.output.read_text());pin=json.loads((ROOT/'tests/lock_wait_timeout/source-manifest.json').read_text())
    assert pin['build_id']==BUILD_ID and pin['required_flag']=='EVILDUCK_ROUTE_B_LOCK_WAIT_TIMEOUT=1'
    assert pin['patch_sha256']==hashlib.sha256((ROOT/'tests/lock_wait_timeout/application.patch').read_bytes()).hexdigest()
    assert pin['parent_prepare_sha256']==hashlib.sha256((ROOT/'tests/source_text_v2/prepare_sources.py').read_bytes()).hexdigest()
    original={r['file'].removeprefix('EvilDuckS3/'):r['sha256'] for r in json.loads((ROOT/'docs/source-text-v2-build.json').read_text())['source_inventory']}
    assert {r['file'] for r in pin['before']}=={r['file'] for r in pin['after']}=={'core.cpp','core.h','adapter.cpp','adapter.h','caps_trial.h'}
    for r in pin['before']:assert original[r['file']]==r['sha256']
    for r in pin['after']:assert hashlib.sha256((a.build_root/'candidate/EvilDuckS3'/r['file']).read_bytes()).hexdigest()==r['sha256']
    entries=json.loads((a.build_root/'build/compile_commands.json').read_text())
    for entry in entries:
        if pathlib.Path(entry['file']).is_relative_to(a.build_root/'build/sketch'):
            assert '-DEVILDUCK_ROUTE_B_LOCK_WAIT_TIMEOUT=1' in entry['arguments']
    elf=a.build_root/'build/EvilDuckS3.ino.elf';assert BUILD_ID.encode() in elf.read_bytes() and b'$_EVILDUCK_LOCK_TIMEOUT' in elf.read_bytes()
    prefix=str(report['link_command'][0]).rsplit('g++',1)[0]
    raw=subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True)
    dem=subprocess.check_output([prefix+'nm','-C','--defined-only',str(elf)],text=True)
    byaddr={l.split()[0]:l.split(maxsplit=2)[2] for l in raw.splitlines() if len(l.split())==3};bodies={}
    for pattern in ('native_b::Adapter::wait(', 'native_b::Adapter::receive(', 'ds_preview::Runtime::completeInstruction(', 'ds_preview::Runtime::evaluationStep(', 'ds_preview::Runtime::rewindExecution()', 'ds_preview::Compiler::statement('):
        matches=[l for l in dem.splitlines() if len(l.split(maxsplit=2))==3 and l.split()[1] in ('T','t','W','w') and l.split(maxsplit=2)[2].startswith(pattern)]
        assert len(matches)==1,(pattern,matches)
        symbol=byaddr[matches[0].split()[0]]
        body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+symbol,str(elf)],text=True)
        assert '<'+symbol+'>:' in body
        bodies[pattern]=subprocess.check_output([prefix+'c++filt'],input=body,text=True)
    assert 'native_b::Adapter::wait(' in bodies['native_b::Adapter::receive(']
    assert 'hid_backend::lockEvidence(' in bodies['native_b::Adapter::wait(']
    assert not any(s in bodies['native_b::Adapter::wait('] for s in ('<malloc>','operator new(','<vTaskDelay>','<delay>'))
    report['source_text_v2_link_adapter']['adapter_sha256']=PARENT_SHA
    report['source_text_v2_link_adapter']['execution']='pinned parent source adapted by timeout_wait_link_adapter; not a separate old-profile check'
    report['timeout_wait_verified']=True;report['timeout_wait_source_pin']=pin;report['timeout_wait_linked_functions']=bodies
    report['timeout_wait_link_adapter']={'parent':'tests/source_text_v2/verify_link.py','parent_sha256':PARENT_SHA,'adapter_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'inherited_safety_predicates_removed':0,'build_id':BUILD_ID}
    report['profile']='ROUTE B LOCK WAIT TIMEOUT REVIEW ONLY; PHYSICAL VALIDATION PENDING'
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS pinned timeout sources, linked dispatch/wait/runtime and all inherited USB/NVS/archive guards')
    return 0
if __name__=='__main__':raise SystemExit(main())
