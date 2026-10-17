import pathlib,sys,json,subprocess,argparse
sys.dont_write_bytecode=True
from prepare_sources import ROOT,H,A,prepare,native_sources,delta
saved=sys.modules['prepare_sources'];sys.modules['prepare_sources']=H
Hrun=H.load(ROOT/'tests/http_snapshot/run_tests.py','led_http_runner');sys.modules['prepare_sources']=saved
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists();a.build_dir.mkdir();s=prepare(a.build_dir/'sources');native_sources(s)
c=Hrun.command(a.build_dir/'native',s,ROOT/'tests/led_return/test_main.cpp');A.delta(s);delta(s)
for file,name in [('http_snapshot','http'),('stop_ui','stop')]:
 text=(ROOT/'tests'/file/'test_main.cpp').read_text().replace('int main(int argc,char**argv)','int historical_'+name+'_main(int argc,char**argv)');(s/(name+'_cases.inc')).write_text(text)
c[1:1]=['-DEVILDUCK_LED_RETURN_TEST=1','-I'+str(ROOT/'tests/led_return/mocks')];c[c.index('-o'):c.index('-o')]=[str(s/'led_receiver.cpp')]
subprocess.run(c,check=True);rows=[]
for n in ['L%02d'%i for i in range(1,20)]+['S%02d'%i for i in range(1,9)]+['H%02d'%i for i in range(1,19)]+['K%02d'%i for i in range(1,26)]+['W%02d'%i for i in range(1,34)]:
 r=Hrun.K.X.W.V.U.execute(a.build_dir/'native',n);rows.append(r);print(r['id'],r['status'],r['stderr'],flush=True)
out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,command=c,sanitizers='ASan/UBSan/leaks',hardware=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
