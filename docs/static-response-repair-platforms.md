# Static-response repair — platform targets and evidence

**NOT INSTALLED / NOT OWNER-HARDWARE-VERIFIED.** The new candidate targets the
static HTTP response defect. It adds no OS detection, keyboard layout, USB/HID,
payload, host-data collection or installer capability. Candidate label:
`ROUTEB-STATIC-RESPONSE-REPAIR-v1`; exact application identity belongs to the final
manifest/report, not the label alone.

Browser access, wired USB input, installation tooling and script/application
assumptions are four independent surfaces. A Linux target build or a byte-correct
package does not validate native browser delivery or physical USB behavior.

| Target | Browser/dashboard evidence | Wired USB input | Installation surface | Script/application assumptions |
|---|---|---|---|---|
| macOS High Sierra 10.13.6 | Owner Chrome **116.0.5845.187**, including fresh Incognito. The prior owner-installed e825 image returned HTTP 200 with `Content-Length: 0` for `index.js`, with the handler undefined and Checking stuck. An isolated GET separately returned the correct 31,932-byte file. The new candidate's full-page delivery/authentication remains **UNVERIFIED** pending owner observation. | Earlier scoped right-modifier, executed STOP-variant and lock-wait passes remain accepted on their recorded configurations. No new physical USB or all-layout claim. | Established Mac workflow targets Bash 3.2, Python 3.8 and preinstalled esptool 4.12. The owner reported writes and both comparisons passing for the prior faulty dashboard image. That does not validate this new ZIP or runtime behavior. Its native execution remains pending. | Existing benign TextEdit/layout observations keep their original scope; no payload or shortcut is exercised for this repair. |
| Newer macOS, version unspecified | **UNTESTED** natively for this candidate. Exact OS/browser/device are unknown. | **UNTESTED** for this target. | Not separately validated on newer macOS. | App, focus, shortcut and input-source assumptions require separate evidence. |
| Windows 10 | Edge/Chrome/Firefox are possible browser targets; native versions/device unknown. **UNTESTED**. | **UNTESTED**; availability of a generic HID driver is not board/cable/policy validation. | No validated Windows installer supplied. | Mac-oriented scripts and shortcuts do not become portable through USB enumeration. |
| Windows 11 | **UNTESTED** natively; browser/device/version unknown. | **UNTESTED** for this target. | No validated Windows installer supplied. | Future Windows validation is independent; its availability does not block Mac-compatible software work. |
| Linux developer environment | Actual composed sources and SDK response behavior are exercised by native mocks and inert Chromium/Playwright fixtures. Final receipts distinguish newly run checks from reused editor/privacy evidence. These are **software checks**, not a native owner dashboard pass or a whole HTTP/TCP/ESP32 heap test. | No board, host input or real HID report delivery exercised. | Developer/build/offline/mock checks run here; no validated physical Linux installation workflow supplied. | No host application, shell or OS shortcut is executed. Linux Chromium is not relabeled as tested Google Chrome on High Sierra. |
| Other Linux distributions/browsers | **UNTESTED** for unrecorded distributions, Firefox or other browser versions. | **UNTESTED**. | No validated physical Linux installer supplied. | Desktop environment/application behavior varies. |
| Android, model/version unspecified | Physical Chrome/other-browser behavior **UNTESTED**. Touch emulation is not Android evidence. | **UNTESTED**; actual USB-host/accessory support, adapter, power, permission and layout conditions are unknown. | No phone-based installation support supplied or validated. | Mobile focus, app shortcuts and device capabilities require specific tests. |
| iOS/iPhone, exact versions unspecified | Owner reports **Chrome on iPhone**, connected to EvilDuck Wi-Fi, with the same stuck Checking display. The supplied screenshot supports that UI symptom. The LTE indicator does not prove the connection path; no cause for that icon is inferred from Low Data Mode. No iPhone response-length/heap measurement exists. The new candidate remains **UNVERIFIED** on iPhone. | **UNTESTED**; iPhone Wi-Fi dashboard use does not prove wired keyboard/accessory support. | No phone-based installation support supplied or validated. | Browser access, wired accessory behavior and app/shortcut handling remain separate. |

**UNTESTED/UNVERIFIED** means unavailable, unperformed or insufficient evidence,
not universal implementation failure. The prior e825 image's observed empty
JavaScript is a concrete dashboard serving failure in the tested configuration;
it must not be erased by earlier software/package passes or called known-good
recovery. Those receipts remain valid for what they actually checked.

The new repair uses static-lifetime resource arrays and explicit byte lengths
through the pinned SDK streaming response overload. Software fixtures cover exact
bodies, partial reads and simulated allocation/concurrency conditions. They do
not measure real ESP32 heap pressure or certify physical browser/TCP behavior.
Complete resources embedded in ELF/BIN were present in the old image too; new
linked response-path verification is separate from owner runtime acceptance.

The four scoped owner-reported right-modifier trials, including the executed STOP
variant, three lock-wait groups and scoped privacy milestones remain closed.
Missing request/session identifiers remain unknown and do not require repeats.
Earlier Canadian/US layout, randomization/timing and fixed-message observations
are not promoted to general OS or new-candidate compatibility. H1 stays opt-in
and experimental; canonical Hak5 numeric encoding remains unresolved.

Only the established High Sierra-oriented application-only review package is
provided. Use its verified offline first command with EvilDuck unplugged:

```bash
python3 preflight.py --directory .
```

Offline integrity and a possible future device check/installation are different
actions. No installation is authorized by this table. A later narrow owner pass
must name its actual OS/browser/version and image identity, without being copied
into the USB, installer or script columns.

The exact older source/text-v2 rollback remains **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It lacks Privacy Fix 1 and later dashboard/editor repairs. It is not merged/full
recovery, does not restore scripts or past settings, and must not be confused with
the faulty e825 candidate. Existing published artifacts and the private owner
backup ending **w7uhm8z7** remain untouched; no backup contents are inspected or
published for this stage.
