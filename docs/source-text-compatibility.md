# Actual composed Route B — source/text compatibility update

Candidate `ROUTEB-SOURCE-TEXT-PORTABILITY-v1` is composed on owner-accepted restart release `2bdf7e6cea7fb1a343d4ac0973a90578264ced07`. This inventory distinguishes actual composed support from legacy or uncomposed preview sources. Fresh software results and physical evidence must remain separate.

| Capability | Candidate behavior / boundary |
|---|---|
| Leading UTF-8 BOM | Optional exact EF BB BF at raw offset0, preserved in capture and counted in8192-byte bound; compiler's existing marker handling reused. Working in fresh composed software tests; physical acceptance pending. |
| Other encoding | No expansion: partial/repeated/misplaced marker, UTF-16 and unsupported non-ASCII reject before output. LF/CRLF/no final newline retain existing rules. |
| Fourteen inline language aliases | New EvilDuck extension: corresponding ordinary STRING/STRINGLN semantics without closing token. No embedded-language execution. Working in fresh composed software tests; physical acceptance pending. |
| Bare aliases / blocks | Preserve accepted argument-free block openers, canonical terminators, formatting and diagnostics. |
| Official suffixed same-line terminated form | Not newly claimed; END_STRING/END_STRINGLN in an inline operand remains literal under ordinary semantics. See source-text-references.json. |
| Inline REPEAT | Nonempty inline aliases use existing permitted text-leaf behavior and bounds; block openers remain invalid repeat bodies. |
| RESTART_PAYLOAD / RESET | Preserve neutral barrier, lease/request identity, budget/caching/STOP/quarantine contracts. Accepted restart trials remain scoped owner evidence. |
| Keyboard, variables, functions, preprocessing, randomization/jitter | Preserve existing supported subset and restrictions, held-state restoration, whole retained-source validation and excluded-source distinction. |
| Lock feedback, WAIT, EDR1, authentication | Preserve current interface-specific evidence, timeouts, fixed-message protocol and access controls; no broad Caps or host-restoration claim. |
| INJECT_VAR / stored keycode properties | Remain blocked pending independent runtime encoding evidence. No new investigation or guessed format. |
| Unicode, additional layouts, new hardware commands | Remain unsupported/outside release. Canadian/US observations are bounded examples, not universal map support. |

The previous BOM-refusal expectation is superseded only in generated candidate tests: P14/V11 become BOM acceptance; V06 removes two inline-alias refusals. Their net+14 assertions are recorded separately; no historical file or obsolete refusal is relabelled as an unchanged pass. No full DuckyScript3 certification or physical compatibility is inferred from Linux tests/builds.
