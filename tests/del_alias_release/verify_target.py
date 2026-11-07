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
import struct
import subprocess
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ROOT / 'tests/static_response_build_integration/verify_target.py'
PARENT_SHA = '764a53bc8825aafb8bcf695afeef11f00ad4dd37b4ba30d6d031758932a122a1'
BUILD_ID = 'ROUTEB-DEL-ALIAS-H1-v1'
OLD_BUILD_ID = 'ROUTEB-PREVIOUS-COMMAND-REPEAT-v1'
SELF_PATH = 'tests/del_alias_release/verify_target.py'
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
    previous_path = ROOT / 'tests/previous_command_repeat_release/verify_target.py'
    require(sha(previous_path) == '31503e5f9c9b0b049d8df9fa2acb18ae4430c5407dd0cfb205791931b807ae90',
            'Historical REPEAT target verifier changed')
    previous = load(previous_path, 'del_complete_previous_repeat_target')
    previous.BUILD_ID = previous.S.BUILD_ID = BUILD_ID
    previous.S.SELF_PATH = SELF_PATH
    captured = []

    def capture(source, filename, mode, *args, **kwargs):
        if mode == 'exec' and isinstance(source, str) and 'source_files=201, previous_repeat_files=4' in source:
            captured.append(source)
        return ORIGINAL_COMPILE(source, filename, mode, *args, **kwargs)

    with patch.object(previous, 'ORIGINAL_COMPILE', capture):
        _, inherited = previous.adapted_parent()
    require(len(captured) == 1, 'Historical complete target capture ambiguous')
    text, changes = captured[0], []

    def replace(old, new, count=1):
        nonlocal text
        require(text.count(old) == count, 'DEL target adaptation occurrence mismatch: ' + old)
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('tests/previous_command_repeat_release/source-manifest.json', 'tests/del_alias_release/source-manifest.json', 2)
    replace('tests/previous_command_repeat_release/identity.patch', 'tests/del_alias_release/identity.patch')
    replace('tests/previous_command_repeat/prepare_sources.py', 'tests/del_alias/prepare_sources.py')
    replace('len(pin["after"]) == 4 and len(pin["unchanged"]) == 197', 'len(pin["after"]) == 5 and len(pin["unchanged"]) == 196')
    replace('Repeat release manifest is not the reviewed 4/197 source delta', 'DEL release manifest is not the reviewed 5/196 source delta')
    replace('{"core.cpp", "webfiles.h", "caps_trial.h", "webserver.cpp"}', '{"core.cpp", "shortcut_keys.h", "webfiles.h", "caps_trial.h", "webserver.cpp"}', 2)
    replace('source_files=201, previous_repeat_files=4, unchanged_files=197', 'source_files=201, del_alias_files=5, unchanged_files=196')
    replace('pin["format"] == "evilduck-previous-command-repeat-release-v1"', 'pin["format"] == "evilduck-del-alias-release-v1"')
    replace('len(pin["before"]) == 4', 'len(pin["before"]) == 5')
    replace('len(pin["cumulative_h1_after"]) == 5', 'len(pin["cumulative_h1_after"]) == 6')
    replace('{"cli.cpp", "core.cpp", "webserver.cpp", "webfiles.h", "caps_trial.h"}', '{"cli.cpp", "core.cpp", "shortcut_keys.h", "webserver.cpp", "webfiles.h", "caps_trial.h"}')
    replace('cumulative_h1_changed_files=5, cumulative_h1_unchanged_files=196', 'cumulative_h1_changed_files=6, cumulative_h1_unchanged_files=195')
    namespace = dict(__name__='del_alias_frozen_target_chain', __file__=str(__file__))
    exec(ORIGINAL_COMPILE(text, str(S.PARENT), 'exec'), namespace)
    return namespace, dict(previous_repeat=inherited, del_alias=changes)


