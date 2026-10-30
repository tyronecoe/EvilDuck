#!/usr/bin/env python3
"""Synthetic parser tests only; never official runtime execution."""
import copy
import hashlib
import importlib.util
import json
import pathlib
import sys
sys.dont_write_bytecode = True
P = pathlib.Path(__file__).with_name('reference_results.py')
spec = importlib.util.spec_from_file_location('reference_results', P)
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)


def receipt(order='little', swapped=False):
    markers = b''.join(v.to_bytes(2, order) for v in M.MARKERS)
    # Fixed independently specified samples: a=usage4, Z=Shift+usage29,
    # 0=usage39, !=Shift+usage30. These are synthetic H1/H2 hypotheses.
    values = [0x0004, 0x021d, 0x0027, 0x021e]
    if swapped:
        values = [((v & 255) << 8) | (v >> 8) for v in values]
    raw = markers + b''.join(v.to_bytes(2, order) * 6 for v in values) + markers
    return dict(format='synthetic-ds3-reference-capture-v1', mode='four-groups',
                synthetic_data_only=True, append_offset=123, capture_length=len(raw),
                capture_hex=raw.hex(), capture_sha256=hashlib.sha256(raw).hexdigest(),
                metadata=dict(device_model='SYNTHETIC MOCK', device_firmware='NOT EXECUTED',
                              compiler_id='MOCK', language_map_sha256='1'*64,
                              source_sha256='2'*64, compiled_sha256='3'*64,
                              host_os='MOCK', host_layout='US', caps_lock=False,
                              authenticity_limitations='Synthetic bytes; no device.', run_id='SYNTHETIC-1'),
                observations=[dict(group=g, property=p, visible_pair=c*2,
                                   visible_evidence_id='SYNTHETIC-'+g)
                              for g, p, c in zip(M.GROUPS, M.PROPERTIES, 'aZ0!')])


def rehash(r, raw):
    r['capture_hex'] = raw.hex(); r['capture_length'] = len(raw)
    r['capture_sha256'] = hashlib.sha256(raw).hexdigest()


def reject(r):
    try: M.inspect(r)
    except (M.InvalidReceipt, TypeError): return
    raise AssertionError('bad receipt accepted')


cases = []
def case(name, fn):
    fn(); cases.append(dict(name=name, status='PASS'))

for order in ('little', 'big'):
    def positive(order=order):
        out=M.inspect(receipt(order)); assert out['byte_order']==order
        assert all(g['h1_matches_text_derived_us_reports'] and g['copy_unchanged'] and
                   g['original_unchanged'] for g in out['groups'])
        assert all(g['official_runtime_value'] is None for g in out['groups'])
        assert not out['canonical_contract_established']
    case(order+'_calibration_and_h1', positive)
    def competing(order=order):
        out=M.inspect(receipt(order, True)); assert all(g['h2_matches_text_derived_us_reports'] for g in out['groups'])
        assert not any(g['h1_matches_text_derived_us_reports'] for g in out['groups'])
    case(order+'_distinguishes_h2', competing)

def mutation():
    r=receipt(); b=bytearray.fromhex(r['capture_hex']); b[12:14]=(5).to_bytes(2,'little'); rehash(r,bytes(b))
    out=M.inspect(r); assert not out['groups'][0]['copy_unchanged']
case('mutation_is_preserved_not_hidden', mutation)
for name, mutate in [
 ('truncated', lambda r: rehash(r, bytes.fromhex(r['capture_hex'])[:-1])),
 ('extra_bytes', lambda r: rehash(r, bytes.fromhex(r['capture_hex'])+b'\0')),
 ('missing_metadata', lambda r: r.pop('metadata')),
 ('missing_visible_evidence', lambda r: r['observations'][0].pop('visible_evidence_id')),
 ('unsupported_layout', lambda r: r['metadata'].update(host_layout='DE')),
 ('caps_unknown', lambda r: r['metadata'].update(caps_lock=None)),
 ('private_data_not_confirmed', lambda r: r.update(synthetic_data_only=False)),
 ('bad_offset', lambda r: r.update(append_offset=-1)),
 ('bad_hash', lambda r: r.update(capture_sha256='0'*64)),
 ('wrong_group', lambda r: r['observations'][0].update(property='$_RANDOM_INT')),
 ('ambiguous_calibration', lambda r: rehash(r, b'\0'*60)),
 ('trailing_calibration_mismatch', lambda r: rehash(r, bytes.fromhex(r['capture_hex'])[:-6]+b'\0'*6)),
]:
    def negative(mutate=mutate):
        r=receipt(); mutate(r); reject(r)
    case(name,negative)

def calibration_only():
    r=receipt();r['mode']='calibration';rehash(r,bytes.fromhex(r['capture_hex'])[:6]);out=M.inspect(r)
    assert out['byte_order']=='little' and not out['canonical_contract_established']
case('calibration_only_before_injection_review',calibration_only)
result=dict(status='PASS_SYNTHETIC_PARSER_CHECKS_ONLY',counts=dict(PASS=len(cases),FAIL=0),
            results=cases,official_runtime_executed=False,hardware_access=False,
            canonical_runtime_contract_established=False)
print(json.dumps(result,indent=2))
