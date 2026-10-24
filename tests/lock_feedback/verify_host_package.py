"""Inspect the actual public host ZIP and run mocked full-launch tests on its source."""
import argparse
import ast
import hashlib
import json
import os
import pathlib
import re
import stat
import subprocess
import sys
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = 'e306108377a10ae3205a6db1d40cd0abe3d91b3a'


def verify(archive, results, guide='docs/lock-feedback-helper-v2.md'):
    assert not results.exists()
    expected = {'led_action.py', 'led_action.c', 'README.md', 'manifest.json'}
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist()) == expected and len(z.infolist()) == len(expected)
        assert z.testzip() is None
        for info in z.infolist():
            assert info.file_size < 200000 and stat.S_ISREG(info.external_attr >> 16)
        files = {name: z.read(name) for name in expected}
    manifest = json.loads(files['manifest.json'])
    commit = manifest['source_commit']
    assert re.fullmatch('[0-9a-f]{40}', commit)
    assert manifest['hardware_tested'] is False and manifest['native_Apple_compilation'] == 'UNVERIFIED'
    assert manifest['build_id'] == 'ROUTEB-LOCK-FEEDBACK-20261023-v1'
    assert set(manifest['files']) == expected - {'manifest.json'}
    for name, row in manifest['files'].items():
        assert len(files[name]) == row['bytes'] and hashlib.sha256(files[name]).hexdigest() == row['sha256']
    for name in ('led_action.py', 'led_action.c'):
        assert files[name] == subprocess.check_output(['git', 'show', commit+':tests/lock_feedback/'+name], cwd=ROOT)
    assert guide in ('docs/lock-feedback-helper-v2.md', 'docs/lock-feedback-helper-v3.md',
                     'docs/lock-feedback-helper-v4.md')
    assert files['README.md'] == subprocess.check_output(['git','show',commit+':'+guide],cwd=ROOT)
    assert files['led_action.c'] == subprocess.check_output(['git','show',BASE+':tests/lock_feedback/led_action.c'],cwd=ROOT)
    tree = ast.parse(files['led_action.py'].decode(), feature_version=(3,8))
    assert not any(isinstance(n, ast.Name) and n.id in ('base64','token') for n in ast.walk(tree))
    for block in files['README.md'].decode().split('```bash')[1:]:
        subprocess.run(['bash','-n'],input=block.split('```')[0],text=True,check=True)
    with tempfile.TemporaryDirectory(prefix='evilduck-host-zip-only-') as tmp:
        for name, data in files.items():
            (pathlib.Path(tmp)/name).write_bytes(data)
        env = dict(os.environ, EVILDUCK_TEST_HELPER_DIR=tmp, PYTHONDONTWRITEBYTECODE='1')
        pattern = ('test_*led*.py' if guide == 'docs/lock-feedback-helper-v4.md' else
                   'test_led_*.py' if guide == 'docs/lock-feedback-helper-v3.md' else 'test_led_action*.py')
        command = [sys.executable,'-m','unittest','discover','-s','tests/lock_feedback','-p',pattern,'-v']
        run = subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
    output = run.stdout + run.stderr
    print(output)
    assert run.returncode == 0
    count = int(re.search(r'Ran (\d+) tests',output).group(1))
    historical = 'test_old_published_main_reproduces_undefined_base64'
    assert historical in output
    report = dict(archive=archive.name,bytes=archive.stat().st_size,
                  sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),source_commit=commit,
                  current_helper_checks=dict(PASS=count-1,FAIL=0),
                  historical_v1_control='EXPECTED_UNDEFINED_BASE64_NAMEERROR_REPRODUCED; no network/native call',
                  total_unittest_checks=count,guide_source=guide,zip_crc_members_source_hashes='PASS',python38_syntax='PASS',
                  guide_shell_syntax='PASS',native_c_unchanged=True,firmware_built=False,
                  native_Apple_compilation='UNVERIFIED',physical_testing=False,
                  mocks='Darwin, password, HTTP, source time, manual ID entry and native subprocess; no hardware or real HTTP',
                  output=output)
    results.write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);p.add_argument('--guide',choices=['docs/lock-feedback-helper-v2.md','docs/lock-feedback-helper-v3.md','docs/lock-feedback-helper-v4.md'],default='docs/lock-feedback-helper-v2.md');a=p.parse_args()
    r=verify(a.archive,a.results,a.guide)
    print(json.dumps({k:v for k,v in r.items() if k!='output'},indent=2))
