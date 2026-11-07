"""Normal Route B SOURCE-ONLY composition with bounded standalone REPEAT.

The inherited release verifiers bind the older exact compiler bytes. A later,
separately authorized target-integration stage must extend those verifiers and
assign a new build identity. Until then this entry fails closed for target builds
rather than silently emitting the older image without the new compiler delta.
"""
import argparse
import json
import pathlib
import shutil
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import prepare_sources as selected


def contained(path, parent):
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def compose(source, output):
    source, output = pathlib.Path(source), pathlib.Path(output)
    selected.pin()
    selected.B.verify_final(source)
    assert not output.exists() and not output.is_symlink(), 'OUTPUT_ALREADY_EXISTS'
    assert not contained(output, ROOT), 'OUTPUT_INSIDE_REPOSITORY_REJECTED'
    assert not contained(output, source), 'OUTPUT_INSIDE_SOURCE_REJECTED'
    destination = output / 'EvilDuckS3'
    output.mkdir(parents=True)
    shutil.copytree(source, destination)
    selected.delta(destination)
    rows = selected.verify_final(destination)
    proof = dict(status='SOURCE_ONLY_COMPOSED', source=str(destination), source_count=len(rows),
                 changed_sources=['core.cpp'], unchanged_sources=200, sources=rows,
                 selected_preparer='tests/previous_command_repeat/prepare_sources.py',
                 selected_manifest_sha256=selected.digest(HERE / 'source-manifest.json'),
                 parent_manifest_sha256=selected.PARENT_MANIFEST_SHA,
                 firmware_built=False, target_build_ready=False, hardware_access=False,
                 build_identity='Inherited historical identity; no new firmware image exists')
    (output / 'composition.json').write_text(json.dumps(proof, indent=2) + '\n')
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compose-only', action='store_true')
    parser.add_argument('--from-composed', type=pathlib.Path)
    parser.add_argument('--output-dir', type=pathlib.Path)
    args = parser.parse_args()
    if not args.compose_only:
        parser.error('SOURCE_ONLY_STAGE: target builds require separately reviewed release-verifier integration; use --compose-only')
    if args.from_composed is None or args.output_dir is None:
        parser.error('--compose-only requires --from-composed and --output-dir')
    proof = compose(args.from_composed, args.output_dir)
    print(json.dumps({k: v for k, v in proof.items() if k != 'sources'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
