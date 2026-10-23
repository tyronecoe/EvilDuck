#!/usr/bin/env python3
"""Assemble verified public app-only artifacts. No device or network operations."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PACKAGE = 'evilduck-routeb-lock-feedback-macos-v1'
ROLLBACK_SHA = 'de0d34d577cbaebb31bdeff825bd264d527f6c894103d6e0ed66140022016cf3'
ROLLBACK_BYTES = 1406016
TABLE_SHA = 'b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e'


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pinned_replace(text, old, new):
    assert text.count(old) == 1, 'Historical installer adaptation marker mismatch'
    return text.replace(old, new)


def prepare(out, build_root, linked_report, core, source_commit):
    out, build_root, linked_report, core = map(pathlib.Path, (out, build_root, linked_report, core))
    assert re.fullmatch('[0-9a-f]{40}', source_commit)
    subprocess.run(['git', 'merge-base', '--is-ancestor', source_commit, 'HEAD'], cwd=ROOT, check=True)
    assert not out.exists() and not out.is_symlink() and ROOT not in out.resolve().parents
    # The source commit must actually contain the release's source delta/tools.
    for name in ('tests/lock_feedback/package.py', 'tests/lock_feedback/preflight.py',
                 'tests/lock_feedback/application.patch', 'tests/lock_feedback/source-manifest.json'):
        assert subprocess.check_output(['git', 'show', source_commit + ':' + name], cwd=ROOT) == (ROOT/name).read_bytes(), name
    receipt = json.loads(linked_report.read_text())
    assert receipt['status'] == 'PASS' and receipt['lock_feedback_verified'] is True
    assert receipt['sdk_archives_identical_to_w'] == 177
    sys.path.insert(0, str(ROOT/'tools'))
    from feedback_core import check_sources
    assert check_sources(core, True) == receipt['core_pin']
    build = build_root/'build'
    for row in receipt['source_inventory']:
        f = build_root/'candidate'/row['file']
        assert f.is_file() and not f.is_symlink() and f.stat().st_size == row['size'] and sha(f) == row['sha256'], row['file']
    for row in receipt['artifacts']:
        f = build/row['file']
        assert f.is_file() and not f.is_symlink() and f.stat().st_size == row['size'] and sha(f) == row['sha256'], row['file']
    app = build/'EvilDuckS3.ino.bin'
    elf = build/'EvilDuckS3.ino.elf'
    table = build/'EvilDuckS3.ino.partitions.bin'
    assert app.stat().st_size == receipt['report']['application_bytes']
    assert sha(app) == receipt['report']['application_sha256']
    assert sha(elf) == receipt['provenance']['elf_sha256']
    assert sha(table) == TABLE_SHA
    rollback = ROOT/'downloads/evilduck-keyboard-control-rollback.bin'
    assert rollback.stat().st_size == ROLLBACK_BYTES and sha(rollback) == ROLLBACK_SHA
    rollback_receipt = json.loads((ROOT/'docs/keyboard-control-build.json').read_text())
    assert rollback_receipt['report']['application_sha256'] == ROLLBACK_SHA
    assert rollback_receipt['report']['application_bytes'] == ROLLBACK_BYTES
    out.mkdir()
    copies = {
        'application.bin': app, 'rollback-application.bin': rollback,
        'expected-partitions.bin': table, 'build-receipt.json': linked_report,
        'rollback-build-receipt.json': ROOT/'docs/keyboard-control-build.json',
        'OWNER-CHECK.md': ROOT/'docs/lock-feedback-owner-check.md',
        'INSTALL-MAC.md': ROOT/'docs/lock-feedback-install.md',
        'ROLLBACK-MAC.md': ROOT/'docs/lock-feedback-rollback.md',
        'firmware-report.md': ROOT/'docs/lock-feedback-report.md',
        'test-results.json': ROOT/'docs/lock-feedback-test-results.json',
        'compatibility.md': ROOT/'docs/lock-feedback-compatibility.md',
        'owner-evidence.md': ROOT/'docs/lock-feedback-owner-acceptance.md',
        'reproduction.md': ROOT/'docs/lock-feedback-reproduction.md',
        'source-manifest.json': ROOT/'tests/lock_feedback/source-manifest.json',
        'dependency-pin.json': ROOT/'docs/caps-stop-dependency-pin.json',
        'gen_esp32part.py': core/'tools/gen_esp32part.py',
        'APACHE-2.0.txt': pathlib.Path('/usr/share/common-licenses/Apache-2.0'),
        'source-LICENSE.txt': ROOT/'LICENSE',
    }
    for name, source in copies.items():
        assert source.is_file() and not source.is_symlink(), source
        shutil.copyfile(source, out/name)
    (out/'README.md').write_text(
        'REVIEW ONLY: Route B lock-feedback application-only Mac package. '
        'Read INSTALL-MAC.md and OWNER-CHECK.md. No installation is authorized by this package. '
        'New lock-feedback physical acceptance remains pending on macOS 10.13.6. '
        'The prior keyboard-control trials are owner-confirmed; new feedback is not physically tested. '
        'Rollback restores ROUTEB-KEYBOARD-CONTROL-20261022-v1, SHA-256 ' + ROLLBACK_SHA + '.\n')
    template = (ROOT/'tests/lock_feedback/preflight.py').read_text()
    bound = dict(source_commit=source_commit, application_bytes=app.stat().st_size,
                 application_sha256=sha(app))
    (out/'preflight.py').write_text(pinned_replace(template, 'RELEASE=None', 'RELEASE='+repr(bound)))
    original = (ROOT/'tests/mac_install/installer.py').read_text()
    original = pinned_replace(original, "ROLLBACK_SHA='c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4'", "ROLLBACK_SHA='"+ROLLBACK_SHA+"'")
    original = pinned_replace(original, 'ROLLBACK_BYTES=1376576', 'ROLLBACK_BYTES='+str(ROLLBACK_BYTES))
    original = pinned_replace(original, "prefix='evilduck-before-caps-'", "prefix='evilduck-before-lock-feedback-'")
    original = pinned_replace(original, ' result=subprocess.run(command,capture_output=True,text=True,timeout=3600)',
        " operation=next((part for part in command[3:] if part in ['version','flash_id','get_security_info','read_flash','write_flash','verify_flash']),None)\n"
        " require(operation is not None,'UNSUPPORTED_OPERATION')\n"
        " tool_process.step=getattr(tool_process,'step',0)+1\n"
        " print('Step %d: %s'%(tool_process.step,operation),flush=True)\n"
        " result=subprocess.run(command,capture_output=True,text=True,timeout=3600)\n"
        " print('Step %d: %s %s'%(tool_process.step,operation,'PASS' if result.returncode==0 else 'FAIL'),flush=True)")
    binding = dict(preflight_sha256=sha(out/'preflight.py'))
    original = pinned_replace(original, 'RELEASE_BINDING=None', 'RELEASE_BINDING='+repr(binding))
    original = original.replace('PREPARATION ONLY: no approved release binding. CLI fails before device access.',
        'Bound application-only Mac installer; check is the default action.')
    original = original.replace('A reviewed build/package must bind this in a later review before installation.',
        'Physical installation still requires separate owner authorization.')
    (out/'installer.py').write_text(original)
    for name in ('install-macos.sh', 'rollback-macos.sh'):
        text = (ROOT/'tests/mac_install'/name).read_text()
        text = text.replace('# PREPARATION ONLY. No release binding; Python exits before any hardware access.',
            '# Bound review package. Default check only; physical installation requires owner authorization.')
        text = text.replace('# PREPARATION ONLY. A separate deliberate rollback action; no implicit retry.',
            '# Bound review package. Separate deliberate rollback only; no implicit retry.')
        (out/name).write_text(text)
    validator = load(out/'preflight.py', 'keyboard_package_preflight')
    support = {p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())
               if p.name not in ('application.bin','rollback-application.bin','expected-partitions.bin')}
    manifest = dict(package_id=PACKAGE, label='REVIEW ONLY; NEW LOCK FEEDBACK PHYSICALLY UNVERIFIED',
        source_commit=source_commit, source_url='https://github.com/tyronecoe/EvilDuck/tree/'+source_commit,
        composition_base_commit='bbc83640a264c6398d396fdca564804f62ece117',
        composition_pin_sha256=sha(out/'source-manifest.json'),
        application_bytes=app.stat().st_size, application_sha256=sha(app),
        application_elf_sha256=sha(elf), table_sha256=TABLE_SHA,
        update_method='FUTURE_ROM_APP_ONLY_BOTH_SLOTS', installation_authorized=False, hardware=False,
        proposed_writes=validator.rows(), rollback_writes=validator.rows('rollback'),
        rollback_bytes=ROLLBACK_BYTES, rollback_sha256=ROLLBACK_SHA,
        rollback_source_commit='c7eb40f20fcdab54670c6bd6dce187faf9250115',
        support_files=support,
        protected_nonapplication_regions='all; bootloader/table/NVS/otadata/SPIFFS/coredump excluded from write plan',
        required_installed_otadata_sha256=validator.OTA_SHA, unsigned_integrity_only=True)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    validator.validate(out)
    return manifest


def archive(directory, destination):
    directory, destination = map(pathlib.Path, (directory, destination))
    load(directory/'preflight.py', 'keyboard_archive_preflight').validate(directory)
    assert not destination.exists() and not destination.is_symlink()
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for source in sorted(directory.iterdir()):
            info = zipfile.ZipInfo(source.name, (2026,10,23,0,0,0))
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info,source.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return dict(file=destination.name, bytes=destination.stat().st_size,sha256=sha(destination),
                files=[p.name for p in sorted(directory.iterdir())])


def main():
    parser = argparse.ArgumentParser()
    for name in ('directory','build-root','linked-report','core','archive'):
        parser.add_argument('--'+name,type=pathlib.Path,required=True)
    parser.add_argument('--source-commit',required=True)
    args = parser.parse_args()
    prepare(args.directory,args.build_root,args.linked_report,args.core,args.source_commit)
    print(json.dumps(archive(args.directory,args.archive),indent=2))


if __name__ == '__main__': main()
