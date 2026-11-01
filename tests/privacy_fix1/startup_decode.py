"""Forward to the exact H1 startup/core verifier without changing predicates."""
import hashlib
import importlib.util
import pathlib


def load_verifier(root):
    parent = pathlib.Path(root) / "tests/h1_right_modifiers/startup_decode.py"
    assert hashlib.sha256(parent.read_bytes()).hexdigest() == "159a565231ea33cace7ea15235f94ef960199d21c5678ee0d0225de09fde0e0c"
    spec = importlib.util.spec_from_file_location("privacy_h1_startup_parent", parent)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_verifier(root)
