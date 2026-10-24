# Composed Route B source compatibility — bounded design

Approved baseline `32e22650f98faec03ebdce71446e9f48e8d39fe5`; installed firmware remains `ROUTEB-LOCK-FEEDBACK-20261023-v1`. This additive layer follows the existing keyboard-control and lock-feedback overlays. It changes only their composed compiler/core header and candidate build identifier, leaving frozen firmware, `language_preview`, runtime/transport, feedback and EDR1 unchanged. No hardware operations are authorized.

## Reference and compatibility decisions

Fresh official Hak5 conditional-compilation and extensions Markdown was retrieved; URLs, hashes and retrieval times are in `source-compat-references.json`. Official syntax is `IF_DEFINED_TRUE #LABEL` / `IF_NOT_DEFINED_TRUE #LABEL`, optional `ELSE_DEFINED`, `END_IF_DEFINED`; `EXTENSION name` / `END_EXTENSION` encloses ordinary code, and `VERSION` is metadata. Official examples support `TRUE/FALSE` flags and inline functions. No independent Hak5 compiler oracle was available. Neither wrappers nor metadata supply the features used by an extension body automatically.

The following are explicit bounded EvilDuck policies, not assertions about undocumented Hak5 compiler behavior:

* Included `DEFINE` declarations determine flags in physical source order. Undefined is false; only selected literal `TRUE` or `FALSE` flag values are accepted. No arithmetic truthiness, recursive evaluation or retroactive forward-flag decisions. Ordinary included `DEFINE` substitution otherwise remains the current two-pass behavior. Inactive definitions have no effect.
* Canonical `#LABEL` names and extension identifiers retain the existing 23-character bound. Preprocessing nests to 8 independently of runtime `IF/WHILE`/function nesting. Sixteen included extension names are unique. Nested wrappers, wrappers inside runtime control/functions, or wrappers crossing runtime/preprocessor boundaries reject. Inline body functions/global statements retain ordinary semantics; no imports or downloads.
* `VERSION` is optional, once before noncomment body content; dotted decimal `N(.N)*`, maximum 63 characters. It is never a runtime event or online version check. New source names are reserved against function shadowing. General metadata/title/forward-definition rules remain reference-limited.
* First-pass fixed 1,025-byte physical-line bitmap freezes inclusion; only selected symbols/functions/constants enter inventory. Second pass emits selected ordinary instructions. All physical bytes still pass through bounded reader/hash verification. Excluded unsupported ordinary statements are not semantically validated, but lexical text/comment delimiters, wrapper/directive nesting and directive syntax remain structural checks. Command-looking text inside blocks stays literal. Expansion cannot manufacture directives or wrappers.

## Bounds and lifecycle

Existing limits of 8,192 source bytes, 256 physical-line bytes, 128 instructions, 4,096 text-arena bytes, 32 symbols, 16 functions/constants, 16 runtime nesting levels, 8 calls, 10,000 runtime steps and 30s execution remain unchanged, as do existing scheduler budgets. Compiler workspace increases from 2,368 to 4,096 bytes, compile-time asserted; metadata has no dynamic table or recursion. `Program`/runtime representation remains unchanged. Source mutation, read/seek failure, cancellation or malformed source prevents `Program` publication and all HID output. Numeric error codes are appended, preserving existing Timeout code 26 and feedback diagnostics.

The new `EVILDUCK_ROUTE_B_SOURCE_COMPAT=1` selector is mandatory in this isolated candidate, in addition to the existing keyboard and lock-feedback selectors. Build identity is `ROUTEB-PREPROCESS-20261024-v1`. Existing dependency pins, 16 MiB partitions, PSRAM-disabled profile and protected USB/NVS core remain mandatory. No automatic transition or autorun is introduced. New static-RAM cost and compiler-frame estimates must be measured by clean build, not assumed from native `sizeof` alone.

Admission boundary: composed `Adapter::step` has a pre-existing ASCII-only check before the compiler. A UTF-8 BOM is rejected there with `Capability`, despite direct compiler BOM support. Retain that existing behavior and distinguish it in tests/inventory; do not widen source admission merely to turn an assumed test expectation into a pass.
