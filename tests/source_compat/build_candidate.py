#!/usr/bin/env python3
"""Isolated source-compat build; inherits approved USB/NVS/archive/startup guards."""
import hashlib
import json
import pathlib
import sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA='8f5d80eecd8a5d259764234b49346f17b7f1499532569044ccde9354e3bbca1c'

def main():
    parent=ROOT/'tests/lock_feedback/build_candidate.py'
    data=parent.read_bytes();assert hashlib.sha256(data).hexdigest()==PARENT_SHA
    text=data.decode()
    assert text.count('lock_feedback')==3
    text=text.replace('lock_feedback','source_compat')
    old="flags='-DEVILDUCK_ROUTE_B_LOCK_FEEDBACK=1"
    assert text.count(old)==1
    text=text.replace(old,"flags='-DEVILDUCK_ROUTE_B_SOURCE_COMPAT=1 -DEVILDUCK_ROUTE_B_LOCK_FEEDBACK=1")
    old='ROUTE B LOCK FEEDBACK REVIEW ONLY; PHYSICAL VALIDATION PENDING'
    assert text.count(old)==1
    text=text.replace(old,'ROUTE B SOURCE PREPROCESSING REVIEW ONLY; PHYSICAL VALIDATION PENDING')
    namespace={'__name__':'source_compat_build_adapter','__file__':str(__file__)}
    exec(compile(text,str(__file__),'exec'),namespace)
    result=namespace['main']()
    if result:return result
    output=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1])/'report.json'
    report=json.loads(output.read_text())
    report['source_compat_build_adapter']=dict(parent='tests/lock_feedback/build_candidate.py',parent_sha256=PARENT_SHA,adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),inherited_safety_predicates_removed=0,build_id='ROUTEB-PREPROCESS-20261024-v1')
    output.write_text(json.dumps(report,indent=2)+'\n')
    return 0
if __name__=='__main__':raise SystemExit(main())
