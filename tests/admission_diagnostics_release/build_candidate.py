#!/usr/bin/env python3
"""Committed clean admission-diagnostics target over the approved observer-v2 profile.

Execute the complete unchanged v2 committed-input guard first; append exact new
inputs and source/identity selection. SDK/archive/USB/partition/PSRAM/startup/link
predicates remain unchanged. No installer, hardware or publication interface.
"""
import argparse
import builtins
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent
PARENT=ROOT/'tests/usb_os_observer_v2_release/build_candidate.py'
PARENT_SHA='65ea2be88dcf28642290754a9d92e52df269a7d23fa77804ecc99de33799869b'
BUILD_ID='ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1'
PROFILE='ADMISSION DIAGNOSTICS / USB OBSERVER V2 / DEFINE / REPEAT / PRIVACY / H1 EXPERIMENTAL / REVIEW ONLY'
BASELINE='eb4c5d721e30893f7df908ac610d287d7541acf5'
DOC_INPUTS=['docs/admission-diagnostics-design.md','docs/admission-diagnostics-owner-check.md','docs/routeb-current-compatibility.md']
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def parent_module():
    assert sha(PARENT)==PARENT_SHA,'Historical v2 build driver changed'
    return load(PARENT,'admission_complete_v2_builder')
def build_inputs():
    inherited=parent_module().build_inputs();head=inherited['source_commit']
    subprocess.run(['git','merge-base','--is-ancestor',BASELINE,head],cwd=ROOT,check=True)
    names={row['file'] for row in inherited['files']}
    for directory in ['tests/admission_diagnostics','tests/admission_diagnostics_release','tests/admission_diagnostics_package']:
        names.update(str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file())
    # Exact postcompile artifact metadata is committed at the later package
    # checkpoint and checked by packaging; it is not compiler/source input.
    names.discard('tests/admission_diagnostics_package/release-binding.json')
    names.update(DOC_INPUTS)
    rows=[]
    for name in sorted(names):
        relative=pathlib.PurePosixPath(name);physical=ROOT/name
        assert not relative.is_absolute() and '..' not in relative.parts
        assert physical.is_file() and not physical.is_symlink(),name
        assert subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)==physical.read_bytes(),name
        rows.append(dict(file=name,size=physical.stat().st_size,sha256=sha(physical)))
    return dict(inherited,build_id=BUILD_ID,profile=PROFILE,files=rows,
        files_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        admission_diagnostics_source_baseline=BASELINE,
        inherited_observer_v2_guard=dict(file=str(PARENT.relative_to(ROOT)),sha256=PARENT_SHA,
            function='build_inputs',executed_unmodified=True,inherited_files_sha256=inherited['files_sha256']),
        postcompile_metadata_exclusions=[dict(file='tests/admission_diagnostics_package/release-binding.json',
            reason='Exact artifact/package identity written after compilation; package-checkpoint guarded separately')])

def adapted_source(source_commit):
    parent=parent_module();text,inherited=parent.adapted_source(source_commit);changes=[]
    def replace(old,new,count=1):
        nonlocal text
        assert text.count(old)==count,('Admission build occurrence mismatch',old,text.count(old))
        text=text.replace(old,new);changes.append(dict(before=old,after=new,occurrences=count))
    replace('tests/usb_os_observer_v2_release/prepare_sources.py','tests/admission_diagnostics_release/prepare_sources.py',4)
    replace('tests/usb_os_observer_v2_release/source-manifest.json','tests/admission_diagnostics_release/source-manifest.json')
    replace("text=text.replace('lock_feedback','usb_os_observer_v2_release')","text=text.replace('lock_feedback','admission_diagnostics_release')",2)
    replace("tests/usb_os_observer_v2_release/verify_target.py","tests/admission_diagnostics_release/verify_target.py",2)
    replace("ROOT / 'tests/usb_os_observer_v2_release'","ROOT / 'tests/admission_diagnostics_release'")
    replace('ROUTEB-USB-ENUM-OBSERVER-H1-v2',BUILD_ID,2)
    replace(parent.PROFILE,PROFILE)
    replace('one capture-only USB observer release overlay -> complete DEFINE parent -> bounded backend observation and authenticated manual diagnostics -> metadata identity last',
        'one admission-diagnostics release overlay -> complete observer-v2 parent -> request-owned diagnostics and existing byte gate -> metadata identity last')
    replace('changed_sources=["core.cpp", "shortcut_keys.h", "webfiles.h", "webserver.cpp", "caps_trial.h", "hid_backend.cpp", "hid_backend.h"],\n                     unchanged_sources=194, comparison_base="privacy-fix1",',
        'changed_sources=["core.cpp", "shortcut_keys.h", "webfiles.h", "webserver.cpp", "caps_trial.h", "hid_backend.cpp", "hid_backend.h", "adapter.cpp", "adapter.h"],\n                     unchanged_sources=192, comparison_base="privacy-fix1",')
    replace('cumulative_h1_changed_sources=["cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h", "core.cpp", "shortcut_keys.h", "hid_backend.cpp", "hid_backend.h"],\n                     cumulative_h1_unchanged_sources=193,',
        'cumulative_h1_changed_sources=["cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h", "core.cpp", "shortcut_keys.h", "hid_backend.cpp", "hid_backend.h", "adapter.cpp", "adapter.h"],\n                     cumulative_h1_unchanged_sources=191,')
    return text,dict(observer_v2=inherited,admission_diagnostics=changes)

