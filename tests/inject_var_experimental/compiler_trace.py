#!/usr/bin/env python3
"""Targeted public compiler assignment/copy handlers; no runtime, browser or HID."""
import argparse, hashlib, json, pathlib, re, subprocess
PAGE_SHA='18efc91b48d8ada4e7aaaaebe0218e9bbc360360eb81ac182a63c4db9c10eee7'
NAMES=['DS3','hexEncode','swapHex','decToHex','varExists','allocateVar','assignValue','getVarAddress','containsFunctionCall','isOperator','isVar','isReservedVar','isReservedConstant','isNumeric','isDecimal','isHex','formatHex','handleAssignment','handleInjectVar','handleExfilVar']

def balanced(source,start):
    depth=0;quote=None;escape=False;line=False;block=False;i=start
    while i<len(source):
        c=source[i];n=source[i+1:i+2]
        if line:
            if c=='\n':line=False
        elif block:
            if c=='*' and n=='/':block=False;i+=1
        elif quote:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c==quote:quote=None
        elif c in "\"'`":quote=c
        elif c=='/' and n=='/':line=True;i+=1
        elif c=='/' and n=='*':block=True;i+=1
        elif c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return i+1
        i+=1
    raise ValueError('Unbalanced declaration')

def compare_hypotheses(character, usage, modifier, observed_scalar=None):
    """Prediction comparison only; caller must separately establish observation provenance."""
    h1=(modifier << 8) | usage
    h2=(usage << 8) | modifier
    return dict(character=character, usage=usage, modifier=modifier,
                H1_prediction=h1, H2_prediction=h2, ASCII_prediction=ord(character),
                observation_supplied=observed_scalar is not None,
                matches=None if observed_scalar is None else dict(H1=observed_scalar==h1,H2=observed_scalar==h2,ASCII=observed_scalar==ord(character)),
                status='UNDERDETERMINED_NO_RUNTIME_OBSERVATION' if observed_scalar is None else 'CONDITIONAL_COMPARISON_REQUIRES_PROVENANCE',
                official_runtime_value=None)

def hypothesis_experiment():
    vectors=[compare_hypotheses(c,u,m) for c,u,m in [('a',4,0),('A',4,2),('Z',29,2),('0',39,0),('!',30,2),('#',32,2)]]
    checks=[]
    def check(name, value):
        assert value,name
        checks.append(dict(name=name,status='PASS',kind='algorithmic prediction check, not runtime validation'))
    check('independent A stroke yields distinct H1/H2 predictions',vectors[1]['H1_prediction']==0x0204 and vectors[1]['H2_prediction']==0x0402)
    check('independent a stroke yields distinct H1/H2 predictions',vectors[0]['H1_prediction']==0x0004 and vectors[0]['H2_prediction']==0x0400)
    check('all absent runtime observations remain underdetermined',all(v['status']=='UNDERDETERMINED_NO_RUNTIME_OBSERVATION' and v['matches'] is None and v['official_runtime_value'] is None for v in vectors))
    synthetic=compare_hypotheses('A',4,2,0x0402)
    check('synthetic counterexample would reject H1 without changing expectations',synthetic['matches']==dict(H1=False,H2=True,ASCII=False))
    check('synthetic H1 match would reject H2 for same US stroke',compare_hypotheses('A',4,2,0x0204)['matches']==dict(H1=True,H2=False,ASCII=False))
    return dict(vectors=vectors,algorithmic_checks=checks,counts=dict(PASS=len(checks),FAIL=0),synthetic_counterexample=dict(provenance='SYNTHETIC_ONLY_NOT_OFFICIAL',hypothetical_observed_scalar=0x0402,comparison=synthetic),language_cell_observation=dict(bytes='0402',character_label='LANG_a',has_runtime_scalar=False,conclusion='Cannot select H1/H2; forced-Shift serialized compiler cell, not observed lowercase getter value'),unparameterized_hypotheses=['layout-table index','tagged value','runtime case transform'],unparameterized_status='No defined scalar function; cannot compute discriminating values without a specific versioned contract',winner=None)

