# Fail-closed editor loading — local source-only implementation

**The reproduced HTTP 409 overwrite path is blocked in software tests.** Failed
reads no longer put generated error text into script source. Save and editor Run
check explicit document eligibility inside their handlers, including when called
directly with UI controls bypassed. No owner script or device was written.

Started clean at `805d989c3ac50cb96025862c95916830c59f8ba7`; local branch
`routeb-editor-failed-load-safety`. This is a local implementation checkpoint:
**no commit, push, firmware build, package, flashing or hardware operation**.
Historical tracked files, refs, firmware images and backups are preserved.

## Actual source ownership and focused diff

The base is the verified 201-file composed Privacy Fix 1 / dashboard / experimental
right-modifier H1 tree, not uncomposed root firmware. Its header SHA-256 is
`7b4be141c776fc2c8d83b6532c62b9c4b9baa033261ce16c60e509dddaea4eab`.
The authoritative fix is the maintained
[source diff](../tests/editor_load_safety/application.patch), applied through the
[new source-only preparer](../tests/editor_load_safety/prepare_sources.py) with
[pinned before/after inventory](../tests/editor_load_safety/source-manifest.json).
Exactly **one composed file**, `webfiles.h`, changes; **200 remain identical**.
Within that header, only `INDEX_HTML` and `INDEX_JS` change.

Final header SHA-256:
`df10d10fd612ecb8be37c0c8e3a092720af463870814cab1c649e8a70304e445`.
Patch SHA-256:
`d20564165f1ead4ee2364c21184f6dfc8f506572982c2f143aa50323d76b8c58`.

The preparer pins the complete dashboard parent, checks all 201 inputs, applies
zero-fuzz patching, and checks all 201 results. Wrong/partial/repeated inputs fail
closed. Its `overlay()` chains the historical composition once, then the editor
delta. A source-copy replay was executed; no target compiler was invoked.
**Historical target builders do not automatically select this overlay.** Future
target integration/build/package verification needs a separately authorized stage;
no installed-image or target-build readiness is claimed here. The existing BuildId
is not changed, because no new firmware image/package is being produced.

## Before and after

| Situation | Previous behavior | Repaired behavior |
|---|---|---|
| HTTP 409 or another failed load | Writes generated REM/error placeholder into editable source; explicit Save can replace the file with it. | Error is separate `editorStatus` text. Prior source remains visible/read-only; Save/editor Run disabled and handler-blocked. No write/run request. |
| Loading B after A | Updates target before response, overwrites the buffer with Loading/error text; no durable binding. | Captures B's requested identity and load generation. Preserves A's draft and identity until valid B success or an explicit decision. |
| Out-of-order/aborted/expired load | Old response can replace current selection/source. | Generation/identity checks ignore stale results; abort is best-effort, with stale guards working even without AbortController. |
| Unsaved changes / switch / New | Changes can silently disappear. | Explicit replace decision first. Cancel retains/restores the original draft, cancels pending replacement and invalidates its responses. Failed switch offers **Retry load** and **Restore preserved draft**. |
| Rename/destination edit on a loaded file | May save A's source under a new B target without loading B. | Invalidates eligibility. Load that target, restore the preserved original, or explicitly choose New. No implicit Save As. |
| New | Initializes editable template. | Explicit New remains valid without a preceding load; no write until explicit Save. Target selection is intentional new-document state. |
| Save then editor Run | Captures a name before awaiting Save; later selection/source changes are unchecked. | Captures document reference, canonical target, generation, revision and text once. Exact Save acknowledgement plus rechecked unchanged snapshot required before dispatching the existing Run path. |

Direct list-row Run is unchanged; this fix concerns the editor's Save-before-Run
flow. No script execution engine, SD root mapping, upload wording, USB/LED protocol,
authentication, timing, ownership, execution budget or STOP backend is altered.

## States and response contract

`none`, `loading`, `loaded`, `dirty`, `new`, `load-failed` and `identity-changed`
are explicit data states, with a separate write-in-flight flag. Eligibility
requires a valid loaded/new document matching the current namespace/path and an
eligible phase. Button disabling is supplementary; both public handlers enforce
that rule. A write in flight blocks duplicate actions and load/New switching.
Changing source/identity while an acknowledgement is pending prevents stale Run.

