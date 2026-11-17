"""Occurrence-checked additive adapters; immutable admission tools stay intact.

edits.json is reviewable input, covered by the committed-input guard. Counts
below measure syntax nodes, never executed assertions or target verification.
"""
import ast
import hashlib
import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def predicates(text):
    tree = ast.parse(text)
    return dict(asserts=sum(isinstance(n, ast.Assert) for n in ast.walk(tree)),
                require_calls=sum(isinstance(n, ast.Call) and
                                  isinstance(n.func, ast.Name) and n.func.id == 'require'
                                  for n in ast.walk(tree)))


def execute(kind, namespace):
    pin = json.loads((HERE / 'edits.json').read_text())[kind]
    parent = ROOT / pin['parent']
    raw = parent.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Admission tool changed'
    text = raw.decode()
    before = predicates(text)
    for edit in pin['edits']:
        assert text.count(edit['before']) == edit['occurrences'], edit
        text = text.replace(edit['before'], edit['after'])
    assert predicates(text) == before, 'Inherited predicate removed'
    # __file__ deliberately remains the selected DEFINE wrapper. This is how
    # the established nested loaders bind HERE, SELF_PATH and verifier context.
    namespace['DEFINE_ADAPTATION'] = dict(pin, syntax_predicates_retained=before)
    exec(compile(text, str(parent), 'exec'), namespace)
