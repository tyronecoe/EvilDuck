#!/usr/bin/env python3
"""Private, offline fresh provisioning/verification. No flash or device operations."""
import argparse,json,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from stage25_fresh_config import controlled_config
from stage24_fresh_images import prepare,verify_fresh
from stage26_installation import verify_public,ranges,row
from s3_validation import require,ROOT

def config(c):
    c=controlled_config(c)
    require(len(c['ap_password'].encode('utf8'))>=12 and len(c['web_password'].encode('utf8'))>=12,'Stage26 preparation requires at least 12 UTF-8 bytes per password')
    return c

def validate_private(core,sdk,generator,mkspiffs,owner_config,private_dir,public_dir):
    c=config(owner_config);public=verify_public(core,mkspiffs,public_dir)
    actual=verify_fresh(core,mkspiffs,private_dir)
    # Reproduce exact typed schema from explicit input; structural NVS validity alone
    # cannot prove credentials, disabled autorun, empty script or complete settings.
    with tempfile.TemporaryDirectory(prefix='stage26-private-recheck-') as temp:
        expected=Path(temp)/'expected';prepare(core,sdk,generator,mkspiffs,c,expected)
        require((expected/'fresh-nvs.bin').read_bytes()==(Path(private_dir)/'fresh-nvs.bin').read_bytes(),'Fresh NVS does not match explicit credentials/schema')
        require((expected/'fresh-spiffs.bin').read_bytes()==(Path(private_dir)/'fresh-spiffs.bin').read_bytes(),'Fresh SPIFFS changed')
    require((Path(private_dir)/'fresh-spiffs.bin').read_bytes()==(Path(public_dir)/'empty-spiffs.bin').read_bytes(),'Private filesystem differs from pinned empty filesystem')
    require(actual['autorun_enabled'] is False and actual['spiffs_files']=={} and actual['spiffs_geometry']==dict(block=4096,page=256,bytes=0x160000),'Fresh configuration policy mismatch')
    m=json.loads((Path(public_dir)/'manifest.json').read_text())
    rows=m['rows']+[row('nvs','fresh-nvs.bin',Path(private_dir)/'fresh-nvs.bin')];ranges(rows,complete=True)
    return dict(label=m['label'],status='PASS',scope='offline fresh review; not installation authorization',private_values_emitted=False,rows=rows,migration_authorized=False,original_firmware_availability=public['original_firmware_availability'],nvs_action='Explicit fresh replacement at 0x9000..0xDFFF; requires future owner approval',physical_recovery_verified=False)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['prepare','verify'])
    for n in ['core-dir','sdk-source','generator-dir','mkspiffs','owner-config','private-dir','review-dir']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--summary',type=Path,required=True);a=p.parse_args()
    require(not a.summary.exists() and not a.summary.is_symlink(),'Never overwrite summaries/backups')
    require(ROOT.resolve() not in a.summary.resolve().parents,'Keep private hash receipts outside repository')
    require(a.owner_config.stat().st_size<=32768,'Oversized private input')
    c=config(json.loads(a.owner_config.read_text()))
    if a.operation=='prepare':prepare(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,c,a.private_dir)
    r=validate_private(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,c,a.private_dir,a.review_dir)
    with a.summary.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print('PASS: private offline schema/images verified; physical installation remains unauthorized')
if __name__=='__main__':
    try:main()
    except Exception:sys.exit('FAIL: private preparation rejected; values omitted; no device operation')