The UI retains one previous draft in page RAM, with its original filename,
namespace and text. Restore is explicit and only recovers a prior valid loaded or
intentional-new document. Confirming replacement permits a later successful load
or New to replace those unsaved edits. This is not persistent recovery: closing
or reloading the page can still lose unsaved work. No draft/credential is newly
written to browser storage or the device.

Loads have a four-second overall UI deadline. Existing read-only 404 lookup
fallbacks (`POST /script/load`, GET `/script`, GET `/library`) are retained; other
errors are not automatically retried. Only HTTP 200, `text/plain`, nonempty,
NUL-free source is accepted. Empty 200 is deliberately rejected because the
current backend cannot distinguish empty file from failed open. An intentional
New document can still be edited to empty; server/compiler semantics are unchanged.
Malformed DuckyScript and genuine diagnostic-looking comment text remain editable
when returned as valid source; there is no guessed client-side language parser.
HTTP/HTML/JSON error-response MIME, 204, rejection, timeout and network failures
cannot activate Save/Run. Errors never become generated textarea source.

Canonical client targets follow supported existing SPIFFS/SD reference forms;
`SD/folder.duck` remains a SPIFFS path, while supported `sd:`/`SD:` and lowercase
slash aliases retain existing meaning. Mixed-case unsupported colon prefixes are
rejected. This does **not** repair the separately audited SD root versus `/scripts`
listing ambiguity.

## Versioning and remaining server limitations

The binding is a **client requested identity and local text revision**, not a
server-authenticated file version. The server reports no ETag, resolved origin,
read hash or compare-and-swap token. Existing bare-name folder/library fallbacks
remain; the UI cannot prove their resolved physical source. Another client/card
writer can alter the file after load or between Save and Run. No server atomicity,
no-overwrite create or immutable Save/Run version guarantee is invented.

New retains the existing deliberate Save behavior: choosing an already existing
target can replace that target. Use a deliberate filename; this stage adds no
server create-if-absent protocol. A lost/invalid Save acknowledgement means outcome
unknown, not proof that no write occurred. It causes no automatic retry or Run.
Explicit future retries still need operator judgment. Abort cannot undo server
work already accepted. Browser handler state is not an authentication boundary;
the existing authenticated backend remains authoritative.

Textarea and multipart line endings are text representations, not raw file byte
identity. The local saved-text baseline uses the actual textarea representation,
so an untouched CRLF load does not become falsely dirty. A separate inert control
confirmed that existing `fetch.text()` removes a leading UTF-8 BOM in both old and
new UI. This is unchanged existing browser behavior, not a new source/text-v2 or
byte-backup guarantee. Compiler/CLI BOM acceptance remains separate. No automatic
repair/restoration of already overwritten files is attempted.

## Focused verification

All current tests use public composed source, synthetic names/text, intercepted
HTTP and mocked storage/Run/Delete. No real script, owner file, device or host
keyboard is accessed. Browser: Debian 13, Chromium **151.0.7922.173**, Playwright
**1.62.0**. Native High Sierra/iPhone acceptance is unperformed.

| Fresh executed check | Result |
|---|---|
| Repaired editor cases | **41 PASS groups / 309 assertions / 0 FAIL** |
| Existing dashboard/Settings/privacy browser suite, unchanged | **9 PASS groups / 207 assertions / 0 FAIL** |
| Existing LED-return STOP UI runner, unchanged | **10 PASS groups / 21 assertions / 0 FAIL** |
| Source boundaries, complete replay and rejected wrong/repeated base | **4 PASS groups / 14 assertions / 0 FAIL** |
| Pre-fix negative control, unchanged audit reproducer | **1 OBSERVED_DEFECT + 1 successful control / 20 checks**; expected unsafe old path, not a safety PASS |

