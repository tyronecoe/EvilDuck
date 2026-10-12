#!/usr/bin/env python3
"""Verify/download immutable Stage21 reference sources; never replace SDK/core files."""
import argparse, hashlib, json, sys, urllib.request
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
PIN=ROOT/'docs/stage21-reference-pin.json'
def verify(directory):
 pin=json.loads(PIN.read_text())
 for row in pin['files']:
  data=(Path(directory)/row['path']).read_bytes()
  if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:
   raise ValueError('Startup reference checksum mismatch')
 return pin
def main():
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
 g.add_argument('--prepare-dir',type=Path);g.add_argument('--verify-dir',type=Path);a=p.parse_args()
 if a.prepare_dir:
  dest=a.prepare_dir.resolve()
  if dest.exists() or dest==ROOT or ROOT in dest.parents:raise ValueError('New external reference directory required')
  pin=json.loads(PIN.read_text());dest.mkdir(parents=True)
  for row in pin['files']:
   if not row['url'].startswith('https://raw.githubusercontent.com/espressif/esp-idf/'+pin['commit']+'/'):raise ValueError('Unexpected reference URL')
   with urllib.request.urlopen(row['url'],timeout=30) as r:data=r.read()
   if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Downloaded source differs from pin')
   path=dest/row['path'];path.parent.mkdir(parents=True,exist_ok=True)
   with path.open('xb') as f:f.write(data)
  verify(dest)
 else:verify(a.verify_dir)
 print('PASS: exact source references verified; no SDK installation or hardware access')
if __name__=='__main__':
 try:main()
 except (ValueError,OSError) as e:sys.exit('FAIL: '+str(e))
