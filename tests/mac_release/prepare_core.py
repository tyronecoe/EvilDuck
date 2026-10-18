#!/usr/bin/env python3
"""Explicit additive archive profile. Disposable copy only; no global install."""
import argparse,json,pathlib,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import archive_core
p=argparse.ArgumentParser();
for flag in ['archive','core','destination','user']:p.add_argument('--'+flag,type=pathlib.Path,required=True)
a=p.parse_args();pin=json.loads((ROOT/'docs/mac-release-dependency-pin.json').read_text());assert archive_core.sha(a.archive)==pin['archive_sha256'],'Publisher archive identity'
r=archive_core.prepare(a.core,a.destination,a.user);r.update(archive_sha256=archive_core.sha(a.archive),profile=pin['profile'],approval='Software build/package only; no installation or hardware authorization')
(a.destination/'patched-core-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
