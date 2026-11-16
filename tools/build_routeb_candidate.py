#!/usr/bin/env python3
"""Canonical committed Route B build for DEFINE statements H1 v1.

Requires a local checkpoint and uses the approved isolated ESP32 3.3.0 profile.
--compose-only remains available for exact final source composition inspection.
No installer, upload, OTA, hardware or package interface is exposed here.
Historical tests/admission_diagnostics_release/build_candidate.py and older
tools/build_s3*.py/stage builders retain their explicit old compositions.
"""
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/define_statements_release'))
from build_candidate import main

if __name__ == '__main__':
    raise SystemExit(main())
