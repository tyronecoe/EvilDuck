"""Preserve the exact historical H1 startup decoder and all safety predicates."""
import hashlib
import importlib.util
import pathlib

def load_verifier(root):
    p=pathlib.Path(root)/'tests/inject_var_experimental/startup_decode.py'
    assert hashlib.sha256(p.read_bytes()).hexdigest()=='12b521619e3a2afce4ca85d4228ae09ebc189f830a43f53c07c762d3f2e2edfd'
    s=importlib.util.spec_from_file_location('right_h1_startup_parent',p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    return m.load_verifier(root)
