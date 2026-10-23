"""Retain the exact approved setup/NVS decoders and every startup predicate."""
import hashlib
import importlib.util
import pathlib

PARENT_SHA = "48406180324f41371d0803547edc4d0844caf1a7c424f965372de045cbce3aba"


def load_verifier(root):
    path = pathlib.Path(root) / "tests/caps_stop/startup_decode.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == PARENT_SHA
    spec = importlib.util.spec_from_file_location("keyboard_control_startup_parent", path)
    parent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    return parent.load_verifier(root)
