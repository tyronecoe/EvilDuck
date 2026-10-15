#!/usr/bin/env python3
"""Compose exact immutable U then V patch in a new external tree only."""
import pathlib,sys,importlib.util,json,hashlib,subprocess,re
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prepare(out):
 out=pathlib.Path(out);assert not out.exists() and not out.resolve().is_relative_to(ROOT)
 m=json.loads((ROOT/'docs/stage28v-source-manifest.json').read_text())
 for x in m['inputs']+[m['patch']]+m.get('candidate_files',[]):assert sha(ROOT/x['file'])==x['sha256'],x['file']
 load(ROOT/'tests/stage28u/prepare_sources.py','immutable_u').prepare(out)
 for x in m['inputs']:(out/pathlib.Path(x['file']).name).write_bytes((ROOT/x['file']).read_bytes())
 subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(ROOT/m['patch']['file'])],cwd=out,check=True,capture_output=True)
 for x in m['outputs']:assert sha(out/x['file'])==x['sha256'],x['file']
 return out
# Token mask keeps offsets/physical lines, excludes braces in strings/comments.
def mask(s):return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:''.join('\n' if c=='\n' else ' ' for c in m[0]),s)
def region(s,pattern):
 z=mask(s);m=re.search(pattern,z);assert m,pattern;a=m.start();b=z.index('{',m.end()-1);depth=1;i=b+1
 while depth:
  if z[i]=='{':depth+=1
  if z[i]=='}':depth-=1
  i+=1
 return a,i
WEB_FUNCTIONS=['checkAuth','sendAuthRequired','isScriptFile','scriptBaseName','isSafeScriptName','parseScriptParam','wantsSdStorage','handleDeleteScript','handleRunScript','handleSaveSettings','onUpload','onFirmwareUpload','handleStop','handleFirmwareComplete','handleStatus','handleSetLed','handleSaveScript','handleSendLine','wsOut','onWsEvent']
def native_sources(out):
 # Replace only lower/platform definitions superseded by the actual modules.
 p=out/'platform.cpp';s=p.read_text()
 for n in ['storage','settings','spiffs','led']:
  a,b=region(s,r'namespace '+n+r'\s*\{');s=s[:a]+s[b:]
 s=s.replace('settings::reset();','/* actual settings fixture loads before execution */')
 p.write_text(s)
 s=(out/'webserver.cpp').read_text();pieces=[];rows=[]
 for n in WEB_FUNCTIONS:
  a,b=region(s,r'static (?:bool|void|String) '+n+r'\([^;{}]*\)\s*\{')
  line=s[:a].count('\n')+1;body=s[a:b];pieces.append('#line '+str(line)+' "'+str(out/'webserver.cpp')+'"\n'+body+'\n')
  rows.append(dict(symbol=n,line=line,sha256=hashlib.sha256(body.encode()).hexdigest()))
 (out/'web_handlers.inc').write_text('\n'.join(pieces));(out/'native-extraction.json').write_text(json.dumps(rows,indent=2)+'\n')
 return rows
if __name__=='__main__':prepare(pathlib.Path(sys.argv[1]))
