#!/usr/bin/env python3
"""Canonical normal Route B build with static response repair selected by default.

Uses the existing approved isolated Arduino ESP32 3.3.0 archive-based profile.
Produces an UNINSTALLED review image, never an installer or device operation.
Historical tools/build_s3*.py and stage builders retain their old compositions.
"""
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/static_response_build_integration'))
from build_candidate import main

if __name__ == '__main__':
    raise SystemExit(main())
