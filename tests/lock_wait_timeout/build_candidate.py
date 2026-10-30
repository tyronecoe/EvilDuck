# Pinned additive adaptation of source_text_v2/build_candidate.py SHA256 6779f98a31447a614ac79601fc383236515873c8e4631d56089bfb70bdda701b
#!/usr/bin/env python3
"""Isolated source/text portability build; inherits approved USB/NVS/archive/startup guards."""
import hashlib
import json
import pathlib
import sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA='8f5d80eecd8a5d259764234b49346f17b7f1499532569044ccde9354e3bbca1c'

def main():
    assert hashlib.sha256((ROOT/'tests/source_text_v2/build_candidate.py').read_bytes()).hexdigest()=='6779f98a31447a614ac79601fc383236515873c8e4631d56089bfb70bdda701b'
    parent=ROOT/'tests/lock_feedback/build_candidate.py'
    data=parent.read_bytes();assert hashlib.sha256(data).hexdigest()==PARENT_SHA
    text=data.decode()
    assert text.count('lock_feedback')==3
    text=text.replace('lock_feedback','lock_wait_timeout')
    old="flags='-DEVILDUCK_ROUTE_B_LOCK_FEEDBACK=1"
    assert text.count(old)==1
    text=text.replace(old,"flags='-DEVILDUCK_ROUTE_B_LOCK_WAIT_TIMEOUT=1 -DEVILDUCK_ROUTE_B_SOURCE_TEXT_V2=1 -DEVILDUCK_ROUTE_B_SOURCE_TEXT=1 -DEVILDUCK_ROUTE_B_PAYLOAD_RESTART=1 -DEVILDUCK_ROUTE_B_TEXT_KEYBOARD=1 -DEVILDUCK_ROUTE_B_RANDOMIZATION_JITTER=1 -DEVILDUCK_ROUTE_B_RANDOM_UPPERCASE=1 -DEVILDUCK_ROUTE_B_RANDOM_LOWERCASE=1 -DEVILDUCK_ROUTE_B_SOURCE_COMPAT=1 -DEVILDUCK_ROUTE_B_LOCK_FEEDBACK=1")
    old='ROUTE B LOCK FEEDBACK REVIEW ONLY; PHYSICAL VALIDATION PENDING'
    assert text.count(old)==1
    text=text.replace(old,'ROUTE B LOCK WAIT TIMEOUT REVIEW ONLY; PHYSICAL VALIDATION PENDING')
    namespace={'__name__':'source_text_v2_build_adapter','__file__':str(__file__)}
    exec(compile(text,str(__file__),'exec'),namespace)
    result=namespace['main']()
    if result:return result
    output=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1])/'report.json'
    report=json.loads(output.read_text())
    report['timeout_wait_build_adapter']=dict(parent='tests/lock_feedback/build_candidate.py',parent_sha256=PARENT_SHA,adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),inherited_safety_predicates_removed=0,build_id='ROUTEB-LOCK-WAIT-TIMEOUT-v1')
    report['source_text_v2_build_adapter']=dict(parent='tests/lock_feedback/build_candidate.py',parent_sha256=PARENT_SHA,adapter_sha256=hashlib.sha256((ROOT/'tests/source_text_v2/build_candidate.py').read_bytes()).hexdigest(),execution='pinned parent source adapted by timeout_wait_build_adapter; not a separate old-profile build',inherited_safety_predicates_removed=0,build_id='ROUTEB-SOURCE-TEXT-PORTABILITY-v2')
    output.write_text(json.dumps(report,indent=2)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
