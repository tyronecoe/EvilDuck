#!/usr/bin/env python3
"""Add source-delta identity and keyboard call-edge proofs to pinned link checks."""
import hashlib
import json
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENT = ROOT / "tests/caps_stop/verify_link.py"
PARENT_SHA = "bf2c6a7050a2601f285f7e76eb26936399f2b07a12bc56f212903e645ccb4e6d"
BUILD_ID = "ROUTEB-KEYBOARD-CONTROL-20261022-v1"


def main():
    source = PARENT.read_bytes()
    assert hashlib.sha256(source).hexdigest() == PARENT_SHA
    text = source.decode()
    # Preserve each existing fingerprint except the explicitly pinned final
    # application layer. Parent archives, routing/startup predicates and all
    # unrelated source checks remain unchanged.
    anchor = "for x in manifest()['outputs']:"
    assert text.count(anchor) == 1
    injection = ("keyboard_pin=json.loads((ROOT/'tests/keyboard_control/source-manifest.json').read_text())\n"
                 "after.update({x['file']:x['sha256'] for x in keyboard_pin['after']})\n")
    text = text.replace(anchor, injection+anchor)
    old = "assert b'CAPS-STOP-TRACE-20261019-v1' in elf.read_bytes()"
    assert text.count(old) == 1
    text = text.replace(old, "assert "+repr(BUILD_ID.encode())+" in elf.read_bytes()")
    # Let the inherited checker run every predicate and record its full evidence.
    namespace = {"__name__": "keyboard_control_link_adapter", "__file__": str(__file__)}
    exec(compile(text, str(__file__), "exec"), namespace)
    args = namespace["a"]
    report = json.loads(args.output.read_text())
    core = pathlib.Path(report["provenance"]["core"])
    sketch = args.build_root / "candidate/EvilDuckS3"
    pin = json.loads((ROOT/"tests/keyboard_control/source-manifest.json").read_text())
    assert pin["baseline"] == "cb3a147719850a0dc4a4797b401b606ea14c6571"
    assert pin["required_flag"] == "EVILDUCK_ROUTE_B_KEYBOARD_CONTROL=1"
    assert pin["build_id"] == BUILD_ID
    assert hashlib.sha256((ROOT/"tests/keyboard_control/application.patch").read_bytes()).hexdigest() == pin["patch_sha256"]
    assert hashlib.sha256((ROOT/"tests/caps_stop/prepare_sources.py").read_bytes()).hexdigest() == pin["parent_prepare_sha256"]
    original = json.loads((ROOT/"docs/caps-stop-build.json").read_text())
    original_hashes = {pathlib.Path(row["file"]).name: row["sha256"] for row in original["source_inventory"]}
    assert {row["file"] for row in pin["before"]} == {row["file"] for row in pin["after"]}
    for row in pin["before"]:
        assert original_hashes[row["file"]] == row["sha256"]
    for row in pin["after"]:
        assert hashlib.sha256((sketch/row["file"]).read_bytes()).hexdigest() == row["sha256"]
    entries = json.loads((args.build_root/"build/compile_commands.json").read_text())
    for entry in entries:
        if pathlib.Path(entry["file"]).is_relative_to(args.build_root/"build/sketch"):
            assert "-DEVILDUCK_ROUTE_B_KEYBOARD_CONTROL=1" in entry["arguments"]
    symbols = report["symbols"]
    for symbol in ("route_b::ownership(", "route_b::modifier(", "backend_b::ownership("):
        assert symbol in symbols, symbol
    compiler = pathlib.Path(report["link_command"][0])
    prefix = str(compiler).rsplit("g++", 1)[0]
    elf = args.build_root / "build/EvilDuckS3.ino.elf"
    # Manglings are discovered from actual symbols rather than fabricated labels.
    raw_symbols = subprocess.check_output([prefix+"nm", "--defined-only", str(elf)], text=True)
    demangled = subprocess.check_output([prefix+"nm", "-C", "--defined-only", str(elf)], text=True)
    by_address = {line.split()[0]: line.split(maxsplit=2)[2] for line in raw_symbols.splitlines() if len(line.split()) == 3}
    bodies = {}
    for pattern in ("route_b::ownership(", "route_b::modifier(", "backend_b::ownership(", "native_b::Adapter::receive("):
        matches = [line for line in demangled.splitlines() if pattern in line and " T " in line]
        assert len(matches) == 1, (pattern, matches)
        name = by_address[matches[0].split()[0]]
        body = subprocess.check_output([prefix+"objdump", "-d", "--disassemble="+name, str(elf)], text=True)
        assert "<"+name+">:" in body
        bodies[pattern] = body
    assert "queueRaw" in bodies["backend_b::ownership("], "Ownership does not reach the actual report-submission function"
    assert "backendAllowed" in bodies["backend_b::ownership("], "Ownership permission gate absent from linked function"
    assert "route_b" in bodies["native_b::Adapter::receive("]
    # Verify both new admissions are reachable from the actual Adapter dispatch,
    # rather than merely finding unreferenced definitions in the ELF.
    receive_body = subprocess.check_output([prefix+"c++filt"], input=bodies["native_b::Adapter::receive("], text=True)
    assert "route_b::ownership(" in receive_body and "route_b::modifier(" in receive_body
    report["profile"] = "ROUTE B KEYBOARD CONTROL REVIEW ONLY; PHYSICAL VALIDATION PENDING"
    report["keyboard_control_source_pin"] = pin
    report["keyboard_control_verified"] = True
    report["keyboard_linked_functions"] = bodies
    report["keyboard_link_adapter"] = dict(historical_source="tests/caps_stop/verify_link.py",
        historical_sha256=PARENT_SHA, adapter_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        inherited_safety_predicates_removed=0, changed_source_identity="exact final keyboard_control/source-manifest after hashes",
        build_id=BUILD_ID)
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print("PASS keyboard source identity, profile guard and linked ownership/modifier functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
