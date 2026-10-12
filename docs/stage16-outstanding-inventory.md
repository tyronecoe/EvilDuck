# Stage 16 USB limitations and compatibility inventory

The144-entry [Stage14 language matrix](stage14-compatibility-matrix.md) and
[internal-variable matrix](stage14-internal-variable-matrix.md) remain current except
that their unpatched HID routing caveat is superseded by this reviewed pairing.
No new DuckyScript commands, encoded scancodes, restart or USB identities are added.
The Stage15 documents remain historical evidence, not the active build status.

| Feature / concern | Current evidence-based status | Remaining gate |
| --- | --- | --- |
| SET_REPORT null/empty OUTPUT extraction and subtraction | Fixed in isolated pinned core; exact source/sanitizer/full-link verification | Normal physical USB delivery still untested |
| OUTPUT/FEATURE separation | Fixed core dispatch and removed firmware FEATURE workaround | Physical control/interrupt delivery patterns |
| Invalid instance/report type/unknown ID | Guarded capacity/type/registry dispatch; debug indexing removed | No claim of general multi-interface or arbitrary pointer safety |
| Stock keyboard null/empty hook | Upstream defect remains; guarded route and actual derived receiver bypass it | Do not call stock hook directly with invalid inputs |
| Stock and other USB event queue blocking | Stock policy observed unchanged; EvilDuck LED callback avoids posting | Dedicated RTOS/event-loop investigation, measured contention |
| Descriptor allocations / generic HID GET/IDLE/PROTOCOL | Not generally hardened by SET_REPORT patch | Separate source-backed scope and regression design |
| Lock feedback evidence | Actual observed state/unknown preserved; captured tokens reject | No on-wire epoch/causal ACK; actual High Sierra Num/Scroll support unknown |
| Persistent ownership/releases | Prior production suites pass; exact IN reports remain ID1/eight bytes | No release delivery guarantee while physically disconnected |
| CDC/MSC/HID integration | Full patched firmware links all class callbacks; MSC fault suites preserved | Physical coexistence/task timing not established; MSC initialization is not host mount or re-enumeration |
| Randomization/jitter | Prior deterministic tests and bounded scheduling preserved | Device entropy/cadence/high-water untested |
| INJECT_VAR / packed random scancodes | Unsupported, encoding independently unresolved | Official versioned encoding/spec vectors; no invented format |
| RESTART_PAYLOAD | Unimplemented; proposed lifetime contract not approved | Independent contract review and bounded progress/release/source rules |
| Personality/identity changes | Not implemented or authorized | Separate reviewed descriptor/session and host validation design |
| High Sierra build compatibility | Python helpers compatible; Linux clean build verified | Actual Darwin CLI/compiler minimum OS smoke test |
| Physical migration | Preparation only; binary exceeds old slots | Owner backup/file checks, NVS-safe exact manifest, ROM recovery, autorun prevention, individual authorization |
| Heap/task-stack/controller concurrency | Host allocation/sanitizer/compiler-frame evidence | Physical measurements; no TSan/RTOS certification |

Recommend reviewing this dependency integration, then separately authorize owner local
backup verification and known-port ROM read-only checks. Application TextEdit/USB tests
need all migration/recovery/autorun gates first; they cannot safely use the original
small application slots. No next implementation stage begins automatically.
