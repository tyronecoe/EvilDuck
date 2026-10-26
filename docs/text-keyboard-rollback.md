# Exact randomization/jitter rollback — review only

The rollback target is accepted `ROUTEB-RANDOMIZATION-JITTER-v1`, **1,411,088 bytes**, SHA-256 `2e1d8345417c6f23a5df3d884db42dd2a0f9f305120ee494c56a58048e677496`. Its source archive is unchanged `evilduck-routeb-randomization-jitter-macos-v1.zip`, SHA-256 `a25e703dbd8198fa9dfa29f3f04a278ae0b704ae220bd377b8fad0036ac964d1`.

Package assembly must extract that prior archive's `application.bin` and verify exact bytes/hash before binding it as the new package's `rollback-application.bin`. The older uppercase image inside the prior package is not this release's rollback target. Distinct historical ZIP/app hashes are not evidence that the older package was incorrect.

Future restoration requires separate owner authorization and satisfied chip, security, installed-layout/OTA metadata and ROM recovery prerequisites. This work performs no physical recovery verification. App rollback does not promise transactional settings/files restoration; this release changes no settings schema or partition layout.

After separate authorization, the existing bound launcher's future command shape is:

```bash
bash rollback-macos.sh --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example only. No rollback command is executed against hardware during development. Preserve the working application, historical public artifacts and private backups.