def main():
    p=argparse.ArgumentParser();p.add_argument('--page',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
    data=a.page.read_bytes();assert hashlib.sha256(data).hexdigest()==PAGE_SHA
    source=data.decode();declarations=[];identities=[]
    for name in NAMES:
        m=re.search(r'^[ \t]*function '+name+r'\s*\(',source,re.M);assert m,name
        end=balanced(source,source.index('{',m.start()));body=source[m.start():end];declarations.append(body)
        identities.append({'function':name,'first_line':source.count('\n',0,m.start())+1,'last_line':source.count('\n',0,end)+1,'sha256':hashlib.sha256(body.encode()).hexdigest()})
    for name in ['operatorMap','reservedVariables','reservedConstants']:
        m=re.search(r'^    const '+name+r' = \{',source,re.M);assert m
        end=balanced(source,source.index('{',m.start()));body=source[m.start():end]+';';declarations.append(body)
        identities.append({'data':name,'first_line':source.count('\n',0,m.start())+1,'last_line':source.count('\n',0,end)+1,'sha256':hashlib.sha256(body.encode()).hexdigest()})
    setup=r'''
var IDE_CONFIG={onlyallowds1:false};var DS3_DETECTED=false;
var varMap={},varValues=['VALUES'],nextAvailableVarAddress=1,oBB=[],requiresLangPack=false;
const operatorKeys=Object.keys(operatorMap),reservedVariablesList=Object.keys(reservedVariables),reservedConstantList=Object.keys(reservedConstants);
const requiresLangPackList=['$_RANDOM_LOWER_LETTER_KEYCODE','$_RANDOM_UPPER_LETTER_KEYCODE','$_RANDOM_LETTER_KEYCODE','$_RANDOM_NUMBER_KEYCODE','$_RANDOM_SPECIAL_KEYCODE','$_RANDOM_CHAR_KEYCODE'];
function dLog(){}function throwError(m){throw new Error(m)}function REGISTERS_TO_STRING(){}
function appendHexStringArray(x){oBB.push(...x)}
function reset(){varMap={};varValues=['VALUES'];nextAvailableVarAddress=1;oBB=[];requiresLangPack=false}
var checks=[];
function check(name,actual,expected){if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error(name+': '+JSON.stringify(actual)+' != '+JSON.stringify(expected));checks.push({name,actual,expected,status:'PASS'})}
'''
    checks=r'''
const properties=[['LOWER_LETTER','fa42'],['UPPER_LETTER','fb42'],['LETTER','ff42'],['NUMBER','fc42'],['SPECIAL','fd42'],['CHAR','fe42']];
for(const [group,selector] of properties){reset();let bytes=handleAssignment('VAR $ORIGINAL = $_RANDOM_'+group+'_KEYCODE').join('');check(group+' assignment uses reserved selector',bytes,'e8010001'+selector+'0000');check(group+' compiler placeholder is not sampled runtime value',[varValues[varMap['$ORIGINAL']],requiresLangPack],['0000',true])}
reset();let producer=handleAssignment('VAR $ORIGINAL = $_RANDOM_LOWER_LETTER_KEYCODE').join('');let copy=handleAssignment('VAR $COPY = $ORIGINAL').join('');let before=JSON.stringify(varValues);handleInjectVar('INJECT_VAR $COPY');handleInjectVar('INJECT_VAR $COPY');check('copy assignment references original register',copy,'e801000200010000');check('two injections reference copy register',oBB.join(''),'e9e90002e9e90002');check('compiler handlers do not mutate placeholders',JSON.stringify(varValues),before);let inject=oBB.join('');oBB=[];handleExfilVar('EXFIL $ORIGINAL');handleExfilVar('EXFIL $COPY');check('EXFIL variable references, not calibration of runtime framing',oBB.join(''),'f6e90001f6e90002');
reset();let literal=handleAssignment('VAR $K = 0x0204').join('');check('hex initializer gets separate constant register',literal,'e801000100020000');check('hex constant serialization vs variable placeholder',varValues,['VALUES','0000','0402']);
JSON.stringify({checks,counts:{PASS:checks.length,FAIL:0}})
'''
    program='\n'.join(declarations)+'\n'+setup+'\n'+checks
    driver="const vm=require('node:vm');let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>console.log(vm.runInNewContext(s,{}, {timeout:2000})));"
    r=subprocess.run(['node','-e',driver],input=program,text=True,capture_output=True,timeout=10)
    if r.returncode:raise RuntimeError(r.stderr)
    result=json.loads(r.stdout);result['hypothesis_comparison']=hypothesis_experiment();result.update(page_sha256=PAGE_SHA,encoder='5b4c1b5-271b6b-1690371896-STABLE',source_functions=identities,node=subprocess.check_output(['node','--version'],text=True).strip(),limitations=['Selected original compiler handlers only; helpers for append/logging/error/UI dependencies are mocks','No complete compiler pipeline, official runtime, bytecode interpreter, browser or HID execution','varValues are compiler placeholders/serialized constants; no generated runtime keycode observed','EXFIL opcode emission is not output-channel framing or runtime scalar evidence'],official_runtime_executed=False,official_runtime_value=None)
    assert not a.output.exists();a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'counts':result['counts'],'receipt':str(a.output)}))
if __name__=='__main__':main()
