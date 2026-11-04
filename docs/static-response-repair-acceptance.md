# Static-response repair — short owner-review sheet

**NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED.** The new review package does not
establish that the installed device is fixed. Installation and the observations
below remain separate owner-operated steps after authorization. This sheet asks
for no payload, settings save, owner-file change or repeated keyboard milestone.

Candidate label: **`ROUTEB-STATIC-RESPONSE-REPAIR-v1`**. Use the final package
manifest/report for the exact application hash and size. A build label, filename
or successful flash comparison alone does not establish dashboard operation.

## First step now — offline only

With **EvilDuck unplugged**, from the extracted folder:

```bash
python3 preflight.py --directory .
```

Require exit 0 and `package_integrity: PASS`. Without installed metadata, expect
`plan_ready: false`, `selected_write_ranges: []`, `hardware_access: false` and
`installation_authorized: false`. Stop on rejection. Do not run an install,
device-check or rollback launcher as this offline check.

## After a separately authorized installation

Preserve the installation receipt privately. Record the actual OS/browser
versions and the candidate application identity; call its hash
*installer-recorded* unless independently read back. Do not reset credentials,
enable diagnostics or run a script for this observation.

1. **Fresh full-page delivery:** on the High Sierra Mac, use a fresh Chrome
   Incognito window at `http://192.168.4.1/`. With Developer Tools → Network open,
   check **Disable cache** and perform one deliberate page load. Inspect that
   load's **index.js** response: HTTP 200, JavaScript content type, **31,932 body
   bytes**, and a nonempty JavaScript Response. A success fetched in isolation
   does not replace this full-page observation. A zero-length response is a
   serving failure even if its status is 200. The unrelated favicon 503 is not
   the password-handler failure.
2. **Handler, authentication and status:** enter the existing dashboard password
   in the normal dashboard field, then click outside it once. This changes
   browser-session state, not the saved device password. Require no
   `saveDuckPw is not defined` error, successful authenticated status retrieval,
   populated SSID/channel/status fields, and execution text that leaves
   **Checking execution**. On an idle device, the running tile should show
   **Idle**. The combined transition verifies that the handler is available;
   no console code or password disclosure is required. Do not press Save, Run,
   Upload, Del, STOP or diagnostic-start controls.
3. **Separate iPhone observation, if available:** after Mac delivery/authentication
   is recorded, use a fresh Chrome session on the iPhone connected to EvilDuck Wi-Fi and
   repeat only normal page load, password entry and populated-status observation.
   Record the actual iPhone/iOS/browser versions if available. Without mobile
   network inspection, record response length as **not measured on iPhone**;
   do not copy the Mac's measurement into that result. The status-bar LTE icon
   alone does not establish the network path or invalidate the owner's reported
   Wi-Fi connection.

Expected script body SHA-256, if a separate harmless GET/hash check is needed:

```text
7fb8068beb12564dc4e5146e8b6b0a9b719b78caf3f4d94cd0f2b8a2c04baf39
```

The 31,932-byte HTTP body excludes the C terminator; the earlier 31,933-byte
embedded-resource measurement includes it. Preserve sanitized status, body length,
error text and UI screenshots associated with this run. Never put the password in
a URL or share it, request headers, HAR exports, script contents or private
installation/backups. No automatic retry or repeated stress campaign is required;
stop on an unexplained failure and retain the partial evidence.

## Classification and preserved history

Record **PASS** only for the observed configuration and transitions above. A
remaining empty-script/undefined-handler failure on the new image is a failed
observation of this repair; missing or ambiguous evidence stays **UNVERIFIED**.
Classify a demonstrated host/tooling constraint as **PLATFORM-LIMITED** where
appropriate. Mac and iPhone results remain separate; neither proves other
platforms, USB behavior or general reliability.

The prior `e825a8fb…56fff0` editor-safety image was owner-installed and exhibited
the confirmed HTTP 200 / `Content-Length: 0` dashboard failure. It is retained as
historical evidence, **not a known-good recovery image**. Its earlier software
and package passes did not establish a functioning physical dashboard.

The accepted right-modifier trials, executed STOP variant, three lock-wait groups
and scoped privacy milestones remain closed. This sheet does not reopen them or
request another Caps, keyboard, LED-return or layout campaign.

Mandatory rollback remains the older **1,413,200-byte** source/text-v2 application:

```text
cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02
```

It predates Privacy Fix 1 and the dashboard/editor repairs. It is an application
image, not merged/full-flash recovery; rolling it back does not restore scripts,
filesystem contents or earlier settings. Preserve the private owner backup ending
**w7uhm8z7** unchanged and never upload its contents. Do not invoke rollback during
this review. Until a fixed installation is separately confirmed, continue avoiding
Save/editor Run after a failed load on the installed firmware.
