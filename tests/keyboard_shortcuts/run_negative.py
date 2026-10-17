#!/usr/bin/env python3
"""Drop the real compiler modifier field in a disposable copy; oracle must fail."""
import pathlib,sys,json,argparse,subprocess,os
sys.dont_write_bytecode=True
from prepare_sources import ROOT,sha
p=argparse.ArgumentParser();p.add_argument('--bridge-results',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir();r=json.loads(a.bridge_results.read_text());cmd=list(r['command']);i=next(i for i,f in enumerate(cmd) if f.endswith('/core.cpp'));f=pathlib.Path(cmd[i]);pin=json.loads((ROOT/'docs/keyboard-shortcuts-source-manifest.json').read_text());assert sha(f)==next(x['sha256'] for x in pin['after'] if x['file']=='core.cpp');text=f.read_text();assert text.count('event_={EventType::KeyTap,ins.target,ins.symbol}')==1
n=a.build_dir/'core.cpp';n.write_text(text.replace('event_={EventType::KeyTap,ins.target,ins.symbol}','event_={EventType::KeyTap,ins.target,0}'));cmd[i]=str(n);cmd[cmd.index('-o')+1]=str(a.build_dir/'native');subprocess.run(cmd,check=True)
v=subprocess.run([str(a.build_dir/'native'),'B01'],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'));assert v.returncode==1 and 'command report' in v.stderr,(v.returncode,v.stderr)
a.results.write_text(json.dumps(dict(status='EXPECTED_REJECTION',fault='real compiler drops modifier field',exit=v.returncode,stdout=v.stdout,stderr=v.stderr,command=cmd,original_sha256=sha(f),mutated_sha256=sha(n),hardware=False),indent=2)+'\n');print('PASS negative control rejected dropped modifiers')
