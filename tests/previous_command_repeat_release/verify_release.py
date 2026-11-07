#!/usr/bin/env python3
"""Preserve the full six-layer 190-Assert chain for the exact REPEAT target.

Only final source hash expectations, selected verifier paths, the new identity
and explicitly named report keys advance. No inherited Assert node is removed.
"""
import argparse
import ast
import builtins
import hashlib
import importlib.util
import json
import pathlib
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ROOT / 'tests/static_response_build_integration/verify_release.py'
PARENT_SHA = '5806329fc180222990386b17edfd8410845d48608477ad40dcc5625002db09f9'
BUILD_ID = 'ROUTEB-PREVIOUS-COMMAND-REPEAT-v1'
ORIGINAL_COMPILE = builtins.compile


class CompilerHandlerExpectations(ast.NodeTransformer):
    """Retarget only the two right-modifier handler-selector constants.

    The reviewed compiler split preserves statement() as its lexical wrapper;
    the unchanged modifier handler now resides in statementImpl(). Actual target
    verification independently requires that wrapper/line/step reaches Impl.
    """
    OLD = 'ds_preview::Compiler::statement('
    NEW = 'ds_preview::Compiler::statementImpl('

    def __init__(self):
        self.edits = []

    def visit_Constant(self, node):
        if isinstance(node.value, str) and node.value == self.OLD:
            self.edits.append(dict(line=getattr(node, 'lineno', None), before=self.OLD, after=self.NEW))
            return ast.copy_location(ast.Constant(self.NEW), node)
        return node


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adapted_parent():
    assert sha(PARENT) == PARENT_SHA, 'Historical full streaming release verifier changed'
    parent = load(PARENT, 'previous_repeat_full_static_release_parent')
    parent.BUILD_ID = BUILD_ID
    captured = []

    def capture(source, filename, mode, *args, **kwargs):
        if str(filename) == str(ROOT / 'tests/dashboard_cleanup/verify_release.py') and mode == 'exec' and isinstance(source, str):
            captured.append(source)
        return ORIGINAL_COMPILE(source, filename, mode, *args, **kwargs)

    # The old adapter first composes the editor source, then its streaming
    # extension. Capture the final extension after all inherited adaptations.
    with patch.object(parent, 'ORIGINAL_COMPILE', capture):
        _, inherited = parent.adapted_parent()
    assert len(captured) == 2, 'Historical release source capture ambiguous'
    text, changes = captured[-1], []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, ('Repeat release adaptation occurrence mismatch', old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('tests/static_response_build_integration/source-manifest.json', 'tests/previous_command_repeat_release/source-manifest.json')
    replace('tests/static_response_build_integration/identity.patch', 'tests/previous_command_repeat_release/identity.patch')
    replace('tests/static_response_build_integration/verify_target.py', 'tests/previous_command_repeat_release/verify_target.py')
    replace('static_response_target_adapter', 'previous_repeat_target_adapter')
    replace('static_response_target_binding', 'previous_repeat_target_binding', 2)
    replace('static_response_release_verification', 'previous_repeat_release_verification')
    replace('report["static_response_build_source_pin"] = pin', 'report["previous_repeat_build_source_pin"] = pin')
    replace('{"cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}',
            '{"cli.cpp", "core.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}', 2)
    replace('Same pinned comparison policy, with the exact four cumulative files.',
            'Same pinned comparison policy, with the exact five cumulative files.')
    replace('        tree = identity.visit(tree)\n        ast.fix_missing_locations(tree)',
            '''        tree = identity.visit(tree)
        handler_edits = []
        if name == REPEAT_HANDLER_PATH:
            handler = REPEAT_HANDLER_ADAPTER()
            tree = handler.visit(tree)
            assert len(handler.edits) == 2, "Expected exactly two right-modifier compiler-handler selectors"
            handler_edits = handler.edits
        ast.fix_missing_locations(tree)''')
    replace('runtime_identity_adaptations=identity.edits))',
            'runtime_identity_adaptations=identity.edits, compiler_handler_adaptations=handler_edits))')
    replace('STATIC RESPONSE REPAIR / EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / REVIEW / NOT OWNER-HARDWARE-VERIFIED',
            'PREVIOUS COMMAND REPEAT / STATIC RESPONSE / EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / REVIEW / NOT OWNER-HARDWARE-VERIFIED')
    namespace = dict(__name__='previous_repeat_frozen_six_layer_release', __file__=str(__file__),
                     REPEAT_HANDLER_PATH=str((ROOT / 'tests/h1_right_modifiers/verify_link.py').resolve()),
                     REPEAT_HANDLER_ADAPTER=CompilerHandlerExpectations)
    exec(ORIGINAL_COMPILE(text, str(ROOT / 'tests/dashboard_cleanup/verify_release.py'), 'exec'), namespace)
    return namespace, dict(static_response=inherited, previous_repeat=changes)


def run_chain(build_root, output):
    namespace, changes = adapted_parent()
    report = namespace['run_chain'](build_root, output)
    info = report['previous_repeat_release_verification']
    binding = info['previous_repeat_target_binding']
    assert info['assertions_preserved'] == 190 and info['assertions_removed'] == 0
    assert len(binding['bundled_resources']) == 5
    assert binding['streaming_response']['status'] == 'PASS'
    assert binding['previous_command_repeat']['status'] == 'PASS'
    assert binding['previous_command_repeat']['standalone_branch_verified'] is True
    assert binding['previous_command_repeat']['modifier_handler_reachable'] is True
    assert binding['committed_source_provenance']['source_commit'] == binding['committed_source_provenance']['verifier_context_commit']
    assert binding['committed_source_provenance']['post_compile_verifier_delta'] is None
    assert sum(len(event['compiler_handler_adaptations']) for event in info['compile_events']) == 2
    assert all(not event['compiler_handler_adaptations'] or event['logical_layer'] == 'right-modifier H1'
               for event in info['compile_events'])
    info.update(actual_parent_verifier_sha256=PARENT_SHA, integration_adaptations=changes,
                installed=False, owner_hardware_verified=False, status_label='REVIEW ONLY / NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED')
    for key, directory in [('dashboard_parent_source_pin', 'dashboard_cleanup'),
                           ('reviewed_editor_source_pin', 'editor_load_safety'),
                           ('editor_build_source_pin', 'editor_build_integration'),
                           ('static_response_source_pin', 'dashboard_response_safety'),
                           ('static_response_build_source_pin', 'static_response_build_integration'),
                           ('previous_repeat_source_pin', 'previous_command_repeat'),
                           ('previous_repeat_build_source_pin', 'previous_command_repeat_release')]:
        report[key] = json.loads((ROOT / 'tests' / directory / 'source-manifest.json').read_text())
    pathlib.Path(output).write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    run_chain(args.build_root, args.output)
    print('PASS full six-layer190Assert chain, committed REPEAT compiler and streaming target; review only')


if __name__ == '__main__':
    main()
