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
_V2_FROZEN_PARENT = _v2_pathlib.Path(__file__).resolve().parents[1] / 'usb_os_observer_release' / 'run_regressions.py'
_V2_FROZEN_SHA = '2d9443de64a036351c3edf47d28b4f1501ec5c92b483b228d24586dd12d02ce4'
_V2_EDITS = [('tests/usb_os_observer_web/', 'tests/usb_os_observer_v2_web/', 1), ('tests/usb_os_observer/', 'tests/usb_os_observer_v2/', 2), ('ROUTEB-USB-ENUM-OBSERVER-H1-v1', 'ROUTEB-USB-ENUM-OBSERVER-H1-v2', 1)]

_V2_EDITS += [(
    " backend.delta(destination)\n web.delta(destination)",
    " original_backend=load(ROOT/'tests/usb_os_observer/prepare_sources.py','observer_v2_native_original_backend_'+label)\n"
    " original_web=load(ROOT/'tests/usb_os_observer_web/prepare_sources.py','observer_v2_native_original_web_'+label)\n"
    " original_backend.delta(destination)\n original_web.delta(destination)\n backend.delta(destination)\n web.delta(destination)",
    1)]

_V2_EDITS += [("mock_source = ROOT / 'tests/usb_os_observer_v2/mocks'", "mock_source = ROOT / 'tests/usb_os_observer/mocks'",1)]

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
    __name__ = 'observer_v2_frozen_run_regressions_py'
    exec(_v2_builtins.compile(_V2_SOURCE, str(_V2_FROZEN_PARENT), 'exec'), globals())
finally:
    __name__ = _v2_original_name


if __name__ == '__main__':
    raise SystemExit(main())
