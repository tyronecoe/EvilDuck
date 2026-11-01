# Privacy Fix 1 — target integration and clean compile

**PASS for the identified source composition, clean target compilation and
compiled-input binding. This is a source review, not a firmware release or
installation approval.** No distributable package or installer was created.

The reviewed source-only checkpoint is
[`93cc8d1a7b162bdda91e239d840a3eee8a70c51c`](https://github.com/tyronecoe/EvilDuck/commit/93cc8d1a7b162bdda91e239d840a3eee8a70c51c),
based on the unchanged right-modifier owner closeout
`a04e54309c9c73bae17ef23c48283828dfebc0ad`. The separate integration commit adds
the target entry point and this evidence. The application patch and its reviewed
201-file source manifest are unchanged from that checkpoint.

## Explicit composition and build ownership

The maintained [privacy builder](../tests/privacy_fix1/build_candidate.py) selects
the [privacy preparer](../tests/privacy_fix1/prepare_sources.py), rather than the
historical H1 preparer. Its wrapper calls the existing privacy overlay exactly
once: H1 composition runs once, followed by the privacy delta with before/after
hash checks and zero patch fuzz. A fresh candidate tree must match all 201 entries
before compilation: only `cli.cpp`, `webserver.cpp` and `webfiles.h` differ from
the recorded H1 source; 198 entries remain byte-identical. There are no extra
metadata-only source differences.

The preparer gained compatibility re-exports of the unchanged H1 library/source
helpers. A thin, hash-pinned startup-decoder forwarder retains the original
protected-core/startup/checked-settings predicates. Historical builders, decoders,
patches, profiles and verifiers are not edited. The source-only manifest's
earlier build-authorization field remains historical checkpoint metadata; this
separately authorized adapter is the explicit target entry point.

The [new target verifier](../tests/privacy_fix1/verify_target.py) binds:

- Candidate and postcompile source inventories to the reviewed manifest.
- Actual compiled CLI/server bytes to those sources, allowing only Arduino's
  exact source-location prefix.
- The patched `webfiles.h` bytes to the header actually named in the server's GCC
  dependency file, rather than merely finding a copied header on disk.
- Verbose target compiler invocations and required H1/controlled-start selectors
  to linked CLI/server objects, their SHA-256 hashes and map LOAD entries.
- Final ELF/BIN hashes and linked privacy strings to the guarded build report.

The inherited builder's protected USB routing, Arduino NVS no-auto-erase,
startup failure isolation, checked-settings and ELF-to-image regeneration checks
executed. **The full historical H1 `verify_link.py` chain was not rerun**: its old
final-source expectations intentionally reject the three privacy files. No claim
is made that every historical H1 disassembly check was freshly repeated.

## Actual build result

The final complete adapter invocation exited **0** on a fresh `build-v2` directory.
It used Arduino ESP32 **3.3.0**, the pinned ESP-IDF **5.5** SDK archive set and
`xtensa-esp-elf-g++ (crosstool-NG esp-14.2.0_20241119) 14.2.0`.
The actual Arduino invocation included **`--clean --verbose`** and compiled the
privacy candidate path recorded in [machine-readable evidence](privacy-fix1-target-build.json).
No compiler warning lines were observed.

The controlled experimental H1 selectors, ESP32-S3, 16 MiB custom geometry,
QIO, 240 MHz CPU, PSRAM disabled, USB-OTG/TinyUSB and CDC-on-boot settings remain
unchanged. The partition-table SHA-256 remains
`b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

| Compiler/build measurement | Recorded H1 build | Privacy build | Change |
|---|---:|---:|---:|
| Program bytes | 1,414,027 | 1,415,827 | +1,800 |
| Application BIN bytes | 1,414,176 | 1,415,968 | +1,792 |
| Static RAM bytes | 113,896 | 113,896 | 0 |
| OTA slot capacity | 7,602,176 | 7,602,176 | 0 |
| Free bytes per OTA slot | 6,188,000 | 6,186,208 | −1,792 |

Compiler stack-frame estimates changed from 128 to 160 bytes for settings save
and 96 to 112 bytes for settings read. CLI parse remains 1,744 bytes. These are
compiler estimates, not physical stack high-water or heap measurements.

Final local application SHA-256:

```text
9e4d3b615d78e87521882a35c4b43ce66403168a15b6b39bcebc81bb32a6b96e
```

Final ELF SHA-256:

```text
af7887ceccfe2694738c173c76b3c211b78cb0c7b667d8d7d942a1b0ef317f6e
```

The **dashboard build ID remains `ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1`**.
That ID alone cannot identify this privacy compile. Use the source inventory,
privacy profile and application SHA. No new runtime build ID or installation
artifact is published. No bit-for-bit cross-build reproducibility claim is made.

## Fresh checks and reused evidence

Fresh evidence establishes one privacy-overlay invocation, exact 201-file fresh
composition, clean target compile, protected-core provenance, consumed-header and
linked-object binding, plus **four verifier parser/source-copy unit tests**.
Read-only controls over real compile evidence passed one positive case and six
expected refusals: old H1 without privacy, changed compiled CLI bytes, missing
patched-header dependency, missing H1 opt-in selector, changed pinned NVS archive
and incomplete selected-SDK inventory. Controls intercept reads; they do not
modify actual sources, archives or compiled artifacts.

The unchanged application source reuses the checkpoint's reconciled software
evidence, **not newly executed results in this stage**:

| Reused verification | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| Privacy native cases | 28 | 0 | 736 |
| Existing composed regressions | 558 | 0 | 23,901 |
| Embedded settings JavaScript groups | 12 | 0 | 221 |

Their ASan/UBSan/leak results are reused. The target image was not executed under
sanitizers or on hardware. The earlier 36 closeout checks remain historical.

Two clean compiler runs are retained. The first compiled and passed inherited
guards, but the additional verifier initially compared different inventory
scopes: 177 historical SDK pins versus 153 actual linked archives. No common hash
differed. The corrected verifier checks **all 177 installed pins** and requires
the actual **153 map-selected archives** to match the reported/pinned set. The
24 pinned but unselected bus-variant archives are listed separately. Six other
installed Zigbee archives are outside that baseline pin set; none is selected or
trusted, and selecting an unpinned archive is rejected.

The full corrected workflow then passed in the new `build-v2` directory. An
initial negative-control mock also missed the SDK's resolved symlink path; its
injection was corrected without changing verifier policy or any archive. Both
initial diagnostics and final results are retained. No failing attempt was
overwritten or relabelled as a successful build.

## Offline reproduction

Choose fresh output paths. This command performs a target compile, not an upload:

```bash
python3 -B tests/privacy_fix1/build_candidate.py \
  --output-dir /workspace/scratch/privacy-fix1-target-reproduction \
  --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
```

The adapter rejects resume, selector-off and diagnostics-off options. It provides
no board/port, installation, upload or package command. Its final source hashes,
actual compiler/link invocations, compiler/core/framework identities, archive
hashes, dependency files, artifacts and local raw-log SHA-256 values are recorded
in `privacy-fix1-target-build.json`. The final integration commit contains the
adapter bytes identified by those hashes; no post-build application source was
changed.

## Preservation and limits

Blank/omitted replacements remain unchanged by design; invalid nonempty
credentials are rejected. Persistence remains non-atomic, and password changes
require reauthentication. Query-password authentication, session storage and other
separate privacy findings are not redesigned here.

The four accepted scoped right-modifier owner passes, executed STOP variant and
3/3 planned lock-wait groups remain closed. Request gaps require no repeats.
H1 remains experimental; canonical Hak5 numeric encoding remains unresolved.
No new physical validation or installed-image identity is inferred.

The existing public package and mandatory **1,413,200-byte** source/text-v2
rollback were read-only verified unchanged. Rollback SHA-256:

```text
cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02
```

No original backup, private configuration, global core/SDK source, installer,
partition metadata, USB identity or historical release artifact was modified.
No hardware, real HID output, payload execution, flashing or OTA occurred. The
published branch is for source review only; firmware installation remains outside
this authorization.
