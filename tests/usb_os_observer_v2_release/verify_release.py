#!/usr/bin/env python3
"""Occurrence-checked v2 adapter over an immutable complete observer-v1 tool.

All original function bodies and predicates remain; exact path/identity edits
are listed below. Additional v2 proof requirements are appended after loading.
"""
import pathlib as _v2_pathlib
import hashlib as _v2_hashlib
import builtins as _v2_builtins
import sys as _v2_sys
_v2_sys.dont_write_bytecode = True
_V2_FROZEN_PARENT = _v2_pathlib.Path(__file__).resolve().parents[1] / 'usb_os_observer_release' / 'verify_release.py'
_V2_FROZEN_SHA = '5f20387df2f322e6744a9d75a78ed054dd88f7bd80764d3462d4e25ff9f29c32'
_V2_EDITS = [('tests/usb_os_observer_release/', 'tests/usb_os_observer_v2_release/', 3), ('ROUTEB-USB-ENUM-OBSERVER-H1-v1', 'ROUTEB-USB-ENUM-OBSERVER-H1-v2', 1)]

def _v2_frozen_source():
    raw = _V2_FROZEN_PARENT.read_bytes()
    assert _v2_hashlib.sha256(raw).hexdigest() == _V2_FROZEN_SHA, 'Historical observer-v1 tool changed'
    text = raw.decode()
    for before, after, count in _V2_EDITS:
        assert text.count(before) == count, ('Observer-v2 adapter occurrence mismatch', before, text.count(before))
        text = text.replace(before, after)
    return text

_V2_SOURCE = _v2_frozen_source()
_v2_original_name = __name__
try:
    __name__ = 'observer_v2_frozen_verify_release_py'
    exec(_v2_builtins.compile(_V2_SOURCE, str(_V2_FROZEN_PARENT), 'exec'), globals())
finally:
    __name__ = _v2_original_name


_V2_INNER_RUN_CHAIN = run_chain

def run_chain(build_root,output):
    report=_V2_INNER_RUN_CHAIN(build_root,output)
    # Keep v1 manifests as immutable historical provenance. Current v2 layers
    # have separate fields and are checked against the actual target binding.
    for key,directory in [('usb_observer_v2_source_pin','usb_os_observer_v2'),
                          ('usb_observer_v2_web_source_pin','usb_os_observer_v2_web'),
                          ('usb_observer_v2_build_source_pin','usb_os_observer_v2_release')]:
        report[key]=json.loads((ROOT/'tests'/directory/'source-manifest.json').read_text())
    info=report['usb_observer_release_verification'];v2=info['usb_observer_target_binding']['usb_observer']['v2_contract']
    assert v2['schema']=='evilduck-usb-observer-v2' and v2['window_ms']==5000 and v2['diagnostic_tail_ms']==5000 and v2['total_ms']==10000
    assert all(v2[key] for key in ['immutable_deadline_source_pinned','generation_tagged_samples_source_pinned',
        'timestamped_records_source_pinned','first_unsupported_witness_source_pinned','tail_cannot_revalidate_source_pinned'])
    info['v2_frozen_adapter']=dict(parent=str(_V2_FROZEN_PARENT.relative_to(ROOT)),parent_sha256=_V2_FROZEN_SHA,
        exact_edits=[dict(before=a,after=b,occurrences=n) for a,b,n in _V2_EDITS],old_predicates_removed=0)
    pathlib.Path(output).write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__ == '__main__':
    raise SystemExit(main())
