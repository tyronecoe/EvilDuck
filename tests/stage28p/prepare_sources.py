#!/usr/bin/env python3
"""Exact public inputs to fresh external native trees; no installed dependency use."""
import argparse,hashlib,json,pathlib,subprocess,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--reuse',type=pathlib.Path);p.add_argument('--mode',choices=['original','adapted','plain-platform'],required=True);a=p.parse_args()
assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
m=json.loads((ROOT/'docs/stage28p-source-and-boundary-manifest.json').read_text());rows=m['original_tinyusb_inputs']+m['new_inputs'];a.output.mkdir()
for row in rows:
 path=row.get('tree_file',row['file']);dst=a.output/path;dst.parent.mkdir(parents=True,exist_ok=True)
 if a.reuse:
  src=a.reuse/path;assert src.resolve()!=dst.resolve();data=src.read_bytes()
 else:data=urllib.request.urlopen(row['url'],timeout=30).read()
 assert hashlib.sha256(data).hexdigest()==row['sha256'],path
 dst.write_bytes(data)
if a.mode=='adapted':
 patch=ROOT/'tests/stage28p/native-io-adaptation.patch';assert hashlib.sha256(patch.read_bytes()).hexdigest()==m['patch_sha256']
 run=subprocess.run(['patch','--batch','--fuzz=0','--no-backup-if-mismatch','-p1','-i',str(patch)],cwd=a.output,capture_output=True,text=True)
 assert run.returncode==0 and 'offset' not in run.stdout and 'fuzz' not in run.stdout,run.stdout+run.stderr
 for row in m['adapted_files']:assert hashlib.sha256((a.output/row['file']).read_bytes()).hexdigest()==row['output_sha256']
elif a.mode=='plain-platform':
 # Only selected platform include is substituted. All common.c/driver bodies exact.
 f=a.output/'src/portable/synopsys/dwc2/dwc2_common.h';text=f.read_text();assert text.count('#include "dwc2_esp32.h"')==1;f.write_text(text.replace('#include "dwc2_esp32.h"','#include "stage28p_platform.h"'))
assert hashlib.sha256((a.output/'builder/dcd_dwc2.c').read_bytes()).hexdigest()==m['new_inputs'][-1]['sha256']
print('PASS fresh',a.mode,'native sources; builder DCD body byte-identical')
