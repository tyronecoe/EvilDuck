# USB observer v2: completed review delivery

**CAPTURE ONLY — NOT INSTALLED — NO OS CLASSIFIER OR VALIDATED HIGH SIERRA RULE.**

[Download the commit-pinned High Sierra review ZIP](https://raw.githubusercontent.com/tyronecoe/EvilDuck/e6d38fa5a3f2ec1b045d799443c55aa1f80b7823/downloads/evilduck-routeb-usb-enum-observer-h1-macos-review-v2.zip).
The published download, all71 archive members, candidate application, both recovery
identities and fresh-extraction offline preflight were verified. This is the one
approved bounded v2 diagnostic revision, not another claim of completed detection.

| Identity | Exact value |
| --- | --- |
| Branch | `routeb-usb-enum-observer-h1-review-v2` |
| Build ID | `ROUTEB-USB-ENUM-OBSERVER-H1-v2` |
| Firmware/verifier checkpoint | `b075e551e07f7b15124bdad3caa564c614f78ba4` |
| Package checkpoint | `e4f0a5a5c9898ca1490d0ba6f9bfa3298e4f5e81` |
| ZIP publication commit | `e6d38fa5a3f2ec1b045d799443c55aa1f80b7823` |
| Application | 1,450,624 bytes; SHA-256 `b7ac50eebe6fb5e3d69d97f20004e1014c46fb116845e30864f56de5de6d384e` |
| ELF | 23,706,764 bytes; SHA-256 `5e473ffd5813e7cea7c30871123352ceeeb64ac657519ff93ad951b096c1622d` |
| ZIP | 5,564,384 bytes; SHA-256 `851ccb1ebec84214d38e4469298a8b7270374fe6fa28aacb32a4c8e37fd5e8af` |

[Artifact manifest](usb-os-observer-v2-artifacts.json),
[actual build and201-file inventory](usb-os-observer-v2-build.json),
[full release verification](usb-os-observer-v2-release-verification.json),
[software/raw receipts](usb-os-observer-v2-results.json),
[package checks](usb-os-observer-v2-package-verification.json), and
[published-byte verification](usb-os-observer-v2-publication-verification.json)
bind the result. The build has144 committed inputs and no post-compilation
verifier delta. V1 files, artifacts and its published branch remain unchanged.

The actual composition changes five files relative to v1: `hid_backend.cpp` and
`hid_backend.h` implement bounded timing/witness metadata, `webserver.cpp` and
`webfiles.h` implement authenticated schema2 export/manual display, and
`caps_trial.h` changes only the candidate ID. The other196 files match exactly.
The [maintained backend patch](../tests/usb_os_observer_v2/application.patch),
[web patch](../tests/usb_os_observer_v2_web/application.patch), preparers and
manifests own these changes; the canonical guarded builder selects them.
Compiler/runtime, keyboard translation, STOP/cleanup/quarantine, execution limits,
authentication/privacy fixes, storage and H1 remain inherited.

The [contract](usb-os-observer-v2-contract.md) fixes exact semantics:

- Retain the original64 selected headers and a five-second prefix including early
  boot records. Timestamp each record using the pinned early-available ISR-safe
  boot clock. Hard callback gates prevent prefix appends at/after five seconds.
- Freeze prefix records/counters/state and its last coherent pre-cutoff SDK sample
  with actual sampling time. Nominal deadline and observed closure time are
  separate. Later recovery/loss cannot rewrite history; a true sample is not
  proof of exact-deadline configuration or transaction completion.
- Export live SDK status separately with expected/current observer generation.
  A generation mismatch is unknown and cannot start/rewrite prefix evidence.
  This does not prove asynchronous TinyUSB task state belongs to that generation.
- Preserve a first unsupported header/order/time/reason with PREFIX/TAIL phase,
  and flag additional distinct headers. Existing unsupported flags and whitelist
  remain; no unsupported request was relabeled merely to obtain COMPLETE.
- Keep a separate five-second diagnostic tail: bounded counters and first late
  selected SETUP/SET_CONFIGURATION witnesses, ending at ten seconds. Tail data
  cannot validate the prefix. Pending closure flags never extend the hard gate.
- Preserve zero timestamps and known full-speed0 as valid values; absent values
  are explicit/null. Tail orders are phase-local, not continuations of prefix
  orders. Live mismatch is latest-sample information, not a sticky race log.

JSON is versioned `evilduck-usb-observer-v2`; the manual download filename is
`evilduck-usb-observations-v2.json`. V1 exports remain historical schema1 evidence.
The authenticated header-only endpoint is unchanged. View/Download do not start,
reset or clear collection; there is no automatic upload/poll or persistent
learning. No payload bodies, descriptor/string contents, HID reports, keystrokes,
host files, credentials, host helper or active lock probe are collected/executed.
An unknown DCD event may increment unsupported without a SETUP witness; absence
of that witness never identifies the omitted event.

| Verification | Final result |
| --- | --- |
| Focused observer native | 34 PASS /10,767 assertions, including5,000 fabricated events |
| Source scope | 9 PASS /27 assertions |
| HTTP/actual DCD-to-JSON/UI | 57 PASS /839 assertions |
| Inherited native including DEL/DEFINE | 691 PASS /28,547 assertions |
| Inherited browser/resource groups | 86 PASS /1,563 assertions |
| Final target/negative controls | 36 PASS, no failures or skips |
| Frozen release chain | All six layers and190 original assertions preserved |
| Policy / focused package | 8 PASS /135 PASS |
| Archive / bound installer mocks | 83 PASS /38 PASS |
| Local and published extracted preflight | Both PASS, no hardware or write plan |

ASan, UBSan and leak checks are clean on the native probes. The maximum populated
JSON is10,533/12,288 bytes. Native tests use injected clocks and mocked DCD/HID,
storage and transport; browser checks use Linux Chromium/mocks. They do not
establish physical High Sierra/iPhone behavior, measured latency or discrimination.
Backend/web layered receipts are distinct from the full final-composition suite.
Historical DEL/DEFINE focused receipts remain labeled historical, separately from
current691-case coverage. Verifier-only fixes did not change the201 C++ source
files, so completed software results were reused rather than repeated.

One preliminary regression attempt was rejected by its source-change guard while
an export precision correction was being frozen; it is not counted as current.
Clean build1 compiled but correctly failed the stale nested v1 verifier selection.
The fix checks actual v2 loading independently of import caching. Diagnostic
inspection also required exact top-level handler matching and bounded reachable
instruction decoding for serializer padding. New controls reject stale imports,
closure-only/duplicate handlers and invalid reachable instructions/literals.
The original ELF literal checks, byte/symbol equivalence and strict receipt
equality remain. The changes were committed, then clean build2 passed all guards.
No failed image was packaged and no verify-existing guard was bypassed.

| Resource | V2 | Change from observer v1 | Change from working DEFINE |
| --- | ---: | ---: | ---: |
| Application bytes | 1,450,624 | +5,616 | +12,576 |
| Static RAM | 115,392 | +424 | +1,496 |
| Observer state plus guard | 1,504 | Separately measured | Separately measured |
| State plus conservative reachable observer-owned callback frames | 2,016/2,048 | 32-byte margin | Fixed bound retained |
| Largest observer callback frame | 80/256 | Within bound | Within bound |
| Compiler workspace | 3,928/4,096 | Unchanged | 168 bytes remain |
| Free bytes per app slot | 6,151,552 | 16MiB/unchanged partitions | PSRAM disabled |

The clock's external entry frames add32+48 bytes separately. The2KiB bound covers
observer-owned state/frames, not total IRQ peak stack. Actual runtime stack and
latency are unmeasured. Actual linked SETUP forwarding, reachable clock/IRAM path,
early BSS initialization, resources and dependencies are verified against the
approved isolated Arduino ESP32 3.3.0 archive profile. Descriptors, VID/PID,
interface registration, modes, partition geometry and dependency guards do not
change. H1 remains opt-in and experimental; canonical Hak5 encoding and unchanged
OS_DETECTION compatibility remain unresolved. No OS getter or branching payload
is added before evidence supports a rule.

The [preserved owner evidence](usb-os-observer-v2-evidence.json) includes all five
original byte strings and original handoff hashes. They describe three v1 boots,
not five independent captures; all have been examined. Missing order21 is fully
accounted for by filtering, but its header cannot be recovered retroactively.
A later live configured sample cannot reconstruct an earlier deadline. MSC remains
registered while media is inactive, so multiple legitimate class requests remain
competing explanations. No known-host label, missing LED, low request count or
familiar descriptor pattern establishes an OS. Last owner-reported running image
remains observer v1, not this uninstalled v2. Current typing acceptance is unknown.
The accepted DEFINE/DEL/H1/right-modifier/lock-wait groups are not reopened.

The kit contains exact original `working-define-labels-macos-review-v1.zip`,
2,691,374 bytes, SHA-256
`b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed`.
Its working app is1,438,048 bytes, SHA-256
`167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`.
Extract separately, preflight unplugged, then use its original guarded **install**
procedure with ROM entry/rediscovered port for a deliberate owner return.

Outer rollback instead selects older source/text-v2 app1,413,200 bytes, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It lacks later privacy/dashboard fixes and is not a full-device restore. Both
identities were verified inside the published ZIP. Existing scripts/settings,
credentials and private backups were not read or changed. A future installer
creates a private full-flash backup before its final write confirmation; preserve
it even if that confirmation is declined. Helpers retain High Sierra10.13.6,
Bash3.2, Python3.8 and esptool4.12 compatibility.

For the one later owner development session, follow [OWNER-CHECK](usb-os-observer-v2-owner-check.md).
First, from the extracted folder with EvilDuck unplugged:

```bash
python3 preflight.py --directory .
```

Expect integrity PASS, plan_ready=false, empty write ranges and hardware/write
authorization false. Installation remains a separate owner-operated step.
After that later installation, record the running v2 ID, connect normally to
the known High Sierra Mac, wait at least ten seconds after dashboard readiness,
and manually download **one development capture**. Do not run a helper/lock probe,
repeat old trials or keep re-downloading the same snapshot to restart collection.
If incomplete, ambiguous, insufficient or regressed, stop and use working DEFINE.
Do not extend time, expand capture or install another observer automatically.
Only if a prospective rule gains independent justification should a separately
scoped fresh, unexamined enumeration validate it. Neither the old exports nor
this development capture is held-out evidence or proof of cross-OS uniqueness.

All97 recorded earlier remote refs and historical file modes remain unchanged.
Of2,626 baseline tree entries, only the authorized compatibility inventory and
canonical builder selector changed;2,624 remain exact. No hardware access,
live USB collection, real HID output, flashing, OTA, formatting, automatic reboot,
owner script or physical trial occurred during development.
