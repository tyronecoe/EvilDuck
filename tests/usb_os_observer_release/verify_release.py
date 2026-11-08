#!/usr/bin/env python3
"""Keep all six frozen layers and190 assertions; bind one capture-only image."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import sys
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent
BUILD_ID='ROUTEB-USB-ENUM-OBSERVER-H1-v1'
PARENT=ROOT/'tests/define_labels_release/verify_release.py'
PARENT_SHA='3cc4c4d3e82d4cec3e0d5ff701869a0d1028bd161b473d2cc430204f900334f2'

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
assert sha(PARENT)==PARENT_SHA,'Historical DEFINE release verifier changed'
D=load(PARENT,'usb_observer_complete_define_release')
CompilerHandlerExpectations=D.CompilerHandlerExpectations
adapt_compiler_handler=D.adapt_compiler_handler
ORIGINAL_COMPILE=D.ORIGINAL_COMPILE

def adapted_parent():
    D.BUILD_ID=BUILD_ID;captured=[]
    def capture(source,filename,mode,*args,**kwargs):
        if mode=='exec' and isinstance(source,str) and 'report["define_labels_release_verification"]' in source:captured.append(source)
        return ORIGINAL_COMPILE(source,filename,mode,*args,**kwargs)
    with patch.object(D,'ORIGINAL_COMPILE',capture):_,inherited=D.adapted_parent()
    assert len(captured)==1,'Complete DEFINE release source capture ambiguous'
    text=captured[0];changes=[]
    def replace(old,new,count=1):
        nonlocal text
        assert text.count(old)==count,('Observer release occurrence mismatch',old,text.count(old))
        text=text.replace(old,new);changes.append(dict(before=old,after=new,occurrences=count))
    replace('tests/define_labels_release/source-manifest.json','tests/usb_os_observer_release/source-manifest.json')
    replace('tests/define_labels_release/identity.patch','tests/usb_os_observer_release/identity.patch')
    replace('tests/define_labels_release/verify_target.py','tests/usb_os_observer_release/verify_target.py')
    replace('define_labels_target_adapter','usb_observer_target_adapter')
    replace('define_labels_target_binding','usb_observer_target_binding',2)
    replace('define_labels_release_verification','usb_observer_release_verification')
    replace('report["define_labels_build_source_pin"] = pin','report["usb_observer_build_source_pin"] = pin')
    replace('{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h"}',
            '{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h", "hid_backend.cpp", "hid_backend.h"}',2)
    replace('Same pinned comparison policy, with the exact six cumulative files.',
            'Same pinned comparison policy, with the exact eight cumulative files.')
    replace('DEFINE LABELS / DEL ALIAS / PREVIOUS COMMAND REPEAT / STATIC RESPONSE / EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / REVIEW / NOT OWNER-HARDWARE-VERIFIED',
            'USB ENUMERATION CAPTURE ONLY / DEFINE LABELS / DEL / REPEAT / PRIVACY / H1 EXPERIMENTAL / REVIEW / NOT OWNER-HARDWARE-VERIFIED')
    ns=dict(__name__='usb_observer_frozen_six_layer_release',__file__=str(__file__),REPEAT_HANDLER_ADAPT=adapt_compiler_handler)
    exec(ORIGINAL_COMPILE(text,str(ROOT/'tests/dashboard_cleanup/verify_release.py'),'exec'),ns)
    return ns,dict(define_labels=inherited,usb_observer=changes)

def run_chain(build_root,output):
    ns,changes=adapted_parent();report=ns['run_chain'](build_root,output)
    info=report['usb_observer_release_verification'];binding=info['usb_observer_target_binding']
    assert info['assertions_preserved']==190 and info['assertions_removed']==0
    assert len(binding['bundled_resources'])==5 and binding['streaming_response']['status']=='PASS'
    assert binding['previous_command_repeat']['standalone_branch_verified'] is True
    assert binding['previous_command_repeat']['modifier_handler_reachable'] is True
    assert binding['del_alias']['status']=='PASS' and binding['del_alias']['usage']==0x4c
    assert binding['define_labels']['workspace_bytes']==4096 and binding['define_labels']['target_compiler_bytes']==3928
    assert binding['define_labels']['max_label_bytes']==31 and binding['define_labels']['constant_slots']==16
    observed=binding['usb_observer'];assert observed['status']=='PASS' and observed['capture_only'] is True
    assert observed['classification']=='UNKNOWN' and observed['original_handler_called_once'] is True
    assert observed['dcd_calls_wrapper'] is True and observed['dedicated_state_bytes']<=2048
    assert observed['early_bss_state'] is True and observed['dynamic_observer_initialization_absent'] is True
    assert binding['committed_source_provenance']['source_commit']==binding['committed_source_provenance']['verifier_context_commit']
    assert binding['committed_source_provenance']['post_compile_verifier_delta'] is None
    assert sum(len(e['compiler_handler_adaptations']) for e in info['compile_events'])==2
    info.update(integration_adaptations=changes,installed=False,owner_hardware_verified=False,
        status_label='CAPTURE ONLY / UNKNOWN / NO OS CLASSIFIER / NOT INSTALLED')
    for key,directory in [('dashboard_parent_source_pin','dashboard_cleanup'),('reviewed_editor_source_pin','editor_load_safety'),
        ('editor_build_source_pin','editor_build_integration'),('static_response_source_pin','dashboard_response_safety'),
        ('static_response_build_source_pin','static_response_build_integration'),('previous_repeat_source_pin','previous_command_repeat'),
        ('previous_repeat_build_source_pin','previous_command_repeat_release'),('del_alias_source_pin','del_alias'),
        ('del_alias_build_source_pin','del_alias_release'),('define_labels_source_pin','define_labels'),
        ('define_labels_build_source_pin','define_labels_release'),('usb_observer_source_pin','usb_os_observer'),
        ('usb_observer_web_source_pin','usb_os_observer_web'),('usb_observer_build_source_pin','usb_os_observer_release')]:
        report[key]=json.loads((ROOT/'tests'/directory/'source-manifest.json').read_text())
    pathlib.Path(output).write_text(json.dumps(report,indent=2)+'\n');return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build-root',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
    run_chain(a.build_root,a.output);print('PASS capture-only observer with all190 inherited assertions, exact wrapper and resource proofs')
if __name__=='__main__':main()
