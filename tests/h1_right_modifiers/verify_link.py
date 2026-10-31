#!/usr/bin/env python3
"""Add final right-modifier identities to the unchanged pinned H1 link checks."""
import argparse, ast, hashlib, json, pathlib, subprocess, sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
PARENT_SHA='6da2ddaad1800354a032193e78e6f1775da376e15c30ce77d170b0f6c87e02e4'
BUILD='ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1'

class FinalRightSources(ast.NodeTransformer):
    def __init__(self):self.edits=[]
    def visit_Constant(self,node):
        if not isinstance(node.value,str):return node
        pairs=[
          ("after.update({x['file']:x['sha256'] for x in json.loads((ROOT/'tests/inject_var_experimental/source-manifest.json').read_text())['after']})", "after.update({x['file']:x['sha256'] for x in json.loads((ROOT/'tests/h1_right_modifiers/source-manifest.json').read_text())['after']})"),
          ('source_after.update({x["file"]:x["sha256"] for x in json.loads((ROOT/"tests/inject_var_experimental/source-manifest.json").read_text())["after"]})', 'source_after.update({x["file"]:x["sha256"] for x in json.loads((ROOT/"tests/h1_right_modifiers/source-manifest.json").read_text())["after"]})'),
          ("    timeout_after.update({x['file']:x['sha256'] for x in json.loads((ROOT/'tests/inject_var_experimental/source-manifest.json').read_text())['after']})\n", "    timeout_after.update({x['file']:x['sha256'] for x in json.loads((ROOT/'tests/h1_right_modifiers/source-manifest.json').read_text())['after']})\n")]
        for i,(old,add) in enumerate(pairs):
            # The first expression is a substring of the third: exclude it there.
            if i==0 and 'timeout_after.update' in node.value:continue
            if old in node.value:
                assert node.value.count(old)==1
                node.value=node.value.replace(old,old+('\n' if i==2 else ';')+add);self.edits.append(i)
        return node
    def visit_Assign(self,node):
        if any(isinstance(t,ast.Name) and t.id=='BUILD' for t in node.targets):node.value=ast.Constant(BUILD)
        return self.generic_visit(node)
    def visit_Assert(self,node):
        text=ast.unparse(node)
        if "pin['build_id'] == BUILD" in text:
            node=ast.parse(text.replace("pin['build_id'] == BUILD", "pin['build_id'] == 'ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1'")).body[0]
        return self.generic_visit(node)
    def visit_For(self,node):
        if ast.unparse(node.iter)=="pin['after']" and isinstance(node.target,ast.Name) and node.target.id=='r':
            assert len(node.body)==1 and isinstance(node.body[0],ast.Assert)
            text=ast.unparse(node.body[0]);assert text.endswith("== r['sha256']")
            node.body=[ast.parse(text.removesuffix("r['sha256']")+"RIGHT_AFTER.get(r['file'], r['sha256'])").body[0]]
            self.edits.append(3)
        return self.generic_visit(node)

