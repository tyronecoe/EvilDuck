"""Read actual target DWARF and cache auxiliary, never-linked layout objects.

No USB/device interface or target execution. The two auxiliary compilations use
the actual approved core.cpp command, compile reviewed source, and are never
linked into the candidate image. Subsequent verifier/package calls only validate
the cached sources, objects, commands and measurements.
"""
import hashlib
import json
import pathlib
import re
import subprocess

BASELINE = pathlib.Path('/workspace/scratch/del-alias-release/build-v1')
BASELINE_ELF_SHA = 'd47c6f0e4fc7339029efaf89a885223c54d023473b40ff36109e42626eebb86f'


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_dwarf(text):
    """Parse bounded readelf DIE blocks and references; never guess type sizes."""
    nodes = {}
    current = None
    stack = []
    for line in text.splitlines():
        match = re.match(r'^\s*<(\d+)><([0-9a-fA-F]+)>: Abbrev Number: (\d+)(?: \((DW_TAG_\w+)\))?', line)
        if match:
            depth, offset, abbreviation = int(match[1]), int(match[2], 16), int(match[3])
            while stack and stack[-1]['depth'] >= depth:
                stack.pop()
            if not abbreviation:
                current = None
                continue
            current = dict(offset=offset, depth=depth, tag=match[4], attrs={}, children=[])
            nodes[offset] = current
            if stack:
                stack[-1]['children'].append(offset)
            stack.append(current)
        elif current:
            match = re.search(r'DW_AT_(\w+)\s*:\s*(.*)$', line)
            if match:
                current['attrs'][match[1]] = match[2]
    return nodes


def name(node):
    value = node['attrs'].get('name', '')
    return value.rsplit(': ', 1)[-1]


def number(value):
    # Numeric DWARF attributes in the selected compiler use decimal or 0xhex.
    match = re.match(r'^(0x[0-9a-fA-F]+|[0-9]+)(?:\s|$)', value)
    require(match is not None, 'DWARF numeric attribute is missing or not literal')
    return int(match[1], 0)


def reference(node, attribute='type'):
    value = node['attrs'].get(attribute, '')
    match = re.fullmatch(r'<0x([0-9a-fA-F]+)>', value)
    require(match is not None, 'DWARF type reference is missing or not direct')
    return int(match[1], 16)


def exact(nodes, tag, selected):
    rows = [n for n in nodes.values() if n['tag'] == tag and name(n) == selected and 'byte_size' in n['attrs']]
    require(len(rows) == 1, 'DWARF complete type absent/ambiguous: ' + selected)
    return rows[0]


def array_length(nodes, selected):
    require(selected['tag'] == 'DW_TAG_array_type', 'Expected DWARF array type')
    ranges = [nodes[n] for n in selected['children'] if nodes[n]['tag'] == 'DW_TAG_subrange_type']
    require(len(ranges) == 1, 'DWARF array range absent/ambiguous')
    lower = number(ranges[0]['attrs'].get('lower_bound', '0'))
    return number(ranges[0]['attrs']['upper_bound']) - lower + 1


def layout_from_dwarf(text):
    nodes = parse_dwarf(text)
    compiler = exact(nodes, 'DW_TAG_class_type', 'Compiler')
    constants = [nodes[n] for n in compiler['children'] if nodes[n]['tag'] == 'DW_TAG_structure_type' and name(nodes[n]) == 'Constant']
    require(len(constants) == 1, 'Compiler Constant type missing/ambiguous')
    constant = constants[0]
    members = {name(nodes[n]): nodes[n] for n in constant['children'] if nodes[n]['tag'] == 'DW_TAG_member'}
    require(set(members) == {'name', 'value'}, 'Constant members changed')
    compiler_members = {name(nodes[n]): nodes[n] for n in compiler['children'] if nodes[n]['tag'] == 'DW_TAG_member'}
    require('constants_' in compiler_members, 'Compiler constant table missing')
    cells = nodes[reference(compiler_members['constants_'])]
    require(reference(cells) == constant['offset'], 'Compiler array has another constant type')
    name_array, value_array = nodes[reference(members['name'])], nodes[reference(members['value'])]
    char_type = nodes[reference(name_array)]
    require(number(char_type['attrs'].get('byte_size', '0')) == 1, 'Constant label cell base is not one byte')
    return dict(compiler_bytes=number(compiler['attrs']['byte_size']), constant_bytes=number(constant['attrs']['byte_size']),
                constant_cell_bytes=array_length(nodes, name_array), constant_value_bytes=array_length(nodes, value_array),
                name_offset=number(members['name']['attrs']['data_member_location']),
                value_offset=number(members['value']['attrs']['data_member_location']),
                constant_slots=array_length(nodes, cells), compiler_die=compiler['offset'])


def command(root):
    selected = [r for r in json.loads((root / 'build/compile_commands.json').read_text()) if pathlib.Path(r['file']).name == 'core.cpp']
    require(len(selected) == 1, 'Layout core compilation absent/ambiguous')
    return selected[0]


