#!/usr/bin/env python3
"""Non-device local tool check. No install, network, serial, USB or enumeration."""
import argparse,importlib.util,json,platform,sys
sys.dont_write_bytecode=True
from package import validate
p=argparse.ArgumentParser();p.add_argument('--public',required=True);a=p.parse_args()
try:
 r=validate(a.public)
 print(json.dumps(dict(status='PASS',python=sys.version.split()[0],system=platform.system(),machine=platform.machine(),public_integrity=r['status'],cryptography_importable=importlib.util.find_spec('cryptography') is not None,private_finalization_dependencies_verified=False,native_mkspiffs_compatibility='NOT TESTED',hardware='NOT TESTED',migration_authorized=False),indent=2))
except Exception:sys.exit('FAIL: local offline public checks rejected; no device operation')
