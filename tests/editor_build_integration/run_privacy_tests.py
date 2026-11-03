#!/usr/bin/env python3
"""Pinned native privacy regressions bound to the final editor target sources.

The historical native cases, expectations, platform mocks, compile flags and
sanitizer execution remain unchanged. Only the final native UI header and the
obsolete Node UI harness selection are adapted. All browser traffic is inert.
No firmware compiler, package, device, owner data or external server is used.
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
PARENT = ROOT / 'tests/privacy_fix1/run_tests.py'
PARENT_SHA = 'fd67a67dfc99dfcb0d07a38d84542ce500bcfeb5aaa612681f6ab2d5d631584a'
PREPARER = ROOT / 'tests/privacy_fix1/prepare_sources.py'
PREPARER_SHA = '0bb594377dd1964926dcefbfb2e746251cdd908434bc6eba4eeb6624a2ba1dca'
BROWSER = ROOT / 'tests/dashboard_cleanup/test_browser.py'
BROWSER_SHA = '3713fa15a9d5ca9fa1bfe1fbfe4fde337af1b662c67c79921efe74aa05ce6166'


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['core', 'build-dir', 'results', 'target-composed']:
        parser.add_argument('--' + name, type=pathlib.Path, required=True)
    args = parser.parse_args()
    assert not args.build_dir.exists() and not args.results.exists(), 'Use fresh native output and receipt'
    browser_output = args.build_dir.with_name(args.build_dir.name + '-browser')
    assert not browser_output.exists(), 'Preserve previous browser evidence'
    target = args.target_composed.resolve()
    assert sha(PARENT) == PARENT_SHA and sha(PREPARER) == PREPARER_SHA and sha(BROWSER) == BROWSER_SHA
    target_pin_path = ROOT / 'tests/editor_build_integration/source-manifest.json'
    target_pin = json.loads(target_pin_path.read_text())
    expected = {row['file']: row['sha256'] for row in target_pin['after'] + target_pin['unchanged']}
    actual = {str(p.relative_to(target)): sha(p) for p in target.rglob('*') if p.is_file()}
    assert len(expected) == len(actual) == 201 and actual == expected, 'Final target composition does not match its manifest'
    reviewed = json.loads((ROOT / 'tests/editor_load_safety/source-manifest.json').read_text())
    assert expected['webfiles.h'] == reviewed['after'][0]['sha256'], 'Final UI differs from the reviewed editor repair'
    privacy = load(PREPARER, 'editor_native_privacy_preparer')
    bindings = []

    def bind_target_sources(source):
        assert not bindings, 'Native final-source binding must occur once'
        source = pathlib.Path(source)
        # Native generation deliberately substitutes framework/platform files.
        # These application implementations must be exact actual target bytes.
        for name in ['cli.cpp', 'webserver.cpp', 'settings.cpp']:
            physical = source / name
            if not physical.is_file():
                physical = ROOT / 'EvilDuckS3' / name
            assert sha(physical) == expected[name], name
            bindings.append(dict(file=name, native_file=str(physical), target_file=str(target / name),
                                 sha256=expected[name], source_bytes_identical=True))
        # Privacy's reviewed delta has just run; only replace the native harness
        # header with the final target's already-reviewed embedded resources.
        shutil.copyfile(target / 'webfiles.h', source / 'webfiles.h')
        assert sha(source / 'webfiles.h') == expected['webfiles.h']
        bindings.append(dict(file='webfiles.h', native_file=str(source / 'webfiles.h'),
                             target_file=str(target / 'webfiles.h'), sha256=expected['webfiles.h'],
                             source_bytes_identical=True, native_only_copy=True))

    text = PARENT.read_text()
    edits = []

    def replace(old, new):
        nonlocal text
        assert text.count(old) == 1, (old, text.count(old))
        text = text.replace(old, new)
        edits.append(dict(before=old, after=new, occurrences=1))

    replace('from prepare_sources import ROOT, delta',
            'ROOT = EDITOR_ROOT\ndelta = EDITOR_PRIVACY_DELTA')
    replace('        delta(source, native=True)',
            '        delta(source, native=True)\n        editor_bind_target_sources(source)')
    replace('    ui_command = ["node", str(ROOT / "tests/privacy_fix1/test_ui.cjs"), str(captured["source"] / "webfiles.h")]',
            '    ui_command = [sys.executable, "-B", str(ROOT / "tests/dashboard_cleanup/test_browser.py"), '
            '"--source", str(captured["source"] / "webfiles.h"), "--output-dir", str(EDITOR_BROWSER_OUTPUT)]')
    namespace = dict(__name__='editor_native_privacy_adapter', __file__=str(PARENT),
                     EDITOR_ROOT=ROOT, EDITOR_PRIVACY_DELTA=privacy.delta,
                     editor_bind_target_sources=bind_target_sources,
                     EDITOR_BROWSER_OUTPUT=browser_output)
    original_args = sys.argv
    try:
        sys.argv = [str(PARENT), '--core', str(args.core), '--build-dir', str(args.build_dir), '--results', str(args.results)]
        exec(compile(text, str(PARENT), 'exec'), namespace)
        status = namespace['main']()
    finally:
        sys.argv = original_args
    result = json.loads(args.results.read_text())
    ui_raw = result['privacy_ui'].get('counts')
    # The new real-browser runner reports a full receipt rather than the old
    # Node harness's twelve-group counts. Do not count old UI groups as fresh.
    result['privacy_ui']['historical_node_ui_executed'] = False
    result['privacy_ui']['browser_output_directory'] = str(browser_output)
    if result['privacy_ui']['exit'] == 0:
        assert ui_raw['counts'] == dict(PASS=9, FAIL=0) and ui_raw['assertions'] == 207
        assert ui_raw['source_sha256'] == expected['webfiles.h']
        result['privacy_ui']['counts'] = ui_raw['counts']
        result['privacy_ui']['assertions'] = ui_raw['assertions']
        result['privacy_ui']['browser_receipt'] = ui_raw
    assert len(bindings) == 4
    assert sha(PARENT) == PARENT_SHA and sha(PREPARER) == PREPARER_SHA and sha(BROWSER) == BROWSER_SHA
    assert {str(p.relative_to(target)): sha(p) for p in target.rglob('*') if p.is_file()} == expected
    # The fixture adapter changes no executable C++ test cases or sanitizer flags.
    assert result['privacy_fix1']['PASS'] + result['privacy_fix1']['FAIL'] == 28
    assert result['all_existing_composed_regressions']['PASS'] + result['all_existing_composed_regressions']['FAIL'] == 558
    assert '-fsanitize=address,undefined' in result['command'], 'Sanitizer compile flags were lost'
    result['editor_build_privacy_adapter'] = dict(
        status='PASS' if status == 0 else 'FAIL', adapter_sha256=sha(__file__), parent_runner_sha256=PARENT_SHA,
        privacy_preparer_sha256=PREPARER_SHA, browser_fixture_sha256=BROWSER_SHA,
        exact_adaptations=edits, final_target_manifest_sha256=sha(target_pin_path), target_source_binding=bindings,
        target_source_entries_verified=201, test_cases_or_expectations_changed=False,
        sanitizer_flags_changed=False, native_platform_substitutions='Inherited SHA-pinned historical RAM mocks',
        native_identity_policy='Historical generated test identity expectations retained; actual candidate ID is verified separately by target/ELF checks',
        historical_node_groups_counted_as_fresh=False, firmware_built=False, hardware=False,
        owner_data_read=False, packaging=False)
    args.results.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ['privacy_fix1', 'all_existing_composed_regressions',
                     'privacy_ui', 'sanitizers', 'editor_build_privacy_adapter']}, indent=2))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
