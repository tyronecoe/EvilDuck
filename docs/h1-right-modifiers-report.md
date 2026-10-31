# Route B right-side modifiers — experimental H1 candidate

**GO: review-only candidate publication. Physical right-modifier acceptance remains pending owner approval/use.** This implements `RCTRL`, `RSHIFT`, `RALT` and `RGUI` in the actual composed H1 Route B path. No hardware access, real HID output, owner-script execution, flashing, OTA, installation, settings reset or EDR1 change occurred.

The same development work records the owner's clarification: **3/3 planned inherited lock-wait groups passed**. Attempts4/5 were owner-confirmed handling mistakes outside that acceptance count, not failed groups or additional planned tests requiring repetition. Original capture limitations remain preserved and neither attempt is relabeled as a successful execution. See owner-evidence.md in the package or [the correction record](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-right-modifiers-owner-correction.md). The separate earlier H1 four-check milestone remains unchanged.

## Implementation and grammar

Actual H1 `shortcut_keys.h:26–32` initially recognized only the existing left-side aliases. Its callers already cover chord parsing, inline INJECT_MOD and HOLD/RELEASE. Existing physical ownership maps all eight modifier bits to usages E0–E7; the existing HID backend merges all eight bits into the unchanged keyboard report. This verified gap therefore needs only a two-header additive patch:

- `shortcut_keys.h`: add named `RCTRL=0x10`, `RSHIFT=0x20`, `RALT=0x40`, `RGUI=0x80`, with explicit right-modifier and H1 prerequisite selectors.
- `caps_trial.h`: distinct build identity **ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1**.

Of 201 generated application sources, all other **199** remain byte-identical to H1, including the compiler/runtime implementation, H1 decoder, scheduler, adapter, backend and web/USB/EDR1 code. The patch SHA-256 is `fbccda7274a085f29874fb6657d94acb0ecd2ce68a18046c3b8737750b277c2f`; the manifest pins exact before/after and unchanged implementation hashes. Preparation uses pinned parents and fuzz-zero patch application in disposable copies. Historical/default builders do not gain these names; the candidate requires **EVILDUCK_ROUTE_B_RIGHT_MODIFIERS_H1=1** and **EVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1**.

Examples of the existing grammar with new names are `RSHIFT a`, `CTRL-RSHIFT a`, `INJECT_MOD RCTRL`, `HOLD RALT`, `RELEASE RALT`. Left meanings, case sensitivity, delimiters, one-operand modifier taps, one-key ownership, terminal chord-key requirement and duplicate-physical-bit rejection remain unchanged. Left/right pairs are distinct. Retained malformed source rejects during full preflight, before earlier text emits. Ordinary STRING/STRINGLN text remains literal. See compatibility.md and [the design](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-right-modifiers-design.md).

The names are documented **EvilDuck extensions**, not an asserted exact canonical Hak5 vocabulary. Right Alt bit support is not general AltGr/dead-key/international-layout support. No descriptors, report IDs, layout selections or additional HID transport are introduced.

H1's packed scalar remains `(modifier<<8)|usage` within its existing finite US-printable policy: modifier zero or **left Shift only**. Its decoder remains byte-identical; numeric right masks are still rejected. Source-level named right modifiers may merge with an otherwise valid H1 tap through existing held/transient report logic, without widening its numeric whitelist. Genuine Hak5 runtime encoding remains unresolved and H1 stays experimental/opt-in.

## Fresh production-source verification

| Executed native group | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| New AD01–AD36 right-side cases | 36 | 0 | 777 |
| Preserved H1 and relevant composed regressions | 522 | 0 | 23,124 |
| Total main native run | **558** | **0** | **23,901** |

**ASan, UBSan and leak detection passed.** Actual parser/runtime/coordinator/adapter/backend sources run against mock storage, HID, clocks and feedback. Exact modifier bytes/report ordering cover all four tokens through chords/taps/ownership, mixed masks through all-right/all-eight combinations, held-state restoration, alias/duplicate/delimiter rejection, inactive retained source, completion/STOP/RESET/restart/error cleanup, blocked releases, disconnect and ambiguous acceptance quarantine, fresh operation/request/lease identities, rollover/collision restrictions, lock waits, budgets and H1 numeric refusal. No uncertain output is automatically replayed.

Separate probes, deliberately excluded from main case/assertion totals: **2 inherited actual-core checks**, **14 unchanged default-vocabulary checks**, and **3 actual-core syntax checks** for REPEAT/right chords, literal STRING/STRINGLN token words and malformed full-preflight rejection. The default probe uses the exact old shared header and confirms all right names remain unsupported there. Native-only access-control relaxation supports fault injection; target flags explicitly reject it.

The final native receipt distinguishes the initially executed main runner from later appended standalone probe modes; the composed C++ test driver and main run inputs did not change. Historical development diagnostics remain labeled historical. This development had no fresh native failures or firmware workaround. Earlier physical milestones and broad encoding investigations were not rerun.

