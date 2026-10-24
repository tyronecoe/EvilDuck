# Actual composed Route B compatibility inventory — focused refresh

This matrix describes the additive candidate on the retained composed lock-feedback compiler, not generic branch names or all historical firmware. Source evidence: `tests/keyboard_control/application.patch`; `tests/lock_feedback/application.patch`; `tests/source_compat/application.patch`. Tests exercise these overlays on actual modules with mocked transport/storage. Working means software-supported within stated bounds, not complete Hak5 or cross-platform certification.

| Feature | Current installed lock-feedback | New review candidate | Evidence / limits |
|---|---|---|---|
| Inline `INJECT_MOD` modifier | Working | Preserved | Existing compiler emits modifier tap; Q01–Q03, Q12; owner keyboard Trial A. One supported modifier spelling/alias. |
| Bare/prefix `INJECT_MOD` | Unsupported | Unsupported | Q03 rejects malformed/argument-free forms; no guessed persistent prefix semantics. |
| Lease-owned `HOLD/RELEASE` | Working | Preserved | Q04–Q37, exact reports, six-key bound, `STOP`/error/backpressure; owner Trials A/B. Direct modifier ownership is documented EvilDuck extension. |
| Lock variables and bounded WAIT | Partial | Preserved | N01–N44; interface-specific fresh output evidence, unknown fails honestly; fixed 5s wait. Owner WAIT/helper evidence separately qualified. |
| Variables/expressions/`IF/WHILE`/functions | Working with limits | Preserved | Existing 16-bit, eager bounded evaluator and call/control limits; existing regressions plus P28. No parser replacement. |
| `STRING/STRINGLN` and blocks | Working subset | Preserved | Existing US printable ASCII, block whitespace/`DEFINE` rules, physical line diagnostics. No arbitrary Unicode or newly claimed locales. |
| Conditional preprocessing | Missing | Partial bounded support | P01–P16, P25–P36; canonical four directives, depth 8; literal Boolean/source-order flag profile; no compiler equivalence claim. |
| Inline EXTENSION wrappers | Missing | Partial bounded support | P17–P25, P28–P29, P36;16 unique, 23-character identifiers; top-level wrappers only; body features still independently validated. |
| `VERSION` metadata | Missing | Partial bounded support | Optional once before content, dotted decimal, at most 63 characters; no online checks, imports or packages. |
| EDR1 fixed-message return | Working tested configuration | Unchanged | Owner previous fixed-message milestone; existing receiver regressions including N30/Q30. Custom protocol, not Hak5 exfiltration or generalized capture. |
| `RESET/release-all`, `INJECT_VAR`, save/restore lock commands, randomization, OS detection | Unsupported or Missing in composed Route B | Unchanged | No new semantics or hardware-status claims added. Older legacy Stage 13 preprocessing does not establish Route B support. |

Legacy CLI `run` and historical `EvilDuckS3` code are separate execution paths; dashboard Route B and explicit CLI `routeb` select composed engine. Standalone `language_preview` files also do not describe the composed overlays accurately. Existing firmware, helper and historical evidence remain separate artifacts. New candidate physical behavior, Windows 11 compatibility, global host Caps restoration and general USB retirement are not established by native mocks or successful linking.

Encoding boundary: direct compiler supports a leading UTF-8 BOM, CRLF/LF and missing final newline, but the existing composed adapter's ASCII-only admission rejects BOM before compilation (`Capability`). P14 records this existing limitation separately and verifies CRLF/no-final-newline success without BOM. This stage does not silently widen admission. A completed compile is not evidence that every source encoding reaches that compiler through the production adapter.
