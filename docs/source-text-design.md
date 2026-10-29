# Route B source/text portability contract

Baseline `2bdf7e6cea7fb1a343d4ac0973a90578264ced07`; branch `routeb-source-text-portability-v1`; candidate `ROUTEB-SOURCE-TEXT-PORTABILITY-v1`. This additive layer targets the actual composed Route B adapter/compiler. It does not widen the legacy engine or change a standalone preview and infer production support.

## Optional leading BOM

Allow exactly UTF-8 marker bytes `EF BB BF` at absolute raw offset zero through the adapter. Preserve all original bytes in the captured source and source identity; the compiler handles the existing marker. Its three bytes count within the unchanged **8,192-byte raw source bound**. No decoder, normalization or marker stripping is introduced.

Prefix validation is bounded and cooperative across arbitrary read/chunk boundaries and zero-byte Retry responses. A new preparation resets its prefix state. Reject incomplete, repeated or misplaced markers, malformed prefixes, UTF-16 and every other unsupported non-ASCII byte before execution. Existing TAB/LF/CR and printable-ASCII admission remains. LF/CRLF and missing final newline preserve the compiler's existing rules. A marker is an encoding prefix, not permission for Unicode payload text or a new layout.

## Fourteen inline text aliases

Each ordinary STRING and STRINGLN family accepts the seven exact suffixes POWERSHELL, BATCH, BASH, JAVASCRIPT, PYTHON, RUBY and HTML. For example:

```ducky
STRING_PYTHON 111join
STRINGLN_HTML 222line
```

Nonempty inline operands use exactly the corresponding ordinary STRING/STRINGLN processing, including existing whitespace, DEFINE, diagnostic, keyboard-report and streaming policies. Command recognition is separate from argument-free block recognition. A bare opener remains a block; its canonical END_STRING/END_STRINGLN terminator and block formatting remain unchanged. Names remain reserved against function shadowing.

Nonempty inline aliases can be bounded REPEAT leaf statements wherever ordinary inline STRING/STRINGLN is allowed. Repeated bare block openers stay rejected. Unknown suffixes and malformed retained source reject before output. Preprocessor-excluded source remains distinct from inactive runtime branches.

These commands emit literal text, not Python/HTML/shell or other embedded-language execution. A token such as `END_STRING` inside an inline operand is **literal text**, just as in the corresponding ordinary inline command. Do not append a closing token to the inline examples above. Block terminators still apply only to open blocks.

## Official evidence and explicit extension boundary

The saved official Keystroke Injection documentation describes the fourteen **block** names and says they work in Community; Pro adds highlighting/completion. Static public Community compiler source separately recognizes suffixed same-line forms **with** END_STRING/END_STRINGLN. Its ordinary no-terminator inline regexes have no suffix. Thus the requested **no-terminator inline aliases are an EvilDuck extension**, not a verified canonical Hak5 grammar claim. Official same-line terminated forms are not newly claimed or silently emulated by stripping text. Primary URLs, hashes, line anchors and exact regex quotations are in [references](source-text-references.json). No official runtime was executed and no INJECT_VAR checks were repeated.

## Preserved boundary

Keep accepted restart/RESET behavior, whole-request budgets, immutable Program/source capture, ownership, held/transient merging, collision/rollover refusals, bounded sampling/jitter, STOP and quarantine unchanged. Preserve authentication, explicit engine selection, storage mutation guards, lock feedback and EDR1. No USB identity/descriptor, partition, SDK/core, PSRAM, settings-schema, Caps timing or layout change is needed. INJECT_VAR remains blocked.
