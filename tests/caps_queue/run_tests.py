import pathlib,sys,json,subprocess,argparse
sys.dont_write_bytecode=True
from prepare_sources import ROOT,B,prepare,native_sources,delta
H=B.H;A=B.A
saved=sys.modules['prepare_sources'];sys.modules['prepare_sources']=H
runner=H.load(ROOT/'tests/http_snapshot/run_tests.py','caps_http_runner');sys.modules['prepare_sources']=saved
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
s=prepare(a.build_dir/'sources');native_sources(s);cmd=runner.command(a.build_dir/'native',s,ROOT/'tests/caps_queue/test_main.cpp');A.delta(s);B.delta(s);delta(s)
for directory,name in [('http_snapshot','http'),('stop_ui','stop'),('led_return','led')]:
 text=(ROOT/'tests'/directory/'test_main.cpp').read_text().replace('int main(int argc,char**argv)','int historical_'+name+'_main(int argc,char**argv)');(s/(name+'_cases.inc')).write_text(text)
cmd[1:1]=['-I'+str(ROOT/'tests/caps_queue/mocks'),'-DEVILDUCK_LED_RETURN_TEST=1','-I'+str(ROOT/'tests/led_return/mocks')];cmd[cmd.index('-o'):cmd.index('-o')]=[str(s/'led_receiver.cpp')]
subprocess.run(cmd,check=True);rows=[]
for n in ['C%02d'%i for i in range(1,23)]+['L%02d'%i for i in range(1,20)]+['S%02d'%i for i in range(1,9)]+['H%02d'%i for i in range(1,19)]+['K%02d'%i for i in range(1,26)]+['W%02d'%i for i in range(1,34)]:
 r=runner.K.X.W.V.U.execute(a.build_dir/'native',n);rows.append(r);print(r['id'],r['status'],r['stderr'],flush=True)
out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,command=cmd,sanitizers='ASan/UBSan/leak detection',hardware=False,target_firmware_built=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