def main():
    parent=ROOT/'tests/inject_var_experimental/verify_link.py'
    assert hashlib.sha256(parent.read_bytes()).hexdigest()==PARENT_SHA
    pin=json.loads((ROOT/'tests/h1_right_modifiers/source-manifest.json').read_text())
    text=parent.read_text()
    old="'FINAL_AFTER':{r['file']:r['sha256'] for r in pin['after']}"
    assert text.count(old)==1
    text=text.replace(old,"'FINAL_AFTER':({r['file']:r['sha256'] for r in pin['after']} | RIGHT_AFTER)")
    transform=FinalRightSources();tree=transform.visit(ast.parse(text));ast.fix_missing_locations(tree)
    assert sorted(transform.edits)==[0,1,2,3],transform.edits
    ns={'__name__':'right_h1_parent_link','__file__':str(__file__),'RIGHT_AFTER':{r['file']:r['sha256'] for r in pin['after']}}
    exec(compile(tree,str(parent),'exec'),ns);assert ns['main']()==0
    p=argparse.ArgumentParser();p.add_argument('--build-root',required=True,type=pathlib.Path);p.add_argument('--output',required=True,type=pathlib.Path);a=p.parse_args()
    r=json.loads(a.output.read_text());sketch=a.build_root/'candidate/EvilDuckS3'
    assert pin['build_id']==BUILD and pin['required_flag']=='EVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1'
    assert pin['parent_prepare_sha256']==hashlib.sha256((ROOT/'tests/inject_var_experimental/prepare_sources.py').read_bytes()).hexdigest()
    assert pin['patch_sha256']==hashlib.sha256((ROOT/'tests/h1_right_modifiers/application.patch').read_bytes()).hexdigest()
    old_inventory={v['file'].removeprefix('EvilDuckS3/'):v['sha256'] for v in json.loads((ROOT/'docs/inject-var-experimental-build.json').read_text())['source_inventory']}
    assert {v['file'] for v in pin['before']}=={v['file'] for v in pin['after']}=={'shortcut_keys.h','caps_trial.h'}
    for v in pin['before']:assert old_inventory[v['file']]==v['sha256']
    for v in pin['after']:assert hashlib.sha256((sketch/v['file']).read_bytes()).hexdigest()==v['sha256']
    # Crucially, all implementation sources apart from the two reviewed headers
    # retain the old H1 identity, including decoder, adapter, scheduler and backend.
    for name,expected in old_inventory.items():
        if name not in {'shortcut_keys.h','caps_trial.h'}:
            assert hashlib.sha256((sketch/name).read_bytes()).hexdigest()==expected,name
    entries=json.loads((a.build_root/'build/compile_commands.json').read_text())
    for e in entries:
        if pathlib.Path(e['file']).is_relative_to(a.build_root/'build/sketch'):
            assert '-DEVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1' in e['arguments']
            assert '-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1' in e['arguments']
            assert '-fno-access-control' not in e['arguments']
    elf=a.build_root/'build/EvilDuckS3.ino.elf';data=elf.read_bytes()
    assert BUILD.encode() in data
    for token in ('RCTRL','RSHIFT','RALT','RGUI'):assert token.encode()+b'\0' in data,token
    prefix=str(r['link_command'][0]).rsplit('g++',1)[0]
    dem=subprocess.check_output([prefix+'nm','-C','--defined-only',str(elf)],text=True)
    raw=subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True)
    symbols={x.split()[0]:x.split(maxsplit=2)[2] for x in raw.splitlines() if len(x.split())==3}
    bodies={}
    for pattern in ('ds_shortcut::modifier(', 'ds_preview::Compiler::statement(', 'native_b::Adapter::receive(', 'hid_backend::beginReport(', 'hid_backend::hold(', 'hid_backend::release('):
        matches=[x for x in dem.splitlines() if len(x.split(maxsplit=2))==3 and x.split()[1] in ('T','t','W','w') and x.split(maxsplit=2)[2].startswith(pattern)]
        assert len(matches)==1,(pattern,matches)
        symbol=symbols[matches[0].split()[0]]
        body=subprocess.check_output([prefix+'objdump','-d','--disassemble='+symbol,str(elf)],text=True)
        assert '<'+symbol+'>:' in body
        bodies[pattern]=subprocess.check_output([prefix+'c++filt'],input=body,text=True)
    assert 'ds_shortcut::modifier(' in bodies['ds_preview::Compiler::statement(']
    assert 'route_b::key(' in bodies['native_b::Adapter::receive(']
    # Source + compiled-source equality and actual target disassembly establish
    # the new parsing and unchanged backend boundary; native tests check bytes.
    r['right_modifiers_verified']=True
    r['right_modifiers_source_pin']=pin
    r['right_modifiers_linked_functions']=bodies
    r['right_modifiers_link_adapter']=dict(parent='tests/inject_var_experimental/verify_link.py',parent_sha256=PARENT_SHA,adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),hash_override_sites=transform.edits,inherited_safety_predicates_removed=0,build_id=BUILD)
    r['inject_var_link_adapter']['execution']='Pinned historical H1 source adapted by right-modifier wrapper; actual wrapper identity is recorded in adapter_sha256'
    r['profile']='RIGHT MODIFIERS H1 EXPERIMENTAL REVIEW ONLY; PHYSICAL ACCEPTANCE PENDING'
    a.output.write_text(json.dumps(r,indent=2)+'\n')
    print('PASS linked right-side source modifiers; unchanged H1 decoder/ownership/backend and inherited USB/NVS/SDK guards')
    return 0
if __name__=='__main__':raise SystemExit(main())