def verify_composed_source(source):
    M = load(HERE / 'prepare_sources.py', 'del_alias_verify_sources')
    rows = M.verify_final(source)
    source = pathlib.Path(source)
    pin = M.pin()
    prior = json.loads((ROOT / 'tests/previous_command_repeat_release/source-manifest.json').read_text())
    previous = {r['file']: r['sha256'] for r in prior['after'] + prior['unchanged']}
    final = {r['file']: r['sha256'] for r in pin['after'] + pin['unchanged']}
    require(len(final) == len(previous) == 201 and
            {n for n in final if final[n] != previous[n]} == {'caps_trial.h', 'core.cpp', 'shortcut_keys.h'},
            'DEL release extends beyond reviewed vocabulary, identifier preservation and metadata')
    caps = (source / 'caps_trial.h').read_bytes()
    require(caps.count(BUILD_ID.encode()) == 1 and OLD_BUILD_ID.encode() not in caps,
            'DEL target identity missing/ambiguous')
    require(hashlib.sha256(caps.replace(BUILD_ID.encode(), OLD_BUILD_ID.encode(), 1)).hexdigest() == previous['caps_trial.h'],
            'DEL identity changed beyond literal label')
    core = (source / 'core.cpp').read_bytes()
    new_reservation = (b' // DEL() predates the key alias; retain its unambiguous function spelling.\n'
        b' if(textKind(p)||(key(p)&&!exact(p,"DEL"))||ds_shortcut::modifier(p))return true;')
    old_reservation = b' if(textKind(p)||key(p)||ds_shortcut::modifier(p))return true;'
    require(core.count(new_reservation) == 1 and
            hashlib.sha256(core.replace(new_reservation, old_reservation, 1)).hexdigest() == previous['core.cpp'],
            'DEL compiler differs beyond preserved DEL() identifier rule')
    keys = (source / 'shortcut_keys.h').read_bytes()
    require(keys.count(b'{"DEL",0x4c},') == 1 and
            hashlib.sha256(keys.replace(b'{"DEL",0x4c},', b'', 1)).hexdigest() == previous['shortcut_keys.h'],
            'DEL shortcut vocabulary differs beyond exact DELETE alias')
    require(final['webfiles.h'] == previous['webfiles.h'] == 'df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445',
            'Reviewed editor/dashboard resources omitted or changed')
    require(final['webserver.cpp'] == previous['webserver.cpp'] == '98bb1d99e2098c29b962285ec4760d1ab3ed0d6d656cceed55d138fba1e7455c',
            'Streaming response implementation omitted or changed')
    return dict(status='PASS', source_files=len(rows), reviewed_repeat_preserved=True,
                reviewed_editor_preserved=True, source_manifest_sha256=sha(HERE / 'source-manifest.json'),
                core_sha256=final['core.cpp'], shortcut_sha256=final['shortcut_keys.h'],
                webfiles_sha256=final['webfiles.h'], webserver_sha256=final['webserver.cpp'],
                previous_repeat_reverse_delta_verified=True, del_function_name_preserved=True, build_id=BUILD_ID)


