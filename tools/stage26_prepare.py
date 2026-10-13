#!/usr/bin/env python3
"""Prepare public review files from verified clean builds; never writes to hardware."""
import argparse,sys
from pathlib import Path
sys.dont_write_bytecode=True
from stage26_installation import prepare
p=argparse.ArgumentParser(description=__doc__)
for name in ['core-dir','build-dir','safe-core-dir','safe-build-dir','mkspiffs','output-dir']:p.add_argument('--'+name,type=Path,required=True)
a=p.parse_args()
try:
    prepare(a.core_dir,a.build_dir,a.safe_core_dir,a.safe_build_dir,a.mkspiffs,a.output_dir)
    print('PASS: new offline review set; compare with trusted committed pin before accepting; no installation authorized')
except Exception:sys.exit('FAIL: preparation rejected; no device operation')
