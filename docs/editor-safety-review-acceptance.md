# Editor safety — short owner-review sheet

**NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED.** Downloading or checking this
package does not authorize installation, device access, flashing, OTA or script
execution. The observations below are a future plan, only after a separately
reviewed installation and owner authorization for those observations.

Candidate: **ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1**; application **1,437,696 bytes**,
SHA-256:

```text
e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0
```

The label is static identification, not proof of installed bytes or board state.

## First step now — offline only

With EvilDuck **unplugged**, from the extracted folder:

```bash
python3 preflight.py --directory .
```

Require exit 0 and `package_integrity: PASS`. Without installed metadata, expect
`plan_ready: false`, no selected write ranges, `hardware_access: false` and
`installation_authorized: false`. Stop on rejection. Do not use an install or
rollback launcher for this check. Package integrity is not physical recovery,
installed-image or native High Sierra proof.

## Future read-only/page-RAM observations

Use High Sierra 10.13.6 Chrome and/or the existing iPhone browser as available.
Record actual OS/browser versions and identity evidence from the separately
approved installation receipt. Call an application hash *installer-recorded*
unless independently read back. Do not start diagnostics or a payload for identity.

1. **Successful read:** choose one owner-approved benign, existing internal script
   by exact path with **Scripts → Edit** or editor **Load**. Confirm expected source,
   filename/destination and separate successful-load status. Do not use Save, Run,
   Upload or Del. A source view is not a byte backup or server version.
2. **New/draft, optional and page-RAM only:** choose **New**, accepting a discard
   decision only deliberately. Its template must appear without any automatic
   save/run. Make a harmless unsaved comment in this new RAM document; attempt to
   load an approved existing script and choose **Cancel**. Confirm the new draft
   and its original target remain together. Never press Save or Run, even if
   enabled. Explicitly discard the RAM draft when finished; page reload/close can
   lose unsaved work. This does not mutate the existing device file.
3. **Failure display, only if naturally encountered:** the error belongs in the
   separate status area, not as generated HTTP/REM source in the textarea.
   Save/editor Run should be unavailable, with any prior source retained and
   locked to its original identity. Do not press these controls to prove a guard
   on hardware. **Retry load** is a deliberate read; **Restore preserved draft**
   restores the prior document/identity without writing or running it. If no
   failure occurs, record *not observed*, not FAIL.

Keep the global STOP/execution controls reachable without sending STOP merely to
review the page. Preserve sanitized notes/screenshots privately; do not publish
source contents, passwords, headers, HAR files or private receipts. Do not change
autorun/timing, enable USB storage, create a device fixture or clear evidence.

Forced 401/404/409/5xx, malformed/empty responses, network/deadline failures, stale
replies, direct handler calls and cross-file Save/Run guards are covered by inert
fixtures. No owner is asked to force failures or execute/overwrite stored scripts.
Those software results are not physical passes. A bounded owner observation
validates only its actual configuration and transitions; unobserved cases remain
software-tested only. Server atomic Save/Run/versioning and SD path ambiguity
remain limitations. Record unexplained symptoms without replay or speculative fixes.

The four accepted right-modifier trials, executed STOP variant, three lock-wait
groups and scoped privacy milestone remain closed. Request gaps do not require
retesting. No keyboard, Caps, LED protocol or lock-wait campaign belongs here.

## Recovery boundary

Exact older source/text-v2 rollback: **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It has **no Privacy Fix 1, dashboard cleanup or editor repair**. Application rollback
does not restore deleted scripts, SD contents or past settings. Existing backups
remain untouched. Do not invoke rollback during review; physical recovery requires
separate approval. Until a fixed build is separately installed and confirmed,
continue avoiding Save/editor Run after failed loading on the installed firmware.
