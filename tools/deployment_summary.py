#!/usr/bin/env python3
"""Strict privacy-safe projection of a private preflight report, not independent verification."""
import argparse,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
from deployment_preflight import OWNER,EXPECTED_FILES
from s3_validation import LEGACY_LAYOUT,LAYOUT,require
CATEGORIES=['invalid','unsupported-format','recovery-potentially-required','insufficient-evidence']
CLASSIFICATIONS=set(CATEGORIES+['compatible-within-verified-checks'])
CODES=set('wrong_region_size dirty_uninitialized_page invalid_page_state page_header_crc page_version header_reserved_bytes duplicate_page_sequence freeing_page bitmap_reserved_bits illegal_entry_state incomplete_entry_write written_after_empty_entry invalid_key_encoding entry_header_crc entry_span_boundary numeric_or_index_span blob_index_chunk blob_index_relationships_unverified variable_span_length incomplete_variable_span variable_data_crc invalid_string_encoding blob_data_chunk blob_data_relationships_unverified entry_type namespace_entry invalid_namespace_index namespace_reference_unresolved duplicate_live_record multiple_active_pages no_erased_free_page'.split())
def summary(report):
    require(report.get('evidence')=='owner-recorded','Not a completed owner-recorded local preflight report')
    require(report.get('owner_files_verified') is True and report.get('hardware_access') is False and report.get('migration_authorized') is False,'Inconsistent preflight evidence flags')
    require(report.get('original_layout')==json.loads(json.dumps(LEGACY_LAYOUT)) and report.get('proposed_layout')==json.loads(json.dumps(LAYOUT)),'Partition evidence differs')
    files=report.get('files',{})
    require(set(files)==set(OWNER),'Unexpected/missing backup evidence')
    for name,(size,digest) in OWNER.items():
        require(files[name].get('bytes')==size and files[name].get('sha256')==digest,'Backup identity differs')
    require(report.get('spiffs_roundtrip_verified') is True,'Missing filesystem roundtrip evidence')
    fs=report.get('spiffs_files',{})
    require(set(fs)==set(EXPECTED_FILES) and all(fs[n].get('bytes')==size for n,size in EXPECTED_FILES.items()),'Filesystem inventory evidence differs')
    apps=report.get('original_applications',{})
    require(set(apps)=={'app0','app1'} and all(a.get('state') in ('valid','erased') for a in apps.values()) and any(a.get('state')=='valid' for a in apps.values()),'Missing recovery application evidence')
    boot=report.get('original_bootloader',{})
    require(boot.get('chip_id')==9 and type(boot.get('image_bytes')) is int and 24<=boot['image_bytes']<=0x8000,'Missing bootloader integrity evidence')
    nvs=report.get('nvs_structure',{});classification=nvs.get('classification')
    require(classification in CLASSIFICATIONS and nvs.get('bytes')==0x5000,'Missing bounded NVS findings')
    require(nvs.get('sdk_immutability_verified') is False and nvs.get('settings_values_validated') is False and nvs.get('migration_authorized') is False,'Unsupported NVS guarantee')
    findings=[]
    for row in nvs.get('issues',[]):
        require(row.get('category') in CATEGORIES and row.get('code') in CODES,'Unknown structural finding')
        projected=dict(category=row['category'],code=row['code'])
        for name,bound in [('page',5),('entry',126)]:
            if name in row:
                require(type(row[name]) is int and 0<=row[name]<bound,'Invalid finding location');projected[name]=row[name]
        findings.append(projected)
    expected=next((c for c in CATEGORIES if any(r['category']==c for r in findings)),'compatible-within-verified-checks')
    require(classification==expected,'Contradictory NVS classification')
    return dict(evidence_class='privacy-safe summary of local report; source backups not independently rechecked',backup_identities_match_recorded=True,original_layout_validated=True,proposed_layout_unchanged=True,bootloader_integrity_reported=True,recovery_application_integrity_reported=True,spiffs_roundtrip_reported=True,spiffs_file_count=7,spiffs_payload_bytes=sum(EXPECTED_FILES.values()),nvs_classification=classification,nvs_findings=findings,sdk_immutability_proven=False,settings_semantics_verified=False,hardware_access=False,migration_authorized=False,readiness='NO-GO migration/application boot/OTA; preservation and authorization gates remain',owner_backup_bytes_included=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--private-report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    require(not a.output.exists(),'Output exists; refusing overwrite')
    require(a.private_report.is_file() and not a.private_report.is_symlink() and a.private_report.stat().st_size<=1024*1024,'Invalid/oversized input report')
    out=summary(json.loads(a.private_report.read_text()))
    with a.output.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print('PASS: privacy-safe summary created; migration remains NO-GO')
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:sys.exit('FAIL: summary rejected; no private values printed')
