#!/usr/bin/env python3
"""Occurrence-checked v2 adapter over an immutable complete observer-v1 tool.

All original function bodies and predicates remain; exact path/identity edits
are listed below. Additional v2 proof requirements are appended after loading.
"""
import pathlib as _v2_pathlib
import hashlib as _v2_hashlib
import builtins as _v2_builtins
import sys as _v2_sys
_v2_sys.dont_write_bytecode = True
_V2_FROZEN_PARENT = _v2_pathlib.Path(__file__).resolve().parents[1] / 'usb_os_observer_release' / 'test_verify_controls.py'
_V2_FROZEN_SHA = 'b2d32afc6de0d6bad07ce2a8881238e59ddf07f82e5b77ae5780daa61b8149db'
_V2_EDITS = [('tests/usb_os_observer_release/', 'tests/usb_os_observer_v2_release/', 1)]

_V2_EDITS += [(
    "tree=ast.parse((HERE/'build_candidate.py').read_text())",
    "tree=ast.parse(B._V2_SOURCE)",1)]

def _v2_frozen_source():
    raw = _V2_FROZEN_PARENT.read_bytes()
    assert _v2_hashlib.sha256(raw).hexdigest() == _V2_FROZEN_SHA, 'Historical observer-v1 tool changed'
    text = raw.decode()
    for before, after, count in _V2_EDITS:
        assert text.count(before) == count, ('Observer-v2 adapter occurrence mismatch', before, text.count(before))
        text = text.replace(before, after)
    return text

_V2_SOURCE = _v2_frozen_source()
_v2_original_name = __name__
try:
    __name__ = 'observer_v2_frozen_test_verify_controls_py'
    exec(_v2_builtins.compile(_V2_SOURCE, str(_V2_FROZEN_PARENT), 'exec'), globals())
finally:
    __name__ = _v2_original_name


def _v2_test_frozen_parent_source_and_predicates(self):
 for module in [V,R,B]:
  original=ast.parse(module._V2_FROZEN_PARENT.read_text())
  adapted=ast.parse(module._V2_SOURCE)
  self.assertEqual(V.sha(module._V2_FROZEN_PARENT),module._V2_FROZEN_SHA)
  for kind in [ast.Assert]:
   self.assertEqual(sum(isinstance(n,kind) for n in ast.walk(original)),sum(isinstance(n,kind) for n in ast.walk(adapted)))
  count=lambda tree:sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' for n in ast.walk(tree))
  self.assertEqual(count(original),count(adapted))

def _v2_test_modified_frozen_parent_refused(self):
 with tempfile.TemporaryDirectory(prefix='observer-v2-frozen-parent-') as folder:
  copy=pathlib.Path(folder)/'modified.py';copy.write_bytes(B._V2_FROZEN_PARENT.read_bytes()+b'\n')
  with patch.object(B,'_V2_FROZEN_PARENT',copy):
   with self.assertRaises(AssertionError):B._v2_frozen_source()

def _v2_test_old_observer_v1_layers_refused(self):
 base=ROOT.parent/'scratch/usb-os-observer-release/build-v3/candidate/EvilDuckS3'
 for name in ['hid_backend.cpp','hid_backend.h','webserver.cpp','webfiles.h','caps_trial.h']:
  self.mutate(name,lambda _,n=name:(base/n).read_bytes())

def _v2_test_missing_contract_fields_or_schema_refused(self):
 for name,before,after in [('hid_backend.h',b'expectedGeneration',b'unboundGeneration'),
                           ('hid_backend.h',b'TailMs=5000',b'TailMs=6000'),
                           ('webserver.cpp',b'evilduck-usb-observer-v2',b'evilduck-usb-observer-v1')]:
  self.mutate(name,lambda b,o=before,n=after:b.replace(o,n,1))

def _v2_test_old_observer_elf_refused(self):
 with self.assertRaises((ValueError,AssertionError)):
  V.observer_binding(ROOT.parent/'scratch/usb-os-observer-release/build-v3')

