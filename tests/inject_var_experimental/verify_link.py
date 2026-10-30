#!/usr/bin/env python3
"""Pin-preserving source overrides for the isolated H1 experimental profile."""
import argparse, ast, hashlib, json, pathlib, subprocess, sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA='d8ab7a0d35efe18ac425bcada05d21ba7d0b84108caa18781661e678e0f1776e'
BUILD='ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1'

class FinalSources(ast.NodeTransformer):
    def __init__(self):self.edits=[]
    def visit_Constant(self,node):
        if not isinstance(node.value,str):return node
        pairs=[
          ("after.update({x['file']:x['sha256'] for x in timeout_pin['after']})", "after.update({x['file']:x['sha256'] for x in timeout_pin['after']});after.update({x['file']:x['sha256'] for x in json.loads((ROOT/'tests/inject_var_experimental/source-manifest.json').read_text())['after']})"),
          ('source_after.update({x["file"]:x["sha256"] for x in json.loads((ROOT/"tests/lock_wait_timeout/source-manifest.json").read_text())["after"]})', 'source_after.update({x["file"]:x["sha256"] for x in json.loads((ROOT/"tests/lock_wait_timeout/source-manifest.json").read_text())["after"]});source_after.update({x["file"]:x["sha256"] for x in json.loads((ROOT/"tests/inject_var_experimental/source-manifest.json").read_text())["after"]})'),
          ("    for row in pin['after']:assert hashlib.sha256((args.build_root/", "    timeout_after.update({x['file']:x['sha256'] for x in json.loads((ROOT/'tests/inject_var_experimental/source-manifest.json').read_text())['after']})\n    for row in pin['after']:assert hashlib.sha256((args.build_root/")]
        for index,(old,new) in enumerate(pairs):
            if index==2 and "timeout_after=" not in node.value:
                continue
            if old in node.value:
                assert node.value.count(old)==1
                node.value=node.value.replace(old,new);self.edits.append(index)
        return node
    def visit_Assign(self,node):
        if any(isinstance(t,ast.Name) and t.id=='BUILD_ID' for t in node.targets):node.value=ast.Constant(BUILD)
        if any(isinstance(t,ast.Name) and t.id=='text' for t in node.targets) and ast.unparse(node.value)=='parent.read_text()':
            node.value=ast.Call(func=ast.Name(id='ADAPT_V2_TEXT',ctx=ast.Load()),args=[node.value],keywords=[])
        return self.generic_visit(node)
    def visit_Assert(self,node):
        # The historical timeout pin must remain its ORIGINAL identity.
        if "pin['build_id'] == BUILD_ID" in ast.unparse(node):
            node=ast.parse(ast.unparse(node).replace("pin['build_id'] == BUILD_ID", "pin['build_id'] == 'ROUTEB-LOCK-WAIT-TIMEOUT-v1'")).body[0]
        return self.generic_visit(node)
    def visit_For(self,node):
        if ast.unparse(node.iter)=="pin['after']" and isinstance(node.target,ast.Name) and node.target.id=='r':
            assert len(node.body)==1 and isinstance(node.body[0],ast.Assert)
            assertion=ast.unparse(node.body[0]);assert assertion.endswith("== r['sha256']")
            node.body=[ast.parse(assertion.removesuffix("r['sha256']")+"FINAL_AFTER.get(r['file'], r['sha256'])").body[0]]
            self.edits.append(3)
        return self.generic_visit(node)

def adapt_v2_text(text):
    # New getter has a read-only local groups table with the function's name.
    # Match executable functions only; data symbols are not callable evidence.
    old="matches=[line for line in demangled.splitlines() if len(line.split(maxsplit=2))==3 and line.split(maxsplit=2)[2].startswith(prefix_name)]"
    new="matches=[line for line in demangled.splitlines() if len(line.split(maxsplit=2))==3 and line.split()[1] in ('T','t','W','w') and line.split(maxsplit=2)[2].startswith(prefix_name)]"
    assert text.count(old)==1
    return text.replace(old,new)

