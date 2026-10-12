#!/usr/bin/env python3
"""Read-only bounded plaintext NVS structure inspection; never emit keys or values."""
import argparse, hashlib, json, struct, sys, zlib
from pathlib import Path
sys.dont_write_bytecode=True
from nvs_blob import validate as validate_blobs
PAGE=4096
SIZE=0x5000
STATES={0xfffffffe:'active',0xfffffffc:'full',0xfffffff8:'freeing'}
NUMERIC={1,0x11,2,0x12,4,0x14,8,0x18}
VARIABLE={0x21,0x41,0x42}
def crc(data):return zlib.crc32(data,0xffffffff)&0xffffffff

def inspect(data):
    """Five-page format subset pinned to IDF b66b5448. No mutation/SDK execution."""
    if len(data)!=SIZE:
        return dict(classification="invalid",issues=[dict(category="invalid",code="wrong_region_size")],bytes=len(data),sdk_immutability_verified=False)
    data=bytes(data)
    indices=[];chunks=[];legacy=[];other=[]
    issues=[];pages=[];records=[];namespace_ids=set();sequences=set();free=0;active=0
    def issue(category,code,page=None,entry=None):
        r=dict(category=category,code=code)
        if page is not None:r['page']=page
        if entry is not None:r['entry']=entry
        issues.append(r)
    for p in range(5):
        b=data[p*PAGE:(p+1)*PAGE];state,seq=struct.unpack_from('<II',b);version=b[8]
        row=dict(page=p,state=STATES.get(state,'unknown'),written_entries=0,erased_entries=0);pages.append(row)
        if b==b'\xff'*PAGE:row['state']='erased';free+=1;continue
        if state==0xffffffff:
            issue('recovery-potentially-required','dirty_uninitialized_page',p);continue
        if state not in STATES:
            issue('invalid','invalid_page_state',p);continue
        if crc(b[4:28])!=struct.unpack_from('<I',b,28)[0]:
            issue('invalid','page_header_crc',p);continue
        if version!=0xfe:
            issue('unsupported-format','page_version',p);continue
        if b[9:28]!=b'\xff'*19:issue('unsupported-format','header_reserved_bytes',p)
        if seq in sequences:issue('recovery-potentially-required','duplicate_page_sequence',p)
        sequences.add(seq)
        if state==0xfffffff8:issue('recovery-potentially-required','freeing_page',p)
        if state==0xfffffffe:active+=1
        bitmap=int.from_bytes(b[32:64],'little');bits=[bitmap>>(2*i)&3 for i in range(126)]
        if bitmap>>252!=15:issue('invalid','bitmap_reserved_bits',p)
        covered=set();empty_seen=False
        for i in range(126):
            v=bits[i];raw=b[64+32*i:96+32*i]
            if v==0:row['erased_entries']+=1;continue
            if v==1:issue('recovery-potentially-required','illegal_entry_state',p,i);continue
            if v==3:
                empty_seen=True
                if raw!=b'\xff'*32:issue('recovery-potentially-required','incomplete_entry_write',p,i)
                continue
            row['written_entries']+=1
            if i in covered:continue
            if empty_seen:issue('recovery-potentially-required','written_after_empty_entry',p,i)
            ns,typ,span,chunk=raw[:4];key=raw[8:24]
            if b'\0' not in key or key[0]==0:issue('invalid','invalid_key_encoding',p,i)
            if crc(raw[:4]+raw[8:])!=struct.unpack_from('<I',raw,4)[0]:
                issue('recovery-potentially-required','entry_header_crc',p,i);continue
            if not span or i+span>126:
                issue('invalid','entry_span_boundary',p,i);continue
            if typ in NUMERIC or typ==0x48:
                if span!=1:issue('invalid','numeric_or_index_span',p,i);continue
                if typ==0x48:
                    if chunk!=255:issue('invalid','blob_index_chunk',p,i)
                    indices.append(dict(ns=ns,key=bytes(key.split(b'\0',1)[0]),page=p,entry=i,size=struct.unpack_from('<I',raw,24)[0],count=raw[28],start=raw[29],reserved=struct.unpack_from('<H',raw,30)[0]))
            elif typ in VARIABLE:
                length=struct.unpack_from('<H',raw,24)[0]
                if span!=1+(length+31)//32 or length>(125-i)*32:
                    issue('invalid','variable_span_length',p,i);continue
                if any(bits[j]!=2 for j in range(i+1,i+span)):
                    issue('recovery-potentially-required','incomplete_variable_span',p,i);continue
                payload=b[96+32*i:96+32*i+length]
                covered.update(range(i+1,i+span))
                if crc(payload)!=struct.unpack_from('<I',raw,28)[0]:issue('recovery-potentially-required','variable_data_crc',p,i)
                if typ==0x21 and (not length or payload[-1]!=0 or b'\0' in payload[:-1]):issue('invalid','invalid_string_encoding',p,i)
                if typ==0x42:
                    if chunk==255:issue('invalid','blob_data_chunk',p,i)
                    chunks.append(dict(ns=ns,key=bytes(key.split(b'\0',1)[0]),page=p,entry=i,chunk=chunk,length=length,reserved=struct.unpack_from('<H',raw,26)[0]))
                if typ==0x41:legacy.append(dict(ns=ns,key=bytes(key.split(b'\0',1)[0])))
            else:
                issue('unsupported-format','entry_type',p,i);continue
            records.append((ns,typ,key.split(b'\0',1)[0],p,i,chunk))
            if typ not in (0x41,0x42,0x48):other.append(dict(ns=ns,key=bytes(key.split(b'\0',1)[0])))
            if ns==0:
                if typ!=1 or not 1<=raw[24]<=254:issue('invalid','namespace_entry',p,i)
                else:namespace_ids.add(raw[24])
            elif ns==255:issue('invalid','invalid_namespace_index',p,i)
    seen=set()
    for ns,typ,key,p,i,chunk in records:
        if ns and ns not in namespace_ids:issue('insufficient-evidence','namespace_reference_unresolved',p,i)
        # The pinned SDK duplicate identity excludes datatype and includes chunk.
        identity=(ns,key,chunk)
        if identity in seen:issue('recovery-potentially-required','duplicate_live_record',p,i)
        seen.add(identity)
    validate_blobs(indices,chunks,legacy,other,issue)
    if active>1:issue('recovery-potentially-required','multiple_active_pages')
    if free==0:issue('recovery-potentially-required','no_erased_free_page')
    ranking=['invalid','unsupported-format','recovery-potentially-required','insufficient-evidence']
    classification=next((c for c in ranking if any(x['category']==c for x in issues)),'compatible-within-verified-checks')
    return dict(classification=classification,bytes=SIZE,sha256=hashlib.sha256(data).hexdigest(),pages=pages,issues=issues,namespace_count=len(namespace_ids),blob_relationships_checked=True,blob_index_count=len(indices),blob_data_count=len(chunks),sdk_immutability_verified=False,settings_values_validated=False,migration_authorized=False,privacy='No keys, namespace names or values emitted',format_reference='esp-idf b66b5448e0dfac6be135e6f0ac21010aba231180; plaintext subset')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full-backup',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists() or a.full_backup.is_symlink():raise ValueError('Existing output or input symlink rejected')
    if a.full_backup.stat().st_size!=0x1000000:raise ValueError('Expected exact 16 MiB full backup')
    with a.full_backup.open('rb') as f:f.seek(0x9000);data=f.read(SIZE)
    result=inspect(data)
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['classification']);return result['classification']!='compatible-within-verified-checks'
if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError) as e:sys.exit('FAIL: '+str(e))
