#!/usr/bin/env python3
"""Explicit one-action future-owner fixture. No source start, STOP, EDR1 or installer API."""
import argparse,getpass,json,os,pathlib,re,subprocess,time,urllib.request
BUILD='ROUTEB-LOCK-FEEDBACK-20261023-v1'
# Only direct Num/Caps actions; Scroll output is deliberately unavailable here.
COMMANDS={'WAIT_FOR_NUM_ON':(0,1,1),'WAIT_FOR_NUM_OFF':(1,1,0),'WAIT_FOR_NUM_CHANGE':(2,1,None),'WAIT_FOR_CAPS_ON':(3,2,1),'WAIT_FOR_CAPS_OFF':(4,2,0),'WAIT_FOR_CAPS_CHANGE':(5,2,None)}
def check_status(s,request,command):
 n,_,_=COMMANDS[command]
 return (s.get('snapshotKind')=='request-capture' and s.get('routeBRequestId')==str(request) and s.get('routeBOwned') is True and s.get('routeBWaiting') is True and type(s.get('routeBWaitCommand')) is int and s['routeBWaitCommand']==n and type(s.get('routeBWaitSession')) is int)
def act(status,identity,invoke,request,command,value,clock=time.monotonic,sleep=time.sleep):
 if command not in COMMANDS or type(value) is not int or value not in (0,1):raise ValueError('INVALID_ACTION')
 if COMMANDS[command][2] is not None and value!=COMMANDS[command][2]:raise ValueError('WRONG_TARGET')
 initial=identity()
 boot=initial.get('bootMarker')
 if not isinstance(boot,str) or not re.fullmatch('[0-9a-fA-F]{16}',boot):raise ValueError('UNKNOWN_BOOT')
 if initial.get('buildId')!=BUILD or initial.get('state')==1:raise ValueError('BUILD_OR_RECEIVER_NOT_SAFE')
 initial_session=initial.get('feedbackSession')
 until=clock()+30
 while clock()<until:
  s=status()
  if check_status(s,request,command):
   # Last bounded fresh read just before native invocation. A later STOP may race;
   # this host action cannot be made atomic with firmware execution ownership.
   again=status()
   if not check_status(again,request,command) or again['routeBWaitSession']!=s['routeBWaitSession']:raise ValueError('WAIT_CHANGED')
   i=identity()
   if i.get('bootMarker')!=boot or i.get('feedbackSession')!=initial_session or i.get('buildId')!=BUILD or type(i.get('state')) is not int or i['state']==1 or i.get('snapshotSessionCoherent') is not True or i.get('feedbackSession')!=s['routeBWaitSession'] or i.get('usbConfiguredSample') is not True or i.get('usbSuspendedSample') is not False:raise ValueError('BUILD_OR_RECEIVER_NOT_SAFE')
   return invoke(COMMANDS[command][1],value)
  if s.get('routeBRequestId')==str(request) and s.get('routeBOwned') is False:raise ValueError('REQUEST_ALREADY_TERMINAL')
  sleep(.1)
 raise ValueError('NO_MATCHING_WAIT_WITHIN_30_SECONDS')
def main():
 p=argparse.ArgumentParser();p.add_argument('--serial',required=True);p.add_argument('--request',type=int,required=True);p.add_argument('--command',choices=sorted(COMMANDS),required=True);p.add_argument('--value',type=int,choices=[0,1],required=True);p.add_argument('--host',default='192.168.4.1');a=p.parse_args()
 if not re.fullmatch('[A-Za-z0-9]{1,128}',a.serial) or a.request<1 or not re.fullmatch('[0-9.]{7,15}',a.host):raise ValueError('INVALID_IDENTITY')
 if os.uname().sysname!='Darwin':raise ValueError('NATIVE_MAC_REQUIRED')
 password=getpass.getpass('Dashboard password (not saved): ')
 if not password:raise ValueError('MISSING_PASSWORD')
 # Same existing dashboard password-header contract; no credentials in argv/receipt.
 token=base64.b64encode(('admin:'+password).encode()).decode()
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 def read(path):
  req=urllib.request.Request('http://'+a.host+path,headers={'X-Duck-Password':password})
  with opener.open(req,timeout=.5) as r:
   data=r.read(65537)
  if len(data)>65536:raise ValueError('RESPONSE_LIMIT')
  return json.loads(data)
 if input('Separate physical approval required. Type APPLY ONCE, then start only the reviewed wait fixture: ')!='APPLY ONCE':return 2
 helper=pathlib.Path(__file__).with_name('led-action-native')
 def invoke(usage,value):
  # No automatic retry; watchdog failure means restoration UNVERIFIED.
  return subprocess.run([str(helper),'--one-approved-action',a.serial,str(usage),str(value)],timeout=5,check=False).returncode
 return act(lambda:read('/status'),lambda:read('/led-test'),invoke,a.request,a.command,a.value)
if __name__=='__main__':raise SystemExit(main())
