"""Forward the exact historical dashboard startup/core guards."""
import hashlib
import importlib.util
import pathlib


def load_verifier(root):
    parent = pathlib.Path(root) / 'tests/dashboard_cleanup/startup_decode.py'
    assert hashlib.sha256(parent.read_bytes()).hexdigest() == 'da27df2f2ec53e7fe07c8f280357bfd031d845eab836b76680996d509933a6bd'
    spec = importlib.util.spec_from_file_location('editor_build_startup_parent', parent)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_verifier(root)