Policy.test_v2_frozen_parent_source_and_predicates=_v2_test_frozen_parent_source_and_predicates
Policy.test_v2_modified_frozen_parent_refused=_v2_test_modified_frozen_parent_refused
Policy.test_v2_old_observer_v1_layers_refused=_v2_test_old_observer_v1_layers_refused
Policy.test_v2_missing_contract_fields_or_schema_refused=_v2_test_missing_contract_fields_or_schema_refused
Policy.test_v2_old_observer_elf_refused=_v2_test_old_observer_elf_refused

def _v2_test_callback_graph_counts_only_reachable_frames_and_refuses_unknown(self):
 wrapper=dict(address=0x42001000,size=12,kind='T',name='__wrap_dcd_event_handler')
 observe=dict(address=0x42002000,size=12,kind='T',name='usb_observer::observe(dcd_event_t const*, bool)')
 clock=dict(address=0x42003000,size=12,kind='T',name='usb_observer::clockMs()')
 foreground=dict(address=0x42004000,size=12,kind='T',name='usb_observer::sampleGeneration()')
 symbols=[wrapper,observe,clock,foreground]
 bodies={wrapper['address']:'42001000: 000005 call8 42002000 <usb_observer::observe(dcd_event_t const*, bool)>\n',
         observe['address']:'42002000: 000005 call8 42003000 <usb_observer::clockMs()>\n',
         clock['address']:'42003000: 000005 call8 40001000 <esp_timer_get_time>\n',
         foreground['address']:''}
 frames=[dict(function='void __wrap_dcd_event_handler(dcd_event_t const*, bool)',bytes=32),
         dict(function='void usb_observer::observe(const dcd_event_t*, bool)',bytes=64),
         dict(function='uint32_t usb_observer::clockMs()',bytes=32),
         dict(function='uint32_t usb_observer::sampleGeneration()',bytes=128)]
 def inspect(objdump,elf,row):return bodies[row['address']],{}
 with tempfile.TemporaryDirectory(prefix='v2-callback-graph-') as folder:
  elf=pathlib.Path(folder)/'actual.elf';elf.write_bytes(b'ELF')
  with patch.object(V,'inspection_disassembly',side_effect=inspect):
   selected,proof=V._v2_callback_frames(frames,symbols,observe,wrapper,'objdump',elf)
   self.assertEqual(sum(row['bytes'] for row in selected),128)
   self.assertEqual(len(proof['functions']),3)
   with self.assertRaises(ValueError):V._v2_callback_frames(frames[:2],symbols,observe,wrapper,'objdump',elf)
   bodies[observe['address']]+='42002003: 000005 call8 42004000 <usb_observer::sampleGeneration()>\n'
   with self.assertRaises(ValueError):V._v2_callback_frames(frames,symbols,observe,wrapper,'objdump',elf)
   bodies[wrapper['address']]=''
   with self.assertRaises(ValueError):V._v2_callback_frames(frames,symbols,observe,wrapper,'objdump',elf)

Policy.test_v2_callback_graph_counts_only_reachable_frames_and_refuses_unknown=_v2_test_callback_graph_counts_only_reachable_frames_and_refuses_unknown

