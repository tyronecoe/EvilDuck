#!/usr/bin/env python3
"""Pinned official generator for synthetic offline tests; no installation or devices."""
import argparse,hashlib,io,json,shutil,tempfile,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify(directory):
    pin=json.loads((ROOT/'docs/stage19-generator-pin.json').read_text())
    for row in pin['files']:
        p=Path(directory)/row['path']
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Generator source mismatch: '+row['path'])
    return pin

def prepare(destination):
    destination=Path(destination)
    if destination.exists():raise ValueError('Refusing to overwrite generator directory')
    pin=json.loads((ROOT/'docs/stage19-generator-pin.json').read_text())
    data=urllib.request.urlopen(pin['url'],timeout=60).read()
    if hashlib.sha256(data).hexdigest()!=pin['wheel_sha256']:raise ValueError('Generator wheel hash mismatch')
    with tempfile.TemporaryDirectory(prefix='evilduck-nvs-generator-') as t:
        t=Path(t)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for row in pin['files']:
                name=Path(row['path'])
                if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe wheel path')
                p=t/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.read(str(name)))
        verify(t);shutil.copytree(t,destination)
    return pin
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--verify-only',action='store_true');a=p.parse_args()
    (verify if a.verify_only else prepare)(a.output)
    print('PASS: hash-verified synthetic generator, no global install')
