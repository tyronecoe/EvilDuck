#!/usr/bin/env python3
"""Committed capture-only USB observer build; no hardware or installation API."""
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
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ROOT / 'tests/define_labels_release/build_candidate.py'
PARENT_SHA = '294569f8a1cf1cc7a43f12ba6740965a64abb46a65e9c178c2705afafd73225d'
BUILD_ID = 'ROUTEB-USB-ENUM-OBSERVER-H1-v1'
OLD_BUILD_ID = 'ROUTEB-DEFINE-LABELS-H1-v1'
PROFILE = 'USB ENUMERATION CAPTURE ONLY / DEFINE LABELS / DEL / REPEAT / PRIVACY / H1 EXPERIMENTAL / REVIEW ONLY'
BASELINE = 'bdc8cbeea024ebb63f952da7fc4f39ac9e32fe29'
DOC_INPUTS = ['docs/usb-os-observer-contract.md', 'docs/usb-os-evidence-gate.json',
              'docs/define-labels-owner-acceptance.md', 'docs/routeb-current-compatibility.md']
ORIGINAL_COMPILE = builtins.compile
FLAG_EVENTS = []

def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

def parent_module():
    assert sha(PARENT) == PARENT_SHA, 'Historical DEFINE builder changed'
    return load(PARENT, 'usb_observer_committed_define_parent')

