#!/usr/bin/env python3
"""Additive committed-source, compiled-core and streaming target verification.

All historical target predicates remain; only exact final source/identity
expectations advance. The core witness additionally binds the actual compile,
linked object, new compiler functions and executable standalone-branch lines.
"""
import argparse
import builtins
import hashlib
import importlib.util
import json
import pathlib
import re
import shlex
import subprocess
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ROOT / 'tests/static_response_build_integration/verify_target.py'
PARENT_SHA = '764a53bc8825aafb8bcf695afeef11f00ad4dd37b4ba30d6d031758932a122a1'
BUILD_ID = 'ROUTEB-PREVIOUS-COMMAND-REPEAT-v1'
OLD_BUILD_ID = 'ROUTEB-STATIC-RESPONSE-REPAIR-v1'
SELF_PATH = 'tests/previous_command_repeat_release/verify_target.py'
ORIGINAL_COMPILE = builtins.compile


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


require(sha(PARENT) == PARENT_SHA, 'Historical static target verifier changed')
S = load(PARENT, 'previous_repeat_frozen_static_target')
S.BUILD_ID = BUILD_ID  # Exact new identity data; all committed-input predicates execute unchanged.
S.SELF_PATH = SELF_PATH  # The active verifier is this new committed wrapper.


def adapted_parent():
    captured = []

    def capture(source, filename, mode, *args, **kwargs):
        if str(filename) == str(S.PARENT) and mode == 'exec' and isinstance(source, str):
            captured.append(source)
        return ORIGINAL_COMPILE(source, filename, mode, *args, **kwargs)

    with patch.object(builtins, 'compile', capture):
        _, inherited = S.adapted_parent()
    require(len(captured) == 1, 'Historical target source capture ambiguous')
    text, changes = captured[0], []

    def replace(old, new, count=1):
        nonlocal text
        require(text.count(old) == count, 'Repeat target adaptation occurrence mismatch: ' + old)
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('tests/static_response_build_integration/source-manifest.json', 'tests/previous_command_repeat_release/source-manifest.json', 2)
    replace('tests/static_response_build_integration/identity.patch', 'tests/previous_command_repeat_release/identity.patch')
    replace('tests/dashboard_response_safety/prepare_sources.py', 'tests/previous_command_repeat/prepare_sources.py')
    replace(", 'len(pin[\"after\"]) == 3 and len(pin[\"unchanged\"]) == 198')",
            ", 'len(pin[\"after\"]) == 4 and len(pin[\"unchanged\"]) == 197')")
    replace('Static response manifest is not the reviewed 3/198 source delta', 'Repeat release manifest is not the reviewed 4/197 source delta')
    replace('{"webfiles.h", "caps_trial.h", "webserver.cpp"}', '{"core.cpp", "webfiles.h", "caps_trial.h", "webserver.cpp"}', 2)
    replace('source_files=201, static_response_files=3, unchanged_files=198', 'source_files=201, previous_repeat_files=4, unchanged_files=197')
    replace('pin["format"] == "evilduck-static-response-build-integration-v1"', 'pin["format"] == "evilduck-previous-command-repeat-release-v1"')
    replace('len(pin["before"]) == 3', 'len(pin["before"]) == 4')
    replace('len(pin["cumulative_h1_after"]) == 4', 'len(pin["cumulative_h1_after"]) == 5')
    replace('{"cli.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}', '{"cli.cpp", "core.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}')
    replace('cumulative_h1_changed_files=4, cumulative_h1_unchanged_files=197', 'cumulative_h1_changed_files=5, cumulative_h1_unchanged_files=196')
    namespace = dict(__name__='previous_repeat_frozen_target_chain', __file__=str(__file__))
    exec(ORIGINAL_COMPILE(text, str(S.PARENT), 'exec'), namespace)
    return namespace, dict(static_response=inherited, previous_repeat=changes)


