"""Retain the unchanged approved startup and protected-core verifier."""
import hashlib
import importlib.util
import pathlib


def load_verifier(root):
    parent = pathlib.Path(root) / 'tests/static_response_build_integration/startup_decode.py'
    assert hashlib.sha256(parent.read_bytes()).hexdigest() == '13ff8a60faa30a2eb1310d734a72737eabb06061fbee9fc54042d9210225156e'
    spec = importlib.util.spec_from_file_location('previous_repeat_startup_parent', parent)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_verifier(root)