def tools(entry):
    compiler = pathlib.Path(entry['arguments'][0])
    stem = compiler.name.rsplit('-', 1)[0]
    return compiler, compiler.with_name(stem + '-readelf'), compiler.with_name(stem + '-nm')


def stack_rows(path):
    rows = {}
    for line in path.read_text().splitlines():
        fields = line.rsplit('\t', 2)
        require(len(fields) == 3 and fields[1].isdigit(), 'Unexpected compiler stack-usage format')
        selected = re.sub(r'^.*?:[0-9]+:[0-9]+:', '', fields[0])
        require(selected not in rows, 'Ambiguous stack-usage function')
        rows[selected] = dict(bytes=int(fields[1]), kind=fields[2])
    return rows


def probe(root, entry, label, source, workspace):
    directory = workspace / label
    source_hashes = {name: sha(source / name) for name in ['core.cpp', 'core.h', 'shortcut_keys.h']}
    probe_source = ('#include ' + json.dumps(str(source / 'core.cpp')) + '\nextern "C" {\n' +
        ''.join('extern __attribute__((used)) const unsigned char evilduck_layout_' + n + '[' + expression + '] = {};\n' for n, expression in [
            ('compiler_size', 'sizeof(ds_preview::Compiler)'), ('compiler_alignment', 'alignof(ds_preview::Compiler)'),
            ('session_size', 'sizeof(ds_preview::CompileSession)'), ('session_alignment', 'alignof(ds_preview::CompileSession)'),
            ('program_size', 'sizeof(ds_preview::Program)'), ('runtime_size', 'sizeof(ds_preview::Runtime)'),
            ('workspace', 'ds_preview::CompileStorage')]) + '}\n')
    require(not any(a in ['-MF', '-MT', '-MQ'] or a.startswith('-fstack-usage=') for a in entry['arguments']),
            'Auxiliary compile has a fixed production side-output path')
    responses = {a[1:]: sha(a[1:]) for a in entry['arguments'] if a.startswith('@')}
    expected = dict(compiler_sha256=sha(entry['arguments'][0]), source_hashes=source_hashes, command_template=entry['arguments'], response_file_hashes=responses,
                    probe_sha256=hashlib.sha256(probe_source.encode()).hexdigest())
    manifest = directory / 'measurement.json'
    if manifest.exists():
        row = json.loads(manifest.read_text())
        require(row['inputs'] == expected, 'Cached layout probe inputs changed')
        require(sha(directory / 'probe.cpp') == expected['probe_sha256'] and sha(directory / 'probe.o') == row['object_sha256'],
                'Cached layout object/source changed')
        require(row['compile_exit'] == 0 and not row['compile_stderr'], 'Cached layout compile failed')
    else:
        require(not directory.exists(), 'Partial layout probe retained; use fresh build evidence')
        directory.mkdir(parents=True)
        (directory / 'probe.cpp').write_text(probe_source)
        args = list(entry['arguments'])
        require(args.count(entry['file']) == 1, 'Layout compile input ambiguous')
        args[args.index(entry['file'])] = str(directory / 'probe.cpp')
        args[args.index('-o') + 1] = str(directory / 'probe.o')
        result = subprocess.run(args, capture_output=True, text=True, timeout=300)
        row = dict(inputs=expected, command=args, compile_exit=result.returncode,
                   compile_stdout=result.stdout, compile_stderr=result.stderr,
                   object_sha256=sha(directory / 'probe.o') if result.returncode == 0 else None,
                   linked_to_firmware=False, target_execution=False)
        manifest.write_text(json.dumps(row, indent=2) + '\n')
        require(result.returncode == 0 and not result.stderr, 'Auxiliary target layout probe compilation failed')
    _, _, nm = tools(entry)
    text = subprocess.check_output([str(nm), '-S', '--defined-only', str(directory / 'probe.o')], text=True)
    values = {}
    for line in text.splitlines():
        match = re.fullmatch(r'[0-9a-fA-F]+ ([0-9a-fA-F]+) [A-Za-z] evilduck_layout_(\w+)', line)
        if match:
            values[match[2]] = int(match[1], 16)
    require(set(values) == {'compiler_size', 'compiler_alignment', 'session_size', 'session_alignment', 'program_size', 'runtime_size', 'workspace'},
            'Auxiliary target layout symbols missing or ambiguous')
    return dict(row, values=values, manifest_sha256=sha(manifest), input_kind='EXACT_APPROVED_TARGET_COMMAND_AUXILIARY_OBJECT_ONLY')


def validate_capacity(baseline, candidate):
    require(baseline['constant_cell_bytes'] == 24 and candidate['constant_cell_bytes'] == 32,
            'Target constant label cells do not show 24-to-32-byte change')
    require(all(v['constant_slots'] == 16 and v['constant_value_bytes'] == 64 and v['name_offset'] == 0
                for v in [baseline, candidate]), 'Target constant slots/value storage changed')
    require(baseline['value_offset'] == 24 and candidate['value_offset'] == 32 and
            candidate['constant_bytes'] - baseline['constant_bytes'] == 8,
            'Target Constant packing differs beyond eight label bytes')
    require(candidate['compiler_bytes'] - baseline['compiler_bytes'] == 128 and candidate['compiler_bytes'] <= 4096,
            'Target Compiler grew beyond the sixteen bounded name cells/workspace')


