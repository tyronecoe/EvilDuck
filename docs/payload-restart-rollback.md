# Exact text/keyboard rollback — review only

Rollback target: accepted `ROUTEB-TEXT-KEYBOARD-v1`, **1,412,400 bytes**, SHA-256 `53acc374ef38be652b6847d4b84f2dc7d42fa73a3dd54ea62d5208be4cbc0167`. Application source commit: `3780a4884bfd5eab9394b2fa5626298f62712349`; accepted release commit: `b6d85e6da700774345c584f4f67fa5df4f0ea854`.

Package assembly must extract `application.bin` from unchanged `evilduck-routeb-text-keyboard-macos-v1.zip` (**2,336,378 bytes**, SHA-256 `9a60e91e142fea74b746bef352d16139cccaf9fd45ca5e5a10549c91b846dc9e`) and independently verify its exact size/hash before binding it as the new `rollback-application.bin`. The older randomization/jitter image inside that previous package is **not** this release's rollback target. Preserve all historical archives and receipts unchanged.

Future restoration needs separate owner authorization and satisfied chip/security, installed-layout/OTA metadata and ROM recovery prerequisites. App rollback does not promise transactional settings/files restoration; this release changes no schema or partition layout. Original firmware remains OWNER CONFIRMED: AVAILABLE EXTERNALLY, not a new availability blocker or proof of physical recovery.

After separate authorization, the bound launcher's future command shape is:

```bash
bash rollback-macos.sh --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example only. No hardware recovery operation is performed during development. Keep the accepted application, historical public artifacts and private backups untouched.
