# Stage 15 outstanding compatibility and readiness inventory

The complete144-entry [Stage14 language inventory](stage14-compatibility-matrix.md)
and [internal-variable inventory](stage14-internal-variable-matrix.md) remain current:
Stage15 adds no production language/USB behavior. This supplement updates evidence
and priorities without reclassifying recognition/proposals as supported functionality.

| Item | Current status / evidence | Next acceptance gate |
| --- | --- | --- |
| SET_REPORT ID0 null/empty extraction | Proven upstream callback fault/length underflow; shipped unpatched | Review paired minimal dependency/firmware proposal, full pinned patched build and normal-host tests |
| OUTPUT/FEATURE/INPUT separation | Proven type-erasing route and ambiguous firmware workaround; paired temporary tests correct separation | Adopt both patches together only after dependency reproducibility review; never claim active protection now |
| Invalid instance/debug type logging | Source/API weakness; logging fault debug-only | Include in upstream regression and log-profile matrix; no physical reachability assertion |
| Stock keyboard OUT hook | Proven unchecked read and indefinite event-post policy; already bypassed by EvilDuck | Keep derived guard; separate event-queue/RTOS review for other core callbacks |
| HID sessions/lock evidence | Bounded observed snapshot; stale captured tokens rejected; no wire epoch or causal ACK | Normal authorized reconnect/feedback tests, no fabricated known=false |
| INJECT_VAR/random packed values | Unsupported; numeric bit layout/locale/multiple-stroke semantics not established | Independent official encoder/specification vectors, then separately reviewed implementation |
| RESTART_PAYLOAD | Unsupported; beginning-flow documented, state lifetime unresolved | Approve explicit bounded lifetime/progress/release/source contract before code |
| Randomization/jitter | Stage14 implemented with explicit source/endpoint/timing profile limits | Device entropy/timing and host cadence validation; no seed.bin/crypto claim |
| Random USB identity/personality | Unsupported; no dynamic descriptor transition | Dependency hardening first, then separate descriptor/session design and approval |
| Button/full canonical LED policy | Deferred; canonical red/green/off map to single RGB | Actual wiring/bootstrap and priority review; no fictitious independent LEDs |
| Other layouts/Unicode/host composition | Limited US/DE mappings; existing unsupported-scalar policy | TextEdit/input-source/dead-key verification; physical host effects not simulated |
| Streamed source mutation | Bounded parser/preflight but no immutable-source guarantee | Active-source mutation policy/fingerprint before restart or concurrent editing claims |
| Physical firmware migration | Prepared only; oldSPIFFS0x170000→new0x160000 cannot raw-copy | Current owner file hashes/contents, ROM recovery, NVS-safe manifest and individual authorization |
| High Sierra build support | Core installed per owner; actual Darwin compiler minimum OS unverified | Offline exact-profile smoke build or reviewed cloud artifacts; no downgrade/workaround changing USB/PSRAM |
| Task/heap/controller contention | Host sanitizer/allocation/compiler-frame evidence only | Separately approved instrumentation and hardware high-water capture |

Recommended next milestone is a reviewed reproducible paired HID routing dependency
hardening adoption and full-stack integration, before identity/personality changes.
Encoding/restart work stays contract-first. Nothing beyond Stage15 has begun.
