#!/usr/bin/env python3
"""File-only Stage26 review validation. No device API, serial port, or flash writer."""
import argparse, hashlib, json, shutil, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode = True
from s3_validation import ROOT, require, LAYOUT, partition_tool, check_table
from s3_migration import pack_files, checked_mkspiffs, source_listing
from s3_write_plan import validate_ota_initializer
from stage25_recovery_check import verify_recovery
from verify_patched_firmware import verify as linked_verify
LABEL = 'REVIEW ONLY — NOT AUTHORIZED FOR FLASHING'
PIN = ROOT/'docs/stage26-artifact-pin.json'
PURPOSES = {'bootloader':'Pinned ESP32-S3 startup loader','partitions':'Approved writable 16 MiB layout with MD5','otadata':'Deterministic initial app0 selection','app0':'Controlled normal-start Stage26 image','app1':'Same controlled image in alternate OTA slot','spiffs':'Empty filesystem; zero scripts','coredump':'New coredump region in erased state','nvs':'Explicit private fresh typed settings; disabled autorun'}
REGIONS = {'bootloader':(0,0x8000), 'partitions':(0x8000,0x9000),
 'nvs':(0x9000,0xe000), 'otadata':(0xe000,0x10000),
 'app0':(0x10000,0x750000), 'app1':(0x750000,0xe90000),
 'spiffs':(0xe90000,0xff0000), 'coredump':(0xff0000,0x1000000)}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def ranges(rows, complete=False):
    roles = set(REGIONS) if complete else set(REGIONS)-{'nvs'}
    require(len(rows)==len(roles) and {r['role'] for r in rows}==roles, 'Exact reviewed role set required')
    footprints=[]
    for r in rows:
        start,end=REGIONS[r['role']]; size=r['bytes']
        require(type(size) is int and 0<size<=end-start and type(r['offset']) is int and r['offset']==start, 'Invalid region or size')
        if r['role'] in ('nvs','otadata','spiffs','coredump'): require(size==end-start,'Complete data region required')
        if r['role']=='partitions': require(size==0xc00,'Canonical generated table required')
        rounded=(start+size+4095)//4096*4096
        require(r['region_end_exclusive']==end,'Wrong region boundary')
        require(rounded<=end and r['erase_start']==start and r['erase_end_exclusive']==rounded,'Invalid sector footprint')
        require(r['initial_write_planned'] is True and r['authorized_for_flashing'] is False,'Review-only plan required')
        footprints.append((start,rounded))
    footprints.sort()
    require(all(a[1]<=b[0] for a,b in zip(footprints,footprints[1:])), 'Overlapping regions')
    return footprints