def verify_input_manifest(build_root):
    # This is the actual historical committed-source guard, not a replica/mock.
    parent = S.verify_input_manifest(build_root)
    require(parent['post_compile_verifier_delta'] is None, 'New clean build cannot use historical post-link exception')
    value = json.loads((pathlib.Path(build_root) / 'build-inputs.json').read_text())
    names = {row['file'] for row in value['files']}
    required = {'tests/del_alias_release/' + name for name in
                ['build_candidate.py', 'prepare_sources.py', 'source-manifest.json', 'identity.patch',
                 'verify_target.py', 'verify_release.py', 'startup_decode.py', 'test_verify_controls.py']}
    required |= {'tests/del_alias/' + name for name in
                 ['application.patch', 'source-manifest.json', 'prepare_sources.py', 'test_main.cpp', 'run_tests.py']}
    require(required.issubset(names), 'Committed REPEAT release/compiler inputs missing')
    verifier_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', SELF_PATH], cwd=ROOT, text=True).strip()
    require(re.fullmatch('[0-9a-f]{40}', verifier_commit) is not None, 'Repeat verifier Git revision missing')
    require(subprocess.run(['git', 'merge-base', '--is-ancestor', verifier_commit, 'HEAD'], cwd=ROOT,
                           capture_output=True).returncode == 0, 'Repeat verifier revision is not an ancestor')
    require(subprocess.check_output(['git', 'show', verifier_commit + ':' + SELF_PATH], cwd=ROOT) == (ROOT / SELF_PATH).read_bytes(),
            'Repeat verifier differs from its committed revision')
    source_commit = parent['source_commit']
    # Last-touch and compilation context are different facts: a later checkpoint
    # can contain this exact unchanged verifier blob. The inherited guard has
    # already checked every committed input/current byte and refused post-link
    # differences; explicitly bind this active verifier to the build checkpoint.
    require(subprocess.check_output(['git', 'show', source_commit + ':' + SELF_PATH], cwd=ROOT) == (ROOT / SELF_PATH).read_bytes(),
            'Active REPEAT verifier is not the compilation-checkpoint Git blob')
    require(subprocess.run(['git', 'merge-base', '--is-ancestor', verifier_commit, source_commit],
                           cwd=ROOT, capture_output=True).returncode == 0,
            'Verifier last-touch revision is newer than the compilation checkpoint')
    return dict(parent, verifier_context_commit=source_commit,
                verifier_last_touch_commit=verifier_commit, verifier_blob_commit=source_commit,
                verifier_blob_sha256=sha(ROOT / SELF_PATH),
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


def elf_bytes(data, address, size):
    """Read a unique file-backed ELF32 little-endian PT_LOAD address range."""
    require(data[:6] == b'\x7fELF\x01\x01', 'Expected ELF32 little-endian target image')
    require(len(data) >= 52 and size >= 0, 'ELF header/range invalid')
    offset = struct.unpack_from('<I', data, 28)[0]
    width, count = struct.unpack_from('<HH', data, 42)
    require(width == 32 and count > 0 and offset + width * count <= len(data),
            'ELF program-header table invalid')
    matches = []
    for index in range(count):
        kind, at, virtual, _, stored, _, _, _ = struct.unpack_from('<IIIIIIII', data, offset + index * width)
        if kind == 1 and address >= virtual and address + size <= virtual + stored:
            start = at + address - virtual
            require(start + size <= len(data), 'ELF load segment exceeds file')
            matches.append(data[start:start + size])
    require(len(matches) == 1, 'ELF address is not one unique file-backed load range')
    return matches[0]


def decode_named_table(data, address, size):
    require(size > 0 and size % 8 == 0 and size <= 4096, 'Named-key table size invalid')
    packed = elf_bytes(data, address, size)
    rows = []
    for index in range(size // 8):
        pointer = struct.unpack_from('<I', packed, index * 8)[0]
        name = bytearray()
        for at in range(32):
            c = elf_bytes(data, pointer + at, 1)[0]
            if not c:
                break
            require(32 <= c <= 126, 'Named-key string is not bounded ASCII')
            name.append(c)
        else:
            raise ValueError('Named-key string is unterminated')
        require(name, 'Named-key string is empty')
        rows.append(dict(name=name.decode('ascii'), usage=packed[index * 8 + 4], pointer=pointer))
    names = [row['name'] for row in rows]
    require(len(names) == len(set(names)), 'Named-key table has duplicate aliases')
    mapping = {row['name']: row['usage'] for row in rows}
    require(mapping.get('DEL') == mapping.get('DELETE') == 0x4c,
            'Actual linked DEL/DELETE mapping is absent or not usage 0x4c')
    return rows


def alias_binding(root, core):
    root = pathlib.Path(root)
    build, source = root / 'build', root / 'candidate/EvilDuckS3'
    entries = json.loads((build / 'compile_commands.json').read_text())
    selected = [row for row in entries if pathlib.Path(row['file']).name == 'core.cpp']
    require(len(selected) == 1, 'DEL compiler command missing/ambiguous')
    args = selected[0]['arguments']
    compiler = pathlib.Path(args[0]); stem = compiler.name.rsplit('-', 1)[0]
    nm, objdump = compiler.with_name(stem + '-nm'), compiler.with_name(stem + '-objdump')
    elf = build / 'EvilDuckS3.ino.elf'
    data = elf.read_bytes()
    symbols = S.symbols(subprocess.check_output([str(nm), '-C', '-S', '--defined-only', str(elf)], text=True))

    def exact(name):
        rows = [row for row in symbols if row['name'] == name]
        require(len(rows) == 1 and rows[0]['size'] > 0, 'DEL symbol missing/ambiguous: ' + name)
        return rows[0]

    function = exact('ds_shortcut::named(char const*)')
    table = exact('ds_shortcut::named(char const*)::names')
    rows = decode_named_table(data, table['address'], table['size'])
    text = subprocess.check_output([str(objdump), '-C', '-d', '--start-address=' + str(function['address']),
                                   '--stop-address=' + str(function['address'] + function['size']), str(elf)], text=True)
    literal_reads = []
    for line in text.splitlines():
        match = re.match(r'^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F]+\s+l32r\s+\w+,\s*([0-9a-fA-F]+)', line)
        if match:
            value = struct.unpack('<I', elf_bytes(data, int(match[2], 16), 4))[0]
            literal_reads.append(dict(instruction=int(match[1], 16), literal_address=int(match[2], 16), value=value))
    values = {row['value'] for row in literal_reads}
    require(table['address'] in values and table['address'] + table['size'] in values,
            'Linked named() does not load actual table begin/end')
    require(re.search(r'\bl8ui(?:\.n)?\s+\w+,\s*\w+,\s*4\b', text) is not None and
            re.search(r'\baddi(?:\.n)?\s+(\w+),\s*\1,\s*8\b', text) is not None,
            'Linked named() does not read usage offset/advance 8-byte rows')
    implementation = next(row for row in core['linked_symbols'] if row['name'] == 'ds_preview::Compiler::statementImpl(char*)')
    handler = subprocess.check_output([str(objdump), '-C', '-d', '--start-address=' + str(implementation['address']),
                                      '--stop-address=' + str(implementation['address'] + implementation['size']), str(elf)], text=True)
    require(re.search(r'\b(?:call\w*|j)\s+[^\n]*<ds_shortcut::named\(char const\*\)>', handler) is not None,
            'Actual compiler handler does not call named-key decoder')
    obj = pathlib.Path(args[args.index('-o') + 1])
    E = S.load(ROOT / 'tests/privacy_fix1/verify_target.py', 'del_header_source_match_parent')
    _, dependencies = E.make_dependencies(obj.with_suffix('.d').read_text())
    compiled_header = build / 'sketch/shortcut_keys.h'
    require(str(compiled_header) in dependencies and
            E.source_matches((source / 'shortcut_keys.h').read_bytes(), compiled_header.read_bytes(), source / 'shortcut_keys.h'),
            'Actual compiled DEL header differs or is absent from core dependencies')
    return dict(status='PASS', report_id=1, usage=0x4c, alias='DEL', equivalent='DELETE',
                source_header_sha256=sha(source / 'shortcut_keys.h'), compiled_header_sha256=sha(compiled_header),
                compiled_header_dependency_verified=True, compiler_calls_named=True,
                linked_named_function=function, linked_named_table=table, decoded_table=rows,
                table_begin_end_loaded=True, row_stride=8, usage_offset=4,
                literal_reads=literal_reads, named_disassembly_sha256=hashlib.sha256(text.encode()).hexdigest(),
                del_function_name_policy_source_verified=True, actual_elf_sha256=sha(elf), hardware=False)


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
    alias = alias_binding(root, repeat)
    binding.update(status='PASS', build_id=BUILD_ID, source_commit=committed['source_commit'],
                   build_inputs_sha256=committed['build_inputs_sha256'], committed_source_provenance=committed,
                   verifier_context_commit=committed['verifier_context_commit'], post_compile_verifier_delta=None,
                   static_response_source_composition=source, previous_repeat_source_composition=source, del_alias_source_composition=source,
                   bundled_resources=complete, streaming_response=streaming, previous_command_repeat=repeat, del_alias=alias,
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
    print('PASS committed DEL source/header/linked-table, retained REPEAT and streaming target guards')


if __name__ == '__main__':
    main()
