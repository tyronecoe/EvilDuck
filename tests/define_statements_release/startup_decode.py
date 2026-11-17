"""Unmodified approved observer-v2 startup decoder re-export."""
import hashlib
import importlib.util
import pathlib
import sys
sys.dont_write_bytecode = True
_path = pathlib.Path(__file__).resolve().parents[1]/'usb_os_observer_v2_release/startup_decode.py'
assert hashlib.sha256(_path.read_bytes()).hexdigest() == 'b24b11fce9bb97dcb1e48c92b68a0f5701d2b4a2bc2c2854bbcd14c84a7e1356'
_spec = importlib.util.spec_from_file_location('admission_unchanged_observer_startup',_path)
_parent = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_parent)
for _name in dir(_parent):
    if not _name.startswith('__'):
        globals()[_name] = getattr(_parent,_name)