def measure(root):
    root = pathlib.Path(root)
    require(sha(BASELINE / 'build/EvilDuckS3.ino.elf') == BASELINE_ELF_SHA, 'Measured DEL baseline ELF changed')
    baseline_entry, current_entry = command(BASELINE), command(root)
    compiler, readelf, nm = tools(current_entry)
    require(sha(compiler) == sha(baseline_entry['arguments'][0]), 'Layout baseline/current compiler differ')
    layouts = {}
    for label, selected in [('baseline', BASELINE), ('candidate', root)]:
        obj = selected / 'build/sketch/core.cpp.o'
        text = subprocess.check_output([str(readelf), '--debug-dump=info', str(obj)], text=True)
        layout = layout_from_dwarf(text)
        # Independently require the linked ELF's complete Compiler type to agree
        # with the source-bound, linked core object's DWARF layout.
        elf = selected / 'build/EvilDuckS3.ino.elf'
        linked = subprocess.check_output([str(readelf), '--debug-dump=info', '--dwarf-depth=3', str(elf)], text=True)
        definitions = []
        for block in re.split(r'(?=\n <[0-9]+><[0-9a-fA-F]+>:)', linked):
            if 'DW_TAG_class_type' in block and re.search(r'DW_AT_name\s*:\s*[^\n]*: Compiler\n', block):
                value = re.search(r'DW_AT_byte_size\s*:\s*([0-9]+)', block)
                if value:
                    definitions.append(int(value[1]))
        require(definitions == [layout['compiler_bytes']], 'Linked ELF/object Compiler layout differs')
        layouts[label] = dict(layout, object_sha256=sha(obj), object_dwarf_sha256=hashlib.sha256(text.encode()).hexdigest(),
                              elf_sha256=sha(elf), linked_elf_compiler_bytes=definitions[0])
    validate_capacity(layouts['baseline'], layouts['candidate'])
    auxiliary = {}
    for label, selected, entry in [('baseline', BASELINE, baseline_entry), ('candidate', root, current_entry)]:
        auxiliary[label] = probe(root, entry, label, selected / 'candidate/EvilDuckS3', root / 'layout-measurements')
        values = auxiliary[label]['values']
        require(values['compiler_size'] == layouts[label]['compiler_bytes'] and values['workspace'] == 4096,
                'Target sizeof object and DWARF/workspace disagree')
        require(values['compiler_alignment'] <= values['session_alignment'] and values['session_alignment'] % values['compiler_alignment'] == 0,
                'Compiler alignment does not fit session storage alignment')
    baseline_stack = stack_rows(BASELINE / 'build/sketch/core.cpp.su')
    candidate_stack = stack_rows(root / 'build/sketch/core.cpp.su')
    differences = [{'function':n, 'before':baseline_stack.get(n), 'after':candidate_stack.get(n)}
                   for n in sorted(set(baseline_stack) | set(candidate_stack)) if baseline_stack.get(n) != candidate_stack.get(n)]
    source = (root / 'candidate/EvilDuckS3/core.cpp').read_text()
    require('static_assert(sizeof(Compiler)<=CompileStorage' in source and 'static_assert(alignof(Compiler)<=alignof(max_align_t)' in source,
            'Compiler workspace/alignment static assertions removed')
    symbols = subprocess.check_output([str(nm), '--defined-only', str(root / 'build/EvilDuckS3.ino.elf')], text=True)
    require('evilduck_layout_' not in symbols, 'Auxiliary layout object was linked into firmware')
    return dict(status='PASS', constant_cell_bytes=32, max_label_bytes=31, constant_slots=16,
                workspace_bytes=4096, workspace_static_assert_retained=True, alignment_static_assert_retained=True,
                target_compiler_bytes=layouts['candidate']['compiler_bytes'],
                target_compiler_alignment=auxiliary['candidate']['values']['compiler_alignment'],
                baseline_target_compiler_bytes=layouts['baseline']['compiler_bytes'],
                compiler_byte_delta=128, workspace_margin_bytes=4096-layouts['candidate']['compiler_bytes'],
                target_layouts=layouts, auxiliary_layout_objects=auxiliary,
                core_stack_usage=dict(baseline_sha256=sha(BASELINE / 'build/sketch/core.cpp.su'),
                    candidate_sha256=sha(root / 'build/sketch/core.cpp.su'), changed_functions=differences,
                    baseline_functions=len(baseline_stack), candidate_functions=len(candidate_stack),
                    baseline_max_bytes=max(v['bytes'] for v in baseline_stack.values()),
                    candidate_max_bytes=max(v['bytes'] for v in candidate_stack.values()), target_measurement=True),
                actual_target_execution=False, production_layout_globals_added=False,
                actual_target_heap_measured=False)
