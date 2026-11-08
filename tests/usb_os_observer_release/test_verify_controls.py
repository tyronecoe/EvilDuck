#!/usr/bin/env python3
"""Offline fail-closed controls for the additive capture-only release layer."""
import argparse
import ast
import builtins
import hashlib
import importlib.util
import io
import json
import pathlib
import shutil
import struct
import tempfile
import unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
V=load(HERE/'verify_target.py','usb_controls_target')
R=load(HERE/'verify_release.py','usb_controls_release')
B=load(HERE/'build_candidate.py','usb_controls_build')
SOURCE=CANDIDATE=None

class Policy(unittest.TestCase):
 def test_all190_frozen_assertions_preserved(self):
  ns,changes=R.adapted_parent();pin=json.loads((HERE/'source-manifest.json').read_text())
  final={r['file']:r['sha256'] for r in pin['cumulative_h1_after']}
  counts=[('h1_right_modifiers',23),('inject_var_experimental',21),('lock_wait_timeout',16),('source_text_v2',46),('lock_feedback',25),('caps_stop',59)]
  total=0
  for directory,count in counts:
   path=ROOT/'tests'/directory/'verify_link.py';self.assertEqual(V.sha(path),ns['FROZEN'][directory])
   original=ast.parse(path.read_text());self.assertEqual(sum(isinstance(n,ast.Assert) for n in ast.walk(original)),count)
   transformed=ns['FinalCandidateExpectations'](final).visit(original)
   transformed=ns['RuntimeIdentityExpectations'](original).visit(transformed)
   if directory=='h1_right_modifiers':
    handler=R.CompilerHandlerExpectations();transformed=handler.visit(transformed);self.assertEqual(len(handler.edits),2)
   self.assertEqual(sum(isinstance(n,ast.Assert) for n in ast.walk(transformed)),count);total+=count
  self.assertEqual(total,190);self.assertTrue(changes['usb_observer'])
  with self.assertRaises(AssertionError):ns['FinalCandidateExpectations']({n:s for n,s in final.items() if n!='hid_backend.cpp'})
 def test_all_target_require_predicates_preserved(self):
  captured={};original=builtins.compile
  paths={str(V.S.PARENT),str(ROOT/'tests/privacy_fix1/verify_target.py')}
  def capture(source,filename,mode,*args,**kwargs):
   if str(filename) in paths and mode=='exec':
    tree=ast.parse(source);captured.setdefault(str(filename),[]).append(sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' for n in ast.walk(tree)))
   return original(source,filename,mode,*args,**kwargs)
  # The outer wrappers retain ORIGINAL_COMPILE; the nested dashboard/privacy
  # adapter uses builtins.compile directly. Observe both without changing any
  # adapted source or predicate, and check every compilation of each layer.
  with patch.object(V,'ORIGINAL_COMPILE',capture),patch.object(builtins,'compile',capture):
   ns,_=V.adapted_parent();ns['parent_namespace']()
  for path in paths:
   expected=sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' for n in ast.walk(ast.parse(pathlib.Path(path).read_text())))
   self.assertIn(path,captured)
   self.assertTrue(captured[path])
   self.assertEqual(set(captured[path]),{expected})
 def test_final201_exact_and_scope(self):
  value=V.verify_composed_source(SOURCE);self.assertEqual(value['source_files'],201)
  self.assertEqual(set(value['changed_sources']),{'hid_backend.cpp','hid_backend.h','webserver.cpp','webfiles.h','caps_trial.h'})
  self.assertTrue(value['compiler_and_runtime_unchanged'])
 def mutate(self,name,edit):
  with tempfile.TemporaryDirectory(prefix='usb-source-refusal-') as folder:
   p=pathlib.Path(folder)/'source';shutil.copytree(SOURCE,p);file=p/name;before=file.read_bytes();after=edit(before)
   self.assertNotEqual(before,after);file.write_bytes(after)
   with self.assertRaises((ValueError,AssertionError)):V.verify_composed_source(p)
 def test_missing_observer_backend_refused(self):
  self.mutate('hid_backend.cpp',lambda _:pathlib.Path('/workspace/scratch/define-labels-release/build-v1/candidate/EvilDuckS3/hid_backend.cpp').read_bytes())
 def test_missing_observer_header_refused(self):
  self.mutate('hid_backend.h',lambda _:pathlib.Path('/workspace/scratch/define-labels-release/build-v1/candidate/EvilDuckS3/hid_backend.h').read_bytes())
 def test_old_dashboard_refused(self):
  self.mutate('webfiles.h',lambda _:pathlib.Path('/workspace/scratch/define-labels-release/build-v1/candidate/EvilDuckS3/webfiles.h').read_bytes())
 def test_old_endpoint_refused(self):
  self.mutate('webserver.cpp',lambda _:pathlib.Path('/workspace/scratch/define-labels-release/build-v1/candidate/EvilDuckS3/webserver.cpp').read_bytes())
 def test_old_identity_refused(self):self.mutate('caps_trial.h',lambda b:b.replace(V.BUILD_ID.encode(),V.OLD_BUILD_ID.encode(),1))
 def test_unrelated_or_compiler_changes_refused(self):
  for name in ['core.cpp','core.h','shortcut_keys.h','adapter.cpp','USBIdentity.h']:
   if (SOURCE/name).exists():self.mutate(name,lambda b:b+b'\n')
 def test_forwarding_changed_refused(self):
  self.mutate('hid_backend.cpp',lambda b:b.replace(b'__real_dcd_event_handler(event,inIsr);',b'__real_dcd_event_handler(nullptr,false);',1))
 def test_all_priors_and_new_selector_preserved(self):
  text,changes=B.adapted_source('a'*40)
  self.assertIn('assert "--verify-existing" not in sys.argv',text)
  self.assertIn('inherited_safety_predicates_removed=0',text)
  self.assertIn('tests/usb_os_observer_release/prepare_sources.py',text)
  self.assertIn('usb_observer_target_binding=binding',text);self.assertTrue(changes['define_labels'])
  tree=ast.parse((HERE/'build_candidate.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build_inputs')
  self.assertTrue(any(isinstance(n,ast.Attribute) and n.attr=='build_inputs' for n in ast.walk(fn)))
 def test_compile_flag_addition_exact_once(self):
  text="args=['compile','--fqbn',s3_validation.FQBN]\nflags='-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1 -fstack-usage'\nargs+=['--build-property','compiler.cpp.extra_flags='+flags]\n"
  B.FLAG_EVENTS.clear();code=B.flag_adapter(text,'control','exec');self.assertEqual(len(B.FLAG_EVENTS),1)
  values=dict(s3_validation=type('P',(),{'FQBN':'unchanged'})());exec(code,values)
  self.assertEqual(values['flags'],'-DEVILDUCK_USB_ENUM_OBSERVER=1 -DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1 -fstack-usage')
  self.assertEqual(values['args'][-2:],['--build-property','compiler.c.elf.extra_flags=-Wl,--wrap=dcd_event_handler'])
  self.assertEqual(values['args'].count('--build-property'),2)
 def test_compile_injection_does_not_touch_unrelated_source(self):
  B.FLAG_EVENTS.clear();namespace={};exec(B.flag_adapter("flags='unchanged'",'unrelated','exec'),namespace)
  self.assertEqual(namespace['flags'],'unchanged');self.assertEqual(B.FLAG_EVENTS,[])
 def test_compile_duplicate_or_missing_property_refused(self):
  for text in ["args=['compile','--fqbn',s3_validation.FQBN]\nflags='-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1'", "args=['compile','--fqbn',s3_validation.FQBN]\nflags='-DEVILDUCK_USB_ENUM_OBSERVER=1 -DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1'"]:
   with self.assertRaises(AssertionError):B.flag_adapter(text,'refusal','exec')
 def test_exact_additive_profile_preserves_complete_old_comparison(self):
  pin=json.loads((ROOT/'docs/h1-right-modifiers-build.json').read_text())
  baseline=pin['report']['verified_cpp_extra_flags']
  original=[word for word in V.shlex.split(baseline) if not word.startswith('-I')]
  current=V.OBSERVER_FLAG+' '+baseline
  self.assertEqual(V.observer_profile_flags(current),original)
  for bad in [baseline,V.OBSERVER_FLAG+' '+current,baseline+' '+V.OBSERVER_FLAG,
              current+' -DUNREVIEWED_PROFILE_CHANGE=1',current.replace('-DEVILDUCK_CONTROLLED_START=1 ',''),
              current.replace('-fstack-usage','-fno-access-control')]:
   with self.assertRaises(ValueError):
    V.require(V.observer_profile_flags(bad)==original,'Controlled H1 profile flags changed')
 def test_exact_additive_link_property_and_wrapper_set(self):
  command=['compile','--build-property',V.OBSERVER_LINK_PROPERTY]
  link=['compiler','-Wl,--wrap=esp_panic_handler','-Wl,--wrap=dcd_event_handler']
  V.observer_link_profile(command,link)
  for cmd,args in [([],link),(command+command[1:],link),
                   (['compile','--build-property',V.OBSERVER_LINK_PROPERTY+' -Wl,--wrap=other'],link),
                   (command,link[:-1]),(command,link+[link[-1]]),
                   (command,link+['-Wl,--wrap=other']),(command,[link[0],link[-1]]),
                   (command,['compiler',link[-1],link[-2]])]:
   with self.assertRaises(ValueError):V.observer_link_profile(cmd,args)
 def test_inspection_copy_requires_all_allocated_bytes_addresses_flags_and_symbols(self):
  def elf():
   data=bytearray(136);data[:6]=b'\x7fELF\x01\x01'
   struct.pack_into('<I',data,32,52);struct.pack_into('<HH',data,46,40,2)
   struct.pack_into('<10I',data,92,0,1,2,0x42000000,132,4,0,0,4,0)
   data[132:]=b'abcd';return data
  with tempfile.TemporaryDirectory(prefix='observer-elf-integrity-control-') as folder:
   original=pathlib.Path(folder)/'original.elf';copy=pathlib.Path(folder)/'copy.elf';data=elf()
   original.write_bytes(data);copy.write_bytes(data);symbols='42000000 T function\n'
   V.inspection_copy_equivalent(original,copy,symbols,symbols)
   for offset,value in [(132,ord('z')),(104,0x40),(100,3)]:
    changed=bytearray(data);changed[offset]=value;copy.write_bytes(changed)
    with self.assertRaises(ValueError):V.inspection_copy_equivalent(original,copy,symbols,symbols)
   copy.write_bytes(data)
   with self.assertRaises(ValueError):V.inspection_copy_equivalent(original,copy,symbols,symbols+'42000004 T extra\n')
 def test_inspection_heading_normalization_is_exact_and_binding_stable(self):
  original=pathlib.Path('/build/actual.elf');a=pathlib.Path('/tmp/first/inspection.elf');b=pathlib.Path('/tmp/second/inspection.elf')
  body='\nDisassembly of section .flash.text:\n42001000: 008136 entry a1, 64\n'
  first=str(a)+':     file format elf32-xtensa-le\n'+body
  second=str(b)+':     file format elf32-xtensa-le\n'+body
  normalized=V.stable_inspection_heading(first,a,original)
  self.assertEqual(normalized,V.stable_inspection_heading(second,b,original))
  self.assertEqual(normalized.split('\n',1)[1],body)
  untouched=first+'\nreference '+str(a)
  self.assertTrue(V.stable_inspection_heading(untouched,a,original).endswith('reference '+str(a)))
  for bad in [body,first+first]:
   with self.assertRaises(ValueError):V.stable_inspection_heading(bad,a,original)
 def test_setup_dispatch_requires_event6_eight_bytes_buffer_and_wrapper(self):
  statements=[('l32r','a11, 100'),('movi.n','a8, 6'),('s8i','a2, a1, 36'),('s8i','a8, a1, 37'),
   ('movi.n','a12, 8'),('addi','a10, a1, 40'),('l32r','a8, 104'),('callx8','a8'),
   ('addi','a5, a1, 36'),('movi','a11, 1'),('or','a10, a5, a5'),('l32r','a8, 108'),('callx8','a8')]
  text='\n'.join('%x: 000000 %s %s'%(0x42000000+3*i,op,args) for i,(op,args) in enumerate(statements))
  edges=[dict(address=0x42000015,target=0x400011f4),dict(address=0x42000024,target=0x42001000)]
  with patch.object(V,'elf_bytes',return_value=struct.pack('<I',0x3fc00000)):
   proof=V.setup_dispatch_witness(text,edges,0x42001000,0x400011f4,0x3fc00000,b'ELF')
   self.assertEqual(proof['event_id'],6);self.assertEqual(proof['setup_bytes'],8)
   for bad in [text.replace('a8, 6','a8, 7'),text.replace('a12, 8','a12, 9'),
               text.replace('a10, a1, 40','a10, a1, 44'),text.replace('a11, 1','a11, 0'),
               text.replace('or a10, a5, a5','or a10, a2, a2')]:
    with self.assertRaises(ValueError):V.setup_dispatch_witness(bad,edges,0x42001000,0x400011f4,0x3fc00000,b'ELF')
   for wrong in [edges[:1],[dict(edges[0],target=0x42002000),edges[1]]]:
    with self.assertRaises(ValueError):V.setup_dispatch_witness(text,wrong,0x42001000,0x400011f4,0x3fc00000,b'ELF')
   with self.assertRaises(ValueError):V.setup_dispatch_witness(text,edges,0x42001000,0x400011f4,0x3fc00004,b'ELF')
 def test_call_decoder_requires_executable_edges(self):
  text='42001000: 000005 call8 42002000 <dcd_event_handler>\n42001003: 000005 j 42003000 <usb_observer::observe(dcd_event_t const*, bool)>\n'
  self.assertEqual([r['target'] for r in V.call_edges(text)],[0x42002000,0x42003000])
  for empty in ['<dcd_event_handler>\n','42001000: 000005 beqz a2, 42002000 <dcd_event_handler>\n']:
   self.assertEqual(V.call_edges(empty),[])
 def test_indirect_literal_call_decoder_and_register_clobber(self):
  with patch.object(V,'elf_bytes',return_value=struct.pack('<I',0x42002000)):
   text='42001000: 000021 l32r a8, 3c000010 <literal>\n42001003: 0000e0 callx8 a8\n'
   self.assertEqual(V.call_edges(text,b'ELF')[0]['target'],0x42002000)
   self.assertEqual(V.call_edges(text.replace('42001003:','42001002: 000012 movi a8, 0\n42001003:'),b'ELF'),[])
 def test_existing_static_dispatch_refusal_retained(self):
  pointers=''.join(' .rodata._ZL%d%s\n'%(len(n),n) for n in V.S.RESOURCES)
  obj='Disassembly of section .literal._ZL12handleStaticP21AsyncWebServerRequest:\n'+pointers+V.S.BYTE_SEND+'\nDisassembly of section .text._ZL12handleStaticP21AsyncWebServerRequest:\n'
  linked=V.S.BYTE_SEND+'\n'+'\n'.join('<'+n+'>' for n in V.S.RESOURCES)
  self.assertTrue(V.S.verify_dispatch_text(obj,linked)['byte_overload_observed'])
  with self.assertRaises(ValueError):V.S.verify_dispatch_text(obj.replace(V.S.BYTE_SEND,'AsyncWebServerRequest::send_P('),linked)
 def test_old_define_elf_is_not_observer(self):
  with self.assertRaisesRegex(ValueError,'Explicit observer compile selector'):V.observer_binding(ROOT.parent/'scratch/define-labels-release/build-v1')
 def test_actual_candidate_when_supplied(self):
  if CANDIDATE is None:self.skipTest('Final target ELF not built yet')
  proof=V.observer_binding(CANDIDATE);web=V.web_binding(CANDIDATE)
  self.assertTrue(proof['original_handler_called_once']);self.assertTrue(proof['early_bss_state'])
  self.assertTrue(proof['actual_setup_path_verified']);self.assertEqual(proof['setup_dispatch']['event_id'],6)
  self.assertEqual(proof['setup_dispatch']['setup_bytes'],8)
  self.assertLessEqual(proof['state_plus_callback_bytes'],2048);self.assertEqual(proof['classification'],'UNKNOWN')
  self.assertTrue(web['authenticated_before_single_snapshot'])

def main():
 global SOURCE,CANDIDATE
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);p.add_argument('--candidate-build',type=pathlib.Path);a=p.parse_args()
 SOURCE=a.source;CANDIDATE=a.candidate_build;assert not a.results.exists(),'Use fresh control evidence'
 stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Policy))
 out=dict(counts=dict(PASS=r.testsRun-len(r.failures)-len(r.errors)-len(r.skipped),FAIL=len(r.failures)+len(r.errors)),skipped=len(r.skipped),details=stream.getvalue(),source=str(SOURCE),test_sha256=V.sha(__file__),firmware_built=False,hardware=False)
 a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['counts']));return int(not r.wasSuccessful())
if __name__=='__main__':raise SystemExit(main())
