#!/usr/bin/env python3
"""Private, read-only blob graph checks using independent synthetic format vectors."""
import argparse, hashlib, json, os, struct, subprocess, sys, tempfile
import importlib.util
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from nvs_inspect import inspect, crc
from nvs_source_prepare import verify
from nvs_blob import ISSUE_CODES
from deployment_summary import summary

ROWS = []
ASSERTIONS = 0
KEY = b'private-blob'
SECRET = b'synthetic-private-payload'

def check(value, message):
    global ASSERTIONS
    ASSERTIONS += 1
    if not value:
        raise AssertionError(message)

def case(name, fn):
    before = ASSERTIONS
    try:
        fn()
        status, error = 'PASS', ''
    except Exception as e:
        status, error = 'FAIL', str(e)
    ROWS.append(dict(name=name, status=status, assertions=ASSERTIONS-before, error=error))
    print(status, name, error, flush=True)

def header(d, page, active):
    off = page * 4096
    struct.pack_into('<II', d, off, 0xfffffffe if active else 0xfffffffc, page+1)
    d[off+8] = 0xfe
    struct.pack_into('<I', d, off+28, crc(d[off+4:off+28]))

def entry(d, page, slot, ns, typ, key, metadata, payload=b'', chunk=255):
    span = 1 + (len(payload)+31)//32 if typ in (0x21, 0x41, 0x42) else 1
    if slot+span > 126:
        raise ValueError('Synthetic fixture page overflow')
    off = page*4096+64+slot*32
    raw = bytearray(b'\xff'*32)
    raw[:4] = bytes([ns, typ, span, chunk])
    raw[8:8+len(key)] = key
    raw[8+len(key)] = 0
    raw[24:24+len(metadata)] = metadata
    struct.pack_into('<I', raw, 4, crc(raw[:4]+raw[8:]))
    d[off:off+32] = raw
    d[off+32:off+32+len(payload)] = payload
    for i in range(slot, slot+span):
        d[page*4096+32+i//4] &= ~(1 << (i%4*2))
    return span

def fixture(children=None, size=None, count=None, start=0, index_page=0,
            index=True, extra_indices=(), extras=(), reserved=0xffff):
    # Child: (physical page, chunk index, payload [, namespace [, key]])
    children = [(0, start, SECRET)] if children is None else children
    d = bytearray(b'\xff'*0x5000)
    cursor = [0]*5
    locations = dict(children=[], indices=[], extras=[])
    entry(d, 0, 0, 0, 1, b'private-ns', b'\x01')
    entry(d, 0, 1, 0, 1, b'private-ns-two', b'\x02')
    cursor[0] = 2
    for child in children:
        page, chunk, payload = child[:3]
        ns = child[3] if len(child)>3 else 1
        key = child[4] if len(child)>4 else KEY
        locations['children'].append((page, cursor[page]))
        meta = struct.pack('<HHI', len(payload), 0xffff, crc(payload))
        cursor[page] += entry(d, page, cursor[page], ns, 0x42, key, meta, payload, chunk)
    if size is None:
        size = sum(len(child[2]) for child in children)
    if count is None:
        count = len(children)
    specs = [(index_page, size, count, start, reserved)] if index else []
    specs += list(extra_indices)
    for page, total, number, first, res in specs:
        locations['indices'].append((page, cursor[page]))
        cursor[page] += entry(d, page, cursor[page], 1, 0x48, KEY,
                             struct.pack('<IBBH', total, number, first, res))
    for page, ns, typ, key, value in extras:
        locations['extras'].append((page, cursor[page]))
        if typ in (0x21, 0x41):
            meta = struct.pack('<HHI', len(value), 0xffff, crc(value))
            cursor[page] += entry(d, page, cursor[page], ns, typ, key, meta, value)
        else:
            cursor[page] += entry(d, page, cursor[page], ns, typ, key, value)
    used = [p for p, n in enumerate(cursor) if n]
    for p in used:
        header(d, p, p==max(used))
    return d, locations

def change(d, location, relative, value, recalc=True):
    p, i = location
    off = p*4096+64+i*32
    d[off+relative:off+relative+len(value)] = value
    if recalc:
        struct.pack_into('<I', d, off+4, crc(d[off:off+4]+d[off+8:off+32]))

def result(vector, expected='compatible-within-verified-checks', code=None):
    d = vector[0] if isinstance(vector, tuple) else vector
    before = bytes(d)
    report = inspect(d)
    check(report['classification']==expected, 'classification '+report['classification'])
    if code:
        check(any(x['code']==code for x in report['issues']), 'expected generic issue '+code)
    else:
        check(not report['issues'], 'healthy fixture has no findings')
    check(bytes(d)==before, 'source bytes unchanged')
    text = json.dumps(report)
    check(all(s not in text for s in ['private-blob', 'private-ns', 'synthetic-private-payload']), 'no private names/values')
    check(report['sdk_immutability_verified'] is False and report['migration_authorized'] is False,
          'no immutability/migration claim')
    return report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk-source', type=Path, required=True)
    p.add_argument('--generator-dir', type=Path, required=True)
    p.add_argument('--results', type=Path, required=True)
    a = p.parse_args()
    verify(a.sdk_source)
    pin = json.loads((ROOT/'docs/stage19-generator-pin.json').read_text())
    for row in pin['files']:
        if hashlib.sha256((a.generator_dir/row['path']).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Pinned generator source mismatch')
    case('blob_single_chunk', lambda:result(fixture()))
    case('blob_empty_writer_layout', lambda:result(fixture(children=[(0,0,b'')], size=0)))
    case('blob_cross_page', lambda:result(fixture(children=[(0,0,b'a'),(1,1,b'b')], index_page=2)))
    case('blob_reversed_physical_order', lambda:result(fixture(children=[(2,0,b'a'),(0,1,b'b')], index_page=1)))
    case('blob_second_generation', lambda:result(fixture(children=[(1,128,b'a'),(0,129,b'b')], start=128)))
    case('blob_same_key_different_namespace', lambda:result(fixture(extras=[(1,2,1,KEY,b'\x01')])))
    case('blob_maximum_page_payload', lambda:result(fixture(children=[(1,0,b'a'*4000)])))
    case('blob_generation_zero_exact_limit', lambda:result(fixture(children=[(i//50,i,b'a') for i in range(128)], index_page=3)))
    case('blob_generation_one_exact_limit', lambda:result(fixture(children=[(i//50,128+i,b'a') for i in range(127)], start=128,index_page=3)))
    def legacy():
        result(fixture(children=[],index=False,extras=[(0,1,0x41,KEY,SECRET)]))
    case('blob_legacy_standalone', legacy)
    recovery = 'recovery-potentially-required'
    negative = [
        ('blob_missing_child', dict(children=[],size=1,count=1), recovery, 'blob_missing_chunk'),
        ('blob_gap_with_matching_count_and_sum', dict(children=[(0,0,b'a'),(1,2,b'b')]), recovery,'blob_missing_chunk'),
        ('blob_extra_child', dict(children=[(0,0,b'a'),(1,1,b'b')],size=1,count=1), recovery,'blob_extra_chunk'),
        ('blob_duplicate_child', dict(children=[(0,0,b'a'),(1,0,b'b')],size=1,count=1), recovery,'blob_duplicate_chunk'),
        ('blob_orphan_child', dict(index=False), recovery,'blob_orphan_data'),
        ('blob_wrong_namespace_child', dict(children=[(1,0,b'a',2)]), recovery,'blob_missing_chunk'),
        ('blob_wrong_key_child', dict(children=[(1,0,b'a',1,b'another-key')]), recovery,'blob_missing_chunk'),
        ('blob_opposite_generation_child', dict(children=[(1,128,b'a')],start=0), recovery,'blob_extra_chunk'),
        ('blob_duplicate_index', dict(extra_indices=[(1,len(SECRET),1,0,65535)]), recovery,'blob_multiple_live_indexes'),
        ('blob_two_live_generations', dict(extra_indices=[(1,len(SECRET),1,128,65535)]), recovery,'blob_multiple_live_indexes'),
        ('blob_legacy_coexistence', dict(extras=[(1,1,0x41,KEY,b'a')]), recovery,'blob_legacy_index_coexistence'),
        ('blob_scalar_coexistence', dict(extras=[(0,1,1,KEY,b'\x01')]), recovery,'blob_nonblob_key_coexistence'),
        ('blob_string_coexistence_cross_page', dict(extras=[(1,1,0x21,KEY,b'a\0')]), recovery,'blob_nonblob_key_coexistence'),
        ('blob_total_length_mismatch', dict(size=1), recovery,'blob_total_length'),
        ('blob_invalid_generation', dict(start=1), 'unsupported-format','blob_chunk_start_unsupported'),
        ('blob_zero_count', dict(children=[],size=0,count=0), 'unsupported-format','blob_zero_chunk_index_unsupported'),
        ('blob_generation_one_limit_plus_one', dict(start=128,count=128), 'invalid','blob_chunk_range'),
        ('blob_generation_zero_limit_plus_one', dict(count=129), 'invalid','blob_chunk_range'),
        ('blob_size_limit_plus_one', dict(size=508001), 'invalid','blob_index_size_limit'),
        ('blob_unknown_index_reserved', dict(reserved=0), 'unsupported-format','blob_index_reserved'),
        ('blob_empty_child_in_nonempty', dict(children=[(0,0,b''),(1,1,b'a')]), 'unsupported-format','blob_noncanonical_empty_layout'),
        ('blob_multiple_empty_children', dict(children=[(0,0,b''),(1,1,b'')]), 'unsupported-format','blob_noncanonical_empty_layout'),
    ]
    for name, kwargs, expected, code in negative:
        case(name, lambda kwargs=kwargs, expected=expected, code=code:result(fixture(**kwargs),expected,code))
    def mutated(which, relative, value, expected, code, recalc=True):
        d, loc = fixture()
        change(d, loc[which][0], relative, value, recalc)
        result(d,expected,code)
    case('blob_invalid_index_chunk',lambda:mutated('indices',3,b'\x00','invalid','blob_index_chunk'))
    case('blob_invalid_data_chunk',lambda:mutated('children',3,b'\xff','invalid','blob_data_chunk'))
    case('blob_unknown_data_reserved',lambda:mutated('children',26,b'\0\0','unsupported-format','blob_data_reserved'))
    case('blob_header_crc_error',lambda:mutated('indices',4,b'\0\0\0\0',recovery,'entry_header_crc',False))
    case('blob_payload_crc_error',lambda:mutated('children',32,b'X',recovery,'variable_data_crc'))
    case('blob_span_error',lambda:mutated('children',2,b'\x01','invalid','variable_span_length'))
    def incomplete():
        d, loc=fixture()
        p,i=loc['children'][0]
        d[p*4096+32+(i+1)//4] |= 1 << ((i+1)%4*2)
        result(d,recovery,'incomplete_variable_span')
    case('blob_incomplete_bitmap_span',incomplete)
    def page_boundary():
        d=bytearray(b'\xff'*0x5000);header(d,0,True)
        entry(d,0,125,1,0x42,KEY,struct.pack('<HHI',0,65535,crc(b'')),chunk=0)
        change(d,(0,125),2,b'\x02')
        result(d,'invalid','entry_span_boundary')
    case('blob_span_cross_page',page_boundary)
    def multi():
        d,loc=fixture()
        p,i=loc['indices'][0];slot=i+1
        slot+=entry(d,0,slot,1,0x42,b'second-key',struct.pack('<HHI',1,65535,crc(b'z')),b'z',0)
        entry(d,0,slot,1,0x48,b'second-key',struct.pack('<IBBH',1,1,0,65535))
        r=result(d);check(r['blob_index_count']==2 and r['blob_data_count']==2,'two independent blobs counted')
    case('blob_multiple_independent_keys',multi)
    def generator(length):
        gen=a.sdk_source/'components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py'
        with tempfile.TemporaryDirectory(prefix='evilduck-blob-generator-') as t:
            t=Path(t);csv=t/'input.csv';csv.write_text('key,type,encoding,value\nsynthetic,namespace,,\nprivate-blob,data,hex2bin,'+('61'*length)+'\n')
            env=dict(os.environ);env['PYTHONPATH']=str(a.generator_dir);env['PYTHONDONTWRITEBYTECODE']='1'
            run=subprocess.run([sys.executable,str(gen),'generate',str(csv),str(t/'nvs.bin'),'0x5000'],env=env,capture_output=True,text=True)
            check(run.returncode==0,'pinned official generator succeeds')
            r=result((t/'nvs.bin').read_bytes())
            check(r['blob_index_count']==1 and r['blob_data_count']>=1,'official writer blob graph counted')
    for length in [0,1,32,33,3904,3968,4000,8000,12000]:
        case('blob_official_generator_'+str(length),lambda length=length:generator(length))
    spec=importlib.util.spec_from_file_location('summary_fixtures', ROOT/'tests/stage20/summary_tests.py')
    summary_fixtures=importlib.util.module_from_spec(spec);spec.loader.exec_module(summary_fixtures)
    def shareable():
        private=summary_fixtures.base();private['nvs_structure']=inspect(fixture(children=[(0,0,b'a'),(1,2,b'b')])[0])
        private['nvs_structure']['private-key']='private-blob'
        before=json.dumps(private,sort_keys=True);out=summary(private)
        check(out['nvs_classification']=='recovery-potentially-required','new graph findings preserved')
        check(json.dumps(private,sort_keys=True)==before,'private input unchanged')
        check('private-blob' not in json.dumps(out),'no name/extra property leak')
        check(out['migration_authorized'] is False,'graph findings never authorize migration')
    case('blob_privacy_summary_new_graph_findings',shareable)
    def codes():
        private=summary_fixtures.base()
        private['nvs_structure'].update(classification='invalid',issues=[dict(category='invalid',code=code,page=0,entry=1) for code in sorted(ISSUE_CODES)])
        out=summary(private)
        check(len(out['nvs_findings'])==len(ISSUE_CODES),'all new generic finding codes recognized')
        check(out['migration_authorized'] is False,'recognized findings not approval')
    case('blob_summary_code_allowlist',codes)
    def owner_record():
        r=json.loads((ROOT/'docs/stage20-owner-preflight-evidence.json').read_text())
        check(r['reported_results']['nvs_classification']=='insufficient-evidence','historical reported classification retained')
        check(r['reported_results']['nvs_issue_count']==10 and r['reported_results']['issue_counts']==dict(blob_data_relationships_unverified=5,blob_index_relationships_unverified=5),'exact reported unresolved counts')
        check(r['codex_independently_inspected'] is False and r['extended_blob_relationship_rerun_reported'] is False,'no invented owner inspection')
        check(r['migration_status']=='NO-GO' and r['owner_nvs_structural_compatibility_established'] is False,'owner preservation gate remains')
    case('blob_owner_evidence_boundaries',owner_record)
    verify(a.sdk_source)
    out=dict(results=ROWS,counts={s:sum(r['status']==s for r in ROWS) for s in ['PASS','FAIL']},assertions=ASSERTIONS,
             sdk_source_commit='b66b5448e0dfac6be135e6f0ac21010aba231180',owner_files_inspected=False,
             hardware_access=False,sdk_initializer_executed=False,fixture_images_only=True)
    with a.results.open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))
    return bool(out['counts']['FAIL'])
if __name__=='__main__':raise SystemExit(main())
