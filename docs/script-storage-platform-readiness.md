# Script-storage audit — separate platform readiness

This assessment is documentation only. Storage identities and cleanup decisions
are separate from browser, USB-input and installation behavior. A missing script,
an unresolved SD path, an HTTP 401/409 or an OS-specific shortcut is not evidence
of the same failure. No firmware, USB descriptor, OS detection, payload capability
or installation tool is changed in this audit.

The reviewed software baseline is dashboard-cleanup closeout
`e117037a15b5f79ba57abb1fb1da45cd4bb15fbf`, composed from firmware implementation
`0db1f980e0ed05390d71fe9e92178304d7a3bc24` with Privacy Fix 1 and experimental
right-modifier H1. Its exact source identity is in
[the 201-file build inventory](dashboard-cleanup-build.json) and
[the final source manifest](../tests/dashboard_cleanup/source-manifest.json).
The actual composed source, not the root firmware snapshot, was inspected at
`/workspace/scratch/dashboard-cleanup/build-v1/candidate/EvilDuckS3`.

The owner supplied **eleven screenshots**, now reviewed: six full-name editor
views and five script-list views. Five editor views show source/data (three
owner-confirmed Edit selections with short delay content, one partial function
fixture and one canary/test-data view); the sixth shows an HTTP 409 error
placeholder, not saved-file contents. Private bodies and raw captures are not
republished. Many other list names remain truncated. These views establish
neither exact saved bytes/hashes/dependencies nor complete new-navigation
acceptance. Editor views show Request 0 / None; list views show Request 1 /
Completed. They do not identify what Request 1 executed or establish boot/session
ordering. No missing request, layout or browser version is filled in from position
or filename resemblance. Visible iPhone browser chrome does not establish a
particular app/version; Safari is not inferred.

## Four independent surfaces

| Surface | Source-supported contract | What it does not establish |
|---|---|---|
| Dashboard | Local AP and HTTP service on port 80, existing authentication, embedded HTML/JS and explicit controls. Composed `webserver.cpp:39`, `authorize():68`, `prepareControlledNetwork():917`, route registrations `950–996`; `webfiles.h:30–51` global STOP/tabs. | HTTP response authentication does not prove TLS, physical USB behavior or every native browser. HTTP 401 means rejected authentication; 409 may mean a bounded ownership/contention refusal. |
| Existing USB keyboard/input | Composed `hid_backend.cpp:33–46` uses the existing USBHID/USBHIDKeyboard objects; `begin():194–198` starts existing USB; `queueRaw():379–415` submits the existing eight-byte keyboard report, ID 1. | Local report acceptance is explicitly not host ACK (`hid_backend.cpp:396`). Generic class support does not certify a host, adapter, layout, lock state or application. |
| Firmware installation | Existing Mac application-only package, offline preflight and bounded installer gates remain unchanged. [Package identity](dashboard-cleanup-package.json), [reproduction](dashboard-cleanup-reproduction.md), [release report](dashboard-cleanup-report.md). | Linux package/mock PASS and Python 3.8 grammar are not native High Sierra execution or safe physical deployment. No validated Windows/Linux/mobile installer is delivered. |
| Script/application/shortcut assumptions | Route B Planner uses `mapUS()` for ordinary character translation (`keyboard.cpp:56–57`); existing named modifier/report paths remain intact. The separate legacy locale system does not make every Route B script layout-independent. | A script targeting TextEdit, a macOS shortcut or a host shell is not portable merely because the same firmware enumerates as a keyboard. This audit executes no such script and does not change translation or scripting semantics. |

Source line references above refer to the exact composed tree and may be
reproduced through the pinned preparation process. They are not links to an
uncomposed root file with a similar name. Interface-specific LED observations,
local completion and host-global lock/release state remain distinct. H1 stays
opt-in/experimental; canonical Hak5 numeric encoding remains unresolved.

## Compact readiness matrix

**UNTESTED** means unavailable or unperformed, not FAIL. Historical scoped owner
results remain accepted; they are not promoted to all new builds or all layouts.
A fresh storage-audit browser run against the unchanged composed source passed
**9 groups / 207 assertions / 0 failures** ([receipt](script-storage-browser-results.json)).
This is separate from the same-sized historical November 2 run, not an accumulated
18-group or 414-assertion claim. The additional editor-error reproduction below
is a demonstrated shared-UI defect, not a passing safety check or hardware trial.

