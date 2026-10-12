#!/usr/bin/env python3
"""Offline compiler stack estimates; never discover or access a device.

Recompile selected translation units from an existing pinned build with GCC's
-fstack-usage. Objects are temporary and never replace the firmware build output.
These per-function estimates exclude library/callee costs and runtime high water.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

MODULES = {'com.cpp', 'duckscript.cpp', 'script_parser.cpp', 'duck_constants.cpp',
           'script_preprocessor.cpp', 'duck_random.cpp', 'duck_vars.cpp', 'duck_expr.cpp', 'script_functions.cpp',
           'keyboard_locale.cpp', 'duck_keys.cpp', 'hid_backend.cpp',
           'usb_msc.cpp', 'attackmode.cpp', 'sd_card.cpp', 'settings.cpp', 'cli.cpp', 'webserver.cpp', 'EvilDuckS3.ino.cpp', 'esp32-hal-misc.c'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build = json.loads((args.build_dir / 's3-build-report.json').read_text())
    if build['core_version'] != '3.3.0' or 'PSRAM=disabled' not in build['fqbn']:
        parser.error('Requires the existing pinned 3.3.0, PSRAM-disabled build')
    commands = json.loads((args.build_dir / 'compile_commands.json').read_text())
    records = []
    found = set()
    with tempfile.TemporaryDirectory(prefix='evilduck-stack-') as directory:
        temporary = Path(directory)
        for entry in commands:
            module = Path(entry['file']).name
            if module not in MODULES:
                continue
            command = list(entry['arguments'])
            command[command.index('-o') + 1] = str(temporary / (module + '.o'))
            command.append('-fstack-usage')
            subprocess.run(command, cwd=entry['directory'], check=True)
            found.add(module)
        if found != MODULES:
            parser.error('Missing source modules in compilation database: ' + str(MODULES - found))
        for source in sorted(temporary.glob('*.su')):
            for line in source.read_text().splitlines():
                symbol, count, qualifier = line.rsplit('\t', 2)
                records.append({'module': source.stem,
                                'symbol': symbol, 'bytes': int(count), 'qualifier': qualifier})
    # Keep compatible with the project's desktop Python >=3.8 expectation.
    report = {'kind': 'per-function compiler estimates, not runtime high-water',
              'core_version': build['core_version'], 'fqbn': build['fqbn'],
              'application_sha256': build['application_sha256'], 'records': records}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    for record in sorted(records, key=lambda item: item['bytes'], reverse=True)[:12]:
        print(record['bytes'], record['qualifier'], record['symbol'])


if __name__ == '__main__':
    main()
