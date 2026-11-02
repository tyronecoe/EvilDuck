# Dashboard cleanup — platform targets and evidence boundaries

This is one firmware/dashboard candidate with explicit platform targets, not an
OS-detecting firmware or a claim of universal compatibility. The UI cleanup adds
no USB descriptor, keyboard report, host-specific execution or installation
capability. An OS-specific shortcut, application or shell command in a script
still depends on that host and does not become portable merely because USB HID
is available.

Three surfaces are independent:

1. **Dashboard:** a browser accesses the Wi-Fi web interface.
2. **USB input:** a wired host recognizes and uses the existing keyboard interface.
3. **Installation:** validated tooling can safely inspect and update firmware.

A dashboard PASS does not establish USB input or installation support. A successful
compile, generic HID class support or a mobile viewport does not establish any
physical-host result. UNTESTED means unavailable/unperformed, not FAIL.

## Compact matrix

Current-candidate inert browser checks passed **9 groups / 207 assertions / 0
failures**, as recorded in the [browser receipt](dashboard-cleanup-browser-results.json).
The actual embedded HTML/CSS/JS was exercised with intercepted HTTP and no real
network requests, device operations or payloads. No current-candidate physical
platform result is claimed. Exact physical adapters, power arrangements, browser
versions and layouts not recorded by the owner remain unknown.

| OS/version | Device / USB adapter | Browser/version | Keyboard layout | Dashboard result | USB-input result | Installer result | Evidence type |
|---|---|---|---|---|---|---|---|
| Debian GNU/Linux 13 | Headless browser fixture; no board/adapter | System Chromium 151.0.7922.173; Playwright 1.62.0 | Not exercised | PASS: inert 1280×900 desktop fixture; shared suite totals 9 groups / 207 assertions / 0 failures | Not tested | Linux installation not validated; retained Mac workflow only | Actual embedded UI with intercepted HTTP, not physical Wi-Fi/USB evidence |
| Debian GNU/Linux 13, touch emulation | 320×640 / 390×844 virtual viewports; no phone, cable or power source | Same system Chromium | Not exercised | PASS: inert layout/navigation fixtures at both sizes; included in shared totals above | Not tested | No phone installation support inferred | Browser viewport/touch emulation, not Android/iOS execution |
| macOS High Sierra 10.13.6 | Owner's Intel MacBook; exact adapter/cable not supplied for these closeouts | Chrome target; exact version unknown and not bound to every historical trial | H1 trial layout unknown; earlier Canadian/US examples remain separately scoped | Historical owner dashboard use; scoped privacy milestone retained as closed per task handoff. New UI: UNTESTED | Historical four right-modifier passes, including executed STOP variant, and three lock-wait groups remain accepted. New candidate: UNTESTED | Existing High Sierra package workflow retained; current package software/native-Mac results must be recorded separately | Scoped owner reports plus prior offline/mock evidence; no new device readback |
| Newer macOS, version unspecified | Device/adapter unknown | Safari / Chrome, versions unknown | Unknown | UNTESTED | UNTESTED | Not validated on this OS; do not infer from High Sierra | Explicit future targets, unavailable physical environments |
| Windows 10 | Device/adapter unknown | Edge / Chrome / Firefox, versions unknown | Unknown | UNTESTED | UNTESTED | No validated Windows installer provided | Explicit future targets; OS class-driver documentation only |
| Windows 11 | Device/adapter unknown | Edge / Chrome / Firefox, versions unknown | Unknown | UNTESTED | UNTESTED | No validated Windows installer provided | Explicit future targets; OS class-driver documentation only |
| Linux, other/current distributions unspecified | Device/adapter unknown | Google Chrome / Firefox, versions unknown | Unknown | UNTESTED for those products; Chromium fixture evidence is the separate row above | UNTESTED | Linux installation not validated | Product/OS targets distinct from the available Chromium engine |
| Android, version/model unspecified | Actual host-capable phone, adapter/cable, power and permission state unknown | Chrome, version unknown | Unknown | UNTESTED | UNTESTED; hardware host/accessory support must be established | Phone-based flashing not provided or validated | Platform target and general Android documentation, no device evidence |
| iOS, version unspecified | Owner's iPhone used Wi-Fi previously; model, wired adapter/cable, power and permission state unknown | Safari / Chrome targets; exact versions unknown | Unknown | Historical iPhone Wi-Fi dashboard use is owner-reported. New UI: UNTESTED | UNTESTED; Wi-Fi access proves no wired-input support | Phone-based flashing not provided or validated | Prior owner Wi-Fi observations, not USB or current-candidate validation |

