#!/usr/bin/env python3
"""Visible fake-phrase-only evdev test. Never records general keys or sends data."""
import argparse,os,select,struct,time,re,stat
PHRASE='EVILDUCK TEST 123'
# Linux input-event-codes.h, press events only; main-row ASCII subset.
KEYS={18:'E',47:'V',23:'I',38:'L',32:'D',22:'U',46:'C',37:'K',57:' ',20:'T',31:'S',2:'1',3:'2',4:'3'}
EVENT=struct.Struct('@llHHI')
class Detector:
 def __init__(self):self.matched=0;self.found=False
 def key(self,code,value=1):
  if value!=1 or self.found:return
  c=KEYS.get(code,'')
  self.matched=self.matched+1 if c==PHRASE[self.matched] else int(c=='E')
  if self.matched==len(PHRASE):self.found=True;self.matched=0
 def result(self):return PHRASE if self.found else ''
def main():
 p=argparse.ArgumentParser();p.add_argument('device',help='Owner-selected /dev/input/eventN; normal read permission required');a=p.parse_args()
 print('VISIBLE FAKE-PHRASE evdev diagnostic. No device opened yet. Only EVILDUCK TEST 123 can be retained. Type START, then manually type it in a second ordinary editor. Ctrl-C stops, 60-second limit. No network or persistence.')
 if input()!='START':return 2
 if not re.fullmatch(r'/dev/input/event[0-9]+',a.device):print('Only an owner-selected evdev path is permitted.');return 2
 try:fd=os.open(a.device,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC)
 except OSError as e:print('Capture unavailable/permission denied:',e.__class__.__name__);return 3
 try:character=stat.S_ISCHR(os.fstat(fd).st_mode)
 except OSError:os.close(fd);print('Input metadata failed; no capture.');return 3
 if not character:os.close(fd);print('Not a character input device.');return 2
 detector=Detector();pending=b'';deadline=time.monotonic()+60
 try:
  while time.monotonic()<deadline and not detector.found:
   if not select.select([fd],[],[],0.1)[0]:continue
   chunk=os.read(fd,EVENT.size*16)
   if not chunk:print('Input stream closed; result unavailable.');return 3
   pending+=chunk
   while len(pending)>=EVENT.size:
    _,_,kind,code,value=EVENT.unpack(pending[:EVENT.size]);pending=pending[EVENT.size:]
    if kind==1:detector.key(code,value)
 except KeyboardInterrupt:print('Stopped by operator.')
 except OSError:print('Input read failed; capture result unavailable.');return 3
 finally:os.close(fd)
 if detector.found:print('FAKE PHRASE OBSERVED:',detector.result());return 0
 print('No fake match. Not proof of security-product prevention.');return 4
if __name__=='__main__':raise SystemExit(main())