def verify_composed_source(source):
    M = load(HERE / 'prepare_sources.py', 'previous_repeat_verify_sources')
    rows = M.verify_final(source)
    source = pathlib.Path(source)
    pin = M.pin()
    prior = json.loads((ROOT / 'tests/previous_command_repeat/source-manifest.json').read_text())
    previous = {r['file']: r['sha256'] for r in prior['after'] + prior['unchanged']}
    final = {r['file']: r['sha256'] for r in pin['after'] + pin['unchanged']}
    require(len(final) == len(previous) == 201 and
            {n for n in final if final[n] != previous[n]} == {'caps_trial.h'},
            'Release extends beyond reviewed REPEAT plus metadata identity')
    caps = (source / 'caps_trial.h').read_bytes()
    require(caps.count(BUILD_ID.encode()) == 1 and OLD_BUILD_ID.encode() not in caps,
            'Repeat target identity missing/ambiguous')
    require(hashlib.sha256(caps.replace(BUILD_ID.encode(), OLD_BUILD_ID.encode(), 1)).hexdigest() == previous['caps_trial.h'],
            'Repeat identity changed beyond literal label')
    require(final['core.cpp'] == prior['after'][0]['sha256'] and
            final['core.cpp'] == '01fda98ee58d34cd523241cfdd1da37b6992e037b889ce964ce3e32c899b0c4b',
            'Reviewed standalone REPEAT compiler omitted or changed')
    require(final['webfiles.h'] == 'df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445',
            'Reviewed editor/dashboard resources omitted or changed')
    require(final['webserver.cpp'] == '98bb1d99e2098c29b962285ec4760d1ab3ed0d6d656cceed55d138fba1e7455c',
            'Streaming response implementation omitted or changed')
    return dict(status='PASS', source_files=len(rows), reviewed_repeat_preserved=True,
                reviewed_editor_preserved=True, source_manifest_sha256=sha(HERE / 'source-manifest.json'),
                core_sha256=final['core.cpp'], webfiles_sha256=final['webfiles.h'],
                webserver_sha256=final['webserver.cpp'], build_id=BUILD_ID)


def verify_input_manifest(build_root):
    # This is the actual historical committed-source guard, not a replica/mock.
    parent = S.verify_input_manifest(build_root)
    require(parent['post_compile_verifier_delta'] is None, 'New clean build cannot use historical post-link exception')
    value = json.loads((pathlib.Path(build_root) / 'build-inputs.json').read_text())
    names = {row['file'] for row in value['files']}
    required = {'tests/previous_command_repeat_release/' + name for name in
                ['build_candidate.py', 'prepare_sources.py', 'source-manifest.json', 'identity.patch',
                 'verify_target.py', 'verify_release.py', 'startup_decode.py', 'test_verify_controls.py']}
    required |= {'tests/previous_command_repeat/' + name for name in
                 ['application.patch', 'source-manifest.json', 'prepare_sources.py', 'test_main.cpp', 'run_tests.py']}
    require(required.issubset(names), 'Committed REPEAT release/compiler inputs missing')
    verifier_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', SELF_PATH], cwd=ROOT, text=True).strip()
    require(re.fullmatch('[0-9a-f]{40}', verifier_commit) is not None, 'Repeat verifier Git revision missing')
    require(subprocess.run(['git', 'merge-base', '--is-ancestor', verifier_commit, 'HEAD'], cwd=ROOT,
                           capture_output=True).returncode == 0, 'Repeat verifier revision is not an ancestor')
    require(subprocess.check_output(['git', 'show', verifier_commit + ':' + SELF_PATH], cwd=ROOT) == (ROOT / SELF_PATH).read_bytes(),
            'Repeat verifier differs from its committed revision')
    require(verifier_commit == parent['source_commit'], 'New clean build verifier must be in its compilation checkpoint')
    return dict(parent, verifier_context_commit=verifier_commit,
                inherited_guard_verifier_context_commit=parent['verifier_context_commit'],
                committed_guard_context_adaptations=dict(build_id=BUILD_ID, verifier_path=SELF_PATH),
                previous_repeat_required_inputs=sorted(required))


def compiler_reachability(texts):
    """Require actual call/tail-jump reachability, including retained line().

    Small wrappers can be inlined into their caller. Only the observed functions
    participate; a name in a label/comment is not an executable call edge.
    """
    start = 'ds_preview::Compiler::step(ds_preview::CompileWork&)'
    goal = 'ds_preview::Compiler::statementImpl(char*)'
    require(start in texts and goal in texts, 'Required cooperative/compiler implementation code absent')
    edges = {name: set() for name in texts}
    witnesses = []
    for caller, text in texts.items():
        for line in text.splitlines():
            match = re.match(r'^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F]+\s+(call\w*|j|jx)\s+.*?<([^>]+)>', line)
            if not match:
                continue
            callee = re.sub(r'\+0x[0-9a-fA-F]+$', '', match[3])
            if callee in texts:
                edges[caller].add(callee)
                witnesses.append(dict(caller=caller, callee=callee,
                                      address=int(match[1], 16), opcode=match[2]))
    queue = [[start]]
    seen = set()
    while queue:
        path = queue.pop(0)
        if path[-1] == goal:
            return dict(path=path, executable_edges=witnesses)
        if path[-1] in seen:
            continue
        seen.add(path[-1])
        queue.extend(path + [callee] for callee in sorted(edges[path[-1]]) if callee not in seen)
    raise ValueError('Linked cooperative compiler cannot reach the new REPEAT implementation')