Chromium is recorded as Chromium, not relabelled as a tested Google Chrome
installation. Firefox and WebKit executables were unavailable in the discovered
environment. No native High Sierra Chrome, newer macOS Safari/Chrome, Windows,
Android or iOS browser execution is implied by Linux emulation.

## Preserved historical observations

The [right-modifier owner closeout](h1-right-modifiers-owner-closeout.md) records
four scoped High Sierra owner-reported passes, including the executed STOP
variant. Its Request 2 gap, cropped build-ID limitation and unavailable original
screenshots/logs remain unchanged. It does not independently establish every
report byte, keyboard layout or general host-release behavior.

The [inherited lock-wait closeout](h1-lock-wait-owner-closeout.md) and later
[owner correction](h1-right-modifiers-owner-correction.md) retain acceptance of
**3/3 planned groups**. Request gaps do not create repeat-test requirements.
Earlier Canadian/US layout observations are limited to the earlier examples and
builds, as retained in [randomization owner evidence](randomization-jitter-owner-evidence.md).
They are not imported as punctuation/dead-key or all-layout certification.

The task handoff states that scoped dashboard-privacy milestones remain closed.
This preserves that owner-reported status without inventing trial dates, browser
versions, device readbacks or receipt/session identifiers. It does not mark the
new dashboard-cleanup image physically accepted or request repeat keyboard tests.

The [Privacy Fix 1 package report](privacy-fix1-macos-package.md) distinguishes
Linux offline/mock checks and Python 3.8 syntax checks from unperformed native
High Sierra execution. The new cleanup candidate must retain that distinction.
Only the verified High Sierra preparation workflow is carried forward; no
Windows/Linux installation claim or mobile flashing interface is introduced.

## Wired phone and Windows boundaries from primary sources

- **Android:** the official [USB host/accessory overview](https://developer.android.com/develop/connectivity/usb)
  lists keyboards among host-mode devices, explains that the Android host powers
  the bus, and states that host/accessory support ultimately depends on device
  hardware, regardless of platform level. Android accessory mode is a distinct
  protocol and is not evidence that this existing HID firmware implements it.
  For a future wired-input observation, record the actual phone/OS, host support,
  adapter/cable, available power and any prompts/permissions encountered. Do not
  infer that an application-level USB permission rule universally governs an
  OS-managed keyboard. Page displayed **Last updated 2026-10-23 UTC** when read.
- **Apple:** [Allow USB and other accessories to connect to your iPhone or iPad](https://support.apple.com/en-ca/111806)
  says a device normally must first be unlocked for an accessory connection and
  describes model-dependent wired-accessory approval settings. This is a security
  prerequisite, not certification of this board/adapter as an iPhone keyboard.
  Record the actual model, iOS version, connector/adapter/cable, power and observed
  approval state; the modern menu descriptions must not be assumed for every
  older iOS device. Page displayed **Published Date: October 23, 2025** when read.
- **Windows:** Microsoft's [included USB device-class drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/supported-usb-classes)
  lists HIDClass/Hidclass.sys and Hidusb.sys for Windows 10/11. Included class
  drivers explain a platform capability; they do not prove this composed
  firmware, a particular cable/port, host policy or script works. Metadata
  reports **2025-06-11**. No driver installation or Windows hardware test occurred.

These three public references were read on **2026-11-02**. Source documentation
is labelled separately from owner reports, browser fixtures and physical tests.
No hardware, private host data, credentials or original firmware was accessed.

## Updating evidence without reopening closed milestones

The Linux desktop and touch-emulated fixture results above are complete and
linked to their receipt. Record any unavailable native platform or engine as
UNTESTED. Add current package offline/mock results separately; they do not
promote any physical installer cell.

For a later separately approved owner check, exercise navigation, mobile
readability/scrolling, authentication errors, reachable STOP, Diagnostics
visibility and unchanged timing/password display. Do not require a live
diagnostic trial, trace enable, Caps toggle, payload or repeated keyboard campaign
merely to validate this rearrangement. Preserve the existing rollback and all
previous evidence; a new platform observation extends only its tested surface.