Editor coverage includes HTTP 401/404/409/500/503, network failure, read/save
deadlines, malformed MIME/empty/NUL/204 responses, explicit retry, ordinary
load/edit/save/run, deliberate New, dirty-cancel/discard/failed-switch restoration,
filename/destination changes, double-clicks, three rapid selections, stale responses
with/without AbortController, pending-save changes, exact/bad Save acknowledgement,
zero Run after unconfirmed Save, CRLF clean state and authenticated deletion.
Direct handler calls bypass disabled controls to verify guards. The independent
nine-group suite checks password fields remain blank/write-only, unrelated saves
omit secrets, timing still requires explicit Apply, active diagnostic visibility
and STOP progress. Settings/Terminal/CSS, auth helpers, authenticated deletion,
direct row Run and the complete STOP block are also byte-identical in static checks.

[Raw final editor receipt](editor-load-safety-browser-results.json) and
[combined commands/results](editor-load-safety-results.json) distinguish fresh,
historical and negative evidence. The first editor run recorded 25 PASS/4 harness
FAIL (readonly fill attempt and Playwright auto-invoking assigned confirm functions).
Those receipts remain in scratch. The corrected second run passed 39 groups, but
three malformed-response cases accidentally still used HTTP 409. The final run
uses HTTP 200 for MIME/empty/NUL validation and adds the strict-prefix/CRLF cases;
only final totals above establish that coverage. Review-found Cancel/pending-load
and uppercase-folder identity issues were corrected and tested before finalizing.
No historical expectations were weakened.

Older standalone privacy/caps UI Node mocks are incompatible even with the
unchanged dashboard baseline (missing timing DOM/setInterval; moved capsTiming).
Their baseline failures are separately preserved; they are not silently called
new regression PASS. The actual unchanged real-browser Settings/privacy cases
are used instead. Unchanged native/backend persistence/ASan/UBSan evidence remains
historical, not freshly rerun. No new C/C++ runtime or target build occurred, so
no fresh sanitizer, firmware size, device heap/stack or physical readiness claim
is made.

## Reproduce locally without a device

```bash
python3 -B tests/editor_load_safety/prepare_sources.py \
  --from-composed /workspace/scratch/dashboard-cleanup/build-v1/candidate/EvilDuckS3 \
  --output /workspace/scratch/editor-load-safety/reproduction-source
python3 -B tests/editor_load_safety/test_browser.py \
  --source /workspace/scratch/editor-load-safety/reproduction-source/webfiles.h \
  --output-dir /workspace/scratch/editor-load-safety/reproduction-browser
python3 -B tests/dashboard_cleanup/test_browser.py \
  --source /workspace/scratch/editor-load-safety/reproduction-source/webfiles.h \
  --output-dir /workspace/scratch/editor-load-safety/reproduction-regressions
node tests/led_return/test_stop_ui.cjs \
  /workspace/scratch/editor-load-safety/reproduction-source/webfiles.h
```

Use fresh output directories and the existing installed browser dependencies.
No compiler, installer, device address or networked board is involved. The new
runner routes/aborts every request; mock Save/Run/Delete are test records only.

## Exact changed-file inventory and rollback

All changes are new local files:

- `tests/editor_load_safety/application.patch`
- `tests/editor_load_safety/source-manifest.json`
- `tests/editor_load_safety/prepare_sources.py`
- `tests/editor_load_safety/test_browser.py`
- `tests/editor_load_safety/test_scope.py`
- `docs/editor-load-safety-report.md`
- `docs/editor-load-safety-browser-results.json`
- `docs/editor-load-safety-results.json`

The working composed preview is
`/workspace/scratch/editor-load-safety/source-replay-v1/webfiles.h`. Source rollback
is simply to keep selecting the historical dashboard preparer and omit this new
overlay; no historical file needs resetting/replacing. No reset command, physical
rollback or cleanup action is performed or requested here.

The unchanged published review ZIP was hash-checked:
`f9221d2f8bd397cbcaf9166126026f4712fc17fd0ae883fe05115cc33578142c`.
Its exact mandatory rollback member is **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It is older source/text-v2 code without Privacy Fix 1/dashboard cleanup and does
not restore deleted scripts or past settings. No package or rollback bytes changed.

This stage ends at local source/test review. Existing saved scripts, SD contents,
accepted milestones and historical artifacts stay untouched. No deletion/archive,
rename, formatting, settings reset, new feature, target build, package, remote
publication, hardware test, flashing or OTA is included.
