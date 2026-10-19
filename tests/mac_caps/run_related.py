#!/usr/bin/env python3
"""Relevant unchanged backend/diagnostic cases on the patched composition."""
import pathlib,sys,json,argparse,subprocess,os
sys.dont_write_bytecode=True
from prepare_sources import ROOT,load,sha
K=load(ROOT/'tests/stage28t/run_tests.py','related_t')
p=argparse.ArgumentParser();p.add_argument('--native-results',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
r=json.loads(a.native_results.read_text());cmd=r['command'];s=next(pathlib.Path(x).parent for x in cmd if x.endswith('/core.cpp'))
pins={}
for name in ['http-snapshot-source-manifest.json','stop-ui-source-manifest.json','led-return-source-manifest.json','caps-queue-source-manifest.json','led-feedback-source-manifest.json','caps-duration-source-manifest.json','mac-caps-source-manifest.json']:
 p=json.loads((ROOT/'docs'/name).read_text());pins.update({r['file']:r['sha256'] for r in p['after']+p.get('additions',[])})
for name,h in pins.items():assert sha(s/name)==h
rows=[];commands=[]
for stage,ids in [('stage28t',[i for i in range(1,48) if i!=34]),('stage28x',[i for i in range(1,20) if i not in (13,15)])]:
 text=(ROOT/'tests'/stage/'test_main.cpp').read_text()
 if stage=='stage28t':text+='\nuint32_t esp_random(){return 0;}\n'
 else:text=text.replace('../stage28w/test_main.cpp',str(ROOT/'tests/stage28w/test_main.cpp'))
 main=s/('related-'+stage+'.cpp');main.write_text(text);c=[x.replace(str(ROOT/'tests/mac_caps/test_main.cpp'),str(main)) for x in cmd];c[c.index('-o')+1]=str(a.build_dir/stage);commands.append(c);subprocess.run(c,check=True)
 for i in ids:
  n=('T' if stage=='stage28t' else 'X')+'%02d'%i;v=K.execute(a.build_dir/stage,n);rows.append(v);print(n,v['status'],v['stderr'],flush=True)
out=dict(counts={k:sum(x['status']==k for x in rows) for k in ['PASS','FAIL']},assertions=sum(x['assertions'] for x in rows),results=rows,commands=commands,not_run=['T34 Linux-thread identity mismatch; K25 uses RTOS identity','X13/X15 assume old 1024-byte diagnostic response/record; H15 tests new bound'],sanitizers='ASan/UBSan/leaks',hardware=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
