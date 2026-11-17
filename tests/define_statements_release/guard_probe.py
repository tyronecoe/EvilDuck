"""Run only the real committed-input guard, including in disposable controls."""
import importlib.util
import pathlib
import sys
sys.dont_write_bytecode = True
path = pathlib.Path(__file__).with_name('build_candidate.py')
spec = importlib.util.spec_from_file_location('define_git_guard_probe', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.build_inputs()
print('PASS committed input guard; no compiler')
