"""Selected public compiler functions only; no browser, official runtime or HID."""
import argparse,hashlib,json,pathlib,re,subprocess
p=argparse.ArgumentParser();p.add_argument('--source',type=pathlib.Path,required=True);a=p.parse_args()
raw=a.source.read_bytes();assert hashlib.sha256(raw).hexdigest()=='18efc91b48d8ada4e7aaaaebe0218e9bbc360360eb81ac182a63c4db9c10eee7'
s=raw.decode();functions={}
for n in ['splitLine','getArgsFromLine','handleString','handleStringln','handleInlineString','handleInlineStringln']:
 m=re.search(r'^    function '+n+r'\([^\n]*\)\s*\{.*?^    }',s,re.M|re.S);assert m,n;functions[n]=m.group()
rx=[l.strip() for l in s.splitlines() if l.strip().startswith(('const inline_string_regex =','const inline_stringln_regex ='))];assert len(rx)==2
code='\n'.join(list(functions.values())+rx)+'''\nresult=cases.map(l=>{let ln=l.startsWith('STRINGLN'),matched=(ln?inline_stringln_regex:inline_string_regex).test(l);if(!matched)return {source:l,matched};try{let a=(ln?handleInlineStringln:handleInlineString)(l);return {source:l,matched,text:a.filter((x,i)=>i%2===0).join('')};}catch(e){return {source:l,matched,error:e.name};}});'''
names=['POWERSHELL','BASH','BATCH','PYTHON','HTML','RUBY','JAVASCRIPT'];cases=['STRING_'+x+' hello END_STRING' for x in names]+['STRINGLN_'+x+' hello END_STRINGLN' for x in names]+['STRING_PYTHON hello END_STRING extra END_STRING','STRING_PYTHON hello END_STRINGLN','STRING_PYTHON\thello\tEND_STRING','STRING_PYTHON hello END_STRING ','STRING_PYTHON hello END_STRINGx END_STRING']
runner="""const vm=require('vm');let d=JSON.parse(require('fs').readFileSync(0,'utf8'));let c={cases:d.cases,dLog(){},DS3(){},getBytesForKey(ch){return[ch]},defaultingHexWarning(){throw Error('unexpected')},throwError(m){throw Error(m)},handleEnter(){return['\\n','00']}};vm.createContext(c);vm.runInContext(d.code,c,{timeout:1000});process.stdout.write(JSON.stringify(c.result));"""
r=json.loads(subprocess.check_output(['node','-e',runner],input=json.dumps(dict(code=code,cases=cases)),text=True))
assert all(x.get('text')==('hello\n' if i>=7 else 'hello') for i,x in enumerate(r[:14]))
assert r[14]['text']=='hello extra END_STRING' and r[15]['matched'] is False and r[16]['error']=='TypeError' and r[17]['matched'] is False and r[18]['text']=='hellox END_STRING'
print(json.dumps(dict(status='PASS',positive_forms=14,edge_observations=5,source_sha256=hashlib.sha256(raw).hexdigest(),selected_function_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in functions.items()},regexes=rx,results=r,node_version=subprocess.check_output(['node','--version'],text=True).strip(),scope='Actual selected compiler functions; character mapping and Enter are stand-ins, not official runtime or HID report execution',hardware=False),indent=2))
