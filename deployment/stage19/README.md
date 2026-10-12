# Stage 19 provisional non-owner artifact inventory

These six generated files are from the clean protected-core builds recorded in
../../docs/stage19-report.md. The machine-readable inventory holds exact hashes/sizes,
proposed offsets/sector erase ranges, linked build provenance and source fingerprint.
Initial plan proposes safe-app in both slots; normal-app is a separately reviewed future
transition, never automatically armed. bootloader/table/OTA initializer/new erased coredump
stay within reviewed regions; NVS9000/5000 is untouched by planned writes/erases.

Owner original full/partition backups and external new SPIFFS image are NOT included.
All three expected SHA256/size pairs are owner-verified locally, not independently
inspected here. No owner data or fabricated substitute exists. External SPIFFS170000 ->
160000 requires the established file-level roundtrip; raw relocation is prohibited.

This remains REVIEW-ONLY and NO-GO for migration/boot/OTA. SDK init/read recovery mutation
is unresolved; safe-start cannot prevent actions occurring before setup. Actual local
full structural/NVS/filesystem preflight, preservation contract, recovery and individual
authorization remain mandatory. No merged full-chip image or flash writer is supplied.
