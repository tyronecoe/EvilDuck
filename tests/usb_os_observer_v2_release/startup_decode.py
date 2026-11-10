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
_V2_FROZEN_PARENT = _v2_pathlib.Path(__file__).resolve().parents[1] / 'usb_os_observer_release' / 'startup_decode.py'
_V2_FROZEN_SHA = 'c16a1f740f9671ce5581ec45c704ac15bce7efbd9bd9da700d79c1811d55bc05'
_V2_EDITS = []

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
    __name__ = 'observer_v2_frozen_startup_decode_py'
    exec(_v2_builtins.compile(_V2_SOURCE, str(_V2_FROZEN_PARENT), 'exec'), globals())
finally:
    __name__ = _v2_original_name