def _v2_probe_nested_selection(generated):
    """Run the real nested selector/import prefix, never the compiler driver.

    Stop as soon as the historical nested driver has executed its actual source
    import path and the generated wrapper has loaded its checked target verifier.
    This catches the selector bug that static source-path assertions missed.
    """
    import sys
    tree=ast.parse(generated)
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    namespace=dict(__name__='v2_nested_selection_control',__file__=str(HERE/'build_candidate.py'))
    native_compile=builtins.compile
    exec(native_compile(generated,'v2-generated-wrapper','exec'),namespace)
    before_import=[]
    for node in main.body:
        if isinstance(node,ast.Import) and any(a.name=='prepare_sources' for a in node.names):break
        before_import.append(node)
    else:raise AssertionError('Actual nested source import missing')
    exec(native_compile(ast.fix_missing_locations(ast.Module(body=before_import,type_ignores=[])),
        'v2-generated-selector','exec'),namespace)
    target_nodes=[];collect=False
    for node in main.body:
        if isinstance(node,ast.Import) and any(a.name=='importlib.util' and a.asname=='selected_target_import' for a in node.names):collect=True
        if collect:target_nodes.append(node)
        if collect and isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='verify' for t in node.targets):break
    else:raise AssertionError('Actual checked target import missing')
    assert target_nodes
    target_code=native_compile(ast.fix_missing_locations(ast.Module(body=target_nodes,type_ignores=[])),
        'v2-generated-checked-import','exec')
    h1=dict(__name__='v2_actual_nested_h1_control',__file__=str(namespace['PARENT']))
    exec(native_compile(namespace['text'],str(namespace['PARENT']),'exec'),h1)
    selected={};old_path=list(sys.path);old_prepare=sys.modules.pop('prepare_sources',None)
    class SelectionReached(Exception):pass
    def compile_probe(source,filename,mode,*args,**kwargs):
        flags=kwargs.get('flags',args[0] if args else 0)
        needle="args=['compile','--fqbn',s3_validation.FQBN"
        if mode=='exec' and isinstance(source,str) and needle in source and not flags&ast.PyCF_ONLY_AST:
            leaf_tree=ast.parse(source);prefix=[]
            for node in leaf_tree.body:
                prefix.append(node)
                if isinstance(node,ast.ImportFrom) and node.module=='prepare_sources':break
            else:raise AssertionError('Actual leaf source import missing')
            leaf=dict(__name__='v2_actual_leaf_import_control',__file__=str(namespace['PARENT']))
            exec(native_compile(ast.fix_missing_locations(ast.Module(body=prefix,type_ignores=[])),filename,'exec'),leaf)
            selected['preparer']=pathlib.Path(sys.modules['prepare_sources'].__file__).resolve()
            assert selected['preparer']==(HERE/'prepare_sources.py').resolve(),'Nested builder selected old preparer'
            exec(target_code,leaf)
            selected['verifier']=pathlib.Path(leaf['target_module'].__file__).resolve()
            selected['verifier_globals']=pathlib.Path(leaf['verify'].__globals__['__file__']).resolve()
            selected['build_id']=leaf['target_module'].BUILD_ID
            raise SelectionReached()
        return native_compile(source,filename,mode,*args,**kwargs)
    try:
        with patch.object(builtins,'compile',compile_probe):
            try:h1['main']()
            except SelectionReached:pass
            else:raise AssertionError('Control failed to intercept compiler driver')
    finally:
        sys.path[:]=old_path
        sys.modules.pop('prepare_sources',None)
        if old_prepare is not None:sys.modules['prepare_sources']=old_prepare
    return selected

def _v2_test_actual_nested_builder_loads_v2_despite_cached_v1(self):
    import sys
    original=V.load(ROOT/'tests/usb_os_observer_release/verify_target.py','v2_cached_v1_target_negative')
    generated,_=B.adapted_source('a'*40)
    with patch.dict(sys.modules,{'verify_target':original}):selected=_v2_probe_nested_selection(generated)
    self.assertEqual(selected['preparer'],(HERE/'prepare_sources.py').resolve())
    self.assertEqual(selected['verifier'],(HERE/'verify_target.py').resolve())
    self.assertEqual(selected['verifier_globals'],selected['verifier'])
    self.assertEqual(selected['build_id'],'ROUTEB-USB-ENUM-OBSERVER-H1-v2')

def _v2_test_old_nested_selector_is_refused(self):
    generated,_=B.adapted_source('a'*40)
    before="text=text.replace('lock_feedback','usb_os_observer_v2_release')"
    self.assertEqual(generated.count(before),2)
    wrong=generated.replace(before,"text=text.replace('lock_feedback','usb_os_observer_release')",1)
    with self.assertRaisesRegex(AssertionError,'Nested builder selected old preparer'):_v2_probe_nested_selection(wrong)

