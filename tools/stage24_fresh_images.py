#!/usr/bin/env python3
"""Explicit local fresh-image REVIEW preparation; never opens a device or repairs data.
Output can contain owner-selected credentials. Keep it private and outside the repository.
No existing backup/image/namespace is read, reused, erased or overwritten.
"""
import argparse,csv,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
from s3_validation import ROOT,require,validate_csv
from s3_migration import checked_mkspiffs,pack_files,inventory,source_listing
from nvs_source_prepare import verify as sdk_verify
from nvs_generator_prepare import verify as generator_verify
from nvs_inspect import inspect
LABEL='EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING'

def validate_config(c):
    require(isinstance(c,dict) and set(c)=={'ssid','ap_password','web_password'},'Require explicit owner SSID, AP password and web password; no defaults')
    require(all(isinstance(v,str) and '\x00' not in v and '\r' not in v and '\n' not in v for v in c.values()),'Invalid credential representation')
    require(1<=len(c['ssid'].encode('utf8'))<=32 and 8<=len(c['ap_password'].encode('utf8'))<=63 and 1<=len(c['web_password'].encode('utf8'))<4000,'Invalid credential lengths')
    return c

def prepare(core,sdk,generator,mkspiffs,config,output):
    c=validate_config(config);sdk,generator,output=map(Path,(sdk,generator,output))
    require(not output.exists() and not output.is_symlink(),'Fresh output directory required; never overwrite')
    protected=[ROOT.resolve(),Path(core).resolve().parents[4],sdk.resolve(),generator.resolve()]
    require(all(output.resolve()!=q and q not in output.resolve().parents for q in protected),'Fresh output overlaps repository or protected dependency')
    sdk_verify(sdk);generator_verify(generator);validate_csv(core);executable=checked_mkspiffs(mkspiffs)
    require(output.parent.is_dir(),'Output parent must already exist')
    with tempfile.TemporaryDirectory(prefix='.fresh-review-',dir=output.parent) as t:
        t=Path(t);os.chmod(t,0o700)
        source=t/'files';source.mkdir() # Empty filesystem; no timestamped files or scripts.
        fs=t/'fresh-spiffs.bin';packed=t/'packed';pack_files(executable,source,packed)
        shutil.copyfile(packed/'spiffs-new-0x160000.bin',fs);shutil.rmtree(packed)
        rows=[('duck','namespace','',''),('autorun_enabled','data','u8',0),('autorun_script','data','string',''),('ap_ssid','data','string',c['ssid']),('ap_password','data','string',c['ap_password']),('ap_channel','data','u8',1),('stealth','data','u8',0),('hidden_ap','data','u8',0),('disable_led','data','u8',0),('led_color','data','u32',0x28),('web_pw','data','string',c['web_password']),('ar_dly_min','data','u16',0),('ar_dly_max','data','u16',0)]
        with (t/'settings.csv').open('w',newline='') as f:
            writer=csv.writer(f);writer.writerow(('key','type','encoding','value'));writer.writerows(rows)
        env=dict(os.environ,PYTHONPATH=str(generator),PYTHONDONTWRITEBYTECODE='1')
        result=subprocess.run([sys.executable,str(sdk/'components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py'),'generate',str(t/'settings.csv'),str(t/'fresh-nvs.bin'),'0x5000'],env=env,capture_output=True,text=True,timeout=60)
        require(result.returncode==0,'Pinned NVS generator failed (private output suppressed)')
        data=(t/'fresh-nvs.bin').read_bytes();structure=inspect(data)
        require(len(data)==0x5000 and structure['classification']=='compatible-within-verified-checks','Generated NVS failed structural verification')
        artifacts=[]
        for file,offset,size in [('fresh-nvs.bin',0x9000,0x5000),('fresh-spiffs.bin',0xe90000,0x160000)]:
            p=t/file;require(p.stat().st_size==size,'Fresh image size mismatch: '+file+' got '+str(p.stat().st_size))
            artifacts.append(dict(file=file,offset=offset,bytes=size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),initial_write_authorized=False))
            os.chmod(p,0o600)
        report=dict(label=LABEL,offline_only=True,migration_authorized=False,hardware_access=False,fresh_only=True,profile="offline-fresh-writable-review",not_compatible_with_readonly_candidate=True,application_settings_schema_changed=False,autorun_enabled=False,credentials='explicit owner inputs; values omitted',nvs_structure=structure,spiffs_geometry=dict(block=4096,page=256,bytes=0x160000),spiffs_files=inventory(source),artifacts=artifacts)
        # Never persist plaintext CSV/config. Publish inventory last; interruptions are not approval.
        (t/'settings.csv').unlink();shutil.rmtree(source)
        (t/'review-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
        require(not output.exists(),'Output appeared during preparation; refusing overwrite')
        output.mkdir(mode=0o700) # Exclusive creation refuses a raced existing directory.
        for name in ['fresh-nvs.bin','fresh-spiffs.bin','review-inventory.json']:shutil.copy2(t/name,output/name)
    return report

def verify_fresh(core,mkspiffs,directory):
    directory=Path(directory);require(directory.is_dir() and not directory.is_symlink(),'Ordinary fresh-artifact directory required')
    report=json.loads((directory/'review-inventory.json').read_text())
    require(report.get('label')==LABEL and report.get('migration_authorized') is False and report.get('profile')=='offline-fresh-writable-review' and report.get('not_compatible_with_readonly_candidate') is True,'Fresh artifact profile/authorization mismatch')
    validate_csv(core);checked_mkspiffs(mkspiffs)
    expected=[('fresh-nvs.bin',0x9000,0x5000),('fresh-spiffs.bin',0xe90000,0x160000)]
    require(len(report['artifacts'])==2,'Unexpected fresh artifact set')
    for row,(name,offset,size) in zip(report['artifacts'],expected):
        require(row['file']==name and row['offset']==offset and row['bytes']==size and row['initial_write_authorized'] is False,'Fresh artifact geometry mismatch')
        path=directory/name;require(path.is_file() and not path.is_symlink() and path.stat().st_size==size,'Fresh artifact file mismatch')
        require(hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],'Fresh artifact hash mismatch')
    require(inspect((directory/'fresh-nvs.bin').read_bytes())['classification']=='compatible-within-verified-checks','Fresh NVS invalid')
    require(source_listing(str(mkspiffs),directory/'fresh-spiffs.bin',0x160000)=={} and report['spiffs_files']=={},'Fresh SPIFFS must be empty')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['core-dir','sdk-source','generator-dir','mkspiffs','owner-config','output-dir']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();prepare(a.core_dir,a.sdk_source,a.generator_dir,a.mkspiffs,json.loads(a.owner_config.read_text()),a.output_dir)
    verify_fresh(a.core_dir,a.mkspiffs,a.output_dir)
    print('PASS: PRIVATE offline review images prepared; no deployment authorized')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError):sys.exit('FAIL: fresh-image preparation rejected; no device operation performed')