def modifier_handler_edges(text):
    """Keep the right-modifier handler guard on its actual new code owner."""
    rows = []
    for line in text.splitlines():
        match = re.match(r'^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F]+\s+(call\w*|j)\s+.*?<ds_shortcut::modifier\(char const\*\)>', line)
        if match:
            rows.append(dict(address=int(match[1], 16), opcode=match[2],
                             callee='ds_shortcut::modifier(char const*)'))
    require(rows, 'Linked statementImpl lacks actual modifier-handler call edge')
    return rows


def core_binding(root):
    root = pathlib.Path(root)
    build, sketch = root / 'build', root / 'candidate/EvilDuckS3'
    report = json.loads((root / 'report.json').read_text())
    entries = json.loads((build / 'compile_commands.json').read_text())
    selected = [row for row in entries if pathlib.Path(row['file']).name == 'core.cpp']
    require(len(selected) == 1, 'Actual REPEAT core compilation missing/ambiguous')
    entry = selected[0]
    compiled, args = pathlib.Path(entry['file']), entry['arguments']
    E = S.load(ROOT / 'tests/privacy_fix1/verify_target.py', 'repeat_core_source_match_parent')
    require(compiled == build / 'sketch/core.cpp' and E.source_matches((sketch / 'core.cpp').read_bytes(), compiled.read_bytes(), sketch / 'core.cpp'),
            'Compiled REPEAT core differs from reviewed final source')
    baseline = json.loads((ROOT / 'docs/h1-right-modifiers-build.json').read_text())
    require(sha(args[0]) == baseline['compiler_sha256'], 'REPEAT object compiler identity differs')
    obj = pathlib.Path(args[args.index('-o') + 1])
    require(obj == build / 'sketch/core.cpp.o', 'REPEAT object selected another tree')
    linked = {r['file']: r for r in report['linked_input_hashes']}
    loads = {line.removeprefix('LOAD ').strip() for line in (build / 'EvilDuckS3.ino.map').read_text().splitlines() if line.startswith('LOAD ')}
    require(str(obj) in linked and str(obj) in loads and linked[str(obj)]['sha256'] == sha(obj) and
            linked[str(obj)]['size'] == obj.stat().st_size, 'Actual REPEAT object not bound to ELF link')
    observed = []
    for line in (build / 's3-build.log').read_text().splitlines():
        if ' -c ' not in line:
            continue
        try:
            command = shlex.split(line)
        except ValueError:
            continue
        if '-o' in command and str(compiled) in command and command[command.index('-o') + 1] == str(obj):
            observed.append(command)
    require(len(observed) == 1 and sha(observed[0][0]) == baseline['compiler_sha256'],
            'Actual verbose REPEAT compile absent/ambiguous')
    dep = obj.with_suffix('.d')
    target, dependencies = E.make_dependencies(dep.read_text())
    require(pathlib.Path(target) == obj and str(compiled) in dependencies and str(build / 'sketch/core.h') in dependencies,
            'Actual REPEAT source/header dependency missing')
    require(E.source_matches((sketch / 'core.h').read_bytes(), (build / 'sketch/core.h').read_bytes(), sketch / 'core.h'),
            'Actual REPEAT header differs')
    compiler = pathlib.Path(args[0]); stem = compiler.name.rsplit('-', 1)[0]
    nm, objdump = compiler.with_name(stem + '-nm'), compiler.with_name(stem + '-objdump')
    elf = build / 'EvilDuckS3.ino.elf'
    object_symbols = S.symbols(subprocess.check_output([str(nm), '-C', '-S', '--defined-only', str(obj)], text=True))
    elf_symbols = S.symbols(subprocess.check_output([str(nm), '-C', '-S', '--defined-only', str(elf)], text=True))
    names = ['ds_preview::Compiler::statementImpl(char*)', 'ds_preview::Compiler::step(ds_preview::CompileWork&)',
             'ds_preview::Compiler::line()', 'ds_preview::Compiler::statement(char*)']
    witnesses, texts = [], {}
    def exact_symbol(rows, name, required=True):
        # Function-local static tables share the function's prefix. They are
        # data, not additional callable definitions, and must not be selected.
        selected = [row for row in rows if row['name'] == name]
        if not selected and not required:
            return None
        require(len(selected) == 1, 'New REPEAT compiler symbol absent/ambiguous: ' + name)
        return selected[0]
    for index, name in enumerate(names):
        object_symbol = exact_symbol(object_symbols, name, required=index < 2)
        symbol = exact_symbol(elf_symbols, name, required=index < 2)
        # An optional wrapper can have an unused object section discarded by
        # link-time GC after all callers inline it. Only linked code is a path.
        if symbol is None:
            continue
        require(object_symbol is not None, 'Linked compiler wrapper lacks core-object definition: ' + name)
        require(object_symbol['size'] > 0 and symbol['size'] > 0, 'New REPEAT compiler code is empty')
        text = subprocess.check_output([str(objdump), '-C', '-d', '--start-address=' + str(symbol['address']),
                                       '--stop-address=' + str(symbol['address'] + symbol['size']), str(elf)], text=True)
        require(re.search(r'^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\w', text, re.M) is not None,
                'New REPEAT symbol lacks executable instructions')
        witnesses.append(dict(**symbol, object_size=object_symbol['size'], disassembly_sha256=hashlib.sha256(text.encode()).hexdigest()))
        texts[name] = text
    reachable = compiler_reachability(texts)
    modifier_edges = modifier_handler_edges(texts[names[0]])
    # Actual linked debug-line addresses identify the new standalone branch, not
    # mere source strings or a detached object. Code remains source-hash pinned.
    source_lines = (sketch / 'core.cpp').read_text().splitlines()
    markers = ['   if(!*count){', '    repeated_=p_.code_[previousRepeatLeaf_];repeated_.line=line_;',
               '    repeatRemaining_=n;return true; // n additional copies; share frozen operands.']
    lines = []
    for marker in markers:
        matches = [i + 1 for i, line in enumerate(source_lines) if line == marker]
        require(len(matches) == 1, 'Pinned standalone branch source marker missing/ambiguous')
        lines.append(matches[0])
    decoded = subprocess.check_output([str(objdump), '--dwarf=decodedline', str(elf)], text=True)
    implementation = witnesses[0]
    observations = []
    for line in decoded.splitlines():
        match = re.match(r'^core\.cpp\s+(\d+)\s+(0x[0-9a-fA-F]+)', line)
        if match and int(match[1]) in lines:
            address = int(match[2], 16)
            if implementation['address'] <= address < implementation['address'] + implementation['size']:
                observations.append(dict(line=int(match[1]), address=address))
    seen = {r['line'] for r in observations}
    require(lines[0] in seen and (lines[1] in seen or lines[2] in seen),
            'Linked new REPEAT standalone branch lacks executable line witnesses')
    return dict(status='PASS', source='core.cpp', source_sha256=sha(sketch / 'core.cpp'),
                compiled_source=str(compiled), compiled_source_sha256=sha(compiled),
                object_file=str(obj), object_sha256=sha(obj), compiled_from_final_source=True,
                object_linked=True, verbose_compile_observed=True, dependency_sha256=sha(dep),
                linked_symbols=witnesses, standalone_branch_verified=True,
                compiler_call_graph=reachable,
                modifier_handler_reachable=True, modifier_handler_call_edges=modifier_edges,
                standalone_source_lines=lines, executable_line_witnesses=observations,
                actual_elf_sha256=sha(elf), nm_sha256=sha(nm), objdump_sha256=sha(objdump), hardware=False)