| OS/version | Device / adapter / browser / layout | Dashboard evidence | USB-input evidence | Installer evidence | OS-specific script scope and limitations |
|---|---|---|---|---|---|
| macOS High Sierra 10.13.6 | Owner Intel MacBook; exact adapter/cable and Chrome version unknown in these closeouts. H1 layout unknown; earlier Canadian/US observations separately scoped. | Historical owner dashboard use, iPhone-assisted controls and scoped privacy milestone retained. Reviewed iPhone screenshots visibly render compact controls; full dashboard-cleanup navigation acceptance/installed-byte identity remains unverified. | Four right-modifier owner-reported passes, including executed STOP variant, and three inherited lock-wait groups remain accepted on their recorded releases. No general report-byte, layout, host-key-release or all-USB guarantee. | Established Mac workflow targets Bash 3.2, Python 3.8 and esptool 4.12. Current package has published Linux offline/mock checks; native execution of that package was not performed by Codex. | TextEdit and benign fixtures are the recorded application scope. Do not assume a macOS-specific shortcut/application exists on other OSs. No repeated accepted keyboard tests required for this audit. |
| Newer macOS, version unspecified | Device/USB adapter, Safari/Chrome version and layout unknown. | UNTESTED on native newer macOS. | UNTESTED. | UNTESTED on this OS; do not infer from High Sierra or Linux mocks. | macOS version/application/input-source differences need evidence for a chosen harmless use, not OS detection in firmware. |
| Windows 10 | Device/adapter, Edge/Chrome/Firefox version and layout unknown. | UNTESTED. | UNTESTED; Microsoft class-driver documentation is capability evidence only. | No validated Windows installer supplied. | Windows applications and shortcuts differ from TextEdit/macOS. No Windows script was run or certified. |
| Windows 11 | Device/adapter, Edge/Chrome/Firefox version and layout unknown. | UNTESTED. | UNTESTED; included HID class drivers are not a test of this composition. | No validated Windows installer supplied. | Same script/application boundary; future chosen use must be harmless and separately authorized. Windows availability is not a prerequisite for independent read-only Mac/storage work. |
| Debian GNU/Linux 13 | No device/adapter. Chromium 151.0.7922.173, Playwright 1.62.0; keyboard layout not exercised. | Fresh audit PASS: actual embedded UI, inert intercepted HTTP; one shared suite **9 groups / 207 assertions / 0 failures**, desktop 1280×900 plus 320×640/390×844 touch emulation. [Fresh receipt](script-storage-browser-results.json). Earlier [November 2 receipt](dashboard-cleanup-browser-results.json) remains historical. Separate mocked editor-error reproduction: one defect and one normal-load control, 20 checks; not a safety PASS. | UNTESTED; no physical USB device, host input or report delivery. | Package/preflight/mock checks ran on Linux; Linux physical installation remains unvalidated. | No host application or shell behavior exercised. Chromium is not relabelled as a tested Google Chrome product. |
| Other Linux distributions / browsers | Devices/adapters, Chrome/Firefox versions and layouts unspecified. | UNTESTED for those products/environments; Chromium fixture result does not establish Firefox. | UNTESTED. | No validated Linux installation workflow supplied. | Desktop environment, applications and shortcuts vary. |
| Android, model/version unspecified | Actual phone, USB-host support, adapter/cable, power, browser Chrome version, permissions and input layout unknown. | UNTESTED on physical Android. Touch emulation is not Android execution. | UNTESTED; must establish actual hardware host capability and conditions. No Bluetooth/Pico-bridge result is imported. | No phone-based installation support supplied or validated. | Mobile focus, physical keyboard handling, applications and shortcuts need a bounded chosen-use check; OS name alone is insufficient. |
| iOS, model/version unspecified | Owner iPhone using Wi-Fi; browser chrome visible in reviewed screenshots, exact app/version, model/iOS, wired connector/adapter/cable, power, permission state and layout unknown. | Owner screenshots show current compact controls and editor/list views; they do not establish complete navigation acceptance, saved-file hashes or installed-byte identity. No native browser execution by Codex. | UNTESTED; iPhone Wi-Fi screenshots do not prove USB keyboard input on that iPhone. No Pico bridge/Bluetooth evidence is borrowed. | No phone-based installation support supplied or validated. | Touch/browser access, wired accessory support and app/shortcut behavior are different surfaces. Do not assume every iPhone/iOS combination is equivalent. |

