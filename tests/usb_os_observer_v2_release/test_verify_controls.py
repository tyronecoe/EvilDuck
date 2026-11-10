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

if __name__ == '__main__':
    raise SystemExit(main())
