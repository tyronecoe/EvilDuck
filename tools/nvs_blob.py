"""Bounded offline NVS v2 blob relationships. Never retain/output payload values."""
MAX_BLOB_BYTES=127*125*32  # Pinned Item::checkHeaderConsistency ceiling.
ISSUE_CODES=set('blob_index_size_limit blob_index_reserved blob_chunk_start_unsupported blob_zero_chunk_index_unsupported blob_chunk_range blob_multiple_live_indexes blob_legacy_index_coexistence blob_nonblob_key_coexistence blob_data_reserved blob_orphan_data blob_duplicate_chunk blob_missing_chunk blob_extra_chunk blob_total_length blob_noncanonical_empty_layout'.split())

def validate(indices, chunks, legacy, other, issue):
    """Inputs are metadata from at most 630 entries in the fixed five-page inspector.
    Group identifiers remain in memory only. No winner/repair/recursive assembly.
    """
    groups={}
    for category,records in [('indices',indices),('chunks',chunks)]:
        for record in records:
            identity=(record['ns'],record['key'])
            group=groups.setdefault(identity,dict(indices=[],chunks=[]))
            group[category].append(record)
    legacy_keys={(r['ns'],r['key']) for r in legacy}
    other_keys={(r['ns'],r['key']) for r in other}
    for identity,group in groups.items():
        owners=group['indices'];children=group['chunks']
        def finding(category,code,r):issue(category,code,r['page'],r['entry'])
        for child in children:
            if child['reserved']!=0xffff:finding('unsupported-format','blob_data_reserved',child)
        if not owners:
            for child in children:finding('recovery-potentially-required','blob_orphan_data',child)
            continue
        if len(owners)!=1:
            for owner in owners:finding('recovery-potentially-required','blob_multiple_live_indexes',owner)
            continue  # Do not choose a generation offline.
        owner=owners[0]
        if identity in legacy_keys:finding('recovery-potentially-required','blob_legacy_index_coexistence',owner)
        if identity in other_keys:finding('recovery-potentially-required','blob_nonblob_key_coexistence',owner)
        count=owner['count'];start=owner['start'];size=owner['size']
        if size>MAX_BLOB_BYTES:
            finding('invalid','blob_index_size_limit',owner);continue
        if owner['reserved']!=0xffff:finding('unsupported-format','blob_index_reserved',owner)
        if start not in (0,0x80):
            finding('unsupported-format','blob_chunk_start_unsupported',owner);continue
        if count==0:
            finding('unsupported-format','blob_zero_chunk_index_unsupported',owner);continue
        # Version0 is 0..127; version1 is 128..254. Never wrap/use CHUNK_ANY=ff.
        limit=0x80 if start==0 else 0xff
        if start+count>limit:
            finding('invalid','blob_chunk_range',owner);continue
        expected=set(range(start,start+count));by_number={}
        for child in children:
            number=child['chunk']
            if number not in expected:
                finding('recovery-potentially-required','blob_extra_chunk',child);continue
            by_number.setdefault(number,[]).append(child)
        if expected-set(by_number):
            finding('recovery-potentially-required','blob_missing_chunk',owner)
        for number in expected:
            entries=by_number.get(number,[])
            if len(entries)>1:
                for child in entries:finding('recovery-potentially-required','blob_duplicate_chunk',child)
        if set(by_number)==expected and all(len(v)==1 for v in by_number.values()):
            matched=[v[0] for v in by_number.values()]
            if sum(r['length'] for r in matched)!=size:finding('recovery-potentially-required','blob_total_length',owner)
            # Pinned writer/generator emit one empty child for an empty blob.
            if (size==0 and (count!=1 or matched[0]['length']!=0)) or (size>0 and any(r['length']==0 for r in matched)):
                finding('unsupported-format','blob_noncanonical_empty_layout',owner)
