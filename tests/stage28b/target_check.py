#!/usr/bin/env python3
"""Compile preview objects only using the frozen build's pinned target flags. No firmware."""
import argparse,hashlib,json,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from patched_core import check_sources
p=argparse.ArgumentParser();p.add_argument('--baseline-build',type=Path,required=True);p.add_argument('--original-core',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
dependency_pin=check_sources(a.original_core)
if a.output_dir.exists():raise ValueError('Fresh external object output required')
a.output_dir.mkdir()
baseline=json.loads((a.baseline_build/'stage16-link-provenance.json').read_text());check_sources(Path(baseline['core']),patched=True);entries=json.loads((a.baseline_build/'compile_commands.json').read_text());entry=next(e for e in entries if Path(e['file']).name=='settings.cpp');compiler=Path(entry['arguments'][0]);digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if digest(compiler)!=baseline['compiler_sha256']:raise ValueError('Compiler pin mismatch')
sdk=a.original_core.parents[2]/'tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3'
for path,key in [(sdk/'lib/libnvs_flash.a','sdk_nvs_archive_sha256'),(sdk/'qio_qspi/include/sdkconfig.h','sdk_config_sha256')]:
 if digest(path)!=baseline['patched_core_pin'][key]:raise ValueError('SDK identity mismatch')
sources=[ROOT/'language_preview/core.cpp',a.output_dir/'sizes.cpp']
sources[1].write_text('#include "'+str(ROOT/'language_preview/core.h')+'"\nextern "C" const unsigned preview_sizes[]={sizeof(ds_preview::Program),sizeof(ds_preview::Runtime),sizeof(ds_preview::Event),sizeof(ds_preview::Instruction),sizeof(ds_preview::Continuation),sizeof(ds_preview::CallFrame),sizeof(ds_preview::ExprToken),sizeof(ds_preview::TextCursor)};\n')
commands=[]
for source in sources:
 cmd=list(entry['arguments']);cmd[cmd.index(entry['file'])]=str(source);cmd[cmd.index('-o')+1]=str(a.output_dir/(source.stem+'.o'));cmd+=['-fstack-usage','-Wall','-Wextra','-Werror','-Wno-misleading-indentation'];subprocess.run(cmd,cwd=entry['directory'],check=True);commands.append(cmd)
# Actual installed compiler uses the common xtensa-esp-elf tool names.
name=compiler.name.removesuffix('g++') if hasattr(compiler.name,'removesuffix') else compiler.name[:-3]
tool=lambda suffix:str(compiler.parent/(name+suffix))
subprocess.run([tool('objcopy'),'--dump-section','.rodata.preview_sizes='+str(a.output_dir/'type-sizes.raw'),str(a.output_dir/'sizes.o')],check=True)
sizes=struct.unpack('<8I',(a.output_dir/'type-sizes.raw').read_bytes());usage=[]
for file in a.output_dir.glob('*.su'):
 for line in file.read_text().splitlines():
  symbol,count,kind=line.rsplit('\t',2);usage.append(dict(symbol=symbol,bytes=int(count),qualifier=kind))
size_output=subprocess.run([tool('size'),'-A',str(a.output_dir/'core.o')],capture_output=True,text=True,check=True).stdout
undefined=subprocess.run([tool('nm'),'-u',str(a.output_dir/'core.o')],capture_output=True,text=True,check=True).stdout
report=dict(dependency_pin=dependency_pin,verified_patched_core_tree_sha256=dependency_pin['patched_tree_sha256'],sdk_nvs_archive_sha256=digest(sdk/'lib/libnvs_flash.a'),sdk_config_sha256=digest(sdk/'qio_qspi/include/sdkconfig.h'),status='PASS',scope='Xtensa target object compilation; not a linked preview firmware or hardware execution',compiler_sha256=digest(compiler),source_sha256=digest(sources[0]),header_sha256=digest(ROOT/'language_preview/core.h'),metadata_dump_bytes=32,object_sha256=digest(a.output_dir/'core.o'),target_sizes=dict(Program=sizes[0],Runtime=sizes[1],Event=sizes[2],Instruction=sizes[3],Continuation=sizes[4],CallFrame=sizes[5],ExprToken=sizes[6],TextCursor=sizes[7]),stack_estimates=usage,section_sizes=size_output,undefined_symbols=undefined,commands=commands,production_firmware_changed=False,flash_authorized=False)
report['selected_sections']={k:0 for k in ['text','literal','rodata','data','bss']}
for line in size_output.splitlines():
 fields=line.split()
 if len(fields)==3 and fields[1].isdigit():
  for key in report['selected_sections']:
   if fields[0]=='.'+key or fields[0].startswith('.'+key+'.'):report['selected_sections'][key]+=int(fields[1])
(a.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS target object compilation:',report['target_sizes'])
