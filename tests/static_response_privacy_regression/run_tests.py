#!/usr/bin/env python3
"""Preserved privacy/keyboard cases with the actual static-response webserver.

Only a generated lower-API mock gains the real SDK's explicit byte/length send
overload. It captures body bytes and is not a streaming/ESP32-heap simulation.
Those transport properties are independently tested by dashboard_response_safety.
No target compiler, package, owner credentials, external server or board is used.
"""
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/static_response_privacy_regression'
PARENT = ROOT / 'tests/editor_build_integration/run_privacy_tests.py'
PARENT_SHA = '8ac89aa0029ad654e8cdb15a063c1aa96895e21819ab4a9e835eb3ef08fd2a30'
HISTORICAL_MOCK_COMMIT = 'e692435a7c70dbc0d917bbff733c57900cf7d57c'
PREPARER = ROOT / 'tests/dashboard_response_safety/prepare_sources.py'
PREPARER_SHA = 'efe6979e6d63238fdb3eb5fa6836e47bf43c350d9bc5f17db3bcd82b1eca44a1'
OLD_SERVER_SHA = '02b1bed01526935e7c8ec1857dfc910221dda3977efc47185eafbc796e4a22f9'
NEW_SERVER_SHA = '98bb1d99e2098c29b962285ec4760d1ab3ed0d6d656cceed55d138fba1e7455c'


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main():
    assert sha(PARENT) == PARENT_SHA, 'Frozen editor privacy runner changed'
    assert sha(PREPARER) == PREPARER_SHA, 'Reviewed static response preparer changed'
    spec = importlib.util.spec_from_file_location('privacy_static_source_pin', PREPARER)
    source_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source_module)
    source_pin = source_module.pin()
    static_patch = ROOT / 'tests/dashboard_response_safety/application.patch'
    assert sha(static_patch) == source_pin['patch_sha256']
    self_sha = sha(__file__)
    mock_patch = HERE / 'network.patch'
    mock_patch_sha = sha(mock_patch)
    prepared = []

    def native_prepare(source, command, target):
        assert not prepared, 'Static native binding must execute once'
        source = pathlib.Path(source)
        target = pathlib.Path(target)
        webserver = source / 'webserver.cpp'
        assert sha(webserver) == OLD_SERVER_SHA
        assert sha(target / 'webserver.cpp') == NEW_SERVER_SHA
        before = {str(p.relative_to(source)): sha(p) for p in source.rglob('*') if p.is_file()}
        patched = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch',
                                  '-p0', '-i', str(static_patch)], cwd=source,
                                 capture_output=True, text=True, check=True)
        assert 'offset' not in patched.stdout.lower() and 'fuzz' not in patched.stdout.lower()
        after = {str(p.relative_to(source)): sha(p) for p in source.rglob('*') if p.is_file()}
        assert set(before) == set(after)
        assert [n for n in before if before[n] != after[n]] == ['webserver.cpp']
        assert sha(webserver) == NEW_SERVER_SHA

        # The historical mock exposes only the former char* API. Copy the full
        # mock include directory so its relative includes resolve consistently.
        # Add the byte+length API to that generated copy, never historical files.
        mock_dir = source.parent / 'static-response-api-mocks'
        assert not mock_dir.exists()
        old_mock_dir = ROOT / 'tests/caps_queue/mocks'
        include_dirs = [pathlib.Path(v[2:]) for v in command if v.startswith('-I')]
        selected = next(p for p in include_dirs if (p / 'network.h').is_file())
        assert selected == old_mock_dir, 'Historical network mock selection changed'
        mock_inputs = {}
        for path in sorted(old_mock_dir.iterdir()):
            assert path.is_file() and not path.is_symlink()
            rel = str(path.relative_to(ROOT))
            recorded = subprocess.check_output(['git', 'show', HISTORICAL_MOCK_COMMIT + ':' + rel], cwd=ROOT)
            assert path.read_bytes() == recorded, rel
            mock_inputs[rel] = sha(path)
        shutil.copytree(old_mock_dir, mock_dir)
        mock_result = subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch',
                                     '-p0', '-i', str(mock_patch)], cwd=mock_dir,
                                    capture_output=True, text=True, check=True)
        assert 'offset' not in mock_result.stdout.lower() and 'fuzz' not in mock_result.stdout.lower()
        for path in mock_dir.iterdir():
            if path.name != 'network.h':
                assert path.read_bytes() == (old_mock_dir / path.name).read_bytes()
        command.insert(1, '-I' + str(mock_dir))
        prepared.append(dict(source=str(source), actual_webserver_sha256=NEW_SERVER_SHA,
                             source_files_changed=['webserver.cpp'], static_patch_sha256=sha(static_patch),
                             mock_delta_sha256=mock_patch_sha, mock_base_commit=HISTORICAL_MOCK_COMMIT,
                             mock_inputs=mock_inputs, mock_include_directory=str(mock_dir),
                             changed_mock_files=['network.h'], generated_mock_sha256=sha(mock_dir / 'network.h'),
                             scope='Lower API byte capture only; actual SDK streaming tested separately'))

    text, changes = PARENT.read_text(), []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace("'tests/editor_build_integration/source-manifest.json'",
            "'tests/static_response_build_integration/source-manifest.json'")
    replace('    def bind_target_sources(source):', '    def bind_target_sources(source, command):')
    replace("        source = pathlib.Path(source)\n        # Native generation",
            "        source = pathlib.Path(source)\n        STATIC_NATIVE_PREPARE(source, command, target)\n        # Native generation")
    replace('editor_bind_target_sources(source)', 'editor_bind_target_sources(source, command)')
    replace('EDITOR_BROWSER_OUTPUT=browser_output)',
            'EDITOR_BROWSER_OUTPUT=browser_output, STATIC_NATIVE_PREPARE=STATIC_NATIVE_PREPARE)')
    replace("'editor_build_privacy_adapter'", "'static_response_privacy_adapter'", count=2)
    namespace = dict(__name__='static_response_privacy_regression', __file__=str(PARENT),
                     STATIC_NATIVE_PREPARE=native_prepare)
    exec(compile(text, str(PARENT), 'exec'), namespace)
    status = namespace['main']()
    output = pathlib.Path(sys.argv[sys.argv.index('--results') + 1])
    result = json.loads(output.read_text())
    assert len(prepared) == 1
    assert result['privacy_fix1'] == dict(PASS=28, FAIL=0, assertions=736)
    assert result['all_existing_composed_regressions'] == dict(PASS=558, FAIL=0, assertions=23901)
    assert '-I' + prepared[0]['mock_include_directory'] in result['command']
    assert '-fsanitize=address,undefined' in result['command']
    assert all(not row['stderr'] for row in result['results']), 'Native sanitizer stderr is not empty'
    assert sha(PARENT) == PARENT_SHA and sha(PREPARER) == PREPARER_SHA
    assert sha(__file__) == self_sha and sha(mock_patch) == mock_patch_sha
    result['static_response_privacy_adapter'].update(
        outer_adapter_sha256=self_sha, parent_editor_adapter_sha256=PARENT_SHA,
        static_preparer_sha256=PREPARER_SHA, static_native_binding=prepared[0],
        exact_outer_adaptations=changes, native_cpp_cases_or_expectations_changed=False,
        sanitizer_flags_changed=False, header_webserver_settings_cli_binding='Exact selected source bytes',
        identity_boundary='Native historical fixture identity retained; new target identity is metadata-only and independently checked in ELF',
        test_mock_transport_claim=False, firmware_built=False, hardware=False)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['privacy_fix1', 'all_existing_composed_regressions',
                                           'privacy_ui', 'sanitizers', 'static_response_privacy_adapter']}, indent=2))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