The relevant complete H1 regression set includes all 35 inherited configurable lock-wait cases, keyboard ownership/routing, lock feedback, EDR1, preprocessing, functions, randomization/jitter, text/BOM/aliases and restart coverage. Their prior physical evidence remains scoped, not promoted into physical certification of this new binary. Fresh package and bound mock-installer checks are separately recorded at [package evidence](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-right-modifiers-package-tests.json) and [installer evidence](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-right-modifiers-installer-tests.json) after assembly; publication requires their successful completion. Native checks do not replace those package gates.

## Clean target build and resources

Approved isolated Arduino ESP32 **3.3.0** archive-based profile: ESP32-S3, **16 MiB**, custom production geometry, **PSRAM disabled**, existing USB-OTG/TinyUSB/CDC identity, 240 MHz and existing flash settings. Global Arduino/SDK installations remain untouched. Target source/flags, source inventory, final ELF-to-BIN, original-error NVS policy, USB safeguards, compiler/core/archive pins and all **177 pinned SDK archive identities** passed final verification. No compilation or post-link check failed.

| Measurement | Owner-tested H1 | New candidate | Delta |
|---|---:|---:|---:|
| Compiler program bytes | 1,413,931 | 1,414,027 | +96 |
| Application BIN bytes | 1,414,080 | 1,414,176 | +96 |
| Static RAM bytes | 113,896 | 113,896 | 0 |
| OTA slot bytes | 7,602,176 | 7,602,176 | 0 |
| Free per OTA slot | 6,188,096 | 6,188,000 | −96 |

Build ID: **ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1**. Application SHA-256:

```text
12134383e75505704d7efebf33cb7b7fdd7bd8f609038fbc575e911a0ad69ca3
```

ELF SHA-256: `b85061de399991f019e364401ef5e23a0c46e1972b34408add2ca886d0f64095`. Final link receipt SHA-256: `f770fd0f49baf3b9d5a9104cd8516bee41ebce682360147dc32e5f52789ac8d1`. Partition table SHA-256 remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

Selected compiler frame estimates: modifier lookup32, compiler statement352, evaluation144, completeInstruction48, adapter receive64, backend beginReport/hold/release48 bytes. These are static estimates, not measured physical task-stack high-water, heap, latency or USB delivery. The new lookup adds four bounded comparisons/constants, with no new allocation or runtime state; static RAM is unchanged.

The linked evidence covers the actual shared modifier function, compiler caller and existing adapter/backend report paths. Target source equality plus the composed native exact-report tests supports the software boundary; compilation alone does not establish physical compatibility.

## One reviewable Mac app package and preserved rollback

The distinct `evilduck-routeb-right-modifiers-h1-experimental-macos-v1.zip` contains this candidate, its exact **mandatory accepted source/text-v2 rollback**, bound preflight/installer, original dependency/build evidence and four new harmless fixtures. It includes no private backups, NVS data or credentials. No old H1/lock-wait helper is silently rebound; none is needed by this acceptance sheet. Source implementation and packaging-tool commit identities are recorded separately in its manifest and publication receipts.

Rollback is the exact **1,413,200-byte** application SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`, extracted from `application.bin` in the pinned accepted v2 ZIP. It is not replaced by the newer H1 application and is not rebuilt. Original packages and historical refs are preserved.

The first fully offline High Sierra check after external ZIP checksum verification/extraction is:

```bash
python3 preflight.py --directory .
```

Expect integrity PASS, no supplied current metadata, no selected write ranges and no hardware access/installation authorization. Read INSTALL-MAC.md, ROLLBACK-MAC.md and OWNER-CHECK.md before seeking separate physical approval. **macOS10.13.6 / Bash3.2 / Python3.8 / esptool4.12** interfaces remain; Linux syntax/mocks are not native Mac or board validation.

The reviewed app-only installer retains exact chip/security/16MiB checks, canonical writable partition table and narrowly supported app0 OTA initializer, fresh private prewrite backup, independent range checks, owner confirmation, refreshed chip/metadata/image validation and both-slot comparisons. Only image-rounded application sectors are programmed after separate approval; bootloader/table/NVS/otadata/SPIFFS/coredump are excluded. Unsupported metadata stops rather than being repaired. No automatic reset/reboot, retry, Start, format or settings reset occurs. Later running firmware retains ordinary existing service/storage behavior and is not a quiescent/read-only profile. Autorun must be separately confirmed disabled using existing controls.

OWNER-CHECK.md prepares four short new-feature checks: `AbCDe` with held/transient right Shift, standalone other right-modifier taps followed by `222taps`, held-right-Shift STOP/no unwanted marker/manual lowercase, and duplicate right-modifier rejection with blank TextEdit. Marker text alone does not prove host-level bit distinction; exact offline byte assertions supply that software evidence. No OS shell/launcher shortcuts or automatic payloads are included. Missing correlation or legacy-host limitations remain scoped inconclusive/platform-limited observations, not universal failure claims.

All implementation, test, build, package and publication receipts are available on the isolated branch. Stop after candidate review; hardware access, installation, flashing, OTA and real HID execution require separate owner instruction.
