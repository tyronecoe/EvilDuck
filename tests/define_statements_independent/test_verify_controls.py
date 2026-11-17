"""Focused behavioral controls; never consumes auxiliary compiler allowance."""
import argparse,ast,copy,io,json,pathlib,subprocess,tempfile,types,unittest
from unittest.mock import patch
import measure_reference as M
import verify_existing as V
class Controls(unittest.TestCase):
 def test_01_authentic_candidate(self):self.assertEqual(M.authenticate()['source_commit'],M.COMMIT)
 def test_02_candidate_real_stack_and_recursion(self):
  self.proof=V.stack_evidence();self.assertEqual(self.proof['max_implementation_depth'],2)
 def stack_reject(self,transform):
  proof=V.stack_evidence();frames=M.parser().stack_rows(M.BUILD/'build/sketch/core.cpp.su');text=transform(proof['disassembly'])
  with self.assertRaises(ValueError):V.validate_stack(frames,text,0x4200bc0c)
 def test_03_missing_guard(self):self.stack_reject(lambda t:t.replace('bnez.n\ta4, 4200c814','nop'))
 def test_04_wrong_recursive_argument(self):self.stack_reject(lambda t:t.replace('movi\ta12, 1','movi\ta12, 0'))
 def test_05_ambiguous_self_call(self):
  def mutate(t):return t+'\n'+next(l for l in t.splitlines() if 'call8' in l and '<'+V.NEW+'>' in l)
  self.stack_reject(mutate)
 def test_06_wrong_prologue(self):self.stack_reject(lambda t:t.replace('entry\ta1, 0x160','entry\ta1, 0x150'))
 def test_07_capacity_positive_and_negatives(self):
  before=dict(constant_cell_bytes=24,constant_slots=16,constant_value_bytes=64,name_offset=0,value_offset=24,constant_bytes=88,compiler_bytes=3800)
  after=dict(before,constant_cell_bytes=32,value_offset=32,constant_bytes=96,compiler_bytes=3928);m=M.parser();m.validate_capacity(before,after)
  for k,value in [('constant_cell_bytes',31),('constant_slots',17),('constant_value_bytes',65),('name_offset',1),('value_offset',31),('constant_bytes',97),('compiler_bytes',4097)]:
   with self.subTest(k=k),self.assertRaises(ValueError):m.validate_capacity(before,dict(after,**{k:value}))
 def test_08_missing_cache_never_compiles(self):
  with tempfile.TemporaryDirectory() as d,patch.object(M.subprocess,'run',side_effect=AssertionError('No subprocess allowed')):
   with self.assertRaisesRegex(ValueError,'Missing measurement'):M.read_cache(pathlib.Path(d),'candidate')
 def test_09_verification_denies_compiler_and_linker(self):
  with V.no_compilation():
   for cmd in [['xtensa-esp32s3-elf-g++','-c','a.cpp'],['xtensa-esp32s3-elf-ld','x.o']]:
    with self.assertRaises(ValueError):subprocess.run(cmd)
 def test_10_changed_cache_refused(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'candidate').mkdir();M.dump(p/'candidate/measurement.json',dict(inputs={'stale':True}))
   with patch.object(M,'frozen_measurement_file',return_value=p/'candidate/measurement.json'),patch.object(M,'cache_inputs',return_value={'current':True}),self.assertRaisesRegex(ValueError,'Stale'):M.read_cache(p,'candidate')
 def test_11_actual_signature_binding_and_refusals(self):
  v=M.load(M.ROOT/'tests/define_statements_release/verify_target.py','controls_target');d,_=V.signature_functions(v);self.assertEqual(d.core_binding(M.BUILD)['linked_symbols'][0]['name'],V.NEW)
  original=d.S.symbols
  for mode in ['absent','old','duplicate','empty','clone']:
   def mutate(text):
    rows=copy.deepcopy(original(text));items=[r for r in rows if r['name']==V.NEW]
    if mode=='absent':return [r for r in rows if r['name']!=V.NEW]
    for r in items:
     if mode=='old':r['name']=V.OLD
     if mode=='empty':r['size']=0
     if mode=='clone':r['name']+=' [clone .isra.0]'
    if mode=='duplicate':rows+=copy.deepcopy(items)
    return rows
   with patch.object(d.S,'symbols',side_effect=mutate),self.assertRaises(ValueError):d.core_binding(M.BUILD)
 def test_12_compiler_invocation_cap(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)
   for i in [0,1]:M.dump(p/('compiler-invocation-'+str(i)+'.json'),{'attempt':i})
   with patch.object(M,'identities',return_value={}),self.assertRaisesRegex(ValueError,'exhausted'):M.create(p,'candidate')
 def test_13_wrong_candidate_binding(self):
  v=M.load(M.ROOT/'tests/define_statements_release/verify_target.py','wrong_binding_control');d,_=V.signature_functions(v)
  with tempfile.TemporaryDirectory() as f:
   p=pathlib.Path(f);(p/'build').mkdir();(p/'candidate').mkdir();(p/'candidate/EvilDuckS3').symlink_to(M.BUILD/'candidate/EvilDuckS3',target_is_directory=True)
   for n in ['report.json','build/compile_commands.json']:(p/n).write_bytes((M.BUILD/n).read_bytes())
   with self.assertRaisesRegex(ValueError,'Compiled REPEAT core differs'):d.core_binding(p)
