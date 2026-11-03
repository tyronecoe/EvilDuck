# One minimal owner-operated inventory, then a private recovery plan

This procedure reads the existing dashboard's script names. It does not execute
scripts, write device files, alter autorun or inspect unrelated Mac files. Codex
has not performed it or connected to the board. No firmware update is needed.
Keep all device responses, script contents, credentials, screenshots and backups
private; only sanitized metadata is needed for a subsequent cleanup review.

## Read names without truncated labels

1. On the existing High Sierra Mac, open the existing EvilDuck dashboard in
   Chrome. Authenticate through its normal **Web UI password** field. Do not put
   a password in a URL, Terminal command or screenshot.
2. Confirm the existing execution status is idle and the device is not serving
   writable USB storage. If active or uncertain, postpone this inventory; this
   procedure does not call STOP, switch storage, reboot or start another run.
   Note the displayed build/identity if available, SD readiness, and existing
   Autorun field without changing or saving any setting. Displayed status is an
   observation, not independent application-image readback.
3. In Chrome choose **View → Developer → Developer Tools → Network**. Enter
   `/list` in the request filter. On the dashboard open **Scripts**, then press
   its **Reload** once. Do not use Run, editor Save, Upload, Del, timing Apply,
   any diagnostic action or an installer.
4. Select the successful **GET /list** request. In its **Response** tab copy only
   the JSON response array into a new private local inventory note. Retain the
   full strings and any duplicate entries; do not expand ellipsized UI names by
   guessing. Record the response status and local observation time alongside it.
   A plain-text local file is enough. Do not copy Headers, **Copy as cURL**, or
   export a HAR: these can retain the `X-Duck-Password` authentication header.
5. A 401 is authentication rejection; 409 is a lock/storage-admission refusal. A
   malformed response, failed read or incomplete list is not evidence of empty
   storage. There is no automatic retry in this procedure. Preserve the error
   without credentials and leave the inventory incomplete if it cannot be read.
6. Keep the raw inventory local. A later review needs exact namespace/name,
   byte length, SHA-256, identified purpose and dependency notes for each
   proposed file, not passwords or unrelated private script text. This first
   read supplies **names only**; it does not yet supply those byte identities.

These controls are verified in composed `webfiles.h:127–148,835–849` and
`webserver.cpp:133–138,950`. Read-only Home status fields are populated at
`webfiles.h:953–965`. Source excerpts/hashes are in
[the source evidence](script-storage-source-evidence.json).

## What this inventory cannot establish

`/list` has no per-file size, hash or physical-path metadata. It lists selected
SPIFFS locations and SD root plus `/scripts`, not every file. A Library entry can
be a compiled example rather than a disk file. Never treat Library union output
as an inventory of stored files.

In particular, **SD `/name.txt` and `/scripts/name.txt` both appear as `sd:name.txt`**.
The editor/HTTP loader resolves that display to `/scripts/name.txt`, while the UI
also deduplicates repeated names. SD nested paths and scripts in unscanned SPIFFS
folders may be absent. The actual SD root paths must be distinguished in a later
owner-local read-only card/filesystem inspection before any cleanup. Do not
remove or remount a card as part of the minimal browser procedure above.

The owner already clicked **Edit** on the first three supplied full-name examples.
That is useful loaded-source evidence, not a saved-byte hash. Editor Load uses
`POST /script/load` with GET fallback, but does not execute a script. It can also
put a first-line preview in dashboard Logs; do not share the Logs indiscriminately.
**A load-failure REM message in the editor is generated UI text, not file
contents. Do not press Save or editor Run after a failed load:** current code can
submit that error buffer as replacement source. A 409 can arise from lock/admission
contention; it does not by itself identify a running script. No actual overwrite
is proven by the supplied image.

Copy/paste from the editor is not a verified byte backup: BOM, line endings or
encoding may change. Do not press Run to identify a file; a legacy Run can even
install a missing compiled example before execution.

