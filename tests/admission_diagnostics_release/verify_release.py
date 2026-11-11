#!/usr/bin/env python3
"""Retain every frozen v2/six-layer190 assertion and append admission proof."""
import argparse
import ast
import hashlib
import importlib.util
import json
import pathlib
import sys
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent
BUILD_ID='ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1'
PARENT=ROOT/'tests/usb_os_observer_v2_release/verify_release.py'
PARENT_SHA='4c6b70f7641f11bbcf2898a7d36631b60e75659153d310196d5dd4bad0fc7aa2'
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
assert sha(PARENT)==PARENT_SHA,'Historical v2 release verifier changed'
P=load(PARENT,'admission_frozen_v2_release')
P.__file__=str(pathlib.Path(__file__).resolve())
P.BUILD_ID=BUILD_ID;P.D.BUILD_ID=BUILD_ID;P.HERE=HERE
ORIGINAL_COMPILE=P.ORIGINAL_COMPILE
RELEASE_EDITS=[
 ('tests/usb_os_observer_v2_release/','tests/admission_diagnostics_release/',3),
 ('{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h", "hid_backend.cpp", "hid_backend.h"}',
  '{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h", "hid_backend.cpp", "hid_backend.h", "adapter.cpp", "adapter.h"}',2),
 ('Same pinned comparison policy, with the exact eight cumulative files.','Same pinned comparison policy, with the exact ten cumulative files.',1),
]
def counts(text):
    tree=ast.parse(text)
    return dict(asserts=sum(isinstance(n,ast.Assert) for n in ast.walk(tree)),require_calls=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' for n in ast.walk(tree)))
def adapted_text(text):
    original=counts(text);changes=[]
    for old,new,count in RELEASE_EDITS:
        assert text.count(old)==count,('Admission release occurrence mismatch',old,text.count(old))
        text=text.replace(old,new);changes.append(dict(before=old,after=new,occurrences=count))
    assert counts(text)==original,'An inherited release predicate was removed'
    return text,dict(edits=changes,predicates_retained=original)
_P_ADAPTED=P.adapted_parent
def adapted_parent():
    events=[]
    def adapt(source,filename,mode,*args,**kwargs):
        if mode=='exec' and isinstance(source,str) and 'report["usb_observer_release_verification"]' in source:
            source,evidence=adapted_text(source);events.append(evidence)
        return ORIGINAL_COMPILE(source,filename,mode,*args,**kwargs)
    with patch.object(P,'ORIGINAL_COMPILE',adapt):namespace,inherited=_P_ADAPTED()
    assert len(events)==1,'Complete v2 release adaptation absent/ambiguous'
    return namespace,dict(observer_v2=inherited,admission_diagnostics=events[0],
        active_verifier_context=dict(file=str(pathlib.Path(__file__).relative_to(ROOT)),
            build_id=BUILD_ID,parent_sha256=PARENT_SHA))
P.adapted_parent=adapted_parent

def run_chain(root,output):
    report=P.run_chain(root,output)
    info=report['usb_observer_release_verification'];binding=info['usb_observer_target_binding']
    assert info['assertions_preserved']==190 and info['assertions_removed']==0
    admission=binding['admission_diagnostics']
    assert admission['status']=='PASS' and admission['existing_error_code']==2
    assert admission['coordinator_source_unchanged'] and admission['status_schema_unchanged']
    assert admission['source_acceptance_unchanged'] and admission['compiler_workspace_bytes']==4096
    assert {row['file'] for row in admission['compiled_units']}=={'adapter.cpp','coordinator.cpp'}
    assert all(row['header_dependency'] for row in admission['compiled_units'])
    assert binding['build_id']==report['actual_runtime_build_id']==BUILD_ID
    report['admission_diagnostics_source_pin']=json.loads((ROOT/'tests/admission_diagnostics/source-manifest.json').read_text())
    report['admission_diagnostics_build_source_pin']=json.loads((HERE/'source-manifest.json').read_text())
    report['admission_diagnostics_release_verification']=dict(status='PASS',build_id=BUILD_ID,
        inherited_assertions_preserved=190,inherited_assertions_removed=0,
        source_manifest_sha256=sha(ROOT/'tests/admission_diagnostics/source-manifest.json'),
        release_manifest_sha256=sha(HERE/'source-manifest.json'),target_binding=admission,
        parent_verifier=str(PARENT.relative_to(ROOT)),parent_sha256=PARENT_SHA,
        installed=False,owner_hardware_verified=False)
    info['status_label']='ADMISSION DIAGNOSTICS / H1 EXPERIMENTAL / NOT INSTALLED'
    pathlib.Path(output).write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build-root',type=pathlib.Path,required=True);parser.add_argument('--output',type=pathlib.Path,required=True);args=parser.parse_args()
    run_chain(args.build_root,args.output)
    print('PASS request-owned admission diagnostics and all190 retained inherited assertions')
if __name__=='__main__':main()
