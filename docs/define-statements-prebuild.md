# DEFINE statements source checkpoint

Candidate identity: `ROUTEB-DEFINE-STATEMENTS-H1-v1`. Development baseline:
`bf339ad383e67c5ee3bb9df1a57bafe15acca8ed`, branch
`routeb-admission-diagnostics-v1`. This checkpoint selects source and verification
rules. It does not establish a target build, installation or hardware acceptance.

`tools/build_routeb_candidate.py` now selects
`tests/define_statements_release/build_candidate.py`. The explicit historical
admission builder remains `tests/admission_diagnostics_release/build_candidate.py`.
No historical builder, manifest, patch or evidence is replaced.

The new preparer applies the complete pinned admission composition, the merged
`tests/define_statements/application.patch`, then `identity.patch` exactly once.
Relative to admission201, only `core.cpp` and the build-ID literal in
`caps_trial.h` differ. The selected core SHA-256 is
`b9c53bd3632e049e674ea66bf6c110bf22bb51c35f0d46ae75e0f5825d069d99`.
The new manifest records the literal's exact before/after hashes and all201
production hashes. Its inherited privacy-relative9/192 and cumulative10/191
sets remain intact; they are different comparisons from the new2/199 delta.

`edits.json` records every occurrence-checked adaptation of the three immutable
admission tools. Their Assert/require syntax counts must stay unchanged. The
target source expectation explicitly permits the reviewed core hash alongside
unchanged admission adapter/header sources. It no longer claims an unchanged
compiler. Both the final201 inventory and identity reversal are mandatory.
The inherited admission target manifest's parent provenance fields continue to
identify the admission runtime preparer. Separate `define_*` and
`admission_release_manifest_sha256` fields pin the additional merged overlay.
This preserves the existing provenance conditions without relabeling history.

The inherited committed-input guard executes before selecting the additional
DEFINE sources, native helper copies, offline controls and this document. Exact
Git blob comparisons remain mandatory. The frozen190 release Assert nodes and
dependency/archive, SDK, USB, startup, partition, PSRAM, stack, RAM, workspace,
streaming and linked-object conditions remain in the inherited verifiers.
Their syntax retention is an offline check; executing those190 artifact
assertions requires an actual target build. All target/link/resource checks
remain pending at this checkpoint.

## Bounded offline closeout

Reuse the already completed core34 and adapter evidence; do not rerun suites.
`verify_evidence.py` verifies the prior receipts,238 adapter input hashes,
44 evidence files,201 production bindings, recovered native inventory, patched
core/SDK, libraries, CLI identity and saved property output without executing
the compiler or initializing Arduino. The saved property command is historical
property resolution, not an actual firmware compilation.

After committing all selected source inputs, use fresh external destinations:

```sh
python -B tests/define_statements_release/verify_evidence.py --output /workspace/scratch/define-statements-prebuild-v1/evidence-final.json
python -B tools/build_routeb_candidate.py --compose-only --from-composed /workspace/scratch/define-statements-resume-preflight-v1/candidate/EvilDuckS3 --output-dir /workspace/scratch/define-statements-prebuild-v1/final-composition
python -B tests/define_statements_release/test_prebuild.py --source /workspace/scratch/define-statements-prebuild-v1/final-composition/EvilDuckS3 --admission-source /workspace/scratch/define-statements-resume-preflight-v1/candidate/EvilDuckS3 --output /workspace/scratch/define-statements-prebuild-v1/offline-controls.json
```

The fail-fast controls check exact composition, omitted overlay, old/missing
identity, missing/extra source, unrelated drift, repeated identity application,
real nested imports and old-selector refusals, frozen predicates and whole-file
safety-guard identities. A disposable local clone exercises actual dirty,
untracked and Git-hidden byte mismatches. No original checkout is mutated by
those controls. The receipt distinguishes test groups, negative mutations,
syntax nodes and runtime assertion counts. It must not claim target PASS.

## Preserved native test sources

`tests/define_statements_release/native/` contains byte copies of the passing
isolated journal, lower-layer instrumentation, repaired DS02 driver and owning
HTTP mock. `provenance.json` records their hashes and original passing receipt.
The original executable, compile command, generated fixture bindings, sanitizer
settings, count-only failure and journals remain in external evidence and the
prebuild evidence bundle. These copies are for reproducibility; existing native
executions are reused, and no compilation from relocated inputs is claimed.
They are outside the201-file firmware inventory. The copied driver still
requires the hash-verified external parent fixture/includes; they are not
replaced with reconstructed test infrastructure.

## Later target command — NOT EXECUTED by this task

```sh
python -B tools/build_routeb_candidate.py --output-dir /workspace/scratch/define-statements-target-build-v1 --config /workspace/scratch/define-statements-cli-init-recovery-v1/arduino-cli-init-recovery.json --core /workspace/scratch/define-statements-dependency-recovery-v4/firmware/data/packages/esp32/hardware/esp32/3.3.0 --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 2
```

The output directory must not already exist. The existing guarded driver retains
its exact controlled-start H1 selectors and observer flag/link wrapper, ESP32
3.3.0/IDF5.5-b66b5448 SDK, esp-x32/2411 compiler,16MiB qio/QSPI profile,
PSRAM disabled and7,602,176-byte application slots. CLI1.3.1 and the recovered
configuration are reused. One actual compilation requires subsequent explicit
approval. A failure must preserve evidence and stop; no automatic rebuild.

Future gates: real ELF/BIN and compile/link provenance, application/RAM/object
sizes, stack frames and deltas, complete release chain, then separately approved
macOS firmware review ZIP/offline verification and harmless owner acceptance.
No target or resource result is supplied by a prebuild source gate.

## Rollback identities remain distinct

- Admission diagnostics: `ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1`, firmware commit
  `c9fd36c3e03b2d7ffa318b289398ff7dc1c9fd44`; application SHA-256
  `fce91bca0774181a1be6bc691a1303d47f61caba49e979e89bfa678ef41f60f1`.
- Accepted DEFINE return: `ROUTEB-DEFINE-LABELS-H1-v1`, firmware commit
  `5d9176dd15f722ffe20d219d33684da7461d1754`; original ZIP SHA-256
  `b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed`;
  application `167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`.
- Separate older source/text-v2 application:1,413,200 bytes, SHA-256
  `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.

These references do not prove current installation or physical recovery. No
target compilation, firmware packaging, push, PR, flash or hardware operation
is authorized by this source closeout.
