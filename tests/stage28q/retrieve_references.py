#!/usr/bin/env python3
"""Retrieve only official manifest references into a fresh external directory."""
import argparse,hashlib,json,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir()
m=json.loads((ROOT/'docs/stage28q-source-and-model-manifest.json').read_text())
for row in m['references']:
 data=urllib.request.urlopen(row['url'],timeout=60).read();assert len(data)==row['size'] and hashlib.sha256(data).hexdigest()==row['sha256'], 'Reference changed/unavailable; fail closed: '+row['file']
 (a.output/row['file']).write_bytes(data)
print('PASS exact official references; no SDK install or device access')
