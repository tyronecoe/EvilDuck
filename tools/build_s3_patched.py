#!/usr/bin/env python3
"""Prepare an isolated verified core then clean-build production firmware, offline."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
from patched_core import prepare, check_sources

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core-dir',type=Path,required=True)
    p.add_argument('--user-dir',type=Path,required=True,help='Existing Arduino library directory')
    p.add_argument('--isolation-dir',type=Path,required=True,help='New external directory')
    p.add_argument('--build-dir',type=Path,required=True)
    p.add_argument('--arduino-cli',required=True)
    profiles=p.add_mutually_exclusive_group()
    profiles.add_argument('--deployment-safe-start',action='store_true')
    profiles.add_argument('--controlled-normal-start',action='store_true')
    p.add_argument('--jobs',type=int,default=2)
    a=p.parse_args()
    receipt=prepare(a.core_dir,a.isolation_dir,a.user_dir)
    command=[sys.executable,str(Path(__file__).with_name('build_s3.py')),'--arduino-cli',a.arduino_cli,'--config-file',receipt['config'],'--patched-core-dir',receipt['core'],'--build-dir',str(a.build_dir),'--jobs',str(a.jobs)]
    if a.deployment_safe_start:command.append('--deployment-safe-start')
    if a.controlled_normal_start:command.append('--controlled-normal-start')
    subprocess.run(command,check=True)
    from verify_patched_firmware import verify
    verify(receipt["core"], a.build_dir)
    check_sources(a.core_dir)
    print('PASS: isolated patched build; installed core unchanged')
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as e:sys.exit('FAIL: '+str(e))
