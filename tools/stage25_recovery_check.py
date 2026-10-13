#!/usr/bin/env python3
"""Offline recovery-bundle format verification. No serial, flash or owner-file writes.
A structural PASS never establishes known-good physical operation or authorizes recovery.
"""
import argparse,hashlib,json,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
from s3_validation import require,partition_tool,check_table,LAYOUT,LEGACY_LAYOUT
from deployment_preflight import esp_image
from s3_write_plan import validate_ota_initializer

def verify_recovery(core,directory):
    directory=Path(directory);manifest=directory/'recovery-review.json'
    require(directory.is_dir() and not directory.is_symlink(),'Ordinary recovery directory required')
    require(manifest.is_file() and not manifest.is_symlink(),'Owner recovery manifest missing')
    spec=json.loads(manifest.read_text());require(spec.get('kind')=='recovery-review' and spec.get('physical_flash_bytes')==0x1000000,'Expected reviewed ESP32-S3 16 MiB device context')
    require(type(spec.get('owner_reported_known_good')) is bool,'Owner known-good evidence field required')
    rows=spec['images'];roles={r['role']:r for r in rows}
    require(len(roles)==len(rows) and set(roles) in ({'bootloader','partitions','otadata','app0'},{'bootloader','partitions','otadata','app0','app1'}),'Require distinct bootloader/table/otadata/app0 roles; no private data artifacts')
    checked={}
    for role,row in roles.items():
        name=row['file'];require(isinstance(name,str) and Path(name).name==name and name not in ('.','..'),'Unsafe recovery filename')
        p=directory/name;require(p.is_file() and not p.is_symlink(),'Recovery image missing or linked')
        require(p.stat().st_size==row['bytes'] and 0<row['bytes']<=0x740000,'Recovery size mismatch')
        require(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'Recovery SHA256 mismatch')
        checked[role]=p.read_bytes()
    require(len(checked['partitions'])<=0x1000,'Partition table exceeds its sector')
    table=partition_tool(core).PartitionTable.from_binary(checked['partitions'])
    geometry=tuple((p.name,p.type,p.subtype,p.offset,p.size) for p in table)
    require(geometry in (LAYOUT,LEGACY_LAYOUT),'Recovery geometry is not one of the reviewed layouts')
    check_table(table,geometry)
    # Canonical serialization also checks expected MD5/padding, not merely label recognition.
    encoded=table.to_binary();require(checked['partitions'][:len(encoded)]==encoded and all(b==255 for b in checked['partitions'][len(encoded):]),'Recovery table integrity/canonical padding mismatch')
    expected={'bootloader':(0,0x8000),'partitions':(0x8000,0x1000),'otadata':(0xe000,0x2000)}
    for role in ['app0','app1']:
        if role in roles:
            p=next(p for p in table if p.name==role);expected[role]=(p.offset,p.size)
    validate_ota_initializer(checked['otadata']) # Deterministic app0 selection, not old moved metadata.
    intervals=[];infos={}
    capacities=[1<<20,2<<20,4<<20,8<<20,16<<20,32<<20,64<<20,128<<20]
    for role,row in roles.items():
        offset,limit=expected[role];require(row['offset']==offset and row['bytes']<=limit,'Recovery region/slot mismatch')
        start=offset//4096*4096;end=(offset+row['bytes']+4095)//4096*4096
        require(start==offset and end<=offset+limit and end<=0x1000000,'Recovery sector footprint exceeds region')
        require(end<=0x9000 or start>=0xe000,'Recovery bundle unexpectedly touches NVS')
        intervals.append((start,end))
        if role in ('bootloader','app0','app1'):
            d=checked[role];info=esp_image(d,limit);require(info['image_bytes']==len(d),'Unexpected trailing application/bootloader data')
            require((d[3]&15) in (0,15),'Recovery flash clock must be reviewed 40/80 MHz')
            require(d[2] in (0,1,2,3),'Require quad-compatible standard flash mode')
            entry=struct.unpack_from('<I',d,4)[0]
            require(0x40370000<=entry<0x403e0000,'Unsupported ESP32-S3 standard IRAM entry point')
            minimum=struct.unpack_from('<H',d,15)[0];maximum=struct.unpack_from('<H',d,17)[0]
            require(minimum<=2 and (role=='bootloader' or maximum in (0,65535) or 2<=maximum),'Image revision bounds exclude owner-reported ESP32-S3 v0.2')
            require(capacities[d[3]>>4]<=0x1000000,'Recovery header exceeds physical flash')
            require(max(p.offset+p.size for p in table)<=capacities[d[3]>>4],'Recovery table exceeds image flash-size profile')
            infos[role]=dict(info,entry_address=entry,flash_mode_code=d[2],flash_mhz=80 if (d[3]&15)==15 else 40,min_revision=minimum,max_revision=maximum)
    intervals.sort();require(all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:])),'Recovery sector footprints overlap')
    return dict(status='PASS',scope='offline image/table/hash/revision/range checks only',owner_reported_known_good=spec['owner_reported_known_good'],known_good_independently_demonstrated=False,hardware_verified=False,recovery_authorized=False,layout='proposed-16MiB' if geometry==LAYOUT else 'original-4MiB',images=rows,image_headers=infos,sector_footprints=intervals)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',required=True,type=Path);p.add_argument('--recovery-dir',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    require(not a.output.exists(),'Never overwrite a report or owner file')
    if not (a.recovery_dir/'recovery-review.json').is_file():
        report=dict(status='BLOCKED',missing='Owner-provided recovery image bundle and trusted hashes/known-good evidence',recovery_authorized=False,hardware_access=False)
        a.output.write_text(json.dumps(report,indent=2)+'\n');print('BLOCKED: recovery resource not supplied; no hardware operation');return 2
    report=verify_recovery(a.core_dir,a.recovery_dir);a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS offline structure only; physical recovery remains unverified');return 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,RuntimeError,KeyError):sys.exit('FAIL: recovery bundle rejected; no device operation performed')
