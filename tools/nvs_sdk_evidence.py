#!/usr/bin/env python3
"""Inspect the exact pinned Xtensa NVS archive without executing SDK or flash APIs."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
from patched_core import check_sources,sha
TARGETS=['nvs_flash_init','nvs_flash_init_partition','nvs::NVSPartitionManager::init_custom','nvs::Storage::init','nvs::Storage::eraseMismatchedBlobIndexes','nvs::Storage::eraseOrphanDataBlobs','nvs::PageManager::load','nvs::PageManager::activatePage','nvs::Page::load','nvs::Page::mLoadEntryTable','nvs::Page::eraseEntryAndSpan','nvs::Page::readItem','nvs::Page::erase','nvs::NVSPartition::erase_range','nvs::NVSPartition::write']
def inspect(core):
    core=Path(core).resolve();pin=check_sources(core)
    tools=core.parents[2]/'tools';archive=tools/'esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3/lib/libnvs_flash.a'
    objdump=tools/'esp-x32/2411/bin/xtensa-esp32s3-elf-objdump'
    text=subprocess.run([str(objdump),'-drC',str(archive)],capture_output=True,text=True,check=True).stdout
    sections=re.split(r'Disassembly of section ',text)[1:];rows=[]
    for target in TARGETS:
        matched=[]
        for section in sections:
            # Only relocation records in the actual function body, excluding literal tables.
            first=section.split('\n',3)
            if section.startswith('.literal.'):continue
            labels=re.findall(r'^0+ <(.+)>:',section,re.M)
            if not any(label.split('(')[0]==target for label in labels):continue
            refs=sorted(set(r for r in re.findall(r'R_XTENSA_[A-Z0-9_]+\s+(.+)',section) if not r.startswith('.')))
            matched.append(dict(section=section.split(':',1)[0],references=refs,has_indirect_call='callx' in section,disassembly_sha256=hashlib.sha256(section.encode()).hexdigest()))
        if not matched:raise ValueError('Missing archive function evidence: '+target)
        rows.append(dict(function=target,sections=matched))
    return dict(archive_sha256=sha(archive),expected_archive_sha256=pin['sdk_nvs_archive_sha256'],objdump_sha256=sha(objdump),functions=rows,sdk_binary_executed=False,hardware_access=False,source_binary_equivalence_certified=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--core-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Existing output rejected')
    data=inspect(a.core_dir)
    with a.output.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    print('PASS: pinned archive inspected, not executed')
