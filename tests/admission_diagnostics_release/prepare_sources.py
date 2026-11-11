"""Exact admission-diagnostic release identity over the complete reviewed source.

The runtime delta belongs to tests/admission_diagnostics. This layer changes only
caps_trial::BuildId after applying that delta and checks the complete201 inventory.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
BUILD_ID = 'ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1'
OLD_BUILD_ID = 'ROUTEB-USB-ENUM-OBSERVER-H1-v2'
PARENT = ROOT / 'tests/admission_diagnostics/prepare_sources.py'
PARENT_SHA = 'f4ef46941f1bdffcc5f33ce16517d511580211d1d8028cdf36b985b34cd32ea1'
MANIFEST_SHA = '3eefbfdff35c637b6a7e913afbda2bb27ccdb88a003be55716f45cd5dd8d69d0'

def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def pin():
    assert digest(HERE/'source-manifest.json') == MANIFEST_SHA, 'ADMISSION_RELEASE_MANIFEST_CHANGED'
    value = json.loads((HERE/'source-manifest.json').read_text())
    assert value['format'] == 'evilduck-routeb-admission-diagnostics-release-v1'
    assert value['build_id'] == BUILD_ID and value['comparison_base'] == 'privacy-fix1'
    assert value['parent_prepare_sha256'] == PARENT_SHA == digest(PARENT), 'ADMISSION_RELEASE_PARENT_CHANGED'
    assert value['parent_manifest_sha256'] == digest(PARENT.with_name('source-manifest.json'))
    assert value['patch_sha256'] == digest(HERE/'identity.patch')
    assert value['admission_source_manifest_sha256'] == digest(PARENT.with_name('source-manifest.json'))
    assert value['observer_v2_release_manifest_sha256'] == digest(ROOT/'tests/usb_os_observer_v2_release/source-manifest.json')
    assert value['privacy_manifest_sha256'] == digest(ROOT/'tests/privacy_fix1/source-manifest.json')
    assert len(value['before']) == len(value['after']) == 9 and len(value['unchanged']) == 192
    assert {r['file'] for r in value['after']} == {'adapter.cpp','adapter.h','core.cpp','shortcut_keys.h','webfiles.h','webserver.cpp','caps_trial.h','hid_backend.cpp','hid_backend.h'}
    assert len(value['cumulative_h1_after']) == 10 and value['source_count'] == 201
    return value

pin()
spec = importlib.util.spec_from_file_location('admission_diagnostics_complete_parent', PARENT)
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)
prepare, native_sources, sha, frameworks, manifest, load = B.prepare, B.native_sources, B.sha, B.frameworks, B.manifest, B.load

def inventory(source):
    return B.inventory(source)

def verify_final(source):
    source = pathlib.Path(source)
    value = pin()
    expected = {r['file']:r['sha256'] for r in value['after']+value['unchanged']}
    assert len(expected) == 201 and inventory(source) == expected, 'ADMISSION_RELEASE_COMPOSITION_MISMATCH'
    assert (source/'caps_trial.h').read_bytes().count(BUILD_ID.encode()) == 1
    return [dict(file='EvilDuckS3/'+n,size=(source/n).stat().st_size,sha256=expected[n]) for n in sorted(expected)]

def delta(source):
    source = pathlib.Path(source)
    pin(); B.verify_final(source)
    before = (source/'caps_trial.h').read_bytes()
    result = subprocess.run(['patch','--batch','--fuzz=0','--no-backup-if-mismatch','-p0','-i',str(HERE/'identity.patch')],cwd=source,capture_output=True,text=True,check=True)
    assert 'fuzz' not in result.stdout.lower() and 'offset' not in result.stdout.lower()
    assert (source/'caps_trial.h').read_bytes() == before.replace(OLD_BUILD_ID.encode(),BUILD_ID.encode(),1)
    verify_final(source)
    return source

def overlay(source):
    pin(); B.overlay(source)
    return delta(source)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-composed',type=pathlib.Path,required=True)
    parser.add_argument('--output-dir',type=pathlib.Path,required=True)
    args = parser.parse_args()
    B.verify_final(args.from_composed)
    assert not args.output_dir.exists() and not args.output_dir.is_symlink()
    for ancestor in (ROOT,args.from_composed):
        assert not args.output_dir.resolve().is_relative_to(ancestor.resolve())
    args.output_dir.mkdir(parents=True)
    destination = args.output_dir/'EvilDuckS3'
    shutil.copytree(args.from_composed,destination)
    delta(destination)
    rows = verify_final(destination)
    (args.output_dir/'composition.json').write_text(json.dumps(dict(status='SOURCE_ONLY_COMPOSED',source=str(destination),source_count=len(rows),sources=rows,build_id=BUILD_ID,firmware_built=False,hardware_access=False),indent=2)+'\n')
    print('PASS exact201 admission-diagnostic release composition; no compiler')

if __name__ == '__main__':
    main()
