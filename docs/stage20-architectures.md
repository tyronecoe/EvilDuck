# Stage 20 preservation architecture decision

The word preservation must name its object and time interval. Normal NVS settings
saves necessarily change flash; keeping the original backup immutable is not keeping
live NVS immutable. A recoverable backup is not automatic transactional rollback.

## Explicit guarantees

| Objective | Current guarantee | Boundary |
| --- | --- | --- |
| No Arduino whole-partition erase recovery | Stage18 exact isolated core captures init error, no erase/retry | SDK/global/boot paths are separate |
| No SDK recovery silently changes saved bytes | NOT established on current writable partition | Source tests show writes/erases before success/error and during reads |
| Detect incompatibility before app boot | Private Stage19 bounded structural inspection + no-go gates | Format subset, blob graphs/settings semantics/physical freshness incomplete |
| No settings writes after failed initialization | Stage18/19 failure guards suppress services/load/save; checked save refuses invalid load | SDK could have changed bytes earlier; normalized NOT_FOUND can hide cleanup |
| Preserve recoverability | Owner reports three expected backup hashes/sizes | Actual binaries/structural report absent here; restore is separate destructive approval |
| Distinguish permitted/unexpected changes | Synthetic flash/API accounting, explicit checked-save contract | No live observer or physical byte comparison; normal SDK garbage collection changes bytes |
| Healthy normal operation | Existing core/SDK/schema, valid load and explicit successful saves remain | No durable multi-key atomicity; read-only policy would disable saves |

Strict byte-for-byte original live-NVS immutability while allowing ordinary saves is
contradictory without a separately owned immutable source/copy. Logical preservation
means all intended settings remain readable/equivalent; structural CRCs cannot prove
this, and SDK cleanup may deliberately discard corrupted items. Transactional recovery
would require a proven snapshot/journal/commit protocol across every writer (including
Wi-Fi), not simply nvs_commit or closing a handle.

## Options compared

| Option | Compatibility and required changes | Failure/recovery, resources/wear | Decision/evidence still needed |
| --- | --- | --- | --- |
| Offline check only | Existing Python checker, no firmware/SDK/table changes | No flash wear; host bounded20KiB inspect, full backup16MiB; rejects known bad states but cannot stop later runtime mutations | Necessary evidence, insufficient live immutability; actual owner report pending |
| Firmware pre-init inspection | Additional core hook before SDK NVS, raw reads/complete validator | Flash reads only in hook, but later SDK can mutate; must prove boot ordering and full format | Deferred; no partial CRC check masquerading as complete guarantee |
| Read-only NVS handle | Already used for settings reads | Does not restrict SDK init/cleanup; corrupted reads can erase entry bits | Rejected as preservation architecture |
| Supported read-only partition flag | Pinned NVSPartition returns descriptor readonly; partition_target write/raw/erase checks flag and returns NOT_ALLOWED | Source-host API tests block lower writes/erases; incomplete/corrupt recovery can fail; healthy explicit saves/Wi-Fi writes fail; no erase wear through those blocked APIs | Promising separate quiescent-profile candidate, NOT enabled. Requires separately reviewed table-flag/profile/provenance changes, exact linked bounds and bypass audit. Current flags unchanged and existing validator deliberately rejects unexpected flags |
| Backup + separately authorized restoration | Current backup/file-level migration tools, no new SDK | Keeps immutable recovery copy; live SDK may change data; restoration can overwrite later data and requires explicit review | Selected current offline preparation strategy, coupled with no-go. Never automatic rollback |
| Source-pinned SDK variant | Rebuild exact IDF/config/patch/ABI/libs in isolation | Could explicitly deny/restrict recovery and propagate errors; boot/read/write compatibility, ignored errors and complete flash paths require tests | Deferred gate not met. Exact binary/source equivalence and reproducible target rebuild not certified; no instruction patch/vendor stack |
| Shadow writable NVS with immutable original | Route every SDK/default/Wi-Fi NVS access to separate named backend, preserve original | Needs spare20KiB+GC overhead/durable sync and early routing; ordinary OTA must not erase shadow; RAM copy alone loses persistence | Deferred. Reviewed16MiB layout consumes space; borrowing OTA padding risks erasure/overlap, changing flags/offsets forbidden here. SD is unavailable before current core init and cannot transparently become early NVS without a new reviewed architecture |
| No boot/migration until evidence and contract | Existing no-go and quiescent profile, no SDK changes | Non-destructive offline work; safe-start itself still invokes writable SDK init before setup | Selected enforcement boundary for this stage; do not mistake software safe-start for authorization to boot |

Recommended next candidate for review: supported read-only **quiescent** partition/profile
policy for initial preservation, plus independently retained original image and private
owner inspection. Native archive shows readonly-byte test/NOT_ALLOWED return paths;
unmodified target-source function bodies are host-tested. This is not certification of
all early code or direct raw-flash bypasses, nor proof of physical enforcement. A normal
writable transition would require separate owner acceptance of logical/persistence risks,
current backup capture and healthy settings/autorun review. It cannot silently reuse a
read-only validation table for normal saves or silently clear flags after first boot.

**Current selected implementation: no new SDK/partition protection; conservative no-go,
backup/inspection/summary, and checked application saves.** The SDK-level implementation
gate is not met for a new production preservation mechanism. Byte immutability and
logical recovery remain blockers; no actual NVS image was examined. This stage does not
change partition flags/offsets/sizes or weaken validators. No guessed flash interception,
fabricated success, auto repair, raw SPIFFS relocation or automatic restoration.
