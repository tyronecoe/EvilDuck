#!/usr/bin/env python3
"""Private offline provisioning for the controlled candidate; no device APIs."""
import argparse,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
from stage24_fresh_images import prepare,validate_config,verify_fresh
from s3_validation import ROOT,require

def controlled_config(config):
    config=validate_config(config)
    # Fail closed if the existing public legacy macro stops being a simple literal.
    match=re.search(r'^#define\s+WIFI_PASSWORD\s+"([^"\\]*)"\s*$',(ROOT/'EvilDuckS3/config.h').read_text(),re.M)
    require(match is not None,'Legacy credential policy source needs explicit review')
    require(config['ap_password']!=match[1],'Legacy AP credential is not accepted')
    return config

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['core-dir','sdk-source','generator-dir','mkspiffs','owner-config','output-dir']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();config=controlled_config(json.loads(a.owner_config.read_text()))
    prepare(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,config,a.output_dir)
    verify_fresh(a.core_dir,a.mkspiffs,a.output_dir)
    print('PASS private offline fresh images; controlled credentials checked; installation unauthorized')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError):sys.exit('FAIL: controlled fresh preparation rejected; private values omitted')