def verify(build_root):
    root = pathlib.Path(build_root).resolve()
    source = verify_composed_source(root / 'candidate/EvilDuckS3')
    committed = verify_input_manifest(root)
    namespace, changes = adapted_parent()
    binding = namespace['verify'](root)
    E = S.load(S.EDITOR, 'repeat_complete_resource_verifier')
    resources = E.literal_resources(root / 'candidate/EvilDuckS3/webfiles.h')
    complete = E.verify_resource_bytes(resources, (root / 'build/EvilDuckS3.ino.elf').read_bytes(),
                                       (root / 'build/EvilDuckS3.ino.bin').read_bytes())
    streaming = S.streaming_binding(root, binding)
    repeat = core_binding(root)
    binding.update(status='PASS', build_id=BUILD_ID, source_commit=committed['source_commit'],
                   build_inputs_sha256=committed['build_inputs_sha256'], committed_source_provenance=committed,
                   verifier_context_commit=committed['verifier_context_commit'], post_compile_verifier_delta=None,
                   static_response_source_composition=source, previous_repeat_source_composition=source,
                   bundled_resources=complete, streaming_response=streaming, previous_command_repeat=repeat,
                   actual_parent_verifier_sha256=PARENT_SHA, integration_verifier_adaptations=changes,
                   physical=False, installed=False, package_created=False)
    return binding


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', required=True, type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    require(not args.output.exists(), 'Use fresh target evidence')
    args.output.write_text(json.dumps(verify(args.build_root), indent=2) + '\n')
    print('PASS committed REPEAT source/object/ELF branch, streaming resources and inherited target guards')


if __name__ == '__main__':
    main()
