# Script storage and platform readiness — read-only audit

**Repository audit complete. No live deletion is approved.** Five editor views
identify likely test fixtures/data for provisional archiving; most
of the list has not been inspected. SD names have a source-supported path ambiguity.
The exact current deletion allowlist is therefore **empty**, with explicit unknowns
in [the machine-readable cleanup table](script-storage-cleanup-allowlist.json).
No device cleanup, firmware change/build/package or Codex hardware operation occurred.

## Verified baseline and evidence boundaries

Started clean on `routeb-dashboard-diagnostics-cleanup-v1`, HEAD
`e117037a15b5f79ba57abb1fb1da45cd4bb15fbf`. The new documentation-only branch is
`routeb-script-storage-platform-audit`. Remote refs were independently snapshotted;
no relevant subsequent work was found in that snapshot. Historical sources,
packages, tests and branches are preserved.

Inspected the actual Privacy Fix 1/right-modifier H1/dashboard composition at
`/workspace/scratch/dashboard-cleanup/build-v1/candidate/EvilDuckS3`. All **201/201**
source sizes/hashes match [the published build inventory](dashboard-cleanup-build.json).
Firmware implementation is `0db1f980e0ed05390d71fe9e92178304d7a3bc24`, package
publication `211e6f8956c3de5277a8b5334a7cd04f91e05622`. This identifies the reviewed
software; the screenshots do not independently identify installed application
bytes. [Baseline receipt](script-storage-baseline.json) and
[hashed source excerpts](script-storage-source-evidence.json) make the actual
composed source/line references below traceable without substituting root files.

The owner supplied **eleven screenshots**: six full-name editor views and five
script-list views. Five editor views show source/data; one is a failed-load
placeholder. The owner specifically confirms clicking **Edit** on the top three
entries. These are loaded-source observations, not merely names typed into
an empty editor. The first three show very short delay-only content; another shows a function/branch
fixture and another canary/test data. Private script bodies
and raw screenshots are not republished here. They do not establish exact saved
bytes, trailing bytes, hash, origin/age, dependencies or a recoverable backup.

Many other names are truncated. Editor images show `Request 0: None`; list
images show `Request 1: Completed`. What Request 1 ran, the boot/session identities,
exact OS/browser versions and image hash remain unknown. Do not associate that
request with a listed filename or infer reboot ordering. Compact controls are
visibly rendered on an iPhone; full navigation/settings acceptance and wired USB
input are not established. Existing right-modifier, three lock-wait groups and
scoped privacy milestones stay closed with their original limitations.

## Exact cleanup/recovery table

Paths marked **expected** are derived from the selected UI namespace and source
mapping, not an independent current-filesystem read. No screenshot provides file
size or SHA-256. All asterisk family labels below are descriptions, not glob
commands or an allowlist. Actual device deletion authorization is **none**.

