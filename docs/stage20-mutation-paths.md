# Stage 20 SDK mutation paths and evidence

NVS physical range9000..dfff (5000bytes/five4096byte pages). All ranges below describe
known partition-relative operations translated to this fixed reviewed region, not a
newly measured owner device. No SDK binary is executed. Exact nominal source commit
b66b5448e0dfac6be135e6f0ac21010aba231180; Stage19 file pin verified again. Actual
libnvs_flash.a hash remains a1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e.
Archive relocations/disassembly confirm call references, not source/binary equivalence.
Stage20 supporting partition-source hashes and inspected target archive are separately
recorded, not substituted into installed libraries.

| Path / trigger | Timing and potential changes | Role / detection / avoidance | Evidence |
| --- | --- | --- | --- |
| nvs_flash_init default writable partition | Before setup; calls partition init/Storage/PageManager | A successful return does not prove preservation; handle NVS_READONLY comes later | Pinned source/config + actual archive references |
| Page.load metadata/version/read failures | Before successful init; earlier pages may already have changed; version <fe returns NEW_VERSION | Offline headers/versions/CRCs flag issues, cannot reverse earlier writes | Stage19 actual source error/fault cases; API/locks not fully executed |
| Incomplete/illegal/bad-header entries and spans | Init writes bitmap words at9000+page*1000+20..3f (up to4byte words/ranges) | Required writable cleanup under normal SDK design; source checker flags subset | Source+archive eraseEntryAndSpan reference; source-runtime ranges retained |
| Duplicate entries / interrupted replacement | Init can mark earlier entries erased, including pages older than current | Valid CRC does not prevent cleanup; offline duplicate detection conservative | Source/runtime duplicate test; exhaustive cross-page variants not run |
| FREEING page | Before init success: erase destination ACTIVE page, activate spare, copy valid32byte entries/header/bitmap, erase old4096byte page | GC/power-loss recovery, not optional healthy writable behavior; offline FREEING detectable | Source/runtime two erases+intermediate writes and write/erase error cases |
| Corrupt free-list activation | Before init completion, chosen page4096byte erase within region | Can discard diagnostic bytes; offline invalid/corrupt states flag risk | Source-runtime corrupt-only activation and readonly-denial case |
| No spare pages / flash errors | May fail after recovery writes/erase; partial flash program effects possible | Arduino no-retry prevents its additional whole erase, not earlier SDK effects | Source-runtime no-free/partial-read/mutation-before-error cases; physical partial programming untested |
| Mismatched blob indexes/orphan data | Storage.init after PageManager, before successful initializer return; bitmap erasure in one/multiple pages | Some cleanup error results ignored; return success not a health certificate; graph verification incomplete | Source+archive calls, source-runtime orphan/index and ignored-write-error cases |
| String/blob payload CRC mismatch during read | After successful init; eraseEntryAndSpan bitmap update then NOT_FOUND if cleanup succeeded | NVS_READONLY handle does not prevent it. Offline CRC catches known payload cases; existing app cannot distinguish this NOT_FOUND from genuine absence | Actual source/runtime exact NOT_FOUND test; target-source readonly guard rejects attempted cleanup |
| Blob chunk missing/length mismatch during read | After init, readMultiPageBlob cleanup can erase index/chunks | Complex blob graph check not proved; source checker reports insufficient evidence | Source investigation; this exact full readMultiPageBlob path not dynamically executed |
| Repeated initialization | Storage may be reused and reloaded, not necessarily no-op; old recovery effects persist | Retrying init is not recovery rollback | Actual same-PageManager/same-Storage host cases; complete API lock/handle lifetime untested |
| Explicit setters / garbage collection | After initialized normal app: entries, headers, bitmap and GC-sector erases can cover whole NVS range | Required ordinary saves; change tracking cannot call every byte change data loss | SDK source and source fixtures; production save tests use explicit API stand-ins |
| nvs_commit | Valid handle returns OK in NVSHandleSimple::commit, no transaction barrier | Checking return is useful API error handling, not atomic multi-key persistence | Exact pinned source; commit-failure injection is a stand-in, not target library fault |

New checked application save performs at most12typed setters in established schema/order,
then one checked commit; first failure stops remaining calls and closes. An already
applied prefix can persist, a failed call may already modify bytes, and commit failure
can occur after all updates. Reset is explicit, never repair after bad load. New UI
acknowledgments match checked result; busy web mutations are rejected before setters.

Important correction of the Stage19 "genuine NOT_FOUND" interpretation: the loader
accepts NOT_FOUND as missing because the public API offers no provenance. Actual source
can recover/delete corrupt data and return the same code. Thus defaults can be selected
without a surfaced read error; Stage19's error latch cannot detect every cleanup. No
SDK error is bypassed here, but successful settings loading is not logical preservation.
Offline structure helps gate first boot, not guarantee future reads/healthy hardware.

## Supported readonly API experiment (not production enabled)

Pinned NVSPartition.get_readonly reads ESP partition descriptor flag. Supporting
partition_target.c write/write_raw/erase_range returns ESP_ERR_NOT_ALLOWED before lower
flash access when readonly. Host tests compile full exact function bodies with synthetic
parameter/flash adapters plus unmodified Page/PageManager/Storage. Clean, incomplete,
bad-entry, FREEING, corrupt activation and corrupted-string cases show where initialization
still succeeds, where it changes to error, and where read cleanup is denied. Lower flash
write/erase calls remain zero in these readonly-source cases. This is not a replacement
for all full SDK/boot/global paths, not a test of the Xtensa binary, and not changes to
the existing reviewed partition descriptor.

Actual inspected libesp_partition.a has a readonly-byte load at descriptor offset42,
conditional return0x10d before downstream flash calls in write/raw/erase functions.
That evidence supports the candidate, without certifying identical upstream source or
all other direct flash callers. Supporting source/SDK config and actual compiled offsets
must be reverified for any later isolated profile. Current CSV has no readonly flags;
no runtime protection from this experiment is claimed.

## Remaining physical evidence

Owner original NVS pages/settings were not available here. Physical flash/security,
ROM recovery, exact installed table, fault timing, read/write reliability, runtime heap
and task high-water remain owner evidence/testing gates. Original full16MiB backup and
4096byte table/destinationSPIFFS hashes are owner-local verified only. No original byte
stream, password/key/name/value or owner script is printed/committed/executed.