def target_main():
    before=build_inputs();parent=parent_module();text,changes=adapted_source(before['source_commit'])
    namespace=dict(__name__='admission_default_target',__file__=str(__file__),LOCAL_INPUTS=build_inputs)
    exec(parent.ORIGINAL_COMPILE(text,str(PARENT),'exec'),namespace)
    parent.FLAG_EVENTS.clear()
    with patch.object(builtins,'compile',parent.flag_adapter):code=namespace['main']()
    if code:return code
    assert len(parent.FLAG_EVENTS)==1,'Expected exactly one unchanged observer compiler-flag adaptation'
    output=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1]);assert build_inputs()==before
    assert json.loads((output/'build-inputs.json').read_text())==before
    report=json.loads((output/'report.json').read_text());target=report['usb_observer_target_adapter']
    assert target['overlay_calls']==1
    target.update(build_inputs_sha256=sha(output/'build-inputs.json'),source_commit_contains_changes=True,source_provenance='COMMITTED_SOURCE_CHECKPOINT')
    report['usb_observer_flag_adapter']=parent.FLAG_EVENTS[0]
    report['admission_diagnostics_build_adapter']=dict(parent=str(PARENT.relative_to(ROOT)),parent_sha256=PARENT_SHA,
        adapter_sha256=sha(__file__),source_commit=before['source_commit'],build_inputs_sha256=sha(output/'build-inputs.json'),
        source_commit_contains_changes=True,build_id=BUILD_ID,exact_adaptations=changes,inherited_safety_predicates_removed=0,
        clean_compile=True,installed=False,owner_hardware_verified=False,canonical_entry='tools/build_routeb_candidate.py')
    report['status_label']='ADMISSION DIAGNOSTICS SOURCE INTEGRATED / COMPILE PASS / RELEASE CHECKS PENDING'
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    receipt=output/'admission-diagnostics-release-verification.json'
    try:load(HERE/'verify_release.py','admission_mandatory_release').run_chain(output,receipt)
    except Exception as error:
        report['status_label']='BLOCKED / ADMISSION DIAGNOSTIC RELEASE VERIFICATION FAILED'
        report['admission_diagnostics_release_failure']=dict(error_type=type(error).__name__,reason=str(error))
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');raise
    assert build_inputs()==before
    report['status_label']='ADMISSION DIAGNOSTICS CANDIDATE BUILT / NOT INSTALLED / NO OS CLASSIFIER'
    report['mandatory_release_verification']=dict(status='PASS',file=receipt.name,sha256=sha(receipt),full_frozen_layers=6,static_assert_nodes_retained=190)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    proof=json.loads((output/'usb-observer-composition.json').read_text())
    proof.update(source_commit_contains_changes=True,build_inputs_sha256=sha(output/'build-inputs.json'),source_provenance='COMMITTED_SOURCE_CHECKPOINT',status_label=report['status_label'])
    (output/'usb-observer-composition.json').write_text(json.dumps(proof,indent=2)+'\n')
    (output/'admission-diagnostics-composition.json').write_text(json.dumps(proof,indent=2)+'\n')
    return 0

def source_main():
    parser=argparse.ArgumentParser(description='Exact source-only admission composition from reviewed v2')
    parser.add_argument('--compose-only',action='store_true',required=True);parser.add_argument('--from-composed',type=pathlib.Path,required=True);parser.add_argument('--output-dir',type=pathlib.Path,required=True);args=parser.parse_args()
    M=load(HERE/'prepare_sources.py','admission_source_only');M.B.B.verify_final(args.from_composed)
    assert not args.output_dir.exists()
    for ancestor in (ROOT,args.from_composed):assert not args.output_dir.resolve().is_relative_to(ancestor.resolve())
    args.output_dir.mkdir(parents=True);source=args.output_dir/'EvilDuckS3';shutil.copytree(args.from_composed,source)
    M.B.delta(source);M.delta(source);rows=M.verify_final(source)
    (args.output_dir/'composition.json').write_text(json.dumps(dict(status='SOURCE_ONLY_COMPOSED',source=str(source),source_count=len(rows),sources=rows,build_id=BUILD_ID,firmware_built=False,hardware_access=False),indent=2)+'\n')
    print('PASS exact201 admission release composition; no compiler');return 0
def main():return source_main() if '--compose-only' in sys.argv else target_main()
if __name__=='__main__':raise SystemExit(main())