| Namespace / exact or reported path | Size / hash | Purpose and reference evidence | Recommendation |
|---|---|---|---|
| UI SPIFFS; expected `/x28-5b41d038bfdd.duck` | Unknown / unknown | Full name and delay-only editor view; owner clicked Edit. Not an application resource or hardcoded prerequisite in inspected startup. External/helper references unknown. | **ARCHIVE CANDIDATE**, provisional; verify saved bytes, references and private backup first. |
| UI SPIFFS; expected `/x28-4c0b7090aeec.duck` | Unknown / unknown | Same scoped editor evidence; origin and saved-byte identity unknown. | **ARCHIVE CANDIDATE**, same conditions. |
| UI SPIFFS; expected `/x28-ab6d99ed45d7.duck` | Unknown / unknown | Same scoped editor evidence; no physical dependency/backup inventory supplied. | **ARCHIVE CANDIDATE**, same conditions. |
| UI SPIFFS; expected `/x28-349b740cfccc.duck` | Unknown / unknown | Visible DEFINE/function/branch fixture, with bottom content not fully visible; saved bytes/references unknown. | **ARCHIVE CANDIDATE**, provisional only. |
| UI SPIFFS; expected `/d-2ce832ec5e50.txt` | Unknown / unknown | Visible canary/test-data text; listing a `.txt` does not prove it is an executable program or unused. | **ARCHIVE CANDIDATE**, provisional only. |
| UI SPIFFS; expected `/x28-32fab547adf7.duck` | Unknown / unknown | HTTP 409 load failure; editor shows a client-generated error placeholder, **not the file contents**. Do not Save or editor Run. | **UNKNOWN**. |
| Unprefixed list labels `lockwait01.txt` through `lockwait05.txt` | Unknown / unknown | Full labels visible; contents and exact saved paths/references uninspected. | **UNKNOWN**; not deletion-eligible from test-like names. |
| `rm-shift.txt`, `rm-taps.txt`, `rm-bad.txt`, `h1-malformed.txt`, `testdoodoo.txt` | Unknown / unknown | Visible list labels only. A repository fixture with a similar name is not proof of matching contents or purpose. | **UNKNOWN**. |
| Other cropped x28/lockwait/wait/rm/h1/test/example labels | Unknown / unknown | Truncation prevents exact identity. No guessed suffix or fixture mapping. | **UNKNOWN**. |
| `sd:loot.txt`, `sd:jtest.txt` | Unknown / unknown | Exact display labels; SD root versus `/scripts` conflated. Contents are unknown user data. | **UNKNOWN**, preserve until owner-local path/content review and authorization. |
| NVS namespace `duck` (not a filesystem path) | Current settings uninspected | Application credentials/configuration; `settings.cpp:63,85–106,164–169`. Not a script. | **KEEP**, outside script cleanup. |
| SD `/sys/usb_disk.img` | Required format 4,194,304 B; actual presence/bytes/hash unknown | Optional MSC backing image; `usb_msc.cpp:20–21,133–137`. No image auto-created. Required only if deliberately activating that feature. | **KEEP**, outside script cleanup; do not infer live presence or activate MSC. |
| SPIFFS `/examples/.installed` if present | Actual bytes/hash unknown | Dormant example installer writes marker; it is not read as its installation predicate. Controlled boot does not invoke installer. | **UNKNOWN**, not required for current dashboard; no removal authorized. |
| Five compiled library example identities below | Public compiled-text sizes/hashes available; live copies unknown | Firmware resources in `script_library.cpp`, not independent deletable disk objects merely because Library lists them. | **KEEP** firmware/history; separately inspect any disk copies. |
| Public `tests/...` regression fixtures and published ZIPs | Exact public metadata in [known assets](script-storage-known-assets.json) | Host/repository test and release provenance, not a device inventory. | **KEEP**, never remove Git evidence to clean device storage. |

No live entry qualifies as **DELETE-ELIGIBLE AFTER BACKUP** yet. That category is
reserved for an exact verified saved object, local dependency review and checked
private archive. The five provisional candidates are the concrete next review
list, not authority to press Del. An empty deletion allowlist is an evidence
boundary, not a claim that the accumulated files are essential.

### Compiled examples versus independent device files

| Compiled library identity | Public text bytes | Disk presence/reference conclusion |
|---|---:|---|
| `examples/hello.txt` | 156 | Optional firmware example; actual SPIFFS copy/hash unknown. |
| `examples/linux_shell.txt` | 140 | OS-specific legacy example, not a startup prerequisite. |
| `examples/save_log.txt` | 130 | Legacy file-I/O example; existence does not prove any SD output's origin. |
| `examples/attackmode_demo.txt` | 106 | Optional example, not a requirement to enable USB storage. |
| `windows/hacker_terminals_3_monitors.txt` | 197 | Windows/personal-path-specific example, not portable application data. |

[Full derived public-text hashes](script-storage-compiled-examples.json) come from
adjacent C++ literals in the verified source, not device reads. They do not assign
those hashes to similarly named uploaded files. No example was executed. The
compiled library has no mutable filename/index asset that must be preserved on
SPIFFS to render the current dashboard.

## Dependency and lifecycle findings

1. **Scripts and application resources are different.** `.txt` and `.duck` are
   executable source candidates (`storage.cpp:19–20`), not proof of essentiality.
   Dashboard HTML/CSS/JS are embedded `webfiles.h` resources; portable Route B's
   static handler refuses general filesystem fallback (`webserver.cpp:859–904`).
   Settings live in NVS, and optional MSC uses a separate binary SD image.
2. **No automatic sample-file installation in this composition.** Controlled
   setup excludes `script_library::installIfNeeded()` and autorun
   (`EvilDuckS3.ino:106–124`); SPIFFS mounts without format (`spiffs.cpp:23–34`).
   SD startup can create `/scripts`, but not example files (`sd_card.cpp:32–49`).
   The dormant installer writes all five examples if any are missing, rather
   than trusting `/examples/.installed` (`script_library.cpp:54–76`). Explicit
   legacy Run can recreate a missing example (`webserver.cpp:249–264`), so Run
   must never be used to identify or back up a file.
