# Stage 20 preservation and persistence contract (before production changes)

Baseline524d643a12af05e4efd9da509eae274ec43959a6. No new SDK/core patch or flash
interceptor. Byte immutability, logical preservation and backup recoverability are
separate guarantees. The fixed Stage18 Arduino whole-partition erase guard and Stage19
startup/inspection safeguards remain. SDK recovery/read mutations are not prohibited.
Migration/application boot/OTA remain NO-GO pending owner evidence and reviewed strategy.

Selected current approach: conservative boot/migration block + independently retained
owner backups + private structural inspection and privacy-safe summary. This is a
practical evidence/preparation architecture, not automatic repair or strict live-data
preservation. A future explicitly reviewed immutable original/shadow NVS architecture
or source-pinned SDK rebuild requires separate acceptance. Neither is implemented here.

## Explicit settings saves and resets

Replace unchecked Preferences put calls with raw typed NVS set calls, capturing the
first error and returning a checked result. Validate current RAM settings before any
namespace open/write. Stop at first failed set; no remaining set/commit, automatic retry,
erase, default repair, replacement namespace or rollback. Close opened handles on all
results. Check final commit. Preserve original key schema and key write order; do not
invent atomicity or silently disarm persisted autorun as a recovery write.

Keep public void save/reset wrappers; add saveChecked/resetChecked/saveError. CLI/web
must report failure rather than false saved success. Failed reset must be detectable.
An explicit reset continues to change RAM values to defaults before attempting their
save, as previously; refusal after invalid load occurs before changing RAM. Failed save
can leave RAM and flash different and an already applied prefix can persist. Failed
commit may occur after all setters changed flash. Closing an SDK handle is not rollback.
Autorun persisted enable/script can be mixed after interruption/partial save. This cannot
be solved by returning an error; next boot with structurally valid mixed settings may
accept them. Migration stays blocked and future atomic schema is a separate review gate.

No auto retry or lockout/repair is invented. Explicit owner retry may perform additional
SDK writes and must be understood as such. Healthy settings save/reset maintains schema,
values and interfaces; only successful save can produce existing success acknowledgments.
Stored values/credentials are never included in new diagnostics. Already existing CLI
setting-value echoes are not expanded. Current settings setters/tasks are not converted
into a transactional concurrency framework; concurrent RAM edits remain a limitation.

## Privacy-safe owner evidence

Existing owner local size/hash verification stays owner-reported, not Codex-inspected.
Private full deployment_preflight must run locally. New strict summary exports only
known artifact identities/status, partition-layout checks, generic NVS classification/
issue locations/counts and SPIFFS roundtrip status. No dynamic filenames, namespace/key/
settings values or NVS payloads are copied. Summary must not confer migration approval
or claim actual device health. Raw private report stays local; validation never modifies
backup bytes. No physical command is supplied/executed.

Additional reviewed implementation decision: web settings/LED handlers currently do not
serialize setters with the already-guarded CLI. Use existing execution::TryGuard on each
handler and checked persistence, rejecting contention before web mutations (409) or raw
save access. Per-call save error is local; latest-result diagnostic is one atomic32-bit
value. No blocking wait/new mutex/report queue is introduced. Void-wrapper logs stay
generic to avoid misattributing another concurrent call's latest numeric error. Existing
CLI outer recursive lock remains. Public direct setters still require serialized caller
ownership; this does not create atomic multi-key flash transactions or cure SDK recovery.
