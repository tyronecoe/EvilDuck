#!/usr/bin/env python3
"""Exact full-composition and capture/privacy boundary controls; no device/build."""
import argparse,hashlib,importlib.util,json,pathlib,shutil,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[2];HERE=pathlib.Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=pathlib.Path,required=True);p.add_argument('--candidate',type=pathlib.Path,required=True);p.add_argument('--results',type=pathlib.Path,required=True);a=p.parse_args();assert not a.results.exists()
 sp=importlib.util.spec_from_file_location('v2_scope',HERE/'prepare_sources.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);rows=[];count=0
 def check(v,message):
  nonlocal count
  count+=1
  if not v:raise AssertionError(message)
 def group(name,fn):
  try:fn();rows.append(dict(id=name,status='PASS'))
  except Exception as e:rows.append(dict(id=name,status='FAIL',diagnostic=str(e)))
 def exact():
  x=m.B.verify_final(a.baseline);y=m.verify_final(a.candidate);check(len(x)==len(y)==201,'full201');old={r['file']:r['sha256'] for r in x};new={r['file']:r['sha256'] for r in y};check({n for n in old if old[n]!=new[n]}=={'EvilDuckS3/hid_backend.cpp','EvilDuckS3/hid_backend.h'},'only2functionalbackendfiles')
 group('VS01',exact)
 def preserve():
  old=(a.baseline/'hid_backend.cpp').read_text();new=(a.candidate/'hid_backend.cpp').read_text();anchor='// Observation is ready before Arduino app_main';stop='namespace feedback_diag {'
  a0=old.index(anchor);b0=old.index(stop,a0);a1=new.index(anchor);b1=new.index(stop,a1);new=new[:a1]+old[a0:b0]+new[b1:]
  new=new.replace('  const uint32_t observationGeneration=usb_observer::sampleGeneration();\n','',1).replace('usb_observer::service(usb_observer::clockMs(),mounted,observationGeneration);','usb_observer::service(millis(),mounted);',1)
  check(new==old,'keyboard/backendlogicbyteequaloutsidedeclaredobserverdelta');h=(a.candidate/'hid_backend.h').read_text();o=(a.baseline/'hid_backend.h').read_text();anchor='// Capture-only USB request metadata';check(h[:h.index(anchor)]==o[:o.index(anchor)],'allpreviouspublicHIDAPIexact')
 group('VS02',preserve)
 def replay():
  with tempfile.TemporaryDirectory() as f:
   q=pathlib.Path(f)/'s';shutil.copytree(a.baseline,q);m.delta(q);check(m.inventory(q)==m.inventory(a.candidate),'zero-fuzzreplayexact')
   try:m.delta(q)
   except AssertionError:check(True,'duplicateoverlayrefused')
   else:check(False,'duplicateoverlayaccepted')
 group('VS03',replay)
 def omit():
  for name in ['hid_backend.cpp','hid_backend.h']:
   with tempfile.TemporaryDirectory() as f:
    q=pathlib.Path(f)/'s';shutil.copytree(a.candidate,q);shutil.copyfile(a.baseline/name,q/name)
    try:m.verify_final(q)
    except AssertionError:check(True,'missingoverlayrefused')
    else:check(False,'missingoverlayaccepted')
 group('VS04',omit)
 def unreviewed():
  for name in ['core.cpp','webserver.cpp','USBIdentity.h']:
   if not (a.candidate/name).exists():continue
   with tempfile.TemporaryDirectory() as f:
    q=pathlib.Path(f)/'s';shutil.copytree(a.candidate,q);file=q/name;file.write_bytes(file.read_bytes()+b'\n')
    try:m.verify_final(q)
    except AssertionError:check(True,'unrelatedsourcechangefailsclosed')
    else:check(False,'unrelatedsourcechangeaccepted')
 group('VS05',unreviewed)
 def unexpected():
  with tempfile.TemporaryDirectory() as f:
   q=pathlib.Path(f)/'s';shutil.copytree(a.candidate,q);(q/'extra.cpp').write_text('bad')
   try:m.verify_final(q)
   except AssertionError:check(True,'extra source refused')
   else:check(False,'extra source accepted')
  with tempfile.TemporaryDirectory() as f:
   q=pathlib.Path(f)/'s';shutil.copytree(a.candidate,q);(q/'core.cpp').unlink();(q/'core.cpp').symlink_to(a.candidate/'core.cpp')
   try:m.verify_final(q)
   except (AssertionError,ValueError):check(True,'symlinkrefused')
   else:check(False,'symlinkaccepted')
 group('VS06',unexpected)
 def callback():
  s=(a.candidate/'hid_backend.cpp').read_text();body=s[s.index('__attribute__((noinline)) void observe('):s.index('uint32_t sampleGeneration()',s.index('__attribute__((noinline)) void observe('))]
  check(body.index('ordinaryEvent(event->event_id)')<body.index('CaptureGuard guard'),'ordinaryeventfastpathbeforelockclock')
  check('event->xfer_complete' not in s and 'event->sof' not in s and 'event->func_call' not in s,'unusedunionneverread')
  check(s.count('__real_dcd_event_handler(event,inIsr);')==1,'exactoriginalforwardonce')
  check('esp_timer_get_time()' in s and 'setClockForTest' in s,'sameSDKclockwithhostinjection')
  check('v.windowClosed&&(!v.tail.started||v.tail.closed)' in body,'tailclosurestopsrequestprocessing')
 group('VS07',callback)
 def boundaries():
  s=(a.candidate/'hid_backend.cpp').read_text();h=(a.candidate/'hid_backend.h').read_text()
  check('MaxRecords=64' in h and 'WindowMs=5000,TailMs=5000' in h,'finiteoriginalandtailbounds')
  check('sizeof(CaptureState)+sizeof(captureMux)<=2048' in s,'dedicatedstatebudgetunchanged')
  check('elapsed>=WindowMs' in s and 'elapsed>=TotalMs' in s,'callbackclockhardgates')
  check('if(!coherent)return;' in s,'mismatchedgenerationdoesnotapplytimerorconfig')
  check('v.state==State::Complete&&!configured' not in s,'no historicalstate downgrade')
  check('$_EVILDUCK_USB_OS' not in (a.candidate/'core.cpp').read_text(),'no classifier getter')
 group('VS08',boundaries)
 def raw():
  s=(a.candidate/'hid_backend.cpp').read_text();check('Phase::Prefix' in s and 'Phase::Tail' in s,'witnessphaseexplicit')
  check('sameHeader(v.firstUnsupported.record,b,port)' in s,'distinctheaderignoresorderandtime')
  check('firstConfigurationKnown' in s and 'b[0]==0&&b[1]==9' in s,'configurationrequestobservednotassumedaccepted')
  check('v.tail.firstConfiguredKnown' in s and 'elapsed<TotalMs' in s,'lateSDKsamplesseparatebounded')
 group('VS09',raw)
 sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();out=dict(status='PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL',counts={x:sum(y['status']==x for y in rows) for x in ['PASS','FAIL']},assertions=count,results=rows,source_manifest_sha256=sha(HERE/'source-manifest.json'),baseline=str(a.baseline),candidate=str(a.candidate),full_source_inventory=m.verify_final(a.candidate),firmware_built=False,hardware_access=False,real_hid=False);a.results.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['status','counts','assertions']}));return int(out['status']!='PASS')
if __name__=='__main__':raise SystemExit(main())
