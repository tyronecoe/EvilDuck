#!/usr/bin/env python3
"""Bind exact verified static-response artifacts to the frozen Mac installer.

No compiler, device, network or private-backup access. The only generated
installer delta is RELEASE_BINDING. Artifact identities must first be frozen in
release-binding.json and committed with these packaging sources.
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
PARENT = ROOT / 'tests/h1_right_modifiers/package.py'
PARENT_SHA = 'b29c8995bf36668da89e092975c3f83cba7214e33349f12050dde7b82db773b2'
DASHBOARD = ROOT / 'tests/dashboard_cleanup/package.py'
DASHBOARD_SHA = 'e696ed2dcb7bea8d8cf0057e526ac86e1f283bcc0116b99fe597459493d82efa'
PACKAGE = 'evilduck-static-response-repair-h1-macos-review-v1'
BUILD_ID = 'ROUTEB-STATIC-RESPONSE-REPAIR-v1'
REVIEWED_REPAIR_COMMIT = '7c3ed81238b89b89b92924c366ecbb9afe391856'
FAULTY_APP_SHA = 'e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0'
ROLLBACK_SHA = 'cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02'
ROLLBACK_BYTES = 1413200
REQUIRED_SOURCE = ['tests/static_response_review_package/' + n for n in
                   ['package.py', 'package_preflight.py', 'test_package.py', 'release-binding.json']] + [
                  'docs/static-response-repair-' + n for n in ['report.md', 'acceptance.md', 'reproduction.md', 'platforms.md', 'results.json']]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def release_binding():
    value = json.loads((HERE / 'release-binding.json').read_text())
    assert value['format'] == 'evilduck-static-response-release-binding-v1'
    assert value['status'] == 'VERIFIED_LOCAL_RELEASE', 'Exact new build identities must be frozen before packaging'
    assert value['build_id'] == BUILD_ID
    assert re.fullmatch('[0-9a-f]{40}', value['source_commit'])
    assert re.fullmatch('[0-9a-f]{40}', value['verifier_context_commit'])
    assert value['verifier_context_commit'] != value['source_commit']
    assert re.fullmatch('[0-9a-f]{40}', value['completion_context_commit'])
    for key in ['application_sha256', 'elf_sha256', 'release_receipt_sha256', 'build_inputs_sha256', 'static_target_binding_sha256', 'verification_delta_sha256', 'completion_receipt_sha256', 'completion_helper_sha256']:
        assert re.fullmatch('[0-9a-f]{64}', value[key]), key
    assert value['application_sha256'] not in (FAULTY_APP_SHA, ROLLBACK_SHA), 'Previous image substitution prohibited'
    assert value['application_bytes'] > 0 and value['elf_bytes'] > 0
    return value


def documents(binding):
    common = ('**REVIEW ONLY — NOT INSTALLED — NOT OWNER-HARDWARE-VERIFIED.**\n\n'
              'This package authorizes no installation, boot, physical test or script execution. H1 remains opt-in '
              'and experimental; canonical Hak5 numeric encoding is unresolved.\n\n')
    identity = ('Build ID: `' + BUILD_ID + '`. Application: **' + str(binding['application_bytes']) +
                ' bytes**, SHA-256 `' + binding['application_sha256'] + '`. Firmware source: `' + binding['source_commit'] +
                '`. These are exact verified new artifacts, not a claim about installed device bytes.\n\n')
    offline = ('First, extract into a new folder, keep EvilDuck **unplugged**, and run only:\n\n'
               '```bash\npython3 preflight.py --directory .\n```\n\n'
               'Expect exit 0, package_integrity=PASS, installed_metadata=NOT_SUPPLIED, plan_ready=false, '
               'selected_write_ranges=[], hardware_access=false and installation_authorized=false. Stop on rejection. '
               'This command is offline; Python 3.8+ standard library only. The install launcher default performs '
               'hardware checks and is NOT this offline step.\n\n')
    rollback = ('Exact older source/text-v2 rollback: **1,413,200 bytes**, SHA-256 `' + ROLLBACK_SHA + '`. '
                'It does not contain Privacy Fix 1 or the subsequent dashboard/editor/static-response repairs. '
                'It is standalone application code, not a complete flash/filesystem recovery image. Application '
                'rollback does not restore deleted scripts or past settings. Preserve every existing backup.\n\n')
    provenance = ('The new application was clean-built from committed source `' + binding['source_commit'] +
                  '`, including the reviewed static-response delta. build-inputs.json and source-attestation.json '
                  'bind those Git blobs. A host-verifier-only correction at `' + binding['verifier_context_commit'] +
                  '` reverified the unchanged compiled image; the compiler context remains the original source commit. '
                  'The attestation retains all 26 original compile-input rows, with only the explicitly verified '
                  'target-verifier row different in the later checkout. No old uncommitted-build provenance is reused. '
                  'The full inherited link/disassembly safeguards and new actual streaming-response proof are '
                  'recorded in build-receipt.json. postcompile-completion.json records the host-only completion helper `' +
                  binding['completion_context_commit'] + '`, unchanged image/input hashes and its exact read-only '
                  'compiler linker-location query; it did not compile firmware.\n\n')
    future = ('Only after separate physical authorization, the existing Mac workflow uses '
              '`bash install-macos.sh --action check --port CURRENT_PORT`, then separately '
              '`bash install-macos.sh --action install --port CURRENT_PORT`; deliberate rollback uses '
              '`bash rollback-macos.sh --port CURRENT_PORT`. Never run the placeholder literally. Rediscover '
              'the port after reconnects. High Sierra 10.13.6, Bash 3.2, Python 3.8+ and preinstalled esptool '
              '4.12.0 remain the target; no dependency is installed/downloaded by this package. Native platform '
              'and physical dashboard acceptance are pending.\n\n'
              'The unchanged installer checks ESP32-S3/16 MiB, security, exact current partition table/OTA '
              'metadata, images and bounded ranges. It creates a new **private full-flash backup before its '
              'final INSTALL confirmation** (or ROLLBACK confirmation); it may contain credentials, scripts and '
              'settings and remains if final confirmation is declined. Keep backups and raw receipts private. '
              'No existing backup is deleted or overwritten. Both application slots are bounded at 0x10000 '
              'and 0x750000 within 0x740000-byte slots. Bootloader, partition table, NVS, OTA metadata, SPIFFS and '
              'coredump are excluded. No automatic reset/reboot, retry, format, settings reset or script Start '
              'occurs. Stop on write/compare failure for a separate recovery review.\n\n')
    historical = ('The inherited source-stage identity `ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1` is historical '
                  'provenance, NOT this candidate Build ID. Prior keyboard/right-modifier, lock-wait, executed STOP '
                  'and scoped privacy milestones remain closed. Four historical rm-*.txt files are provenance '
                  'only; do not execute them for this transport repair.\n\n'
                  'The previous editor-safety image `' + FAULTY_APP_SHA + '` remains historical evidence: the '
                  'owner observed empty JavaScript/Checking on hardware. It is **not a known-good recovery image**. '
                  'The new candidate is not declared fixed on hardware before separate owner acceptance.\n\n')
    return {'README.md': common + identity + offline + provenance + rollback + historical +
                         'Read OWNER-CHECK.md, INSTALL-MAC.md and ROLLBACK-MAC.md. This release repairs static '
                         'resource serving and preserves the existing authentication/editor/keyboard paths.\n',
            'INSTALL-MAC.md': common + identity + offline + provenance + rollback + future + historical,
            'ROLLBACK-MAC.md': common + rollback + offline + future + historical}


def adapter(binding, attestation_file, completion_file):
    assert sha(PARENT) == PARENT_SHA and sha(DASHBOARD) == DASHBOARD_SHA
    dashboard = load(DASHBOARD, 'static_review_dashboard_parent')
    _, inherited = dashboard.adapter(binding['source_commit'], binding['application_sha256'], binding['application_bytes'],
                                     binding['elf_sha256'], binding['release_receipt_sha256'])
    text = PARENT.read_text()
    for row in inherited:
        assert text.count(row['before']) == row['occurrences']
        text = text.replace(row['before'], row['after'])
    changes = []
    def replace(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old))
        text = text.replace(old, new)
        changes.append(dict(before=old, after=new, occurrences=count))
    replace(repr(dashboard.PACKAGE), repr(PACKAGE))
    replace('tests/dashboard_cleanup/package_preflight.py', 'tests/static_response_review_package/package_preflight.py', 2)
    for name in ['acceptance', 'report', 'platforms', 'reproduction']:
        replace('docs/dashboard-cleanup-' + name + '.md', 'docs/static-response-repair-' + name + '.md')
    replace('docs/dashboard-cleanup-browser-results.json', 'docs/static-response-repair-results.json')
    replace('    for name, source in copies.items():',
            "    copies['reviewed-editor-source-manifest.json'] = ROOT/'tests/editor_load_safety/source-manifest.json'\n"
            "    copies['editor-build-source-manifest.json'] = ROOT/'tests/editor_build_integration/source-manifest.json'\n"
            "    copies['response-source-manifest.json'] = ROOT/'tests/dashboard_response_safety/source-manifest.json'\n"
            "    copies['static-response-build-source-manifest.json'] = ROOT/'tests/static_response_build_integration/source-manifest.json'\n"
            "    copies['build-inputs.json'] = build_root/'build-inputs.json'\n"
            "    copies['source-attestation.json'] = ATTESTATION_FILE\n"
            "    copies['postcompile-completion.json'] = COMPLETION_FILE\n"
            '    for name, source in copies.items():')
    replace('firmware_build_id=' + repr(dashboard.BUILD_ID) + ',', 'firmware_build_id=' + repr(BUILD_ID) + ',')
    replace('composition_base_commit=' + repr(dashboard.BASE_COMMIT), 'composition_base_commit=' + repr(REVIEWED_REPAIR_COMMIT))
    replace('dashboard_release_receipt_sha256=RECEIPT_SHA', 'static_release_receipt_sha256=RECEIPT_SHA')
    anchor = "    (out/'preflight.py').write_text("
    replace(anchor,
            "    bound.update(editor_pin_sha256=sha(ROOT/'tests/editor_load_safety/source-manifest.json'),\n"
            "        editor_build_pin_sha256=sha(ROOT/'tests/editor_build_integration/source-manifest.json'),\n"
            "        response_pin_sha256=sha(ROOT/'tests/dashboard_response_safety/source-manifest.json'),\n"
            "        static_build_pin_sha256=sha(ROOT/'tests/static_response_build_integration/source-manifest.json'),\n"
            "        static_build_adapter_sha256=sha(ROOT/'tests/static_response_build_integration/build_candidate.py'),\n"
            "        static_release_adapter_sha256=sha(ROOT/'tests/static_response_build_integration/verify_release.py'),\n"
            "        static_target_verifier_sha256=sha(ROOT/'tests/static_response_build_integration/verify_target.py'),\n"
            "        build_inputs_sha256=FROZEN_BINDING['build_inputs_sha256'],\n"
            "        source_attestation_sha256=sha(ATTESTATION_FILE), application_elf_sha256=ELF_SHA,\n"
            "        application_elf_bytes=FROZEN_BINDING['elf_bytes'],\n"
            "        static_target_binding_sha256=FROZEN_BINDING['static_target_binding_sha256'],\n"
            "        verifier_context_commit=FROZEN_BINDING['verifier_context_commit'],\n"
            "        verification_delta_sha256=FROZEN_BINDING['verification_delta_sha256'],\n"
            "        completion_receipt_sha256=FROZEN_BINDING['completion_receipt_sha256'],\n"
            "        completion_helper_sha256=FROZEN_BINDING['completion_helper_sha256'],\n"
            "        completion_context_commit=FROZEN_BINDING['completion_context_commit'])\n" + anchor)
    anchor = "    (out/'manifest.json').write_text("
    replace(anchor,
            "    manifest.update(static_response_profile='STATIC_RESPONSE_REPAIR_H1_OWNER_REVIEW',\n"
            "        firmware_source_identity_kind='COMMITTED_CLEAN_BUILD_INPUTS', source_checkpoint_after_build=False,\n"
            "        status_label='NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED', application_elf_bytes=FROZEN_BINDING['elf_bytes'],\n"
            "        reviewed_editor_pin_sha256=sha(out/'reviewed-editor-source-manifest.json'),\n"
            "        editor_build_pin_sha256=sha(out/'editor-build-source-manifest.json'),\n"
            "        response_composition_pin_sha256=sha(out/'response-source-manifest.json'),\n"
            "        static_response_build_pin_sha256=sha(out/'static-response-build-source-manifest.json'),\n"
            "        build_inputs_sha256=FROZEN_BINDING['build_inputs_sha256'], source_attestation_sha256=sha(out/'source-attestation.json'),\n"
            "        verifier_context_commit=FROZEN_BINDING['verifier_context_commit'],\n"
            "        verification_delta_sha256=FROZEN_BINDING['verification_delta_sha256'], post_build_verifier_only_delta=True,\n"
            "        completion_receipt_sha256=FROZEN_BINDING['completion_receipt_sha256'],\n"
            "        completion_helper_sha256=FROZEN_BINDING['completion_helper_sha256'],\n"
            "        completion_context_commit=FROZEN_BINDING['completion_context_commit'],\n"
            "        previous_faulty_application_sha256='" + FAULTY_APP_SHA + "', previous_faulty_candidate_is_recovery=False,\n"
            "        static_packaging_parent_sha256='" + DASHBOARD_SHA + "')\n" + anchor)
    namespace = dict(__name__='static_review_frozen_packager', __file__=str(PARENT),
                     GENERATED_DOCS=documents(binding), ATTESTATION_FILE=pathlib.Path(attestation_file),
                     COMPLETION_FILE=pathlib.Path(completion_file), FROZEN_BINDING=binding)
    exec(compile(text, str(PARENT), 'exec'), namespace)
    return namespace, inherited, changes


def verifier_delta(binding, rows):
    compiler, verifier = binding['source_commit'], binding['verifier_context_commit']
    assert re.fullmatch('[0-9a-f]{40}', compiler) and re.fullmatch('[0-9a-f]{40}', verifier)
    assert compiler != verifier
    for earlier, later in [(compiler, verifier), (verifier, 'HEAD')]:
        subprocess.run(['git', 'merge-base', '--is-ancestor', earlier, later], cwd=ROOT, check=True)
    allowed = 'tests/static_response_build_integration/verify_target.py'
    assert len(rows) == 26 and len({row['file'] for row in rows}) == 26
    changes = []
    for row in rows:
        assert set(row) == {'file', 'size', 'sha256'} and not row['file'].startswith('/') and '..' not in row['file'].split('/')
        old = subprocess.check_output(['git', 'show', compiler + ':' + row['file']], cwd=ROOT)
        assert len(old) == row['size'] and hashlib.sha256(old).hexdigest() == row['sha256'], row['file']
        selected = ROOT / row['file']
        assert selected.is_file() and not selected.is_symlink()
        assert ROOT.resolve() in selected.resolve().parents
        current = selected.read_bytes()
        if current != old:
            assert row['file'] == allowed, 'Unapproved post-build change: ' + row['file']
            committed = subprocess.check_output(['git', 'show', verifier + ':' + allowed], cwd=ROOT)
            assert committed == current, 'Current verifier differs from exact D commit'
            last = subprocess.check_output(['git', 'log', '-1', '--format=%H', 'HEAD', '--', allowed], cwd=ROOT, text=True).strip()
            assert last == verifier, 'Verifier context is not its exact last-touch commit'
            changes.append(dict(file=allowed, before=dict(row),
                                after=dict(file=allowed, size=len(current), sha256=hashlib.sha256(current).hexdigest())))
    assert len(changes) == 1, 'Require exactly the independently recorded host verifier delta'
    return dict(format='evilduck-static-response-host-verifier-delta-v1',
                compiler_source_commit=compiler, verifier_context_commit=verifier,
                file=allowed, before=changes[0]['before'], after=changes[0]['after'],
                original_compile_input_rows_verified=26, other_compile_inputs_identical=25,
                git_blobs_verified=True, role='HOST_VERIFICATION_ONLY',
                compiled_application_sources_changed=False, firmware_recompiled=False)


def completion_helper_context(binding):
    name = 'tests/static_response_postlink/complete_existing.py'
    commit = binding['completion_context_commit']
    data = (ROOT/name).read_bytes()
    assert sha(ROOT/name) == binding['completion_helper_sha256']
    assert subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT) == data
    assert subprocess.check_output(['git','log','-1','--format=%H','HEAD','--',name],cwd=ROOT,text=True).strip() == commit
    subprocess.run(['git','merge-base','--is-ancestor',binding['verifier_context_commit'],commit],cwd=ROOT,check=True)
    subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=ROOT,check=True)
    return dict(file=name,source_commit=commit,size=len(data),sha256=hashlib.sha256(data).hexdigest(),
                git_blob_verified=True,role='HOST_POSTCOMPILE_COMPLETION_ONLY')


def verify_completion(path, linked_report, binding, target_binding):
    assert sha(path) == binding['completion_receipt_sha256']
    value = json.loads(pathlib.Path(path).read_text())
    release = json.loads(pathlib.Path(linked_report).read_text())
    assert value['status']=='PASS' and value['firmware_recompiled'] is False and value['hardware'] is False
    assert value['actual_compile_source_commit']==binding['source_commit']
    assert value['verifier_context_commit']==binding['verifier_context_commit']
    assert value['post_compile_verifier_delta']==target_binding['committed_source_provenance']['post_compile_verifier_delta']
    assert value['immutable_artifacts']==dict(application_sha256=binding['application_sha256'],elf_sha256=binding['elf_sha256'],inputs_sha256=binding['build_inputs_sha256'])
    assert value['release_receipt_sha256']==binding['release_receipt_sha256'] and value['unchanged_source_entries']==201
    adapter = value['post_compile_completion_adapter']
    assert adapter['helper_sha256']==binding['completion_helper_sha256']
    assert adapter['firmware_compilation_prefix_rerun'] is False and adapter['all_target_and_release_predicates_after_compile_preserved'] is True
    for query in value['read_only_compiler_queries']:
        assert query['command']==[release['link_command'][0],'-print-prog-name=ld']
        assert query['classification']=='READ_ONLY_PINNED_LINKER_LOCATION_QUERY' and query['pinned_compiler_sha256']==release['compiler_sha256']
    assert len(value['read_only_compiler_queries'])==1
    completion_helper_context(binding)
    return value


def source_attestation(build_root, binding):
    file = pathlib.Path(build_root) / 'build-inputs.json'
    assert sha(file) == binding['build_inputs_sha256']
    value = json.loads(file.read_text())
    assert value['format'] == 'evilduck-committed-build-inputs-v1'
    assert value['source_commit'] == binding['source_commit'] and value['source_commit_contains_changes'] is True
    assert value['uncommitted_local_changes'] is False
    assert canonical(value['files']) == value['files_sha256']
    delta = verifier_delta(binding, value['files'])
    assert canonical(delta) == binding['verification_delta_sha256'], 'Host verifier delta must be frozen exactly'
    return dict(format='evilduck-committed-build-source-attestation-v1', source_commit=binding['source_commit'],
                source_commit_contains_changes=True, source_checkpoint_after_build=False,
                git_blobs_verified=True, build_inputs_sha256=sha(file), files=value['files'],
                files_sha256=value['files_sha256'], hardware=False,
                verifier_context_commit=binding['verifier_context_commit'],
                post_build_verifier_delta=delta, verification_delta_sha256=canonical(delta),
                postcompile_completion_helper=completion_helper_context(binding))


def prepare(directory, build_root, linked_report, core, source_commit, completion_report):
    binding = release_binding()
    assert re.fullmatch('[0-9a-f]{40}', source_commit)
    for ancestor in [REVIEWED_REPAIR_COMMIT, binding['source_commit']]:
        subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, source_commit], cwd=ROOT, check=True)
    for name in REQUIRED_SOURCE:
        assert subprocess.check_output(['git', 'show', source_commit + ':' + name], cwd=ROOT) == (ROOT/name).read_bytes(), name
    build_root, linked_report = pathlib.Path(build_root).resolve(), pathlib.Path(linked_report).resolve()
    target = load(ROOT / 'tests/static_response_build_integration/verify_target.py', 'static_review_exact_target')
    target_binding = target.verify(build_root)
    assert canonical(target_binding) == binding['static_target_binding_sha256']
    recorded = target_binding['committed_source_provenance']
    own_delta = verifier_delta(binding, json.loads((build_root/'build-inputs.json').read_text())['files'])
    expected_delta = dict(path=own_delta['file'], compile_source_commit=own_delta['compiler_source_commit'],
                          verification_context_commit=own_delta['verifier_context_commit'],
                          compile_size=own_delta['before']['size'], compile_sha256=own_delta['before']['sha256'],
                          verification_size=own_delta['after']['size'], verification_sha256=own_delta['after']['sha256'],
                          git_compile_blob_verified=True, git_verifier_blob_verified=True)
    assert recorded['verifier_context_commit'] == binding['verifier_context_commit']
    assert recorded['post_compile_verifier_delta'] == expected_delta, 'Source attestation disagrees with actual target verifier provenance'

    assert sha(linked_report) == binding['release_receipt_sha256'], 'Exact new verified release receipt required'
    verify_completion(completion_report, linked_report, binding, target_binding)
    receipt = json.loads(linked_report.read_text())
    built = json.loads((build_root/'report.json').read_text())
    evidence = receipt['static_response_release_verification']
    assert evidence['status'] == 'PASS' and evidence['full_frozen_h1_chain_executed'] is True
    assert evidence['source_commit'] == binding['source_commit'] and evidence['source_commit_contains_changes'] is True
    assert evidence['build_inputs_sha256'] == binding['build_inputs_sha256']
    assert evidence['application_sha256'] == binding['application_sha256'] and evidence['elf_sha256'] == binding['elf_sha256']
    assert evidence['actual_runtime_build_id'] == receipt['actual_runtime_build_id'] == BUILD_ID
    assert evidence['adapter_sha256'] == sha(ROOT/'tests/static_response_build_integration/verify_release.py')
    assert evidence['assertions_preserved'] == 190 and evidence['assertions_removed'] == evidence['unrelated_expected_hashes_changed'] == 0
    assert evidence['historical_source_pin_build_ids_changed'] is False
    assert evidence['recompiled'] is False and evidence['target_source_or_images_modified'] is False
    assert evidence['static_response_target_binding'] == target_binding == built['static_response_target_adapter']['static_response_target_binding']
    assert receipt['static_response_target_adapter'] == built['static_response_target_adapter']
    for name in ['source_inventory', 'report', 'provenance']:
        assert receipt[name] == built[name], name
    app, elf = build_root/'build/EvilDuckS3.ino.bin', build_root/'build/EvilDuckS3.ino.elf'
    assert app.stat().st_size == binding['application_bytes'] and sha(app) == binding['application_sha256']
    assert elf.stat().st_size == binding['elf_bytes'] and sha(elf) == binding['elf_sha256']
    for name, key in [('tests/dashboard_response_safety/source-manifest.json', 'static_response_source_pin'),
                      ('tests/static_response_build_integration/source-manifest.json', 'static_response_build_source_pin')]:
        assert receipt[key] == json.loads((ROOT/name).read_text()), key
    attestation = source_attestation(build_root, binding)
    with tempfile.TemporaryDirectory(prefix='public-static-source-attestation-') as temporary:
        attestation_file = pathlib.Path(temporary)/'source-attestation.json'
        attestation_file.write_text(json.dumps(attestation, indent=2)+'\n')
        namespace, inherited, changes = adapter(binding, attestation_file, completion_report)
        manifest = namespace['prepare'](directory, build_root, linked_report, core, source_commit)
    return manifest, inherited, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['directory', 'build-root', 'linked-report', 'completion-report', 'core', 'archive']:
        parser.add_argument('--'+name, type=pathlib.Path, required=True)
    parser.add_argument('--source-commit', required=True)
    args = parser.parse_args()
    prepare(args.directory, args.build_root, args.linked_report, args.core, args.source_commit, args.completion_report)
    binding = release_binding()
    namespace, _, _ = adapter(binding, args.directory/'source-attestation.json', args.completion_report)
    print(json.dumps(namespace['archive'](args.directory, args.archive), indent=2))


if __name__ == '__main__':
    main()
