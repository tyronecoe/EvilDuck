"""Forward the exact privacy startup/core checker without predicate changes."""
import hashlib
import importlib.util
import pathlib


def load_verifier(root):
    parent = pathlib.Path(root) / "tests/privacy_fix1/startup_decode.py"
    assert hashlib.sha256(parent.read_bytes()).hexdigest() == "bd534708173f268a7249242155aff015078fa210920be3184606e718e803d24f"
    spec = importlib.util.spec_from_file_location("dashboard_privacy_startup_parent", parent)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_verifier(root)
