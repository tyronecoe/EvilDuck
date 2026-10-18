# Owner acceptance and installation gate

**There is no new verified firmware binary for this change. Do not install the
source-review branch or relabel the previous ZIP as containing these fixes.**
The clean build is blocked by the dependency provenance discrepancy documented
in `caps-queue-build-blocker.json`. Keep the working STOP/LED installation.

Current retained package (unchanged, already owner-installed):

https://raw.githubusercontent.com/tyronecoe/EvilDuck/3dd4a083aa6634cf413ac7a43c36baaa749b7540/downloads/evilduck-stop-led-install-v1.zip

2,133,598 bytes; ZIP SHA-256:
`d7fe3e6400deb689dc807b0a08285dcb06f5682caf134c90aba38e986b83c255`.
Its application is1,376,576 bytes, SHA
`c20dc3991a72b3411c506c107300e57ea96156d3ca233caa682f6a0c6a7a07d4`.
Its included `rollback-application.bin` is the earlier5c19f0d candidate:
1,359,808 bytes, SHA
`de241287b972c24e510d3e8d22d888a17f13d1e972142559ba3df19f6195b41d`.
[The exact existing installation/rollback guide](stop-led-install.md) applies only
to those exact artifacts and its fresh layout/OTA/security gates. Do not edit that
manifest or bypass rejection to install an unbuilt source change.

## Future package preparation, not a hardware action now

After the historical core-tree discrepancy is resolved without weakening pins:

1. Build the new composed source with `tests/caps_queue/build_candidate.py` in a
   new external output directory, then its `verify_link.py` post-check. Verify
   protected USB/NVS sources, compiler/SDK identity, actual linked sources, BIN/ELF
   and production partition geometry.
2. Report that build's actual bytes/hash/resources. Generate a **new** named app-only
   package by adapting the existing strict package/preflight structure, with its
   own artifact pins and rollback to the currently installed c20dc399 application.
   Do not reuse its checksum or the old preflight unchanged for new firmware.
3. Review the actual new package and get separate owner approval. Use fresh chip,
   ROM port, partition and OTA reads; `/dev/cu.usbmodem33` is a past observation,
   not a command default. A different supported layout/OTA state needs review,
   not automatic repair, NVS erase or filesystem formatting.
4. Preserve bootloader/table/NVS/OTA/SPIFFS/coredump/settings/scripts/USB identity.
   Embedded assets need no filesystem upload. Keep the working package and private
   backup resources untouched. Stock availability is owner-confirmed external.

There is deliberately no new write command or automatic installation script for
an unverified binary. No physical activity was carried out as part of this task.

## Staged supervised acceptance, only after a separately reviewed build/install

Use a blank TextEdit document, no host shell or private content. The Mac starts
with Caps off. Disable/record editor automatic capitalization so it cannot be
mistaken for a keyboard lock result. Autorun stays off. Each trial gets **one**
explicit Start; record the request ID. Never automatically repeat a refused,
unknown or queued run.

1. **Basic typing:** `DELAY 5000` then `STRING 123test456`. Expected exact text,
   same request terminal Completed and no device faults. Queued alone is not PASS.
2. **Caps path:** short `CAPSLOCK` is supported. Record the Mac's actual lock LED
   and before/after letter case separately from device LED feedback. No forced
   uppercase or Caps compensation was added. A short tap may or may not toggle
   this host; source-level report submission is not delivery evidence.
   **Do not repeat the longer HOLD script through Route B:** the selected adapter
   rejects HOLD/RELEASE before output. The new UI should show Unsupported capability.
   A long-press physical experiment requires separately reviewed support; no legacy
   fallback is authorized or automatically selected here.
3. **Raw host LED observation:** with no script running, deliberately toggle host
   Caps and Num separately and refresh Observe LEDs. Capture only state, callback
   count/last ID/length, reports, rejected, session/time evidence and faults.
   Compare counter deltas across the trial; entry counters are boot-lifetime, not proof of a current-session report.
   `callbacks=0` means no keyboard callback reached this handler; it cannot exclude
   upstream rejection. Increasing callbacks but rejected/unknown narrows the failure.
   `connected:false` is not evidence of cable removal. If Caps AND Num evidence are
   absent, stop before the two-bit fake-message sender. macOS may lack usable Num.
4. **Fixed phrase:** only after raw Caps+Num reports are established on that host,
   explicitly start the finite receiver and run the existing reviewed helper once.
   View/download `/led-test/data`. Complete means exactly **17 bytes**
   `EVILDUCK TEST 123`, no newline/JSON/HTML, with device integrity true. Verify
   `wc -c` and compare exact text locally. Incomplete capture must give409 and no
   success-looking download. Independently test Stop receiving and timeout.
5. **Queue / STOP:** start a harmless10-second DELAY then output, cancel before
   output; correlate202 admission with its status ID and Cancelled terminal. Test
   another page/reload and failed poll: STOP remains accessible while uncertain.
   A STOP202 is a request, not confirmed cancellation or host key release. On an
   unexpected fault stop testing and retain sanitized status, line/code and request
   ID. Do not perform a series of blind Starts.
6. **Temporary SD deletion:** create/save a harmless uniquely named temporary file,
   read it back, confirm its SD name in Library, cancel Delete once (file remains),
   then confirm exactly that target and verify disappearance. A firmware-only entry
   has no Delete. Try while a harmless delayed script owns storage:409, no deletion.
   Never test by deleting an existing owner script or formatting media.

## Native helper prerequisites (not run by Codex)

The helpers remain visible, finite and limited to the fake phrase. Read
`host_tests/led_return/README.md`. Native compilation/execution on both hosts is
PENDING; ordinary OS permissions/security policy must be respected.

Mac with already installed Apple developer tools, from `host_tests/led_return`:

```sh
clang -std=c11 -Wall -Wextra send-macos.c -framework IOKit -framework CoreFoundation -o send-macos
```

Only after actual Caps+Num feedback and exact serial matching:
`./send-macos --caps-num-confirmed EXACT_USB_SERIAL`; type SEND deliberately.
Missing/ambiguous output elements or permissions is unsupported, not success.

Windows11 with standard PowerShell5.1/.NET Framework:
`powershell -NoProfile -File .\send-windows.ps1`; no policy bypass or elevation
workaround. It prompts for SEND. Both platforms independently attempt Caps and
Num restoration and fail if unconfirmed. APIs confirming local state do not prove
USB delivery; process kill/power loss can prevent restoration. Check manually.
No helper should be launched by installation or ordinary web Run.
