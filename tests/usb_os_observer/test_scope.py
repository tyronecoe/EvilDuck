#!/usr/bin/env python3
"""Composition/privacy scope controls only; never a target build or USB run."""
import argparse,hashlib,importlib.util,json,pathlib,shutil,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
HERE=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=pathlib.Path,required=True);p.add_argument('--candidate',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists()
 spec=importlib.util.spec_from_file_location('observer_scope',HERE/'prepare_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 results=[];assertions=0
 def check(value,message):
  nonlocal assertions
  assertions+=1
  if not value:raise AssertionError(message)
 def group(name,fn):
  try:fn();results.append({'id':name,'status':'PASS'})
  except Exception as e:results.append({'id':name,'status':'FAIL','diagnostic':type(e).__name__+': '+str(e)})
 def composition():
  old=m.B.verify_final(a.baseline);new=m.verify_final(a.candidate);check(len(old)==len(new)==201,'exact201sourcecount');d={r['file']:r['sha256'] for r in old};e={r['file']:r['sha256'] for r in new};check({n for n in d if d[n]!=e[n]}=={'EvilDuckS3/hid_backend.cpp','EvilDuckS3/hid_backend.h'},'onlytwoobserverbackendfileschanged')
 group('OS01',composition)
 def preservation():
  cpp=(a.candidate/'hid_backend.cpp').read_text();old=(a.baseline/'hid_backend.cpp').read_text();start=cpp.index('// Observation is ready before Arduino app_main');end=cpp.index('namespace feedback_diag {',start);cpp=cpp[:start]+cpp[end:];cpp=cpp.replace('  usb_observer::service(millis(),mounted);\n','',1);check(cpp==old,'existingbackendexactafterobserverblockandservicehookremoved');h=(a.candidate/'hid_backend.h').read_text();check(h[:h.index('// Capture-only USB request metadata.')].rstrip()==(a.baseline/'hid_backend.h').read_text().rstrip(),'allpriorpublicbackendAPIsunchanged')
 group('OS02',preservation)
 def replay():
  with tempfile.TemporaryDirectory() as d:
   q=pathlib.Path(d)/'s';shutil.copytree(a.baseline,q);m.delta(q);check(m.inventory(q)==m.inventory(a.candidate),'zero-fuzzreplay');
   try:m.delta(q)
   except AssertionError:check(True,'duplicateoverlayrefused')
   else:check(False,'duplicateoverlayaccepted')
 group('OS03',replay)
 def omissions():
  for name in ['hid_backend.cpp','hid_backend.h']:
   with tempfile.TemporaryDirectory() as d:
    q=pathlib.Path(d)/'s';shutil.copytree(a.candidate,q);shutil.copyfile(a.baseline/name,q/name)
    try:m.verify_final(q)
    except AssertionError:check(True,'partialoverlayrefused')
    else:check(False,'partialoverlayaccepted')
 group('OS04',omissions)
 def extra():
  with tempfile.TemporaryDirectory() as d:
   q=pathlib.Path(d)/'s';shutil.copytree(a.candidate,q);(q/'unreviewed.cpp').write_text('bad')
   try:m.verify_final(q)
   except AssertionError:check(True,'unexpectedsourcefilefailsclosed')
   else:check(False,'unexpectedsourcefileaccepted')
  with tempfile.TemporaryDirectory() as d:
   q=pathlib.Path(d)/'s';shutil.copytree(a.candidate,q);f=q/'core.cpp';f.unlink();f.symlink_to(a.candidate/'core.cpp')
   try:m.verify_final(q)
   except (AssertionError,ValueError):check(True,'symlinkrefused')
   else:check(False,'symlinkaccepted')
 group('OS05',extra)
 def callback():
  s=(a.candidate/'hid_backend.cpp').read_text();body=s[s.index('__attribute__((noinline)) void observe('):s.index('void service(uint32_t',s.index('__attribute__((noinline)) void observe('))];check('sizeof(tusb_control_request_t)==8' in s,'SDKsetupsizeguard');check('event->setup_received' in body and 'event->bus_reset.speed' in body,'onlyselectedunionmembers');check('event->xfer_complete' not in s and 'event->func_call' not in s and 'event->sof' not in s,'unrelatedunionsnotread');check(body.index('ordinaryEvent(event->event_id)')<body.index('CaptureGuard guard'),'otherDCDactivityfastignoredbeforelock');check('__real_dcd_event_handler(event,inIsr);' in s and s.count('__real_dcd_event_handler(event,inIsr);')==1,'originalforwardonce');check(s.index('extern "C" void* evilduck_hid_keyboard_identity')<s.index('CaptureState captureState{};'),'priorconstructorlabelorderingpreserved')
 group('OS06',callback)
 def bounds():
  h=(a.candidate/'hid_backend.h').read_text();s=(a.candidate/'hid_backend.cpp').read_text();check('MaxRecords=64' in h and 'WindowMs=5000' in h,'exactcapacityandwindow');check('sizeof(CaptureState)+sizeof(captureMux)<=2048' in s,'separatestatebudgetguard');check('if(v.state!=State::Capturing)return;' in s,'closedwindowsignorelatertraffic');check('v.generation==UINT32_MAX' in s and 'State::Exhausted' in s,'generationexhaustionguard');check('$_EVILDUCK_USB_OS' not in (a.candidate/'core.cpp').read_text(),'noclassificationgetterorparseraddition')
 group('OS07',bounds)
 def categories():
  s=(a.candidate/'hid_backend.cpp').read_text();h=(a.candidate/'hid_backend.h').read_text()
  check('unsupportedReasons=0' in h and 'unsupported=0' in h,'explicitboundedunsupportedfields')
  check('v.state=v.unsupportedReasons?State::Unsupported:' in s,'unsupportedcannotbecomplete')
  check('DCD_EVENT_XFER_COMPLETE||id==USBD_EVENT_FUNC_CALL' in s,'ordinaryeventfastpathisdeclared')
  check('excludedCdcHeader(b)' in s and 'unsupported(1)' in s and 'unsupported(2)' in s and 'unsupported(4)' in s,'setupandunknownDCDcategoriesexplicit')
 group('OS08',categories)
 value={'status':'PASS' if all(r['status']=='PASS' for r in results) else 'FAIL','counts':{k:sum(r['status']==k for r in results) for k in ['PASS','FAIL']},'assertions':assertions,'results':results,'source_manifest_sha256':sha(HERE/'source-manifest.json'),'baseline':str(a.baseline),'candidate':str(a.candidate),'inventory':m.verify_final(a.candidate),'firmware_built':False,'hardware_access':False,'hid_output':False};a.results.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value[k] for k in ['status','counts','assertions']}));return int(value['status']!='PASS')
if __name__=='__main__':raise SystemExit(main())
