# Stage27 owner readiness checklist — Stage26 review

REVIEW ONLY — NOT AUTHORIZED FOR FLASHING

## VERIFIED OFFLINE — PASS

- Exact Stage25 source baseline retained; no firmware/interpreter/schema/USB/partition changes.
- Controlled-normal-start requires critical credentials, rejects critical settings failures,
  stops autorun, skips examples and uses SPIFFS.begin(false). Failed setup cannot re-arm itself.
- Layout is checked before application services; this is after Arduino/SDK NVS initialization.
- Clean controlled and deployment-safe builds use isolated Arduino3.3.0 with existing verified
  USB routing and no-auto-erase patches. Final source/core/SDK/ELF-to-BIN provenance passed.
- Standard S3 bootloader0/table0x8000,16MiB image profile,80MHz, both0x740000 OTA slots,
  canonical table/MD5 and initial app0 metadata are validated.
- Public artifact set, SHA256SUMS and fail-closed validator are present. Empty filesystem was
  packed/unpacked with the pinned geometry. New coredump initialization is bounded.
- Private factory schema is exercised using synthetic credentials and exact regeneration;
  no owner secrets or backups are present in Git. Private image publication cannot overwrite
  an existing directory; an interrupted public set cannot pass verification.
- No physical installation, boot, USB, Wi-Fi, storage or recovery tests were executed.

## OWNER CONFIRMATION REQUIRED — BLOCKED until the applicable gate is satisfied

1. Prepare owner-selected strong credentials privately and run the local fresh-image verifier.
   Review only the new private NVS hash/size and complete eight-role range receipt. Do not send
   credentials or backup images to Codex/GitHub. This is the only missing initial-install image.
2. Before an authorized physical session, confirm the correct board/serial path, stable power,
   data cable and usable ROM download/recovery access; compare chip/16MiB/security facts with
   the already supplied historical evidence. No repeated request for those facts is made here.
   Actual recovery execution for these new artifacts remains untested, not a demonstrated FAIL.
3. Review the complete image/range plan and explicitly authorize the chosen physical operation,
   including fresh NVS/SPIFFS replacement, both apps and the separately controlled first boot.
   Stop if observations or hashes disagree. This approval has not been supplied.

Original firmware: **OWNER CONFIRMED — AVAILABLE EXTERNALLY.** Availability is NOT a blocker.
No original-firmware search, request, download or reconstruction is necessary. The owner may
choose stock recovery or the separately reviewed quiescent fallback; matching artifacts and
ROM recoverability still matter. Old firmware/data preservation is optional. Existing backups
remain untouched. Owner-reported previous full preflight/SPIFFS roundtrip/NVS-zero-findings
remain historical private results, not independently inspected Codex files and not prerequisites
for preserving old data now that fresh installation is accepted.

## READY FOR CONTROLLED INSTALLATION — conditions, not a current authorization

Ready only when the private receipt, complete artifact review, physical prerequisites and
explicit owner authorization above are satisfied together. The next practical milestone is
Stage27's owner-controlled installation review/session, not another scripting architecture stage.
A reviewed prebuilt binary avoids requiring High Sierra firmware compilation. Local cryptography
and macOS mkspiffs must work for private preparation, or an explicitly reviewed compatible
private-generation environment must be selected. No system toolchain upgrade is assumed.

For first boot: no payloads; verify diagnostic outcome, AP/authentication, empty script list and
no automatic formatting/examples/autorun. Later USB/TextEdit keyboard, SD, LED feedback,
reconnection, timing, heap and task-stack tests need separate harmless physical-test scope.
Application HID infrastructure exists after healthy controlled startup, but does not automatically
inject keys. SDK/CDC/RTOS startup remains active. Writable SDK NVS can perform ordinary recovery
and Wi-Fi state writes; original NVS immutability is not promised or required. Multi-key saves
remain non-atomic. The quiescent profile is not USB-detached and cannot automatically arm itself.

**GO:** owner-local private preparation and final installation review.
**NO-GO:** physical flashing, application boot, migration or OTA until separately authorized.
There is no demonstrated Stage26 technical FAIL and no claim of physical readiness from simulation.
