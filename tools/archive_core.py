#!/usr/bin/env python3
"""Separately approved archive profile; historical profiles remain unchanged."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from s3_validation import ROOT, require, partition_tool

PATCH = ROOT / 'proposals/arduino-esp32-3.3.0-hid-routing.patch'
PIN = ROOT / 'docs/mac-release-dependency-pin.json'
NVS_PATCH = ROOT / 'proposals/arduino-esp32-3.3.0-nvs-preservation.patch'
ROUTING = 'libraries/USB/src/USBHID.cpp'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def tree_hash(root):
    records = [(str(p.relative_to(root)), sha(p)) for p in sorted(Path(root).rglob('*')) if p.is_file() and p.relative_to(root) != Path('installed.json')]
    return hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()

def check_sources(core, patched=False):
    # Additive owner-approved archive profile. Historical guards are untouched.
    for file in ['tools/patched_core.py','tools/verify_patched_firmware.py','docs/stage18-dependency-pin.json']:
        require((ROOT/file).read_bytes() == subprocess.check_output(['git','show','f47e46dec2fa19ef7310ea6ffd36fed8a23aefb3:'+file],cwd=ROOT), 'Historical guard changed')
    require(not any(p.is_symlink() for p in Path(core).rglob('*')), 'Core source links prohibited')
    core = Path(core).resolve()
    partition_tool(core)  # exact platform version and partition tooling
    pin = json.loads(PIN.read_text())
    require(sha(NVS_PATCH) == pin['nvs_patch_sha256'], 'NVS patch provenance mismatch')
    require(sha(core/pin['nvs_source']) == pin['patched_nvs_source_sha256' if patched else 'original_nvs_source_sha256'], 'NVS source mismatch')
    require(sha(PATCH) == pin['patch_sha256'], 'Routing patch provenance mismatch')
    require(sha(ROOT/'proposals/evilduck-hid-feature-companion.patch') == pin['companion_patch_sha256'], 'Companion patch provenance mismatch')
    require(sha(ROOT/'EvilDuckS3/hid_backend.cpp') == pin['integrated_backend_sha256'], 'Paired production backend mismatch')
    require(tree_hash(core) == pin['patched_tree_sha256' if patched else 'original_tree_sha256'], 'Core tree mismatch')
    sdk = core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3'
    require(sha(sdk/'lib/libnvs_flash.a') == pin['sdk_nvs_archive_sha256'], 'NVS SDK archive mismatch')
    require(sha(sdk/'qio_qspi/include/sdkconfig.h') == pin['sdk_config_sha256'], 'SDK configuration mismatch')
    for record in json.loads((ROOT/'docs/stage15-upstream-sources.json').read_text())['sources']:
        path = record['path']
        if '/hardware/esp32/3.3.0/' in path:
            suffix = path.split('/hardware/esp32/3.3.0/', 1)[1]
            actual = core / suffix
            expected = pin['patched_routing_sha256'] if patched and suffix == ROUTING else record['sha256']
        else:
            actual = core.parents[2] / 'tools' / path.split('/tools/', 1)[1]
            expected = record['sha256']
        require(sha(actual) == expected, 'Pinned source mismatch: '+str(actual))
    receipt = json.loads((ROOT/'docs/stop-led-build.json').read_text())
    sdk_archives = {r['file'].split('/esp32s3/',1)[1]:r['sha256'] for r in receipt['linked_input_hashes'] if '/esp32-arduino-libs/' in r['file'] and r['file'].endswith('.a')}
    require(len(sdk_archives)==177, 'SDK inventory incomplete')
    for name, expected in sdk_archives.items():
        require(sha(sdk/name)==expected, 'SDK archive changed: '+name)
    return pin

def prepare(core, destination, user):
    core, destination, user = Path(core).resolve(), Path(destination).resolve(), Path(user).resolve()
    require(not destination.exists(), 'Isolation destination must not exist')
    require(destination != ROOT and ROOT not in destination.parents, 'Use an external disposable directory')
    require(core not in destination.parents and destination not in core.parents, 'Isolation must not overlap installed core')
    original_data = core.parents[4]
    require(original_data != destination and original_data not in destination.parents and destination not in original_data.parents, 'Isolation must not overlap installed Arduino data')
    require(user != destination and user not in destination.parents and destination not in user.parents, 'Isolation must not overlap installed Arduino user directory')
    pin = check_sources(core)
    data = destination / 'data'
    copied = data / 'packages/esp32/hardware/esp32/3.3.0'
    copied.parent.mkdir(parents=True)
    shutil.copytree(core, copied)  # independent bytes, never hardlinks
    original_data = core.parents[4]
    for package in (original_data / 'packages').iterdir():
        if (package / 'tools').is_dir():
            target = data / 'packages' / package.name / 'tools'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(package / 'tools', target_is_directory=True)
    for index in original_data.glob('*index.json*'):
        shutil.copyfile(index, data / index.name)
    # Only reviewed HID routing and early NVS policy are patched. Tool executables and libraries are read-only inputs;
    # their build products go to the external build/cache, never their source trees.
    for patch in (PATCH, NVS_PATCH):
        subprocess.run(['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', str(patch)], cwd=copied, check=True)
    check_sources(copied, True)
    check_sources(core)
    config = destination / 'arduino-cli.json'
    config.write_text(json.dumps({'directories': {'data': str(data), 'downloads': str(destination/'downloads'), 'user': str(user)}, 'build_cache': {'path': str(destination/'cache')}}, indent=2)+'\n')
    receipt = dict(core=str(copied), original_core=str(core), pin=pin, config=str(config), user=str(user), tools_shared_read_only=True)
    (destination / 'patched-core-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return receipt
