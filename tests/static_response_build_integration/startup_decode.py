"""Retain the exact editor/dashboard startup and approved core guards."""
import hashlib
import importlib.util
import pathlib


def load_verifier(root):
    parent = pathlib.Path(root) / 'tests/editor_build_integration/startup_decode.py'
    assert hashlib.sha256(parent.read_bytes()).hexdigest() == '785400a5c3b50eb9654ebfaf571d1f53ea25730d05aaec2ddb7b9f7aa5d2be2f'
    spec = importlib.util.spec_from_file_location('static_response_startup_parent', parent)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_verifier(root)
