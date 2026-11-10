#!/usr/bin/env python3
"""Occurrence-checked v2 adapter over an immutable complete observer-v1 tool.

All original function bodies and predicates remain; exact path/identity edits
are listed below. Additional v2 proof requirements are appended after loading.
"""
import pathlib as _v2_pathlib
import hashlib as _v2_hashlib
import builtins as _v2_builtins
import sys as _v2_sys
_v2_sys.dont_write_bytecode = True
_V2_FROZEN_PARENT = _v2_pathlib.Path(__file__).resolve().parents[1] / 'usb_os_observer_release' / 'build_candidate.py'
_V2_FROZEN_SHA = 'd07ab71ef92c9af5bb8cbe43b82ec9237156353e3ae004c9b5e0b924aafe72ca'
_V2_EDITS = [('tests/usb_os_observer_release/', 'tests/usb_os_observer_v2_release/', 2), ("'tests/usb_os_observer_release'", "'tests/usb_os_observer_v2_release'", 1), ("'tests/usb_os_observer_web'", "'tests/usb_os_observer_v2_web'", 1), ("'tests/usb_os_observer'", "'tests/usb_os_observer_v2'", 1), ('ROUTEB-USB-ENUM-OBSERVER-H1-v1', 'ROUTEB-USB-ENUM-OBSERVER-H1-v2', 1), ('bdc8cbeea024ebb63f952da7fc4f39ac9e32fe29', 'fe6ed1c291a2af234793cca86aa9b8c979ac6d8e', 1), ('docs/usb-os-observer-contract.md', 'docs/usb-os-observer-v2-contract.md', 1), ('docs/usb-os-evidence-gate.json', 'docs/usb-os-observer-v2-evidence.json', 1), ('USB ENUMERATION CAPTURE ONLY / DEFINE LABELS / DEL / REPEAT / PRIVACY / H1 EXPERIMENTAL / REVIEW ONLY', 'USB ENUMERATION EVIDENCE V2 / DEFINE LABELS / DEL / REPEAT / PRIVACY / H1 EXPERIMENTAL / REVIEW ONLY', 1)]

def _v2_frozen_source():
    raw = _V2_FROZEN_PARENT.read_bytes()
    assert _v2_hashlib.sha256(raw).hexdigest() == _V2_FROZEN_SHA, 'Historical observer-v1 tool changed'
    text = raw.decode()
    for before, after, count in _V2_EDITS:
        assert text.count(before) == count, ('Observer-v2 adapter occurrence mismatch', before, text.count(before))
        text = text.replace(before, after)
    return text

_V2_SOURCE = _v2_frozen_source()
_v2_original_name = __name__
try:
    __name__ = 'observer_v2_frozen_build_candidate_py'
    exec(_v2_builtins.compile(_V2_SOURCE, str(_V2_FROZEN_PARENT), 'exec'), globals())
finally:
    __name__ = _v2_original_name


DOC_INPUTS += ['docs/usb-os-observer-v1-owner-evidence/HANDOFF.txt'] + ['docs/usb-os-observer-v1-owner-evidence/export-%d.json'%i for i in range(5)]

_V2_INNER_BUILD_INPUTS = build_inputs

def build_inputs():
    # Execute the full original v1 committed-input guard before extending it.
    parent = load(_V2_FROZEN_PARENT, 'observer_v2_unchanged_v1_build_guard')
    inherited = parent.build_inputs()
    current = _V2_INNER_BUILD_INPUTS()
    assert inherited['source_commit'] == current['source_commit']
    names = {row['file'] for row in inherited['files']} | {row['file'] for row in current['files']}
    rows=[]
    for name in sorted(names):
        path=ROOT/name
        assert path.is_file() and not path.is_symlink()
        assert subprocess.check_output(['git','show',current['source_commit']+':'+name],cwd=ROOT)==path.read_bytes(),name
        rows.append(dict(file=name,size=path.stat().st_size,sha256=sha(path)))
    current.update(files=rows,files_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        inherited_observer_v1_guard=dict(file=str(_V2_FROZEN_PARENT.relative_to(ROOT)),sha256=_V2_FROZEN_SHA,
            executed_unmodified=True,files_sha256=inherited['files_sha256']))
    return current

_V2_INNER_TARGET_MAIN = target_main

def target_main():
    code=_V2_INNER_TARGET_MAIN()
    if code:return code
    output=pathlib.Path(sys.argv[sys.argv.index('--output-dir')+1])
    report=json.loads((output/'report.json').read_text())
    report['usb_observer_v2_frozen_adapter']=dict(parent=str(_V2_FROZEN_PARENT.relative_to(ROOT)),parent_sha256=_V2_FROZEN_SHA,
        exact_edits=[dict(before=a,after=b,occurrences=n) for a,b,n in _V2_EDITS],
        adapted_parent_sha256=hashlib.sha256(_V2_SOURCE.encode()).hexdigest(),old_predicates_removed=0)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
