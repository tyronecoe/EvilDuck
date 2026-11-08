#!/usr/bin/env python3
"""Canonical committed Route B build for the bounded USB metadata observer.

Requires a local checkpoint and uses the approved isolated ESP32 3.3.0 profile.
--compose-only remains available for exact final source composition inspection.
No installer, upload, OTA, hardware or package interface is exposed here.
Historical tools/build_s3*.py and stage builders retain their old compositions.
"""
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/usb_os_observer_release'))
from build_candidate import main

if __name__ == '__main__':
    raise SystemExit(main())