## Private backup and restore procedure — required before future removal

This is the proposed recovery sequence for a later, file-specific cleanup review,
not permission to delete, move, import, export, restore, attach storage or write
anything now. There is **no established bulk archive download/restore feature** in
the current firmware, and no new exporter/helper is implemented in this audit.
Do not claim the names-only inventory or an existing old backup completes it.

1. Resolve each selected item's actual volume and full path first. For SPIFFS,
   a later authenticated **GET /script?s=...** can read an exact leading-slash
   path (for example the URL-encoded `/path/name.duck`). The leading slash
   prevents the editor's unqualified-folder search and compiled-example fallback.
   The response is text, not an attachment/archive. Preserve response bytes using
   a separately reviewed owner-local downloader, without text/clipboard conversion
   or credential logging; no such downloader is delivered or executed here.
   Reject authentication/errors and unexplained empty results. Existence followed
   by failed open can currently produce HTTP 200 with an empty body, so that
   response alone does not verify a genuine zero-byte file.
2. SD `sd:name` is insufficient to back up a root file. Establish root versus
   `/scripts` and nested paths through an owner-approved read-only filesystem
   view/card backup. Record the exact volume/path, bytes and SHA-256 locally.
   Preserve relevant non-script assets too if making a full card archive; the
   script list omits them. Do not enable MSC or invoke CLI `export` to gather
   this audit: `export` **writes to SD**, and `import` **writes to SPIFFS**.
3. Make a new private host archive outside cloud/shared folders and outside
   EvilDuck's executable list. Keep original volume/path mappings and byte files
   plus a manifest of sizes/SHA-256. Use a fresh destination; never overwrite or
   delete an existing backup. Keep source content out of public receipts/Git.
4. Check archive integrity, extract into a new empty private host directory, and
   compare every extracted volume/path, size and SHA-256 with the original
   manifest. Check entry count and no unexpected/missing or unsafe paths. Record
   the archive hash too. An archive checksum/CRC alone does not establish that
   all intended device files were captured or that their paths are correct.
   Re-read the selected device files while idle and compare with the captured
   identities; unexplained changes, ambiguous reads or missing metadata stop
   eligibility. No physical flash secure-erasure or atomic filesystem snapshot
   guarantee is implied.
5. Only after those checks and explicit owner authorization may a later exact
   per-file cleanup allowlist be used. The current allowlist is empty. A prefix,
   matching fixture name, disabled autorun, or currently missing list entry is
   not a substitute for identity/reference review. No wildcard deletion is
   proposed. Moving a file on-device is a write and can break path references;
   an unlisted folder is not a secure disabled archive.
6. Future restoration must deliberately select the same original namespace and
   full path. Current HTTP script Save uses `POST /script` with `name`, `content`
   and the correct storage destination; it supports safe `.txt`/`.duck` script
   names, not general binary assets. The existing editor can restore reviewed
   text only when exact BOM/newline bytes can be preserved and verified; it is
   not a proven bulk or arbitrary-byte restore tool. Files outside that contract
   require a separately reviewed filesystem recovery path. Refuse unintended
   overwrites. After a separately authorized write, read back the exact path and
   compare bytes/size/hash without Run; a status code or visual text match alone
   is not a successful byte-restore test.

The existing installer is not an inventory exporter. Invoking it can create a
private full-flash backup before final write confirmation and involves hardware;
do not run it for this task. Existing backups remain untouched, but an older
backup may predate these script uploads. Exact source/text-v2 application rollback
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`
restores **application code only**, without Privacy Fix 1/dashboard cleanup. It
cannot restore deleted script bytes, filesystem layout or past NVS settings.

Names can be collected now through the existing read-only interface. Destructive
cleanup/restore readiness remains conditional on the exact private archive and
path verification above; that limitation does not require another firmware build
or reopening accepted keyboard/lock-wait/privacy milestones.
