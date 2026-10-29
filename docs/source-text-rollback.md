# Exact restart rollback — review only

Rollback target: accepted `ROUTEB-PAYLOAD-RESTART-v1`, **1,412,688 bytes**, SHA-256 `1d4ea6394306885b832619adb3436eaeeccc0a67ce8b73e1f20dd0f9c7d0a060`. Application source commit: `f9f343ce9ff5362e143f5410ad353e55d3868414`; accepted release commit: `2bdf7e6cea7fb1a343d4ac0973a90578264ced07`.

Extract `application.bin` from unchanged `evilduck-routeb-payload-restart-macos-v1.zip` (**2,371,203 bytes**, SHA-256 `36e2ca0df08eeea1cec5e766330a0e4699351d28cfa2b2f382d3e112052d15f2`) and independently verify its exact size/hash before binding it as the new `rollback-application.bin`. The older text/keyboard image inside that package is **not** the new rollback target. Preserve historical archives and receipts unchanged.

Future restoration needs separate owner authorization and satisfied chip/security, installed-layout/OTA metadata and ROM recovery prerequisites. App rollback does not promise transactional settings/files restoration; this release changes no schema or partition layout. Original firmware remains OWNER CONFIRMED: AVAILABLE EXTERNALLY, not a new availability blocker or proof of physical recovery.

After separate authorization, the existing bound launcher's future command shape is:

```bash
bash rollback-macos.sh --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example only. No hardware recovery operation occurs during development. Keep the accepted application, historical public artifacts and private backups untouched.
