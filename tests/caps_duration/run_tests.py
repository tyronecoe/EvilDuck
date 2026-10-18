import pathlib,sys,json,subprocess,argparse
sys.dont_write_bytecode=True
from prepare_sources import ROOT,B as F,prepare,native_sources,delta
C=F.B
B=C.B
H=B.H;A=B.A
saved=sys.modules['prepare_sources'];sys.modules['prepare_sources']=H
runner=H.load(ROOT/'tests/http_snapshot/run_tests.py','caps_http_runner');sys.modules['prepare_sources']=saved
p=argparse.ArgumentParser();p.add_argument('--core',type=pathlib.Path,required=True);p.add_argument('--build-dir',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.build_dir.exists() and not a.results.exists();a.build_dir.mkdir()
s=prepare(a.build_dir/'sources');native_sources(s);cmd=runner.command(a.build_dir/'native',s,ROOT/'tests/caps_duration/test_main.cpp');A.delta(s);B.delta(s);C.delta(s);F.delta(s);delta(s)
for directory,name in [('led_feedback','feedback'),('caps_queue','caps'),('http_snapshot','http'),('stop_ui','stop'),('led_return','led')]:
 text=(ROOT/'tests'/directory/'test_main.cpp').read_text().replace('int main(int argc,char**argv)','int historical_'+name+'_main(int argc,char**argv)');(s/(name+'_cases.inc')).write_text(text.replace('LED-FEEDBACK-BOUNDARY-', 'CAPS-DURATION-') if name=='feedback' else text)
cmd[1:1]=['-I'+str(ROOT/'tests/caps_queue/mocks'),'-DEVILDUCK_LED_RETURN_TEST=1','-I'+str(ROOT/'tests/led_return/mocks')];cmd[cmd.index('-o'):cmd.index('-o')]=[str(s/'led_receiver.cpp'),str(s/'feedback_diag.cpp'),str(s/'caps_trial.cpp')]
core=a.core
sys.path.insert(0,str(ROOT/'tools'));from feedback_core import check_sources
check_sources(core,True)
coretext=(core/'libraries/USB/src/USBHID.cpp').read_text()
def body(marker):
 a=coretext.index(marker);b=coretext.index('{',a);depth=1;end=b+1
 while depth:depth+=(coretext[end]=='{')-(coretext[end]=='}');end+=1
 return coretext[a:end]
(s/'routing_slice.inc').write_text('\n'.join(body(m) for m in ['USBHIDDevice *tinyusb_get_device_by_report_id(','static bool tinyusb_on_set_feature(','void tud_hid_set_report_cb(','void tud_hid_report_complete_cb(']))
usbtext=(core/'cores/esp32/USB.cpp').read_text()
def usbbody(marker):
 a=usbtext.index(marker);b=usbtext.index('{',a);depth=1;end=b+1
 while depth:depth+=(usbtext[end]=='{')-(usbtext[end]=='}');end+=1
 return usbtext[a:end]
(s/'lifecycle_slice.inc').write_text('\n'.join(usbbody(m) for m in ['void tud_mount_cb(','void tud_umount_cb(','void tud_suspend_cb(','void tud_resume_cb(']))
subprocess.run(cmd,check=True);rows=[]
for n in ['E%02d'%i for i in range(1,29)]+['D%02d'%i for i in range(1,23)]+['C%02d'%i for i in range(1,23)]+['L%02d'%i for i in range(1,20)]+['S%02d'%i for i in range(1,9)]+['H%02d'%i for i in range(1,19)]+['K%02d'%i for i in range(1,26)]+['W%02d'%i for i in range(1,34)]:
 r=runner.K.X.W.V.U.execute(a.build_dir/'native',n);rows.append(r);print(r['id'],r['status'],r['stderr'],flush=True)
out=dict(counts={k:sum(r['status']==k for r in rows) for k in ['PASS','FAIL']},assertions=sum(r['assertions'] for r in rows),results=rows,command=cmd,sanitizers='ASan/UBSan/leak detection',hardware=False,target_firmware_built=False);a.results.write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(bool(out['counts']['FAIL']))