class ProvenanceControls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  M.authenticate()
  cls.binding=json.loads((M.BLOCKED_EVIDENCE/'verification/target.json').read_text())
  cls.attestation=V.derive_attestation(M.BUILD,cls.binding)
  cls.block=V.generated_provenance_block()
  cls.code=compile(cls.block,'actual-generated-release-provenance-controls','exec')
  cls.committed=cls.binding['committed_source_provenance']
 def execute(self,value):
  namespace=dict(build_root=M.BUILD,binding_after=self.binding,sha=M.sha,
   target_module=types.SimpleNamespace(verify_input_manifest=lambda root:self.committed))
  # Only substitute the supplied record. Every original assertion and the new
  # provenance-separation check execute from the actual adapted release block.
  with patch.object(V,'derive_attestation',return_value=value):
   exec(self.code,namespace)
  return namespace
 def reject(self,change,message):
  value=copy.deepcopy(self.attestation);change(value)
  with self.assertRaisesRegex((AssertionError,ValueError),message):self.execute(value)
 def test_01_actual_complete_predicate_accepts_derived_record(self):
  result=self.execute(copy.deepcopy(self.attestation))
  self.assertEqual(result['source_info']['source_commit'],M.COMMIT)
  self.assertEqual(sum(isinstance(n,ast.Assert) for n in ast.walk(self.block)),5)
 def test_02_wrong_manifest_hash(self):self.reject(lambda v:v.update(build_inputs_sha256='0'*64),'Wrong committed-input identity')
 def test_03_inventory_digest_is_not_outer_hash(self):self.reject(lambda v:v.update(build_inputs_sha256=v['files_sha256']),'Wrong committed-input identity')
 def test_04_wrong_source_revision(self):self.reject(lambda v:v.update(source_commit='0'*40),'Wrong committed source revision')
 def test_05_wrong_verifier_identity(self):self.reject(lambda v:v['verification_provenance'].update(verifier_identity_sha256=M.COMMIT),'Independent verifier identity mismatch')
 def test_06_verifier_digest_is_not_build_revision(self):self.reject(lambda v:v['verification_provenance'].update(build_source_commit=v['verification_provenance']['verifier_identity_sha256']),'Build/verifier provenance conflated')
 def test_07_outer_hash_is_not_inventory_digest(self):self.reject(lambda v:v.update(files_sha256=v['build_inputs_sha256']),'Inventory digest substituted')
 def test_08_supplement_identity_is_not_manifest_hash(self):self.reject(lambda v:v.update(build_inputs_sha256=V.identity_digest(v)),'Wrong committed-input identity')
 def test_09_new_record_is_not_builder_metadata(self):self.reject(lambda v:v.update(produced_by_original_builder=True),'misattributed')
 def test_10_overlay_and_clean_compile_are_still_required(self):
  self.reject(lambda v:v.update(overlay_calls=0),'Default overlay/clean build evidence missing')
  self.reject(lambda v:v.update(clean_compile=False),'Default overlay/clean build evidence missing')
 def test_11_wrong_actual_target_binding(self):self.reject(lambda v:v.update(usb_observer_target_binding={}), 'Target binding differs')
 def test_12_old_measurements_new_reader_no_compiler(self):
  directory=pathlib.Path('/workspace/scratch/define-independent-v1-authenticated')
  with V.no_compilation():
   for label in ['reference','candidate']:
    row=M.read_cache(directory,label)
    self.assertNotEqual(row['inputs']['auth']['code'],M.code_ids())
    self.assertEqual(row['inputs']['auth']['code'],json.loads((directory/'authentication.json').read_text())['code'])
 def test_13_modified_cache_receipt_rejected(self):
  with tempfile.TemporaryDirectory() as directory:
   root=pathlib.Path(directory);(root/'candidate').mkdir()
   (root/'candidate/measurement.json').write_text('{}\n')
   with V.no_compilation(),self.assertRaisesRegex(ValueError,'Preserved measurement changed'):M.read_cache(root,'candidate')
 def test_14_proof_of_source_commit_is_still_required(self):self.reject(lambda v:v.update(source_commit_contains_changes=False),'Missing committed implementation proof')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--provenance-only',action='store_true');a=p.parse_args();M.require(not a.output.exists(),'Keep original controls');s=io.StringIO()
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(ProvenanceControls)
 if a.provenance_only:
  suite.addTests(Controls(name) for name in ['test_08_missing_cache_never_compiles','test_09_verification_denies_compiler_and_linker','test_10_changed_cache_refused'])
 else:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
 r=unittest.TextTestRunner(stream=s,verbosity=2,failfast=True).run(suite)
 M.dump(a.output,dict(status='PASS' if r.wasSuccessful() else 'BLOCKED',scope='provenance/cache only' if a.provenance_only else 'all independent controls',groups_executed=r.testsRun,failures=len(r.failures),errors=len(r.errors),output=s.getvalue(),runtime_assertion_total='not emitted; not inferred',code=M.code_ids(),auxiliary_compilations=0))
 print(s.getvalue());raise SystemExit(not r.wasSuccessful())