def row(role,name,path):
    start,end=REGIONS[role];n=path.stat().st_size
    return dict(role=role,purpose=PURPOSES[role],region_end_exclusive=end,file=name,offset=start,bytes=n,sha256=sha(path),erase_start=start,
      erase_end_exclusive=(start+n+4095)//4096*4096,initial_write_planned=True,authorized_for_flashing=False)

def prepare(core,build,safe_core,safe_build,mkspiffs,output):
    output=Path(output);require(not output.exists() and not output.is_symlink(),'Fresh output required')
    current=linked_verify(core,build);safe=linked_verify(safe_core,safe_build)
    require(current['controlled_normal_start'] and not current['deployment_safe_start'],'Controlled firmware required')
    require(safe['deployment_safe_start'] and not safe['controlled_normal_start'],'Quiescent fallback required')
    checked_mkspiffs(mkspiffs)
    with tempfile.TemporaryDirectory(prefix='.stage26-review-',dir=output.parent) as tmp:
        t=Path(tmp)
        files={'bootloader.bin':Path(build)/'EvilDuckS3.ino.bootloader.bin',
          'partitions.bin':Path(build)/'EvilDuckS3.ino.partitions.bin',
          'controlled-stage26.bin':Path(build)/'EvilDuckS3.ino.bin',
          'ota-app0.bin':Path(core)/'tools/partitions/boot_app0.bin',
          'deployment-safe-stage26.bin':Path(safe_build)/'EvilDuckS3.ino.bin'}
        for name,path in files.items(): shutil.copyfile(path,t/name)
        empty=t/'empty';empty.mkdir();pack_files(mkspiffs,empty,t/'packed')
        shutil.copyfile(t/'packed/spiffs-new-0x160000.bin',t/'empty-spiffs.bin')
        (t/'coredump-erased.bin').write_bytes(b'\xff'*0x10000)
        rows=[row(r,n,t/n) for r,n in [('bootloader','bootloader.bin'),('partitions','partitions.bin'),('otadata','ota-app0.bin'),('app0','controlled-stage26.bin'),('app1','controlled-stage26.bin'),('spiffs','empty-spiffs.bin'),('coredump','coredump-erased.bin')]]
        ranges(rows)
        fallback=dict(file='deployment-safe-stage26.bin',bytes=(t/'deployment-safe-stage26.bin').stat().st_size,sha256=sha(t/'deployment-safe-stage26.bin'),initial_write_planned=False,purpose='Quiescent fallback; not proof of physical recovery')
        manifest=dict(label=LABEL,kind='stage26-controlled-installation-review',profile='controlled-normal-start',migration_authorized=False,hardware_access=False,flash_bytes=0x1000000,rows=rows,fallback=fallback,private_nvs='REQUIRED LATER: explicit fresh owner credentials; not included',geometry=dict(block=4096,page=256,bytes=0x160000,files=0),source_baseline='f929bdf2353e0022f10c164d2c09cb3db2564a5a')
        output.mkdir() # Exclusive creation. Publish manifest last: interrupted sets fail closed.
        for name in list(files)+['empty-spiffs.bin','coredump-erased.bin']: shutil.copyfile(t/name,output/name)
        (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest,current,safe

def verify_public(core,mkspiffs,directory):
    directory=Path(directory);require(directory.is_dir() and not directory.is_symlink(),'Ordinary review directory required')
    m=json.loads((directory/'manifest.json').read_text());pin=json.loads(PIN.read_text())
    require(m==pin,'Manifest differs from trusted Stage26 checkout pin; do not mix builds/profiles')
    require(m['label']==LABEL and m['migration_authorized'] is False and m['profile']=='controlled-normal-start' and m['flash_bytes']==0x1000000,'Wrong profile or authorization')
    ranges(m['rows'])
    for r in m['rows']+[m['fallback']]:
        name=r['file'];require(Path(name).name==name,'Unsafe filename')
        p=directory/name
        require(p.is_file() and not p.is_symlink() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Missing/corrupt/mismatched artifact')
    table=partition_tool(core).PartitionTable.from_binary((directory/'partitions.bin').read_bytes())
    check_table(table,LAYOUT)
    require(table.to_binary()==(directory/'partitions.bin').read_bytes(),'Table integrity mismatch')
    validate_ota_initializer((directory/'ota-app0.bin').read_bytes())
    with tempfile.TemporaryDirectory(prefix='stage26-header-check-') as temp:
        t=Path(temp)
        for r in m['rows']:
            if r['role'] in ('bootloader','partitions','otadata','app0','app1'): shutil.copyfile(directory/r['file'],t/r['file'])
        spec=dict(kind='recovery-review',physical_flash_bytes=0x1000000,owner_reported_known_good=False,images=[dict(role=r['role'],file=r['file'],bytes=r['bytes'],sha256=r['sha256'],offset=r['offset']) for r in m['rows'] if r['role'] in ('bootloader','partitions','otadata','app0','app1')])
        (t/'recovery-review.json').write_text(json.dumps(spec));details=verify_recovery(core,t)
        # Intended 16 MiB/QIO80 profile. Bootloader encoding can advertise DIO for loader safety.
        for role,info in details['image_headers'].items():
            data=(t/next(r['file'] for r in spec['images'] if r['role']==role)).read_bytes()
            require(data[3]==0x4f,'Wrong 16MiB/80MHz image header')
        shutil.copyfile(directory/m['fallback']['file'],t/m['fallback']['file'])
        for r in spec['images']:
            if r['role'] in ('app0','app1'):r.update(file=m['fallback']['file'],bytes=m['fallback']['bytes'],sha256=m['fallback']['sha256'])
        (t/'recovery-review.json').write_text(json.dumps(spec));verify_recovery(core,t)
    checked_mkspiffs(mkspiffs)
    require(m['geometry']==dict(block=4096,page=256,bytes=0x160000,files=0) and source_listing(str(mkspiffs),directory/'empty-spiffs.bin',0x160000)=={},'Nonempty or wrong geometry SPIFFS')
    require((directory/'coredump-erased.bin').read_bytes()==b'\xff'*0x10000,'Coredump initialization mismatch')
    return dict(status='PASS',scope='offline pinned artifacts and ranges only',private_nvs_ready=False,migration_authorized=False,original_firmware_availability='OWNER CONFIRMED — AVAILABLE EXTERNALLY',physical_recovery_verified=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--mkspiffs',type=Path,required=True);p.add_argument('--review-dir',type=Path,required=True)
    a=p.parse_args();print(json.dumps(verify_public(a.core_dir,a.mkspiffs,a.review_dir),indent=2))
if __name__=='__main__':
    try: main()
    except (OSError,ValueError,RuntimeError,KeyError,TypeError): sys.exit('FAIL: offline review set rejected; no physical operation')
