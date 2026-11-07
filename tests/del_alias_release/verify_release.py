#!/usr/bin/env python3
"""Preserve the full six-layer 190-Assert chain for the exact DEL alias target.

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
BUILD_ID = 'ROUTEB-DEL-ALIAS-H1-v1'
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


def adapt_compiler_handler(tree, logical_layer, filename):
    """Filename reuse by nested historical adapters is not a layer identity.

    The frozen chain already derives logical_layer from its distinctive report
    assignments. Only that validated right-modifier unit owns these selectors.
    """
    if logical_layer != 'right-modifier H1':
        return tree, []
    handler = CompilerHandlerExpectations()
    tree = handler.visit(tree)
    assert len(handler.edits) == 2, 'Expected exactly two right-modifier compiler-handler selectors'
    for edit in handler.edits:
        edit.update(logical_layer=logical_layer, filename=filename)
    return tree, handler.edits


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adapted_parent():
    previous_path = ROOT / 'tests/previous_command_repeat_release/verify_release.py'
    assert sha(previous_path) == 'e8332ae4ad431db2955000b82d49451b0121fda4e6049663d0f2d95a5a07571e', 'Historical REPEAT release verifier changed'
    previous = load(previous_path, 'del_complete_previous_repeat_release')
    previous.BUILD_ID = BUILD_ID
    captured = []

    def capture(source, filename, mode, *args, **kwargs):
        if mode == 'exec' and isinstance(source, str) and 'report["previous_repeat_release_verification"]' in source:
            captured.append(source)
        return ORIGINAL_COMPILE(source, filename, mode, *args, **kwargs)

    with patch.object(previous, 'ORIGINAL_COMPILE', capture):
        _, inherited = previous.adapted_parent()
    assert len(captured) == 1, 'Historical complete release source capture ambiguous'
    text, changes = captured[0], []

    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, ('DEL release adaptation occurrence mismatch', old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('tests/previous_command_repeat_release/source-manifest.json', 'tests/del_alias_release/source-manifest.json')
    replace('tests/previous_command_repeat_release/identity.patch', 'tests/del_alias_release/identity.patch')
    replace('tests/previous_command_repeat_release/verify_target.py', 'tests/del_alias_release/verify_target.py')
    replace('previous_repeat_target_adapter', 'del_alias_target_adapter')
    replace('previous_repeat_target_binding', 'del_alias_target_binding', 2)
    replace('previous_repeat_release_verification', 'del_alias_release_verification')
    replace('report["previous_repeat_build_source_pin"] = pin', 'report["del_alias_build_source_pin"] = pin')
    replace('{"cli.cpp", "core.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}',
            '{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h"}', 2)
    replace('Same pinned comparison policy, with the exact five cumulative files.',
            'Same pinned comparison policy, with the exact six cumulative files.')
    replace('PREVIOUS COMMAND REPEAT / STATIC RESPONSE / EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / REVIEW / NOT OWNER-HARDWARE-VERIFIED',
            'DEL ALIAS / PREVIOUS COMMAND REPEAT / STATIC RESPONSE / EDITOR SAFETY / PRIVACY FIX 1 / H1 EXPERIMENTAL / REVIEW / NOT OWNER-HARDWARE-VERIFIED')
    namespace = dict(__name__='del_alias_frozen_six_layer_release', __file__=str(__file__),
                     REPEAT_HANDLER_ADAPT=adapt_compiler_handler)
    exec(ORIGINAL_COMPILE(text, str(ROOT / 'tests/dashboard_cleanup/verify_release.py'), 'exec'), namespace)
    return namespace, dict(previous_repeat=inherited, del_alias=changes)


def run_chain(build_root, output):
    namespace, changes = adapted_parent()
    report = namespace['run_chain'](build_root, output)
    info = report['del_alias_release_verification']
    binding = info['del_alias_target_binding']
    assert info['assertions_preserved'] == 190 and info['assertions_removed'] == 0
    assert len(binding['bundled_resources']) == 5
    assert binding['streaming_response']['status'] == 'PASS'
    assert binding['previous_command_repeat']['status'] == 'PASS'
    assert binding['previous_command_repeat']['standalone_branch_verified'] is True
    assert binding['previous_command_repeat']['modifier_handler_reachable'] is True
    assert binding['del_alias']['status'] == 'PASS'
    assert binding['del_alias']['usage'] == 0x4c and binding['del_alias']['table_begin_end_loaded'] is True
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
                           ('previous_repeat_build_source_pin', 'previous_command_repeat_release'),
                           ('del_alias_source_pin', 'del_alias'),
                           ('del_alias_build_source_pin', 'del_alias_release')]:
        report[key] = json.loads((ROOT / 'tests' / directory / 'source-manifest.json').read_text())
    pathlib.Path(output).write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', type=pathlib.Path, required=True)
    parser.add_argument('--output', type=pathlib.Path, required=True)
    args = parser.parse_args()
    run_chain(args.build_root, args.output)
    print('PASS full six-layer190Assert chain, committed DEL mapping plus REPEAT compiler/streaming target; review only')


if __name__ == '__main__':
    main()
