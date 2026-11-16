#!/usr/bin/env python3
"""DEFINE-specific additive wrapper; exact frozen edits are in edits.json."""
import importlib.util as _imports
import pathlib as _paths
import sys as _sys
_sys.dont_write_bytecode = True
_spec = _imports.spec_from_file_location('define_release_adaptation', _paths.Path(__file__).with_name('adaptation.py'))
_adapter = _imports.module_from_spec(_spec)
_spec.loader.exec_module(_adapter)
_adapter.execute('verify_release', globals())