def main():
    parent=ROOT/'tests/lock_wait_timeout/verify_link.py'
    assert hashlib.sha256(parent.read_bytes()).hexdigest()==PARENT_SHA
    pin=json.loads((ROOT/'tests/inject_var_experimental/source-manifest.json').read_text())
    transformer=FinalSources();tree=transformer.visit(ast.parse(parent.read_text()));ast.fix_missing_locations(tree)
    assert sorted(transformer.edits)==[0,1,2,3],transformer.edits
    namespace={'__name__':'experimental_inject_parent','__file__':str(__file__),'FINAL_AFTER':{r['file']:r['sha256'] for r in pin['after']},'ADAPT_V2_TEXT':adapt_v2_text}
    exec(compile(tree,str(parent),'exec'),namespace);assert namespace['main']()==0
    parser=argparse.ArgumentParser();parser.add_argument('--build-root',type=pathlib.Path,required=True);parser.add_argument('--output',type=pathlib.Path,required=True);a=parser.parse_args()
    report=json.loads(a.output.read_text());sketch=a.build_root/'candidate/EvilDuckS3'
    assert pin['build_id']==BUILD and pin['required_flag']=='EVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1'
    assert pin['patch_sha256']==hashlib.sha256((ROOT/'tests/inject_var_experimental/application.patch').read_bytes()).hexdigest()
    assert pin['parent_prepare_sha256']==hashlib.sha256((ROOT/'tests/lock_wait_timeout/prepare_sources.py').read_bytes()).hexdigest()
    before={r['file'].removeprefix('EvilDuckS3/'):r['sha256'] for r in json.loads((ROOT/'docs/lock-wait-timeout-build.json').read_text())['source_inventory']}
    assert {r['file'] for r in pin['before']}=={r['file'] for r in pin['after']}=={'core.cpp','core.h','caps_trial.h'}
    for r in pin['before']:assert before[r['file']]==r['sha256']
    for r in pin['after']:assert hashlib.sha256((sketch/r['file']).read_bytes()).hexdigest()==r['sha256']
    for entry in json.loads((a.build_root/'build/compile_commands.json').read_text()):
        if pathlib.Path(entry['file']).is_relative_to(a.build_root/'build/sketch'):
            assert '-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1' in entry['arguments']
            assert '-fno-access-control' not in entry['arguments']
    elf=a.build_root/'build/EvilDuckS3.ino.elf';data=elf.read_bytes();assert BUILD.encode() in data
    for marker in (b'INJECT_VAR', b'$_RANDOM_LOWER_LETTER_KEYCODE', b'$_RANDOM_UPPER_LETTER_KEYCODE', b'$_RANDOM_CHAR_KEYCODE'):assert marker in data,marker
    prefix=str(report['link_command'][0]).rsplit('g++',1)[0]
    raw=subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True);dem=subprocess.check_output([prefix+'nm','-C','--defined-only',str(elf)],text=True)
    names={l.split()[0]:l.split(maxsplit=2)[2] for l in raw.splitlines() if len(l.split())==3};bodies={}
    for pattern in ('ds_preview::decodeExperimentalKeycodeH1(', 'ds_preview::Runtime::completeInstruction(', 'ds_preview::Runtime::evaluationStep(', 'native_b::Adapter::receive('):
        matches=[l for l in dem.splitlines() if len(l.split(maxsplit=2))==3 and l.split()[1] in ('T','t','W','w') and l.split(maxsplit=2)[2].startswith(pattern)]
        assert len(matches)==1,(pattern,matches)
        symbol=names[matches[0].split()[0]];body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+symbol,str(elf)],text=True);assert '<'+symbol+'>:' in body
        bodies[pattern]=subprocess.check_output([prefix+'c++filt'],input=body,text=True)
    assert 'ds_preview::decodeExperimentalKeycodeH1(' in bodies['ds_preview::Runtime::completeInstruction(']
    assert 'route_b::key(' in bodies['native_b::Adapter::receive(']
    report['inject_var_experimental_verified']=True;report['official_runtime_encoding_verified']=False
    report['inject_var_experimental_source_pin']=pin;report['inject_var_experimental_linked_functions']=bodies
    report['inject_var_link_adapter']={'parent_sha256':PARENT_SHA,'adapter_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'hash_override_sites':transformer.edits,'symbol_match_adaptation':'Executable symbols only; read-only getter groups table is not a function','inherited_safety_predicates_removed':0}
    report['profile']='EXPERIMENTAL H1 POLICY ONLY; NOT CANONICAL HAK5 COMPATIBILITY; NOT AUTHORIZED FOR INSTALLATION'
    a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS isolated H1 source/flag/decoder-to-KeyTap link and inherited USB/NVS/ownership/timeout guards')
    return 0
if __name__=='__main__':raise SystemExit(main())
