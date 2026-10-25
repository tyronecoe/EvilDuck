# Composed compatibility update

| Group | Classification | Verification boundary |
|---|---|---|
| Six random-character commands | Working in offline software tests | Exact no-argument grammar; documented alphabets and explicit72-character policy; physical combined release pending |
| RANDOM_INT/MIN/MAX | Working in offline software tests | Inclusive uint16 ranges; checked assignments; draw-time interval check; resumable exactly-once operands |
| JITTER_ENABLED/MAX | Working in offline software tests | Per-run settings; bounded pre-press gate; release/cleanup bypass; scheduling policy explicitly documented |
| Lower/uppercase baseline | Preserved | Scoped owner evidence is recorded separately; new composed regressions required |
| Variables/expressions/IF/WHILE/functions | Preserved bounded subset | Existing evaluator and continuation; no new parser |
| HOLD/RELEASE, inline INJECT_MOD, STOP | Preserved | Existing lease, merge, cleanup and quarantine paths; no universal host-release claim |
| Preprocessing/extensions/VERSION | Preserved | Retained malformed source checked; excluded source keeps distinct semantics |
| Lock feedback/WAIT/EDR1/authentication | Preserved | Interface-specific observation and current limits; EDR1 protocol unchanged |
| INJECT_VAR/random-keycode variables | Unsupported | Unresolved canonical numeric encoding; original findings/vectors unchanged |
| RNG seeds, new layouts, extra feature groups | Missing/outside release | No new support claimed |

Primary sources and retrieval hashes: randomization-jitter-references.json. Exact policies/limits: randomization-jitter-design.md. Offline support does not establish physical host compatibility, measured uniformity or timing.