3. **Host fixtures are not silently deployed.** H1 packager copies its four
   `rm-*.txt` fixtures into the host ZIP (`tests/h1_right_modifiers/package.py:133–154`).
   The app-only installer writes application slots, not SPIFFS/SD; it does not
   populate the script list. A manual supported script Save persists until
   replaced/removed (`webserver.cpp:765–801`). Multipart `/upload` is disabled
   by early 503 (`webserver.cpp:394–397`). Reviewed wait observer/LED helper do
   not upload scripts; origins of owner-generated x28 names or unavailable local
   helpers remain unknown. No automatic fixture-deletion lifecycle is established.
4. **Exact namespaces matter.** Plain `foo.duck` maps to SPIFFS `/foo.duck`;
   `sd:foo.duck` maps to SD `/scripts/foo.duck`, not `/sd:foo.duck`
   (`storage.cpp:23–35,72–75,104–126`). Only selected SPIFFS prefixes are scanned:
   `/examples`, `/demos`, `/windows`, `/linux`, `/macos`, `/advanced`, `/scripts`,
   plus top-level script files (`storage.cpp:329–367`). SD scans root and
   `/scripts` nonrecursively. This is an active-list view, not all storage.
5. **No general cross-file include in composed Route B.** Its program operation
   set/compiler does not implement general INCLUDE/READ/SAVE/APPEND
   (`core.h:20`, `core.cpp:438–462`). Functions, DEFINE and restart are in-program
   behavior, not independent required script files. Legacy `com.cpp:310–329`
   does have file I/O. Saved autorun strings, owner instructions/bookmarks and
   unavailable external helpers can still refer to paths. Disabled autorun alone
   does not prove no dependency; external references were not inspected.
6. **Moving is not a disabled archive feature.** SPIFFS `/archive/file.duck` is
   outside the enumerated prefixes but can still load by explicit path.
   `/scripts/archive/file.duck` remains in the recursive SPIFFS listing. SD
   `sd:archive/file.duck` targets `/scripts/archive/file.duck` although nested
   files are not listed by the SD scanner. Renaming/moving may break saved paths
   or legacy file references. No on-device ZIP archive browsing or safe
   nonexecutable archive feature is established. Use a private host archive.

## Concrete defects and limitations found; no repairs made

- **Failed-load editor can overwrite source:** the latest screenshot shows HTTP
  409 in `x28-32fab547adf7.duck` while status displays Request 0/None.
  `loadScript()` inserts a generated `REM Load failed` buffer on any failed
  read (`webfiles.h:875–893`). Save submits that buffer without a successful-load
  gate (`912–924`), and editor Run first calls Save (`927–932`). No actual
  overwrite is demonstrated by the screenshot, but the path is a concrete
  data-loss risk. Do not press Save or Run from that view. The 409 is a combined
  admission failure: `mutation_guard.h:8–10` requires both TryGuard acquisition
  and `enterMutation()` (`coordinator.cpp:88–94`). It can mean lock contention
  as well as execution ownership; the message alone does not prove a payload is
  active. No runtime cause or repeated-lock failure is established here.
  [Fresh inert reproduction](script-storage-editor-error-observation.json)
  confirms **1 OBSERVED_DEFECT**, **1 successful-load control**, **20 checks**
  and zero final harness errors. The real UI's explicit Save submitted the
  generated placeholder to a mocked save endpoint. No device file was written.
  Exit 0 means the audit reproduction completed, **not** that this behavior is
  safe. Multipart serialization changes textarea LF to CRLF; this observation
  also reinforces why editor text is not a proven byte backup. The first harness
  run assumed LF on the wire and recorded two HARNESS_ERROR results; that receipt
  remains local, and the corrected expectation records exact CRLF submission.
- **SD path loss:** `sd_card.cpp:172–202` strips parent paths for root and
  `/scripts`, while `storage.cpp:72–75` loads only `/scripts/name`. Two files can
  be conflated; UI `Set` deduplication (`webfiles.h:843`) hides duplicate labels.
  This is a source-supported identity defect, not a newly observed physical
  deletion incident. Fix it before relying on dashboard-only SD cleanup.
- **Editor/Route B lookup mismatch:** editor loader searches known folders for a
  missing bare SPIFFS name, then compiled examples (`storage.cpp:144–160`,
  `webserver.cpp:701–726`). Route B FileSource uses exact parse/existence only
  (`file_source.cpp:5–10`). Legacy resolution can also cross volumes
  (`storage.cpp:255–278`). Successful editor Load is not universal proof of what
  a later unqualified Run will load. Use exact qualified paths in any future
  file-specific review; do not execute anything to disambiguate it.
