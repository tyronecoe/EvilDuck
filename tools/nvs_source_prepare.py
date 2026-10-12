#!/usr/bin/env python3
"""Fetch only pinned official source for host recovery tests; never replace an SDK."""
import argparse,hashlib,json,shutil,tempfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify(directory):
    pin=json.loads((ROOT/'docs/stage19-sdk-source-pin.json').read_text())
    for row in pin['files']:
        p=Path(directory)/row['path']
        if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Pinned SDK source mismatch: '+row['path'])
    return pin

def prepare(destination):
    destination=Path(destination)
    if destination.exists():raise ValueError('Refusing to overwrite source directory')
    pin=json.loads((ROOT/'docs/stage19-sdk-source-pin.json').read_text())
    with tempfile.TemporaryDirectory(prefix='evilduck-idf-source-') as t:
        t=Path(t)
        for row in pin['files']:
            url='https://raw.githubusercontent.com/espressif/esp-idf/'+pin['commit']+'/'+row['path']
            data=urllib.request.urlopen(url,timeout=60).read()
            if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('Downloaded source checksum mismatch')
            p=t/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        verify(t);shutil.copytree(t,destination)
    return pin
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--verify-only',action='store_true');a=p.parse_args()
    (verify if a.verify_only else prepare)(a.output)
    print('PASS: hash-verified host-test source only; installed SDK untouched')
