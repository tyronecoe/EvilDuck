# Editor-safety review package — platform targets and evidence

**NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED.** This package adds no platform,
USB, HID, host-data collection or scripting capability. Its exact application is
1,437,696 bytes, SHA-256
`e825a8fb8e1c52ec998509b0191939e47572806b156ca591e51be1ece356fff0`,
with static label `ROUTEB-EDITOR-SAFETY-UNINSTALLED-v1`. A label alone does not prove
installed bytes or physical acceptance.

Four surfaces remain independent: **browser dashboard**, **wired USB input**,
**installation tooling**, and **script/application/shortcut assumptions**. Success
in one does not establish the others. The same ESP32-S3 image is not evidence
that a Mac-specific script, keyboard layout or shortcut works on another OS.

## Compact evidence matrix

UNTESTED means unavailable or unperformed, not FAIL. Earlier owner results retain
their original release/configuration scope. This table does not promote them to
physical acceptance of the editor candidate or this review ZIP.

| Target OS/version | Browser / device / layout evidence | Dashboard surface | Existing wired USB input | Installation surface | Script/application assumptions |
|---|---|---|---|---|---|
| macOS High Sierra 10.13.6 | Owner MacBook; Chrome target, exact version and adapter/cable not recorded for these closeouts. Earlier Canadian/US observations separately scoped; right-modifier layout unknown. | Historical owner dashboard use; current editor repair is software-tested only. Native candidate navigation/draft/failure observations remain unverified. | Four scoped right-modifier owner passes including the executed STOP variant, and three planned lock-wait groups remain accepted on their recorded releases. No all-layout, report-byte or host-global release guarantee. | Review package targets Bash 3.2, Python 3.8+ (owner previously reported 3.8.10) and preinstalled esptool 4.12. Linux offline/mock/source-grammar checks do not prove this ZIP ran natively on High Sierra. | Existing harmless TextEdit examples are historical scope; no physical payload is requested for this editor review. |
| Newer macOS, version unspecified | Safari/Chrome targets; exact OS, browser, device, adapter and layout unknown. | UNTESTED natively. | UNTESTED for this target. | Not separately validated on newer macOS; do not infer from High Sierra or Linux mocks. | Application, shortcut and input-source differences require specific evidence. |
| Windows 10 | Edge/Chrome/Firefox targets; device/adapter, versions and layout unknown. | UNTESTED natively. | UNTESTED; generic HID class-driver availability is not a test of this board/cable/policy. | No validated Windows installer supplied. | Mac-oriented applications/shortcuts are not portable by virtue of USB enumeration. |
| Windows 11 | Edge/Chrome/Firefox targets; device/adapter, versions and layout unknown. | UNTESTED natively. | UNTESTED. | No validated Windows installer supplied. | No Windows execution/shortcut compatibility claim; Windows availability does not block independent software verification. |
| Debian GNU/Linux 13 | Chromium 151.0.7922.173 / Playwright 1.62.0; desktop 1280×900 and 320×640/390×844 touch emulation; no board/adapter or keyboard layout exercised. | Reused exact-source evidence: editor **41 groups /309 assertions** and dashboard/privacy **9 groups /207 assertions**, zero final failures, intercepted inert HTTP. The native harness separately repeated 9/207; that repeat is not extra platform coverage. Packaging-stage fresh checks must be distinguished from this reused evidence. | UNTESTED physically; no host input or real report delivery. | Linux ran developer/build/offline/mock checks. No validated Linux physical installation workflow supplied. | No host application, shell or OS shortcut was exercised. Chromium is not relabelled as a tested Google Chrome installation. |
| Other Linux distributions / Chrome / Firefox | Versions, device/adapter and layout unknown. | UNTESTED for those environments. Chromium on Debian does not establish Firefox or another distribution. | UNTESTED. | No validated Linux installer supplied. | Desktop environments and applications differ. |
| Android, model/version unspecified | Chrome target; actual phone, adapter/cable, available power, USB-host/accessory support, permission state and layout unknown. | UNTESTED on a physical Android browser. Touch emulation is not Android evidence. | UNTESTED; actual hardware host/accessory conditions must be established per device. | No phone-based installation support supplied or validated. | Mobile focus, keyboard handling, app shortcuts and capabilities are device-specific. No Pico/Bluetooth result is imported. |
| iOS, model/version unspecified | Safari/Chrome targets; owner iPhone historically used Wi-Fi. Exact model/iOS/browser/version, wired connector/adapter/cable, power, permission state and layout unknown. | Historical owner screenshots show dashboard/editor/list rendering on an earlier installed state; they do not prove the new repair, full navigation or installed-image identity. | UNTESTED; iPhone Wi-Fi access does not prove wired USB keyboard support on that iPhone. | No phone-based installation support supplied or validated. | Browser access, accessory compatibility and app/shortcut behavior are separate; not all iPhone/iOS combinations are equivalent. |