def _v2_test_old_verifier_path_is_refused(self):
    generated,_=B.adapted_source('a'*40)
    wrong=generated.replace("target_path = ROOT / 'tests/usb_os_observer_v2_release/verify_target.py'",
        "target_path = ROOT / 'tests/usb_os_observer_release/verify_target.py'",1)
    self.assertNotEqual(wrong,generated)
    with self.assertRaises(AssertionError):_v2_probe_nested_selection(wrong)

Policy.test_v2_actual_nested_builder_loads_v2_despite_cached_v1=_v2_test_actual_nested_builder_loads_v2_despite_cached_v1
Policy.test_v2_old_nested_selector_is_refused=_v2_test_old_nested_selector_is_refused
Policy.test_v2_old_verifier_path_is_refused=_v2_test_old_verifier_path_is_refused

def _v2_test_export_handler_requires_exact_top_level_function(self):
    name='handleUsbObservations(AsyncWebServerRequest*)'
    top=dict(name=name,address=0x42001000,size=100,kind='t')
    nested=dict(name=name+'::{lambda(usb_observer::Witness const&)#1}::operator()(usb_observer::Witness const&) const',
        address=0x42002000,size=40,kind='t')
    self.assertEqual(V._v2_export_handler([top,nested]),top)
    for rows in [[nested],[top,dict(top)],[dict(top,size=0),nested]]:
        with self.assertRaises(ValueError):V._v2_export_handler(rows)

Policy.test_v2_export_handler_requires_exact_top_level_function=_v2_test_export_handler_requires_exact_top_level_function

def _v2_test_web_cfg_reenters_real_target_and_skips_unreachable_padding(self):
    start=0x42001000;target=start+0x10
    bodies={start:'42001000: 000006 j 42001010 <handleUsbObservations+0x10>\n'
        '42001003: fffff1 l32r a8, fffffff0 <unreachable-padding>\n',
        target:'42001010: 000005 call8 42002000 <authorize>\n'
        '42001013: 000005 call8 42003000 <snapshot>\n42001016: f01d retw.n\n'}
    seen=[]
    def decode(at,end):seen.append(at);return bodies[at]
    text,proof=V._v2_reachable_instructions(start,0x20,decode)
    self.assertEqual(seen,[start,target]);self.assertNotIn('unreachable-padding',text)
    self.assertEqual([r['target'] for r in V.call_edges(text) if r['opcode'].startswith('call')],[0x42002000,0x42003000])
    self.assertTrue(proof['exact_branch_target_reentry'])

def _v2_test_web_cfg_rejects_unresolved_code_and_bad_reachable_literals(self):
    for text in ['42001000: ffffff ill\n','42001000: 000006 jx a8\n',
                 '42001000: 000006 beqz a2, 42002000 <outside>\n',
                 '42001003: f01d retw.n\n']:
        with self.assertRaises(ValueError):V._v2_reachable_instructions(0x42001000,0x20,lambda a,b,t=text:t)
    text,_=V._v2_reachable_instructions(0x42001000,0x20,
        lambda a,b:'42001000: fffff1 l32r a8, fffffff0 <bad-reachable-literal>\n42001003: f01d retw.n\n')
    with patch.object(V,'elf_bytes',side_effect=ValueError('ELF address is not one unique file-backed load range')):
        with self.assertRaises(ValueError):V.call_edges(text,b'ELF')

Policy.test_v2_web_cfg_reenters_real_target_and_skips_unreachable_padding=_v2_test_web_cfg_reenters_real_target_and_skips_unreachable_padding
Policy.test_v2_web_cfg_rejects_unresolved_code_and_bad_reachable_literals=_v2_test_web_cfg_rejects_unresolved_code_and_bad_reachable_literals

if __name__ == '__main__':
    raise SystemExit(main())
