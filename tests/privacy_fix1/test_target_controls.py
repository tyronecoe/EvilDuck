#!/usr/bin/env python3
"""Read-only rejection controls over existing real compile evidence.

Only intercepted reads differ for negative controls; no source/artifact is edited
and no firmware is compiled or executed by this script.
"""
import argparse
import json
import pathlib
from unittest.mock import patch

from verify_target import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-root", required=True, type=pathlib.Path)
    parser.add_argument("--baseline-build-root", required=True, type=pathlib.Path)
    parser.add_argument("--output", required=True, type=pathlib.Path)
    args = parser.parse_args()
    assert not args.output.exists()
    root = args.build_root.resolve()
    results = []
    assert verify(root)["status"] == "PASS"
    results.append(dict(id="unchanged-real-evidence", status="PASS"))

    def denied(name, operation, expected):
        try:
            operation()
        except ValueError as error:
            assert expected in str(error), (name, str(error))
            results.append(dict(id=name, status="EXPECTED_REJECTION", reason=str(error)))
        else:
            raise AssertionError("Unsafe evidence accepted: " + name)

    denied("old-H1-without-privacy", lambda: verify(args.baseline_build_root),
           "Candidate source identity mismatch: cli.cpp")

    read_bytes = pathlib.Path.read_bytes
    compiled = root / "build/sketch/cli.cpp"

    def altered_cli(path):
        data = read_bytes(path)
        return data + b"\n// synthetic compiled-input mismatch\n" if path == compiled else data

    with patch.object(pathlib.Path, "read_bytes", altered_cli):
        denied("changed-compiled-CLI", lambda: verify(root), "Compiled source bytes differ from privacy source: cli.cpp")

    read_text = pathlib.Path.read_text
    dependency = root / "build/sketch/webserver.cpp.d"
    header = root / "build/sketch/webfiles.h"

    def missing_header(path, *values, **keywords):
        text = read_text(path, *values, **keywords)
        return text.replace(str(header), "/synthetic/unreviewed-header.h") if path == dependency else text

    with patch.object(pathlib.Path, "read_text", missing_header):
        denied("missing-patched-header-dependency", lambda: verify(root),
               "Patched webfiles.h absent from actual webserver dependencies")

    commands = root / "build/compile_commands.json"

    def missing_selector(path, *values, **keywords):
        text = read_text(path, *values, **keywords)
        if path == commands:
            entries = json.loads(text)
            entry = next(e for e in entries if pathlib.Path(e["file"]).name == "cli.cpp")
            entry["arguments"].remove("-DEVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1")
            return json.dumps(entries)
        return text

    with patch.object(pathlib.Path, "read_text", missing_selector):
        denied("missing-H1-opt-in-selector", lambda: verify(root), "Application profile selector missing")

    report_path = root / "report.json"
    report = json.loads(read_text(report_path))
    nvs_archive = pathlib.Path(next(row["file"] for row in report["linked_input_hashes"]
        if "/esp32-arduino-libs/" in row["file"] and row["file"].endswith("/libnvs_flash.a")))

    def altered_sdk(path):
        data = read_bytes(path)
        # The isolated SDK path is a symlink to the pinned archive store.
        # Intercept the actual file read, regardless of its recorded alias.
        return data + b"synthetic SDK mismatch" if path.resolve() == nvs_archive.resolve() else data

    with patch.object(pathlib.Path, "read_bytes", altered_sdk):
        denied("changed-pinned-NVS-archive", lambda: verify(root), "Installed pinned SDK archive changed:")

    def missing_sdk_record(path, *values, **keywords):
        text = read_text(path, *values, **keywords)
        if path == report_path:
            record = json.loads(text)
            record["linked_input_hashes"] = [row for row in record["linked_input_hashes"]
                                            if row["file"] != str(nvs_archive)]
            return json.dumps(record)
        return text

    with patch.object(pathlib.Path, "read_text", missing_sdk_record):
        denied("incomplete-linked-SDK-inventory", lambda: verify(root),
               "Actual map LOAD SDK coverage differs from build report")
    result = dict(status="PASS", positive_checks=1, expected_rejections=6,
                  results=results, altered_real_files=False, firmware_compiled=False, hardware=False)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