Linux fixture results operate on the tested embedded HTML/JS/CSS with every HTTP
request fulfilled or aborted by an inert allowlist. Mock Save/Run/Delete are test
records, not device mutations. Current ELF/BIN resource matching proves the built
image contains those bytes; it does not prove a real browser received them or a
host accepted/released keys. Firefox, WebKit, native High Sierra, newer macOS,
Windows, Android and iOS were not exercised by Codex for this candidate.

The pre-fix editor error-placeholder overwrite path was reproduced separately.
The repaired source rejects Save/editor Run after unsuccessful loads, and protects
local draft/identity state in fixtures. That shared-JavaScript repair is not an
OS-specific HID change. Unknown native behavior remains a verification gap,
not a universal failure or compatibility promise. The existing modern JavaScript
and browser APIs still need observations on the actual chosen browser/version.

## Retained historical milestones

The four scoped owner-reported right-modifier trials, including the executed STOP
variant, remain accepted. The three planned inherited lock-wait groups and the
scoped dashboard-privacy milestone stay closed. Missing request/session identifiers
are not filled in and do not create a repeat-test requirement. Earlier layout,
randomization, timing and fixed-message observations retain their original
limits; they are not whole-platform or current-candidate certification.

H1 remains explicitly selected and experimental; canonical Hak5 numeric encoding
remains unresolved. This task changes no interpreter, protocol, USB descriptor,
OS detection or host-facing capability. No physical acceptance or broad Caps,
keyboard, LED-return or lock-wait campaign is requested for review packaging.

## Mobile wired prerequisites and source limits

The prior platform audit read the primary references below on 2026-11-02. They
are reused documentation, not new physical tests or fresh claims about any phone:

- [Android USB host/accessory overview](https://developer.android.com/develop/connectivity/usb):
  support depends on actual device hardware; host-mode power, adapter/cable and
  prompts/permissions must be recorded. Accessory mode is a distinct protocol.
  Do not apply an application-level permission rule indiscriminately to an
  OS-managed keyboard.
- [Apple wired accessory approval](https://support.apple.com/en-ca/111806): unlock,
  approval/security settings, connector/model and power conditions matter. Modern
  menu descriptions cannot be assumed for every older iOS device. This is not
  certification that the board works as a keyboard on a given iPhone.
- [Microsoft included USB device-class drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/supported-usb-classes):
  Windows 10/11 HID class drivers establish platform capability, not validation
  of this firmware, cable, policy or intended script.

Future observations should record the exact surface, OS/browser version,
device/adapter/power/permission conditions and layout where relevant. A narrow
browser result must not be copied into USB-input or installer columns. No new
installation capability is introduced merely to fill an untested matrix cell.

## Package and recovery scope

Only the established High Sierra-oriented application-only review workflow is
provided. Offline preflight and device-check/installation are different actions;
use the extracted package README's verified first offline command with EvilDuck
unplugged. No installer execution is authorized by this document. Newer macOS,
Windows, Linux or phone installation support is not advertised without separate
validation.

The exact 1,413,200-byte source/text-v2 rollback remains
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It predates Privacy Fix 1, dashboard cleanup and the editor repair. Application
rollback does not restore owner scripts or past settings, and existing backups
must remain untouched. Until a separately reviewed fixed build is installed and
confirmed, avoid Save/editor Run after failed loading on the installed firmware.
