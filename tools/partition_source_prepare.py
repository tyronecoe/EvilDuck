#!/usr/bin/env python3
"""Fetch checksum-pinned official source for host experiments only; never install an SDK."""
import argparse,hashlib,json,shutil,tempfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def prepare(destination):
    destination=Path(destination).resolve()
    if destination.exists() or destination==ROOT or ROOT in destination.parents:raise ValueError('Use a new external source directory')
    records=json.loads((ROOT/'docs/stage20-partition-reference.json').read_text())
    with tempfile.TemporaryDirectory(prefix='evilduck-partition-reference-') as t:
        t=Path(t)
        for r in records:
            data=urllib.request.urlopen(r['url'],timeout=60).read()
            if hashlib.sha256(data).hexdigest()!=r['sha256']:raise ValueError('Reference checksum mismatch')
            (t/Path(r['url']).name).write_bytes(data)
        shutil.copytree(t,destination)
    return records
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();prepare(a.output)
    print('PASS: pinned host reference source prepared; installed SDK unchanged')
