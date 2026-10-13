#!/usr/bin/env python3
"""Focused offline installation faults; synthetic private inputs, no physical interfaces."""
import argparse,copy,hashlib,json,shutil,struct,sys,tempfile,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
import stage26_installation as install
from stage26_private import config,validate_private
from stage24_fresh_images import prepare,verify_fresh
from s3_validation import partition_tool
from s3_migration import pack_files
p=argparse.ArgumentParser()
for n in ['core-dir','sdk-source','generator-dir','mkspiffs','results','controlled-core','controlled-build','safe-core','safe-build']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();rows=[]
def case(name,fn,deny=False):
    try:
        fn()
        if deny:raise AssertionError('Unsafe input accepted')
        status='PASS';error=''
    except (ValueError,OSError,RuntimeError,KeyError,TypeError):status='PASS' if deny else 'FAIL';error='Expected-safe rejection' if deny else 'Unexpected rejection'
    except Exception:status='FAIL';error='Assertion or unexpected exception; private data suppressed'
    rows.append(dict(name=name,status=status,assertions=1,error=error));print(status,name)
with tempfile.TemporaryDirectory(prefix='stage26-fixtures-') as temp:
    t=Path(temp);public=ROOT/'review/stage26-installation';original=json.loads((public/'manifest.json').read_text());trusted=install.PIN
    case('pinned_public_set',lambda:install.verify_public(a.core_dir,a.mkspiffs,public))
    def altered(name,change,repin=False):
        d=t/name;shutil.copytree(public,d);m=copy.deepcopy(original);change(d,m);(d/'manifest.json').write_text(json.dumps(m))
        if repin:install.PIN=t/(name+'-pin.json');install.PIN.write_text(json.dumps(m))
        try:return install.verify_public(a.core_dir,a.mkspiffs,d)
        finally:install.PIN=trusted
    def update_file(d,m,name,data):
        (d/name).write_bytes(data)
        for r in m['rows']+[m['fallback']]:
            if r['file']==name:r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    for name,fn in [('missing_image',lambda d,m:(d/'controlled-stage26.bin').unlink()),('bad_hash',lambda d,m:m['rows'][0].update(sha256='0'*64)),('wrong_address',lambda d,m:m['rows'][0].update(offset=0x9000)),('wrong_profile',lambda d,m:m.update(profile='normal')),('wrong_flash_context',lambda d,m:m.update(flash_bytes=0x400000)),('wrong_ota',lambda d,m:update_file(d,m,'ota-app0.bin',b'\xff'*0x2000)),('wrong_spiffs_geometry',lambda d,m:m['geometry'].update(page=512)),('interrupted_generation_no_manifest',lambda d,m:None)]:
        if name=='interrupted_generation_no_manifest':
            d=t/name;d.mkdir();shutil.copyfile(public/'bootloader.bin',d/'bootloader.bin');case(name,lambda:install.verify_public(a.core_dir,a.mkspiffs,d),True)
        else:case(name,lambda n=name,f=fn:altered(n,f),True)
    case('overlap_even_with_updated_trusted_fixture',lambda:altered('overlap',lambda d,m:m['rows'][1].update(offset=0x4000,erase_start=0x4000),True),True)
    case('oversized_app',lambda:altered('oversized',lambda d,m:update_file(d,m,'controlled-stage26.bin',b'\xff'*(0x740000+1)),True),True)
    case('incorrect_erase_range',lambda:altered('erase',lambda d,m:m['rows'][0].update(erase_end_exclusive=0xe000),True),True)
    case('out_of_range_nvs_not_allowed_in_public_set',lambda:altered('nvs-public',lambda d,m:m['rows'].append(dict(role='nvs',file='invented',offset=0,bytes=0x5000)),True),True)
    case('invalid_ota_with_matching_hash',lambda:altered('ota-content',lambda d,m:update_file(d,m,'ota-app0.bin',b'\xff'*0x2000),True),True)
    def header(d,m,offset,value):
        name='controlled-stage26.bin';data=bytearray((d/name).read_bytes());data[offset]=value;data[-32:]=hashlib.sha256(data[:-32]).digest();update_file(d,m,name,bytes(data))
    case('wrong_chip_with_matching_hash',lambda:altered('chip',lambda d,m:header(d,m,12,0),True),True)
    case('unsupported_flash_mode',lambda:altered('mode',lambda d,m:header(d,m,2,99),True),True)
    case('wrong_flash_header',lambda:altered('flash',lambda d,m:header(d,m,3,0x2f),True),True)
    case('corrupt_image_with_matching_hash',lambda:altered('corrupt',lambda d,m:header(d,m,0,0),True),True)
    def table(d,m):
        tool=partition_tool(a.core_dir);entries=tool.PartitionTable.from_binary((d/'partitions.bin').read_bytes());entries[0].readonly=True;update_file(d,m,'partitions.bin',entries.to_binary())
    case('experimental_table_rejected',lambda:altered('table',table,True),True)
    case('mixed_safe_app_rejected',lambda:altered('mixed',lambda d,m:update_file(d,m,'controlled-stage26.bin',(d/'deployment-safe-stage26.bin').read_bytes())),True)
    case('symlink_image_rejected',lambda:altered('link',lambda d,m:((d/'bootloader.bin').unlink(),(d/'bootloader.bin').symlink_to(public/'bootloader.bin'))),True)
    case('corrupt_coredump_matching_hash',lambda:altered('core',lambda d,m:update_file(d,m,'coredump-erased.bin',bytes(0x10000)),True),True)
    credentials={'ssid':'SyntheticStage26','ap_password':'synthetic-ap-26-only','web_password':'synthetic-web-26-only'}
    case('explicit_secure_config',lambda:config(credentials))
    for name,c in [('missing_credentials',{}),('short_ap',dict(credentials,ap_password='abcdefgh')),('short_web',dict(credentials,web_password='x')),('empty_web',dict(credentials,web_password='')),('incomplete',{'ssid':'synthetic'}),('newline',dict(credentials,ssid='bad\n')),('wrong_type',dict(credentials,ap_password=1))]:case(name,lambda c=c:config(c),True)
    import re
    legacy=re.search(r'^#define\s+WIFI_PASSWORD\s+"([^"\\]*)"\s*$',(ROOT/'EvilDuckS3/config.h').read_text(),re.M)[1]
    case('legacy_password',lambda:config(dict(credentials,ap_password=legacy)),True)
    private=t/'private';case('real_pinned_generator_empty_fs_roundtrip',lambda:prepare(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,credentials,private))
    before=(private/'fresh-nvs.bin').read_bytes()
    case('complete_private_schema_and_plan',lambda:validate_private(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,credentials,private,public))
    case('existing_outputs_not_overwritten',lambda:prepare(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,credentials,private),True)
    case('different_credentials_rejected_even_structurally_valid',lambda:validate_private(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,dict(credentials,web_password='different-synthetic-web'),private,public),True)
    def corrupt_private():
        report=json.loads((private/'review-inventory.json').read_text());data=bytes(0x5000);(private/'fresh-nvs.bin').write_bytes(data);report['artifacts'][0]['sha256']=hashlib.sha256(data).hexdigest();(private/'review-inventory.json').write_text(json.dumps(report));verify_fresh(a.core_dir,a.mkspiffs,private)
    case('corrupt_nvs_even_matching_hash',corrupt_private,True)
    case('review_never_contains_private_nvs',lambda: (_ for _ in ()).throw(AssertionError()) if any(p.name=='fresh-nvs.bin' for p in public.iterdir()) else None)
    def nonempty(d,m):
        files=t/'unexpected-files';files.mkdir();(files/'unexpected.txt').write_text('harmless');out=t/'nonempty-packed';pack_files(a.mkspiffs,files,out);update_file(d,m,'empty-spiffs.bin',(out/'spiffs-new-0x160000.bin').read_bytes())
    case('nonempty_fs_even_matching_hash',lambda:altered('nonempty',nonempty,True),True)
    def cli_reprepare():
        new=t/'cli-reprepared'
        subprocess.run([sys.executable,str(ROOT/'tools/stage26_prepare.py'),'--core-dir',str(a.controlled_core),'--build-dir',str(a.controlled_build),'--safe-core-dir',str(a.safe_core),'--safe-build-dir',str(a.safe_build),'--mkspiffs',str(a.mkspiffs),'--output-dir',str(new)],check=True,capture_output=True,timeout=120)
        install.verify_public(a.core_dir,a.mkspiffs,new)
    case('public_preparation_cli_exact_repeat',cli_reprepare)
    def interrupted_publication():
        destination=t/'interrupted-real-publication';original_copy=shutil.copyfile
        def fail_copy(source,dest,*args,**kwargs):
            if Path(dest).parent==destination and Path(dest).name=='partitions.bin':raise OSError('Synthetic interrupted copy')
            return original_copy(source,dest,*args,**kwargs)
        try:
            shutil.copyfile=fail_copy
            try:install.prepare(a.controlled_core,a.controlled_build,a.safe_core,a.safe_build,a.mkspiffs,destination)
            except OSError:pass
            else:raise AssertionError('Fault did not run')
        finally:shutil.copyfile=original_copy
        if not destination.is_dir() or (destination/'manifest.json').exists():raise AssertionError('Incomplete set published')
        try:install.verify_public(a.core_dir,a.mkspiffs,destination)
        except OSError:return
        raise AssertionError('Incomplete set accepted')
    case('actual_publication_interruption_fails_closed',interrupted_publication)
case('public_inputs_unchanged',lambda: (_ for _ in ()).throw(AssertionError()) if (public/'manifest.json').read_text()!=json.dumps(original,indent=2)+'\n' else None)
result=dict(results=rows,counts={s:sum(r['status']==s for r in rows) for s in ['PASS','FAIL']},assertions=len(rows),hardware_access=False,synthetic_credentials_only=True,actual_generator_executed=True,actual_mkspiffs_executed=True,physical_recovery_verified=False)
with a.results.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
raise SystemExit(any(r['status']=='FAIL' for r in rows))
