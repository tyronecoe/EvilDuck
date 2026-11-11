#!/usr/bin/env python3
"""Offline fail-closed source/selection/predicate controls; never compile firmware."""
import argparse
import ast
import builtins
import hashlib
import importlib.util
import io
import json
import pathlib
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
B=load(HERE/'build_candidate.py','admission_controls_builder')
V=load(HERE/'verify_target.py','admission_controls_target')
R=load(HERE/'verify_release.py','admission_controls_release')
M=load(HERE/'prepare_sources.py','admission_controls_source')
SOURCE=None

class Controls(unittest.TestCase):
    def mutate(self,name,change):
        with tempfile.TemporaryDirectory(prefix='admission-source-refusal-') as folder:
            copy=pathlib.Path(folder)/'source';shutil.copytree(SOURCE,copy)
            path=copy/name;before=path.read_bytes();after=change(before)
            self.assertNotEqual(before,after);path.write_bytes(after)
            with self.assertRaises((ValueError,AssertionError)):V.verify_composed_source(copy)
    def test_exact201_scope_and_new_identity(self):
        proof=V.verify_composed_source(SOURCE)
        self.assertEqual(proof['source_files'],201)
        self.assertEqual(set(proof['changed_sources']),{'adapter.cpp','adapter.h','caps_trial.h'})
        self.assertEqual(proof['build_id'],B.BUILD_ID)
    def test_omitted_adapter_fix_refused(self):
        prior=ROOT.parent/'scratch/usb-os-observer-v2-release/build-v2/candidate/EvilDuckS3'
        for name in ['adapter.cpp','adapter.h']:
            self.mutate(name,lambda _,n=name:(prior/n).read_bytes())
    def test_old_build_identity_refused(self):
        self.mutate('caps_trial.h',lambda b:b.replace(B.BUILD_ID.encode(),V.OLD_BUILD_ID.encode(),1))
    def test_no_compiler_usb_or_dashboard_drift(self):
        for name in ['core.cpp','core.h','coordinator.cpp','hid_backend.cpp','webserver.cpp','webfiles.h','cli.cpp']:
            self.mutate(name,lambda b:b+b'\n')
    def test_exact_root_delta_manifest(self):
        root=M.B.pin();value=M.pin()
        self.assertEqual({r['file'] for r in root['after']},{'adapter.cpp','adapter.h'})
        self.assertEqual(len(root['unchanged']),199)
        self.assertEqual(len(value['after']),9)
        self.assertEqual(len(value['cumulative_h1_after']),10)
        self.assertEqual(root['parent_manifest_sha256'],V.sha(ROOT/'tests/usb_os_observer_v2_release/source-manifest.json'))
    def test_old_or_modified_parent_pins_refused(self):
        with tempfile.TemporaryDirectory(prefix='admission-builder-pin-') as folder:
            modified=pathlib.Path(folder)/'modified.py';modified.write_bytes(B.PARENT.read_bytes()+b'\n')
            with patch.object(B,'PARENT',modified):
                with self.assertRaises(AssertionError):B.parent_module()
    def test_pinned_parent_reused_under_active_hook_and_guard_still_runs(self):
        parent=B.parent_module();calls=[];original=parent.build_inputs
        def guard():
            calls.append('unchanged-parent-guard')
            return original()
        with patch.object(parent,'build_inputs',guard),patch.object(builtins,'compile',parent.flag_adapter):
            self.assertIs(B.parent_module(),parent)
            try:
                value=B.build_inputs()
            except AssertionError as error:
                # During development, the real inherited committed-source
                # guard must reject our uncommitted control/builder changes.
                self.assertEqual(str(error),'Commit the selected build checkpoint first')
            else:
                self.assertEqual(value['source_commit'],value['inherited_observer_v2_guard'] and
                    B.subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
        self.assertEqual(calls,['unchanged-parent-guard'])
    def test_full190_frozen_asserts_retained(self):
        ns,_=R.adapted_parent();value=M.pin();final={row['file']:row['sha256'] for row in value['cumulative_h1_after']}
        counts=[('h1_right_modifiers',23),('inject_var_experimental',21),('lock_wait_timeout',16),('source_text_v2',46),('lock_feedback',25),('caps_stop',59)]
        total=0
        for directory,expected in counts:
            path=ROOT/'tests'/directory/'verify_link.py';self.assertEqual(V.sha(path),ns['FROZEN'][directory])
            original=ast.parse(path.read_text());self.assertEqual(sum(isinstance(n,ast.Assert) for n in ast.walk(original)),expected)
            transformed=ns['FinalCandidateExpectations'](final).visit(original)
            transformed=ns['RuntimeIdentityExpectations'](original).visit(transformed)
            if directory=='h1_right_modifiers':
                handler=R.P.CompilerHandlerExpectations();transformed=handler.visit(transformed);self.assertEqual(len(handler.edits),2)
            self.assertEqual(sum(isinstance(n,ast.Assert) for n in ast.walk(transformed)),expected);total+=expected
        self.assertEqual(total,190)
        with self.assertRaises(AssertionError):ns['FinalCandidateExpectations']({k:v for k,v in final.items() if k!='adapter.cpp'})
    def test_target_adaptations_preserve_assert_and_require_counts(self):
        ns,evidence=V.adapted_parent();self.assertIn('admission_diagnostics',evidence)
        self.assertGreater(evidence['admission_diagnostics']['predicates_retained']['require_calls'],0)
        ns['parent_namespace']()
    def test_release_adaptations_preserve_assert_counts(self):
        _,evidence=R.adapted_parent()
        self.assertGreater(evidence['admission_diagnostics']['predicates_retained']['asserts'],0)
    def test_active_target_and_release_context_hash_new_wrappers(self):
        for module in [V,R]:
            namespace,evidence=module.adapted_parent()
            self.assertEqual(pathlib.Path(namespace['__file__']).resolve(),pathlib.Path(module.__file__).resolve())
            self.assertEqual(evidence['active_verifier_context']['build_id'],B.BUILD_ID)
            self.assertEqual(evidence['active_verifier_context']['parent_sha256'],module.PARENT_SHA)
    def test_nested_guard_paths_and_unchanged_profile(self):
        text,_=B.adapted_source('a'*40)
        self.assertEqual(text.count('tests/admission_diagnostics_release/prepare_sources.py'),4)
        self.assertIn('tests/admission_diagnostics_release/source-manifest.json',text)
        self.assertEqual(text.count("text=text.replace('lock_feedback','admission_diagnostics_release')"),2)
        self.assertIn('assert "--verify-existing" not in sys.argv',text)
        self.assertIn('inherited_safety_predicates_removed=0',text)
        self.assertIn("target_module.BUILD_ID == '"+B.BUILD_ID+"'",text)
    def probe(self,generated):
        C=load(ROOT/'tests/usb_os_observer_v2_release/test_verify_controls.py','admission_actual_nested_selector_probe')
        C.HERE=HERE
        return C._v2_probe_nested_selection(generated)
    def test_actual_nested_import_selects_new_preparer_and_verifier(self):
        text,_=B.adapted_source('a'*40)
        selected=self.probe(text)
        self.assertEqual(selected['preparer'],(HERE/'prepare_sources.py').resolve())
        self.assertEqual(selected['verifier'],(HERE/'verify_target.py').resolve())
        self.assertEqual(selected['verifier_globals'],selected['verifier'])
        self.assertEqual(selected['build_id'],B.BUILD_ID)
    def test_old_nested_selector_refused(self):
        text,_=B.adapted_source('a'*40)
        wrong=text.replace("text=text.replace('lock_feedback','admission_diagnostics_release')","text=text.replace('lock_feedback','usb_os_observer_v2_release')",1)
        with self.assertRaisesRegex(AssertionError,'Nested builder selected old preparer'):self.probe(wrong)
    def test_old_nested_verifier_refused(self):
        text,_=B.adapted_source('a'*40)
        wrong=text.replace("target_path = ROOT / 'tests/admission_diagnostics_release/verify_target.py'","target_path = ROOT / 'tests/usb_os_observer_v2_release/verify_target.py'",1)
        with self.assertRaises(AssertionError):self.probe(wrong)
    def test_committed_source_guard_excludes_only_postcompile_binding(self):
        tree=ast.parse((HERE/'build_candidate.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build_inputs')
        calls=[n for n in ast.walk(fn) if isinstance(n,ast.Call)]
        self.assertTrue(any(isinstance(n.func,ast.Attribute) and n.func.attr=='build_inputs' for n in calls))
        discard=[n for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=='discard']
        self.assertEqual(len(discard),1);self.assertEqual(discard[0].args[0].value,'tests/admission_diagnostics_package/release-binding.json')
        self.assertIn("['git','show',head+':'+name]",(HERE/'build_candidate.py').read_text())

def main():
    global SOURCE
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=pathlib.Path,required=True);parser.add_argument('--output',type=pathlib.Path,required=True);args=parser.parse_args();SOURCE=args.source
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    value=dict(status='PASS' if result.wasSuccessful() else 'FAIL',cases=result.testsRun,failures=len(result.failures),errors=len(result.errors),output=stream.getvalue(),source=str(SOURCE),runner_sha256=V.sha(__file__),hardware=False,target_build=False)
    args.output.write_text(json.dumps(value,indent=2)+'\n');print(stream.getvalue());return int(not result.wasSuccessful())
if __name__=='__main__':raise SystemExit(main())
