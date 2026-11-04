#!/usr/bin/env python3
"""Bind the committed streaming composition to actual compiled/linked response code.

Every frozen privacy/dashboard target predicate is retained with exact reviewed
final source expectations. Actual object relocations and ELF call edges add the
serving proof missing from resource-presence-only verification.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import struct
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/static_response_build_integration'
BUILD_ID = 'ROUTEB-STATIC-RESPONSE-REPAIR-v1'
OLD_BUILD_ID = 'ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1'
PARENT = ROOT / 'tests/dashboard_cleanup/verify_target.py'
PARENT_SHA = '01ff00b6dfe7fe74baf2854123a1a65af38837eb7ee58e7c6f9a82eab8221bb1'
EDITOR = ROOT / 'tests/editor_build_integration/verify_target.py'
EDITOR_SHA = '3de9e0a39ce39ed40204c23b94a36b875f8f5999fbe956d9d35f700b15c6a810'
PIN = HERE / 'source-manifest.json'
BYTE_SEND = 'AsyncWebServerRequest::send(int, char const*, unsigned char const*, unsigned int,'
BYTE_FACTORY = 'AsyncWebServerRequest::beginResponse(int, char const*, unsigned char const*, unsigned int,'
PROGMEM_CTOR = 'AsyncProgmemResponse::AsyncProgmemResponse(int, char const*, unsigned char const*, unsigned int,'
FILL = 'AsyncProgmemResponse::_fillBuffer(unsigned char*, unsigned int)'
RESOURCES = ['INDEX_HTML', 'SETTINGS_HTML', 'TERMINAL_HTML', 'CREDITS_HTML',
             'ERROR404_HTML', 'STYLE_CSS', 'INDEX_JS', 'SETTINGS_JS', 'TERMINAL_JS']
SELF_PATH = 'tests/static_response_build_integration/verify_target.py'
POST_COMPILE_SOURCE = '68f7fb2de5af2988a3136eb9222fb8c3e7dee8f5'
POST_COMPILE_VERIFIER_SHA = '379150aa1beb44f5b908529a2bfaa24a41293b9924d4b1709a50548c3acf978e'
POST_COMPILE_VERIFIER_BYTES = 17976


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adapted_parent():
    require(sha(PARENT) == PARENT_SHA, 'Historical dashboard target verifier changed')
    text, changes = PARENT.read_text(), []

    def replace(old, new, count=1):
        nonlocal text
        require(text.count(old) == count, 'Target adaptation occurrence mismatch: ' + old)
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))

    replace('BUILD_ID = "ROUTEB-DASHBOARD-CLEANUP-v1"', 'BUILD_ID = ' + repr(BUILD_ID))
    replace('tests/dashboard_cleanup/source-manifest.json', 'tests/static_response_build_integration/source-manifest.json', 2)
    replace('tests/dashboard_cleanup/application.patch', 'tests/static_response_build_integration/identity.patch')
    replace("'sha(ROOT / \"tests/privacy_fix1/prepare_sources.py\")'", "'sha(ROOT / \"tests/dashboard_response_safety/prepare_sources.py\")'")
    replace('len(pin["after"]) == 2 and len(pin["unchanged"]) == 199', 'len(pin["after"]) == 3 and len(pin["unchanged"]) == 198')
    replace('Dashboard manifest is not the reviewed 2/199 source delta', 'Static response manifest is not the reviewed 3/198 source delta')
    replace('{"webfiles.h", "caps_trial.h"}', '{"webfiles.h", "caps_trial.h", "webserver.cpp"}', 2)
    replace('source_files=201, dashboard_files=2, unchanged_files=199', 'source_files=201, static_response_files=3, unchanged_files=198')
    replace('pin["format"] == "evilduck-dashboard-cleanup-v1"', 'pin["format"] == "evilduck-static-response-build-integration-v1"')
    replace('pin["baseline"] == "70d08e9f789c187c5e27350a66f4d0d52992964b"', 'pin["baseline"] == "e692435a7c70dbc0d917bbff733c57900cf7d57c"')
    replace('len(pin["before"]) == 2', 'len(pin["before"]) == 3')
    replace('DASHBOARD CLEANUP / PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW', 'STATIC RESPONSE REPAIR / PRIVACY FIX 1 / H1 EXPERIMENTAL / OWNER REVIEW')
    namespace = dict(__name__='static_response_frozen_dashboard_target', __file__=str(__file__))
    exec(compile(text, str(PARENT), 'exec'), namespace)
    return namespace, changes


def verify_composed_source(source):
    M = load(HERE / 'prepare_sources.py', 'streaming_verify_composition')
    rows = M.verify_final(source)
    source = pathlib.Path(source)
    pin = M.pin()
    repair = json.loads((ROOT / 'tests/dashboard_response_safety/source-manifest.json').read_text())
    repaired = {r['file']: r['sha256'] for r in repair['after'] + repair['unchanged']}
    final = {r['file']: r['sha256'] for r in pin['after'] + pin['unchanged']}
    require(len(final) == len(repaired) == 201 and
            {n for n in final if final[n] != repaired[n]} == {'caps_trial.h'},
            'Target delta extends beyond streaming repair and metadata identity')
    caps = (source / 'caps_trial.h').read_bytes()
    require(caps.count(BUILD_ID.encode()) == 1 and OLD_BUILD_ID.encode() not in caps, 'Target identity missing/ambiguous')
    require(hashlib.sha256(caps.replace(BUILD_ID.encode(), OLD_BUILD_ID.encode(), 1)).hexdigest() == repaired['caps_trial.h'],
            'Identity header changed beyond literal label')
    require(final['webfiles.h'] == 'df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445',
            'Reviewed editor/dashboard resources omitted or changed')
    require(final['webserver.cpp'] == '98bb1d99e2098c29b962285ec4760d1ab3ed0d6d656cceed55d138fba1e7455c',
            'Streaming response implementation omitted or changed')
    return dict(status='PASS', source_files=len(rows), repaired_files=1, identity_only_files=1,
                reviewed_editor_preserved=True, source_manifest_sha256=sha(PIN),
                webfiles_sha256=final['webfiles.h'], webserver_sha256=final['webserver.cpp'], build_id=BUILD_ID)


def verify_input_manifest(build_root):
    path = pathlib.Path(build_root) / 'build-inputs.json'
    value = json.loads(path.read_text())
    commit = value.get('source_commit', '')
    require(value.get('format') == 'evilduck-committed-build-inputs-v1' and
            value.get('source_commit_contains_changes') is True and
            value.get('uncommitted_local_changes') is False and value.get('build_id') == BUILD_ID and
            re.fullmatch('[0-9a-f]{40}', commit) is not None, 'Committed build input provenance missing or false')
    kind = subprocess.run(['git', 'cat-file', '-t', commit], cwd=ROOT, text=True, capture_output=True)
    require(kind.returncode == 0 and kind.stdout.strip() == 'commit',
            'Recorded source identity is not a Git commit')
    require(subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], cwd=ROOT,
                           capture_output=True).returncode == 0, 'Recorded source checkpoint is not an ancestor')
    rows = value['files']
    names = [r['file'] for r in rows]
    require(len(rows) > 0 and len(names) == len(set(names)), 'Committed source inventory missing/duplicated')
    required = {'tools/build_routeb_candidate.py'} | {'tests/static_response_build_integration/' + n for n in
        ['build_candidate.py', 'prepare_sources.py', 'identity.patch', 'source-manifest.json', 'verify_target.py',
         'verify_release.py', 'startup_decode.py', 'test_verify_controls.py']}
    require(required.issubset(names), 'Default builder/overlay/verifiers absent from committed input manifest')
    require(hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest() == value['files_sha256'],
            'Committed input-list digest differs')
    # A post-link decoder correction is host-only: do not rewrite the original
    # clean compilation's C manifest or pretend the target was compiled at D.
    # Resolve the stable last-touch revision, not HEAD, so later package-only
    # commits cannot change the canonical verification binding.
    verifier_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', SELF_PATH],
                                               cwd=ROOT, text=True).strip()
    require(re.fullmatch('[0-9a-f]{40}', verifier_commit) is not None, 'Verifier revision is absent')
    require(subprocess.run(['git', 'merge-base', '--is-ancestor', verifier_commit, 'HEAD'],
                           cwd=ROOT, capture_output=True).returncode == 0, 'Verifier revision is not an ancestor')
    verifier_blob = subprocess.check_output(['git', 'show', verifier_commit + ':' + SELF_PATH], cwd=ROOT)
    require(verifier_blob == (ROOT / SELF_PATH).read_bytes(), 'Current verifier differs from its last-touch Git revision')
    post_compile_delta = None
    for row in rows:
        relative = pathlib.PurePosixPath(row['file'])
        selected = ROOT / row['file']
        require(not relative.is_absolute() and '..' not in relative.parts and selected.is_file() and
                not selected.is_symlink() and selected.resolve().is_relative_to(ROOT), 'Unsupported committed input path')
        committed = subprocess.check_output(['git', 'show', commit + ':' + row['file']], cwd=ROOT)
        require(len(committed) == row['size'] and hashlib.sha256(committed).hexdigest() == row['sha256'],
                'Original compilation input differs from its Git blob: ' + row['file'])
        current = selected.read_bytes()
        if committed != current:
            require(row['file'] == SELF_PATH and post_compile_delta is None,
                    'Non-verifier input changed since compilation: ' + row['file'])
            require(commit == POST_COMPILE_SOURCE and row['sha256'] == POST_COMPILE_VERIFIER_SHA and
                    row['size'] == POST_COMPILE_VERIFIER_BYTES,
                    'Unreviewed post-compilation verifier source context')
            require(subprocess.run(['git', 'merge-base', '--is-ancestor', commit, verifier_commit],
                                   cwd=ROOT, capture_output=True).returncode == 0,
                    'Post-link verifier does not descend from the compilation checkpoint')
            require(current == verifier_blob, 'Post-link verifier is not the recorded Git verifier blob')
            post_compile_delta = dict(path=SELF_PATH, compile_source_commit=commit,
                verification_context_commit=verifier_commit, compile_size=len(committed),
                compile_sha256=hashlib.sha256(committed).hexdigest(), verification_size=len(current),
                verification_sha256=hashlib.sha256(current).hexdigest(),
                git_compile_blob_verified=True, git_verifier_blob_verified=True)
    return dict(source_commit=commit, build_inputs_sha256=sha(path), files_sha256=value['files_sha256'],
                input_count=len(rows), source_commit_contains_changes=True, uncommitted_local_changes=False,
                verifier_context_commit=verifier_commit, post_compile_verifier_delta=post_compile_delta)


def resource_literals(source):
    found = re.findall(r'static const char (\w+)\[\] PROGMEM = R"rawliteral\((.*?)\)rawliteral";',
                       pathlib.Path(source).read_text(), re.S)
    values = dict(found)
    require(len(values) == len(found) and set(values) == set(RESOURCES), 'Static resource inventory differs')
    return {name: values[name].encode() for name in RESOURCES}


def object_sections(disassembly):
    chunks = disassembly.split('Disassembly of section ')
    literal = [c for c in chunks if c.startswith('.literal._ZL12handleStaticP21AsyncWebServerRequest:')]
    text = [c for c in chunks if c.startswith('.text._ZL12handleStaticP21AsyncWebServerRequest:')]
    require(len(literal) == len(text) == 1, 'Compiled static-handler sections missing/ambiguous')
    return literal[0], text[0]


def verify_dispatch_text(object_disassembly, linked_handler):
    literal, code = object_sections(object_disassembly)
    selected = literal + code
    require(BYTE_SEND in selected or BYTE_FACTORY in selected, 'Static assets lack byte-pointer/length overload')
    require('AsyncWebServerRequest::send_P(' not in selected, 'Old heap-copy static send_P is still compiled')
    require(BYTE_SEND in linked_handler or BYTE_FACTORY in linked_handler, 'Linked static assets lack streaming call edge')
    require('AsyncWebServerRequest::send_P(' not in linked_handler, 'Linked static assets retain old heap-copy call')
    for name in RESOURCES:
        require(re.search(r'\.rodata\._ZL\d+' + re.escape(name) + r'(?:\s|$)', literal) is not None,
                'Compiled handler lacks resource pointer: ' + name)
        require('<' + name + '>' in linked_handler, 'Linked handler lacks resource pointer: ' + name)
    return dict(byte_overload_observed=True, char_send_P_absent=True, resources=RESOURCES,
                unknown_path_char_response_allowed=True, object_sections_sha256=hashlib.sha256(selected.encode()).hexdigest(),
                linked_handler_sha256=hashlib.sha256(linked_handler.encode()).hexdigest())


def decode_literal_pool(dump):
    """Decode objdump -s bytes (little-endian words remain raw until used)."""
    pool = bytearray()
    for line in dump.splitlines():
        match = re.match(r'^\s+([0-9a-fA-F]+)\s+((?:[0-9a-fA-F]{8}\s*){1,4})', line)
        if match:
            offset = int(match[1], 16)
            require(offset == len(pool), 'Noncontiguous static-handler literal pool')
            pool.extend(bytes.fromhex(''.join(match[2].split())))
    require(len(pool) > 0 and len(pool) % 4 == 0, 'Missing/misaligned static-handler literal pool')
    return bytes(pool)


def decode_asset_calls(object_disassembly, literal_pool, expected_lengths):
    """Check the actual Xtensa a13 pointer/a14 length at each asset send.

    The pinned compiler emits signed MOVI followed by ADDMI for some lengths.
    objdump's ADDMI operand already includes its 8-bit shift: 152 + 0x2f00,
    not 152 + (0x2f00 << 8). Other lengths use L32R or plain MOVI. This is a
    narrow fail-closed decoder for the observed instruction forms, not a general
    Xtensa emulator. Calls invalidate caller registers, preventing stale values
    from one URI branch from being reused for another.
    """
    literal, code = object_sections(object_disassembly)
    pointers = {}
    for line in literal.splitlines():
        match = re.match(r'^\s*([0-9a-fA-F]+):\s+R_XTENSA_32\s+\.rodata\._ZL\d+(\w+)\s*$', line)
        if match and match[2] in expected_lengths:
            pointers[int(match[1], 16)] = match[2]
    instructions, indexed = [], {}
    for line in code.splitlines():
        match = re.match(r'^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]+)\s+([a-z][a-z0-9_.]*)\s*(.*)$', line)
        if match:
            address = int(match[1], 16)
            row = dict(address=address, opcode=match[3], operands=match[4], relocations=[])
            instructions.append(row)
            indexed[address] = row
            continue
        match = re.match(r'^\s*([0-9a-fA-F]+):\s+(R_XTENSA_\w+)\s+(.+)$', line)
        if match and int(match[1], 16) in indexed:
            indexed[int(match[1], 16)]['relocations'].append((match[2], match[3]))
    registers, traces, calls = {}, {}, []

    def integer(value):
        return int(value, 0)

    for row in instructions:
        opcode, operands = row['opcode'], [p.strip() for p in row['operands'].split(',')]
        where = '0x%x: %s %s' % (row['address'], opcode, row['operands'])
        destination = operands[0] if operands else ''
        if opcode in {'movi', 'movi.n'}:
            registers[destination] = integer(operands[1])
            traces[destination] = [where]
        elif opcode in {'addi', 'addi.n', 'addmi'}:
            value = registers.get(operands[1])
            registers[destination] = value + integer(operands[2]) if isinstance(value, int) else None
            traces[destination] = traces.get(operands[1], []) + [where]
        elif opcode in {'mov', 'mov.n'}:
            registers[destination] = registers.get(operands[1])
            traces[destination] = traces.get(operands[1], []) + [where]
        elif opcode == 'or' and len(operands) == 3 and operands[1] == operands[2]:
            registers[destination] = registers.get(operands[1])
            traces[destination] = traces.get(operands[1], []) + [where]
        elif opcode == 'l32r':
            expanded = [target for kind, target in row['relocations'] if kind == 'R_XTENSA_ASM_EXPAND']
            offset = [re.fullmatch(r'\.literal\._ZL12handleStaticP21AsyncWebServerRequest(?:\+(0x[0-9a-fA-F]+))?', target)
                      for kind, target in row['relocations'] if kind == 'R_XTENSA_SLOT0_OP']
            offset = [m for m in offset if m is not None]
            if expanded:
                require(len(expanded) == 1, 'Ambiguous call target in static handler')
                registers[destination] = ('function', expanded[0])
            elif len(offset) == 1:
                index = int(offset[0][1] or '0', 0)
                require(index + 4 <= len(literal_pool), 'Literal read beyond static-handler pool')
                registers[destination] = (('resource', pointers[index]) if index in pointers else
                                          struct.unpack_from('<I', literal_pool, index)[0])
            else:
                registers[destination] = None
            traces[destination] = [where]
        elif opcode.startswith('call'):
            target = registers.get(destination) if opcode.startswith('callx') else ('function', row['operands'])
            if isinstance(target, tuple) and target[0] == 'function' and BYTE_SEND in target[1]:
                pointer, length = registers.get('a13'), registers.get('a14')
                require(isinstance(pointer, tuple) and pointer[0] == 'resource' and pointer[1] in expected_lengths,
                        'Asset byte call lacks an independently decoded resource pointer')
                name = pointer[1]
                require(isinstance(length, int) and length == expected_lengths[name],
                        'Compiled asset argument length mismatch: ' + name)
                calls.append(dict(resource=name, http_bytes=length, object_call_offset=row['address'],
                                  pointer_instructions=traces.get('a13', []),
                                  length_instructions=traces.get('a14', [])))
            for register in ['a' + str(n) for n in range(8, 16)]:
                registers.pop(register, None)
                traces.pop(register, None)
        elif (re.fullmatch(r'a\d+', destination) and not opcode.startswith(('b', 's8i', 's16i', 's32i')) and
              opcode not in {'j', 'jx', 'entry', 'retw', 'retw.n', 'memw', 'nop', 'nop.n'}):
            registers[destination] = None
            traces[destination] = [where]
    require(set(row['resource'] for row in calls) == set(expected_lengths),
            'Not every static resource has an exact compiled pointer/length call witness')
    return calls


def symbols(nm_output):
    rows = []
    for line in nm_output.splitlines():
        m = re.match(r'^([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+\w\s+(.+)$', line)
        if m:
            rows.append(dict(address=int(m[1], 16), size=int(m[2], 16), name=m[3]))
    return rows


def one_symbol(rows, prefix):
    selected = [r for r in rows if r['name'].startswith(prefix)]
    unique = {(r['address'], r['size'], r['name']): r for r in selected}
    require(len(unique) == 1, 'Linked response symbol absent/ambiguous: ' + prefix)
    return next(iter(unique.values()))


def streaming_binding(root, binding):
    build, sketch = root / 'build', root / 'candidate/EvilDuckS3'
    entries = json.loads((build / 'compile_commands.json').read_text())
    rows = [r for r in entries if pathlib.Path(r['file']).name == 'webserver.cpp']
    require(len(rows) == 1, 'Actual webserver compiler entry ambiguous')
    args = rows[0]['arguments']
    compiler = pathlib.Path(args[0])
    stem = compiler.name.rsplit('-', 1)[0]
    objdump, nm = compiler.with_name(stem + '-objdump'), compiler.with_name(stem + '-nm')
    require(objdump.is_file() and nm.is_file(), 'Pinned compiler companion inspection tools missing')
    obj = pathlib.Path(args[args.index('-o') + 1])
    objtext = subprocess.check_output([str(objdump), '-C', '-dr', str(obj)], text=True)
    elf = build / 'EvilDuckS3.ino.elf'
    syms = symbols(subprocess.check_output([str(nm), '-C', '-S', str(elf)], text=True))

    def body(prefix):
        symbol = one_symbol(syms, prefix)
        text = subprocess.check_output([str(objdump), '-C', '-d', '--start-address=' + str(symbol['address']),
                                       '--stop-address=' + str(symbol['address'] + symbol['size']), str(elf)], text=True)
        return symbol, text

    handle, handle_text = body('handleStatic(AsyncWebServerRequest*)')
    dispatch = verify_dispatch_text(objtext, handle_text)
    factory, factory_text = body(BYTE_FACTORY)
    require(PROGMEM_CTOR in factory_text, 'Linked byte/length factory does not call Progmem response constructor')
    require('AsyncBasicResponse::AsyncBasicResponse' not in factory_text and 'String::copy(' not in factory_text,
            'Linked asset factory constructs full-resource heap String')
    fill, fill_text = body(FILL)
    require('memcpy' in fill_text, 'Linked Progmem fill body lacks the pinned memory-copy edge')
    send = None
    if BYTE_SEND in handle_text:
        send_symbol, send_text = body(BYTE_SEND)
        require(BYTE_FACTORY in send_text, 'Linked byte/length send wrapper does not call byte factory')
        send = dict(**send_symbol, disassembly_sha256=hashlib.sha256(send_text.encode()).hexdigest())

    # Full compiled and linked source/object provenance is inherited. Bind the
    # actual SDK factory/fill consumers too, including their real map LOADs.
    report = json.loads((root / 'report.json').read_text())
    map_loads = {line.removeprefix('LOAD ').strip() for line in (build / 'EvilDuckS3.ino.map').read_text().splitlines() if line.startswith('LOAD ')}
    linked = {r['file']: r for r in report['linked_input_hashes']}
    sdk = []
    for name in ['WebRequest.cpp', 'WebResponses.cpp']:
        selected = [r for r in report['framework_compiles'] if pathlib.Path(r['source']).name == name]
        require(len(selected) == 1, 'SDK response implementation compile absent: ' + name)
        row = selected[0]
        require(sha(row['source']) == row['sha256'], 'SDK response source changed: ' + name)
        require(row['object'] in map_loads and row['object'] in linked and sha(row['object']) == linked[row['object']]['sha256'],
                'SDK response consumer object not linked: ' + name)
        sdk.append(dict(source=row['source'], source_sha256=row['sha256'], object=row['object'], object_sha256=sha(row['object']), linked=True))

    values = resource_literals(sketch / 'webfiles.h')
    raw = subprocess.check_output([str(objdump), '-s', '-j', '.literal._ZL12handleStaticP21AsyncWebServerRequest', str(obj)], text=True)
    calls = decode_asset_calls(objtext, decode_literal_pool(raw), {name: len(value) for name, value in values.items()})
    sizes = {row['http_bytes'] for row in calls}
    table = []
    for name, value in values.items():
        require(len(value) in sizes, 'Compiled handler lacks exact non-NUL resource length: ' + name)
        table.append(dict(resource=name, http_bytes=len(value), sha256=hashlib.sha256(value).hexdigest(),
                          compiled_pointer_observed=True, compiled_length_observed=True, c_nul_excluded=True))
    return dict(status='PASS', asset_overload='const uint8_t*+size_t',
                compiled_object=dict(file=str(obj), sha256=sha(obj), **dispatch),
                linked_handler=dict(**handle, disassembly_sha256=hashlib.sha256(handle_text.encode()).hexdigest()),
                linked_send_wrapper=send,
                linked_factory=dict(**factory, progmem_ctor_observed=True, full_resource_string_copy=False,
                                    disassembly_sha256=hashlib.sha256(factory_text.encode()).hexdigest()),
                fill_buffer=dict(**fill, disassembly_sha256=hashlib.sha256(fill_text.encode()).hexdigest()),
                sdk_consumers=sdk, pointer_length_table=table,
                compiled_asset_call_witnesses=calls,
                objdump_sha256=sha(objdump), nm_sha256=sha(nm), actual_elf_sha256=sha(elf),
                hardware=False, actual_ESP32_heap_measured=False)


def verify(build_root):
    root = pathlib.Path(build_root).resolve()
    source = verify_composed_source(root / 'candidate/EvilDuckS3')
    committed = verify_input_manifest(root)
    namespace, changes = adapted_parent()
    binding = namespace['verify'](root)
    require(sha(EDITOR) == EDITOR_SHA, 'Historical complete resource verifier changed')
    E = load(EDITOR, 'streaming_exact_editor_resource_verifier')
    resources = E.literal_resources(root / 'candidate/EvilDuckS3/webfiles.h')
    complete = E.verify_resource_bytes(resources, (root / 'build/EvilDuckS3.ino.elf').read_bytes(),
                                       (root / 'build/EvilDuckS3.ino.bin').read_bytes())
    streaming = streaming_binding(root, binding)
    binding.update(status='PASS', build_id=BUILD_ID, source_commit=committed['source_commit'],
                   build_inputs_sha256=committed['build_inputs_sha256'], committed_source_provenance=committed,
                   verifier_context_commit=committed['verifier_context_commit'],
                   post_compile_verifier_delta=committed['post_compile_verifier_delta'],
                   static_response_source_composition=source, bundled_resources=complete,
                   streaming_response=streaming, actual_parent_verifier_sha256=PARENT_SHA,
                   integration_verifier_adaptations=changes, physical=False, installed=False, package_created=False)
    return binding


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root', required=True, type=pathlib.Path)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    args = parser.parse_args()
    require(not args.output.exists(), 'Use fresh target evidence')
    args.output.write_text(json.dumps(verify(args.build_root), indent=2) + '\n')
    print('PASS exact composed source, compiled asset factory/lengths, linked streaming code and five full resources')


if __name__ == '__main__':
    main()