The fresh and historical Linux browser runs were memory-only, with an exact inert
HTTP allowlist and unknown requests aborted. Each run's desktop and touch profiles
share one suite total; they must not be counted as multiple independent OS passes.
Firefox and WebKit were unavailable in that environment. The available receipt
is scoped to its exact source hash and engine, not native Chrome on High Sierra,
any iPhone browser or arbitrary future firmware.

## Accepted evidence retained without reopening milestones

- [Right-modifier owner closeout](h1-right-modifiers-owner-closeout.md): four
  scoped owner-reported High Sierra passes, including the executed STOP variant.
  Request 2 remains unknown; source/readback, boot/session and original capture
  limitations remain. These gaps do not create a retest requirement.
- [Inherited lock-wait closeout](h1-lock-wait-owner-closeout.md) and
  [owner correction](h1-right-modifiers-owner-correction.md): **3/3 planned
  groups accepted**. Distinct earlier inconclusive attempts stay historical and
  do not reopen the accepted groups.
- [Randomization evidence](randomization-jitter-owner-evidence.md): Canadian/US
  observations apply to those short examples/builds; they are not general locale,
  punctuation/dead-key or randomness/timing certification.
- The task handoff preserves the scoped dashboard-privacy milestone. This audit
  does not invent unsupplied trial dates, installed application hashes or native
  browser versions to strengthen it.

No new broad Caps investigation, keyboard campaign, Windows dependency or
receipt-checker stage is requested. The mandatory rollback remains the exact
source/text-v2 application SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`,
older code without Privacy Fix 1 or dashboard cleanup. An application rollback
cannot restore deleted scripts, filesystem bytes or past settings.

## Primary platform constraints and next evidence

The following official references were read in the prior dashboard task on
**2026-11-02** and are reused as documentation, not freshly queried hardware:

- [Android USB host/accessory overview](https://developer.android.com/develop/connectivity/usb)
  (displayed last update 2026-10-23): host/accessory support ultimately depends on
  device hardware; the host powers the bus. Record exact phone/OS, host support,
  adapter/cable, power and actual prompts/permissions. Android accessory mode is
  distinct from this existing HID interface. Do not assume an app-level USB
  permission rule universally governs OS-managed keyboard input.
- [Apple wired accessory approval](https://support.apple.com/en-ca/111806)
  (displayed publication 2025-10-23): unlock/approval settings and connector/model
  conditions matter. Record actual model/iOS, adapter, available power and
  permission state. The page is not certification that this board is an iPhone
  keyboard, and modern menu text may not match older devices.
- [Microsoft included USB device-class drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/supported-usb-classes)
  (metadata 2025-06-11): HID class drivers exist for Windows 10/11. That is not
  physical validation of this firmware, cable, host policy or script.

A **shared dashboard editor defect** is now source-supported and reproduced with
inert Linux Chromium: a failed GET writes a `REM Load failed` placeholder into
the editor, and a later explicit Save can submit that placeholder as replacement
source. The [observation receipt](script-storage-editor-error-observation.json)
records **1 OBSERVED_DEFECT + 1 CONTROL_CONFIRMED, 20 checks, no harness error**;
exit zero means the reproduction completed, not that this behavior is safe. No
automatic save or real-device overwrite occurred. See [the audit report](script-storage-audit.md).
The affected composed path is `webfiles.h:875–927` (load/editor/save); this issue
is not attributed specifically to High Sierra, iOS or another OS. Do not Save or
use editor Run after a failed load. A bounded repair needs separate implementation
scope; this audit changes no firmware.

The screenshot combining a 409 placeholder with Request 0 / None does not prove
an active payload. The existing storage-admission path can reject lock contention
as well as ownership; the precise device-side cause remains unknown. It does not
prove a missing file or an OS/USB regression. No newly reproduced OS-specific
dashboard defect is established. Older native Chrome/Safari behavior, mobile
accessory support and unknown browser versions remain verification gaps, not
universal failures. The existing modern-JavaScript features and browser APIs must be tested on the actual
chosen browser before claiming native support; Linux Chromium alone is not proof.
If a concrete portability issue is later reproduced with inert data, propose a
small browser-only repair with exact source/engine evidence and separate scope.
Do not change USB identities, add OS detection or implement new execution/HID
capability to fill a table cell.

The immediate next evidence is the owner-local **read-only file inventory and
private archive verification** specified by the storage audit. It neither needs
nor authorizes any new payload, diagnostic action, settings reset, cleanup or
firmware installation. Keep that work independent of future browser/USB checks.
