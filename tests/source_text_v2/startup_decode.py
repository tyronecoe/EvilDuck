# Additive source/text-portability adaptation of tests/payload_restart/startup_decode.py
# Parent SHA-256: 89446c879b2432300699f6d8227214d1fb01efff041612a03764f9407dbc55f5
# Additive payload-restart adaptation of tests/text_keyboard/startup_decode.py
# Parent SHA-256: b3ce64a3afe26b8260a990d0018cca7e14cf4b1fd5eea489f23a5e907cac5a0f
"""Use every existing startup and NVS decoder predicate unchanged."""
import hashlib
import importlib.util
import pathlib
PARENT_SHA = '7f20325f8ce1ef17097a90f2178a84864bf7294b2b11d8be7201f506d2457fca'
def load_verifier(root):
    p=pathlib.Path(root)/'tests/lock_feedback/startup_decode.py'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==PARENT_SHA
    s=importlib.util.spec_from_file_location('source_compat_startup_parent',p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    return m.load_verifier(root)
