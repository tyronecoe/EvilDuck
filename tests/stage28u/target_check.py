#!/usr/bin/env python3
"""Pinned Xtensa compile-only candidate check. Never invokes a linker."""
import pathlib,sys,json,hashlib,subprocess,argparse,struct,importlib.util
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from patched_core import check_sources
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline-build',type=pathlib.Path,required=True);p.add_argument('--output-dir',type=pathlib.Path,required=True);a=p.parse_args()
 assert not a.output_dir.exists() and not a.output_dir.resolve().is_relative_to(ROOT);a.output_dir.mkdir(parents=True)
 baseline=json.loads((a.baseline_build/'stage16-link-provenance.json').read_text());pin=check_sources(pathlib.Path(baseline['core']),True)
 entry=next(e for e in json.loads((a.baseline_build/'compile_commands.json').read_text()) if pathlib.Path(e['file']).name=='settings.cpp')
 compiler=pathlib.Path(entry['arguments'][0]);assert sha(compiler)==baseline['compiler_sha256']
 spec=importlib.util.spec_from_file_location('prepare_u',ROOT/'tests/stage28u/prepare_sources.py');prep=importlib.util.module_from_spec(spec);spec.loader.exec_module(prep);scratch=prep.prepare(a.output_dir/'sources')
 metadata=a.output_dir/'layout.cpp';metadata.write_text('#include "'+str(ROOT/'tests/stage28u/coordinator.cpp')+'"\nextern "C" const unsigned route_u_sizes[]={sizeof(route_u::pub),sizeof(route_u::adapter),sizeof(route_u::file),sizeof(ds_preview::Program),sizeof(ds_preview::CompileSession),sizeof(ds_preview::Runtime),sizeof(u_platform::Gate),sizeof(backend_b::Scope),sizeof(route_u::Status)};\n')
 sources=[scratch/n for n in ['com.cpp','hid_backend.cpp','duckscript.cpp','cli.cpp','storage.cpp','attackmode.cpp','keyboard_locale.cpp','webserver.cpp','EvilDuckS3.ino']]+[ROOT/'tests/stage28u'/n for n in ['adapter.cpp','file_source.cpp','coordinator.cpp']]+[ROOT/'language_preview/core.cpp',metadata]
 commands=[];rows=[]
 for source in sources:
  out=a.output_dir/(source.stem+'.o');cmd=list(entry['arguments']);cmd[cmd.index(entry['file'])]=str(source);cmd[cmd.index('-o')+1]=str(out)
  cmd=[x for x in cmd if x!='-w'];cmd[1:1]=['-x','c++','-I'+str(scratch),'-I'+str(ROOT/'tests/stage28u'),'-I'+str(ROOT/'language_preview'),'-DEVILDUCK_PORTABLE_ROUTE_B','-fstack-usage','-Wall','-Wextra','-Werror','-Wno-misleading-indentation']
  assert '-c' in cmd and not any(x in cmd for x in ['-shared','-Wl,']);commands.append(cmd)
  run=subprocess.run(cmd,cwd=entry['directory'],capture_output=True,text=True);rows.append(dict(source=str(source),source_sha256=sha(source),exit=run.returncode,stdout=run.stdout,stderr=run.stderr,object_sha256=sha(out) if out.exists() else None))
 prefix=compiler.name[:-3];tool=lambda n:str(compiler.parent/(prefix+n));symbols={};sections={}
 for source in sources:
  obj=a.output_dir/(source.stem+'.o')
  if obj.exists():
   symbols[source.stem]=subprocess.check_output([tool('nm'),'-C',str(obj)],text=True)
   sections[source.stem]=subprocess.check_output([tool('size'),'-A',str(obj)],text=True)
 layout=None;raw=a.output_dir/'layout.raw'
 if (a.output_dir/'layout.o').exists():
  subprocess.run([tool('objcopy'),'--dump-section','.rodata.route_u_sizes='+str(raw),str(a.output_dir/'layout.o')],check=True)
  layout=dict(zip(['Publication','Adapter','FileSource','Program_nested','CompileSession_nested','Runtime_nested','Gate','Scope','Status'],struct.unpack('<9I',raw.read_bytes())))
 frames=[]
 for f in a.output_dir.glob('*.su'):
  for line in f.read_text().splitlines():
   name,bytes_,kind=line.rsplit('\t',2);frames.append(dict(symbol=name,bytes=int(bytes_),qualifier=kind))
 forbidden=[n for n,t in symbols.items() if any(x in t for x in ['std::thread','__emutls','_ZTH'])]
 report=dict(status='PASS' if all(x['exit']==0 for x in rows) and not forbidden else 'FAIL',scope='actual target declarations and candidate objects only; no linked firmware or target execution',sources=rows,commands=commands,compiler_sha256=sha(compiler),compiler_version=subprocess.check_output([str(compiler),'--version'],text=True).splitlines()[0],pin=pin,layout=layout,frames=frames,symbols=symbols,sections=sections,forbidden_host_thread_symbols=forbidden,firmware=False,hardware=False)
 (a.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],layout);return report['status']!='PASS'
if __name__=='__main__':raise SystemExit(main())