def build_inputs():
    # Executes the complete unchanged committed-source guard chain.
    inherited = parent_module().build_inputs()
    head = inherited['source_commit']
    subprocess.run(['git', 'merge-base', '--is-ancestor', BASELINE, head], cwd=ROOT, check=True)
    names = {row['file'] for row in inherited['files']}
    for directory in ['tests/usb_os_observer', 'tests/usb_os_observer_web', 'tests/usb_os_observer_release']:
        names.update(str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*') if p.is_file())
    names.update(DOC_INPUTS)
    rows = []
    for name in sorted(names):
        relative = pathlib.PurePosixPath(name); physical = ROOT/name
        assert not relative.is_absolute() and '..' not in relative.parts
        assert physical.is_file() and not physical.is_symlink()
        assert subprocess.check_output(['git','show',head+':'+name], cwd=ROOT) == physical.read_bytes(), name
        rows.append(dict(file=name,size=physical.stat().st_size,sha256=sha(physical)))
    return dict(inherited,build_id=BUILD_ID,profile=PROFILE,files=rows,
        files_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        usb_observer_source_baseline=BASELINE,
        inherited_define_guard=dict(file=str(PARENT.relative_to(ROOT)),sha256=PARENT_SHA,
            function='build_inputs',executed_unmodified=True,inherited_files_sha256=inherited['files_sha256']))

def adapted_source(source_commit):
    parent = parent_module(); text, inherited = parent.adapted_source(source_commit); changes=[]
    def replace(old,new,count=1):
        nonlocal text
        assert text.count(old)==count,('Observer build occurrence mismatch',old,text.count(old))
        text=text.replace(old,new);changes.append(dict(before=old,after=new,occurrences=count))
    replace('tests/define_labels_release/prepare_sources.py','tests/usb_os_observer_release/prepare_sources.py',4)
    replace('tests/define_labels_release/source-manifest.json','tests/usb_os_observer_release/source-manifest.json')
    replace("text=text.replace('lock_feedback','define_labels_release')","text=text.replace('lock_feedback','usb_os_observer_release')",2)
    replace('one DEFINE-label release overlay -> complete DEL parent -> bounded constant cells and collection/flag length checks -> metadata identity last',
            'one capture-only USB observer release overlay -> complete DEFINE parent -> bounded backend observation and authenticated manual diagnostics -> metadata identity last')
    replace(parent.PROFILE,PROFILE)
    replace('dashboard_build_id='+repr(OLD_BUILD_ID),'dashboard_build_id='+repr(BUILD_ID))
    replace('changed_sources=["core.cpp", "shortcut_keys.h", "webfiles.h", "webserver.cpp", "caps_trial.h"],\n                     unchanged_sources=196, comparison_base="privacy-fix1",',
            'changed_sources=["core.cpp", "shortcut_keys.h", "webfiles.h", "webserver.cpp", "caps_trial.h", "hid_backend.cpp", "hid_backend.h"],\n                     unchanged_sources=194, comparison_base="privacy-fix1",')
    replace('cumulative_h1_changed_sources=["cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h", "core.cpp", "shortcut_keys.h"],\n                     cumulative_h1_unchanged_sources=195,',
            'cumulative_h1_changed_sources=["cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h", "core.cpp", "shortcut_keys.h", "hid_backend.cpp", "hid_backend.h"],\n                     cumulative_h1_unchanged_sources=193,')
    for old,new,count in [('define-labels-composition.json','usb-observer-composition.json',2),
        ('define-labels-target-verification.json','usb-observer-target-verification.json',1),
        ('define-labels-target-failure.json','usb-observer-target-failure.json',1),
        ('define-labels-target-verification','usb-observer-target-verification',1),
        ('report["define_labels_target_adapter"]','report["usb_observer_target_adapter"]',1),
        ('define_labels_target_binding=binding','usb_observer_target_binding=binding',1)]:replace(old,new,count)
    return text,dict(define_labels=inherited,usb_observer=changes)

def flag_adapter(source,filename,mode,*args,**kwargs):
    if mode=='exec' and isinstance(source,str) and "args=['compile','--fqbn',s3_validation.FQBN" in source:
        old="flags='-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1"
        new="flags='-DEVILDUCK_USB_ENUM_OBSERVER=1 -DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1"
        assert source.count(old)==1 and 'EVILDUCK_USB_ENUM_OBSERVER' not in source
        source=source.replace(old,new,1)
        old="'--build-property','compiler.cpp.extra_flags='+flags]"
        new="'--build-property','compiler.cpp.extra_flags='+flags,'--build-property','compiler.c.elf.extra_flags=-Wl,--wrap=dcd_event_handler']"
        assert source.count(old)==1
        source=source.replace(old,new,1)
        FLAG_EVENTS.append(dict(filename=str(filename),cpp_flag='EVILDUCK_USB_ENUM_OBSERVER=1',
            additive_link_property='compiler.c.elf.extra_flags=-Wl,--wrap=dcd_event_handler',
            compiled_adapter_sha256=hashlib.sha256(source.encode()).hexdigest(),original_predicates_removed=0))
    return ORIGINAL_COMPILE(source,filename,mode,*args,**kwargs)

def target_main():
    before=build_inputs();text,changes=adapted_source(before['source_commit'])
    namespace=dict(__name__='usb_observer_default_build',__file__=str(__file__),LOCAL_INPUTS=build_inputs)
    exec(ORIGINAL_COMPILE(text,str(PARENT),'exec'),namespace)
    FLAG_EVENTS.clear()
    with patch.object(builtins,'compile',flag_adapter):code=namespace['main']()
    if code:return code
    assert len(FLAG_EVENTS)==1,'Expected exactly one real compile-driver adaptation'
    output=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1]);assert build_inputs()==before
    assert json.loads((output/'build-inputs.json').read_text())==before
    report=json.loads((output/'report.json').read_text());target=report['usb_observer_target_adapter']
    assert target['overlay_calls']==1
    target.update(build_inputs_sha256=sha(output/'build-inputs.json'),source_commit_contains_changes=True,
                  source_provenance='COMMITTED_SOURCE_CHECKPOINT')
    report['usb_observer_flag_adapter']=FLAG_EVENTS[0]
    report['usb_observer_build_adapter']=dict(parent=str(PARENT.relative_to(ROOT)),parent_sha256=PARENT_SHA,
        adapter_sha256=sha(__file__),source_commit=before['source_commit'],build_inputs_sha256=sha(output/'build-inputs.json'),
        source_commit_contains_changes=True,build_id=BUILD_ID,exact_adaptations=changes,
        inherited_safety_predicates_removed=0,clean_compile=True,installed=False,owner_hardware_verified=False,
        canonical_entry='tools/build_routeb_candidate.py')
    report['status_label']='CAPTURE-ONLY SOURCE INTEGRATED / COMPILE PASS / RELEASE CHECKS PENDING'
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    receipt=output/'usb-observer-release-verification.json'
    try:load(HERE/'verify_release.py','usb_observer_mandatory_release').run_chain(output,receipt)
    except Exception as error:
        report['status_label']='BLOCKED / USB OBSERVER RELEASE VERIFICATION FAILED'
        report['usb_observer_release_failure']=dict(error_type=type(error).__name__,reason=str(error))
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');raise
    assert build_inputs()==before
    report['status_label']='CAPTURE-ONLY CANDIDATE BUILT / NOT INSTALLED / NO OS CLASSIFIER'
    report['mandatory_release_verification']=dict(status='PASS',file=receipt.name,sha256=sha(receipt),
        full_frozen_layers=6,static_assert_nodes_retained=190)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    proof=json.loads((output/'usb-observer-composition.json').read_text())
    proof.update(source_commit_contains_changes=True,build_inputs_sha256=sha(output/'build-inputs.json'),
        source_provenance='COMMITTED_SOURCE_CHECKPOINT',status_label=report['status_label'])
    (output/'usb-observer-composition.json').write_text(json.dumps(proof,indent=2)+'\n')
    return 0

def source_main():
    p=argparse.ArgumentParser(description='Exact source-only capture candidate composition')
    p.add_argument('--compose-only',action='store_true',required=True)
    p.add_argument('--from-composed',type=pathlib.Path,required=True);p.add_argument('--output-dir',type=pathlib.Path,required=True)
    a=p.parse_args();m=load(HERE/'prepare_sources.py','usb_observer_source_only')
    m.B.verify_final(a.from_composed);assert not a.output_dir.exists()
    for ancestor in (ROOT,a.from_composed):assert not a.output_dir.resolve().is_relative_to(ancestor.resolve())
    a.output_dir.mkdir(parents=True);source=a.output_dir/'EvilDuckS3';shutil.copytree(a.from_composed,source)
    m.delta(source);rows=m.verify_final(source)
    (a.output_dir/'composition.json').write_text(json.dumps(dict(status='SOURCE_ONLY_COMPOSED',source=str(source),
        source_count=len(rows),sources=rows,build_id=BUILD_ID,firmware_built=False,hardware_access=False),indent=2)+'\n')
    print('PASS exact201 capture-only source composition; no compiler');return 0

def main():return source_main() if '--compose-only' in sys.argv else target_main()
if __name__=='__main__':raise SystemExit(main())