- **Backup ambiguity:** `/list` has no sizes/hashes; a successful existence test
  followed by failed open may return HTTP 200/empty text. No supported bulk
  byte-backup/restore contract was found. Copying editor text is not byte backup.
  See the precise limits and recovery sequence in
  [the inventory/private-backup guide](script-storage-owner-inventory.md).
- **External filename JSON:** list construction does not escape quotes/backslashes
  (`storage.cpp:341`, `sd_card.cpp:192`). HTTP Save restricts accepted names
  (`webserver.cpp:86–98`), but externally populated SD media can exceed that
  assumption. Malformed JSON means incomplete inventory, not zero scripts.
- **Bounded UI wording issues:** the empty-list message still suggests flashing
  `data/`/Sketch Data Upload (`webfiles.h:828`), and Library describes scripts on
  SPIFFS although its listing can include SD/compiled entries. The visible Upload
  control calls a disabled endpoint. These are workflow/wording mismatches, not
  evidence of an OS or interpreter regression. No wording/backend change is made.

## Verification and platform assessment

Fresh in this audit: **201 source hashes/sizes matched**; the existing actual-UI
inert browser runner passed **9 groups / 207 assertions / 0 failures**, exit 0.
[Fresh receipt](script-storage-browser-results.json): Debian 13, Chromium
151.0.7922.173, Playwright 1.62.0, 1280×900 desktop and 320×640/390×844 touch
emulation; exact embedded header hash matches the build receipt. HTTP requests
were intercepted by the fixture; no real dashboard/device action occurred.
Earlier identical browser results and firmware/package/sanitizer receipts are
historical, not accumulated or relabelled as newly executed hardware evidence.
No firmware/native suites or sanitizers were rerun for a documentation-only task.

The [four-surface platform matrix](script-storage-platform-readiness.md) separates
browser dashboard access, wired USB input, installation tooling and script/app
assumptions across High Sierra, newer macOS, Windows 10/11, Linux, Android and iOS.
Native OS/browser versions not supplied remain unknown. New firmware physical
readiness is not inferred from Linux or screenshots. iPhone Wi-Fi rendering is
not USB input; mobile use needs exact host/accessory hardware, adapter, power and
permission evidence. No separate Pico Bluetooth results are imported.

## Recommended next action

Use the single existing-interface, read-only **Scripts → Reload / GET /list**
procedure in [the owner guide](script-storage-owner-inventory.md) to collect full
names privately. It needs no firmware update and no script execution. Resolve SD
paths independently before any SD cleanup, and verify an exact private archive
before promoting any candidate to a later file-specific removal allowlist. No
private contents, credentials or backups need to be uploaded to Codex/Git.

For a future separately scoped software repair, prioritize **failed-load editor save protection** (preserve the prior buffer,
show errors outside source, and prevent Save/editor Run until a valid deliberate
state exists). Next address **unambiguous SD listing/loading identity and
corresponding inventory tests**, then truthful
upload/empty-list/Library wording. The editor repair must keep old content paired
with its original filename: a failed attempt to load B after A must not make A's
text saveable as B. Guard loading/failed state, keep errors outside source, and
require successful load or explicit New before Save/editor Run. Do not suppress
409, weaken admission/STOP, retry automatically or change storage/backend policy
to hide the failure. This is a proposal only; no fix is implemented here. That is a concrete storage/UI correctness
issue; do not turn it into new HID/OS detection or scripting functionality. Keep
cleanup, browser portability and future firmware repair as separate decisions.

Mandatory rollback remains the actual **1,413,200-byte** source/text-v2 application,
SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
Its bytes were rechecked from the unchanged published ZIP; it is older code
without Privacy Fix 1/dashboard cleanup. Application rollback does not restore
deleted scripts, SD contents or past settings. All existing backups and release
artifacts remain untouched. No file removal/move, format/reset, log clearing,
merge, firmware build/package, hardware access, flashing, OTA or real payload
execution is authorized or performed here.

## Audit-only reproduction and scope

Fresh commands and classifications are recorded in
[verification](script-storage-verification.json). The new
[audit reproducer](../tests/script_storage_audit/test_editor_error.py) pins the
existing browser-fixture hash and blocks all real/external traffic. It clicks
explicit Save only against mock storage; no owner source or executable payload
is used. It is an observation of the current defect, not a repaired regression
test or physical acceptance pass. All earlier tests/firmware/packages stay intact.

Only new `docs/script-storage-*` documents/metadata and the inert audit reproducer
are added on the isolated review branch. No private screenshot/source body,
credential, backup, firmware image, installer or dependency change is published.
The owner can retain the supplied original screenshots in this conversation and
local evidence; no screenshot hash or binary archival receipt is invented.
