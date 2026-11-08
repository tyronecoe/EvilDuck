# Bounded DEFINE-label capacity contract

Target: **`ROUTEB-DEFINE-LABELS-H1-v1`**, branch
`routeb-define-labels-h1-v1`, based on the complete DEL composition published at
`6bcfb605c8249b63be2be9f79a00e4e81863fbf6`. The DEL firmware/verification
checkpoint is `2e3efa295d46aef55b4d39af9cf3a9a40bb70422`.

This is one language-capacity increment. It does not implement OS detection.
Actual execution, target measurements, image/package identities and publication
outcomes belong in the [release report](define-labels-release-delivery.md) and
[structured results](define-labels-release-results.json). This contract does not
claim installation or physical acceptance of the new candidate.

## Evidence and exact change

Hak5's pinned [OS_DETECTION v1.1 extension](https://github.com/hak5/usbrubberducky-payloads/blob/4fa639fd06972cd7efd9c48cc73136443f9cffb1/payloads/extensions/os_detect.txt)
uses this physical line 50:

```ducky
DEFINE #WINDOWS_HOST_REQUEST_COUNT 2
```

The name is **27 bytes including `#`**. The DEL parent's `Constant.name[24]`
accepts at most 23 bytes and the original unmodified extension actually rejected
at this line with Identifier/code6. The pinned 7,875-byte source has SHA-256
`ef137faf626782fdcc6b43405f361b7a3c923c634f98dfd7774c73072e18399f`.
[Reference identities](define-labels-references.json) reuse completed primary
evidence; no broad research or official compiler-function checks are repeated.

The new contract is **DEFINE labels of 1–31 bytes**, excluding the terminating
NUL and including optional leading `#`. Existing identifier grammar still
applies, so an otherwise invalid short label is not admitted. The maximum is an
**EvilDuck bounded-capacity policy**, not an asserted official DS3 limit.

Only the composed compiler's constant paths change:

1. Grow each of the existing sixteen constant-name cells from 24 to 32 bytes.
2. Derive collection/validation's length limit from that cell size.
3. Apply the same cell-derived limit to conditional-preprocessor flag lookup.

The third path matters: `IF_DEFINED_TRUE` and `IF_NOT_DEFINED_TRUE` previously
checked their `#` label against 24 independently. A long DEFINE must survive
both collection and flag lookup. No new preprocessing syntax is introduced.

Ordinary variable names remain at their prior 23-byte bound including `$`;
function identifiers remain at their prior 23-byte bound excluding `()`.
Extension names, numeric internal-variable recognition and all other identifier
buffers remain unchanged. The change must not admit unsupported native variables
or incidentally enlarge variable/function names.

## Complete constant path and unchanged semantics

Collection retains the original grammar, optional-label forms, case sensitivity,
pass/declaration order and sixteen-slot limit. The validated full name is copied
including NUL into its 32-byte cell. There is no truncation or heap allocation.
Duplicate detection uses full-name exact comparison, so distinct long names that
share a prefix remain distinct. The seventeenth selected constant still fails.
Constant values retain their existing 64-byte cells and value bounds.

Comparison and expansion continue to use the complete stored name and longest
matching label. Existing `#`-prefixed and bare-label token-boundary behavior
remains unchanged; this release does not redefine delimiters or reinterpret
adjacent text. Expansion remains bounded and nonrecursive. The line/operand
budgets still apply after substitution, and DEFINE cannot manufacture new
command/prefix forms outside the existing expansion positions.

Conditional flags retain their existing literal TRUE/FALSE requirements,
selection/declaration order, unknown-flag behavior and depth-eight budget.
Preprocessor-excluded source remains distinct from retained inactive runtime
branches and unused functions. Every retained statement still preflights before
output. Rejections retain physical source line accounting. A label of exactly
32 bytes rejects during DEFINE collection with Identifier/code6; an overlong
conditional flag retains the preprocessor diagnostic contract.

No source, line, IR, operand-storage, nesting, expression, execution or constant
count limit is enlarged. No opcode, runtime evaluator, scheduler, HID/report,
USB descriptor/mode, storage, authentication, dashboard or LED protocol change
is needed. DEL/DELETE, preserved DEL() functions, REPEAT, H1, right modifiers,
bounded feedback, STOP/cleanup and quarantine remain inherited behavior.

## Workspace and measurement requirements

The fixed **4,096-byte CompileSession workspace** and its existing Compiler-size
static assertion remain. Sixteen name cells growing by eight bytes nominally
add 128 bytes to Compiler. The previous host measurement was 3,856 bytes; this is
historical host evidence, not an ESP32 measurement or a prospective resource
claim.

Record actual before/after host and ESP32 Compiler size/alignment, workspace
headroom, target application/static RAM and relevant compiler stack frames.
Retain the placement-new allocation model and do not raise workspace/stack
budgets or weaken guards to fit the change. If the target does not fit, report
the measured blocker and a bounded alternative. No resource delta is claimed
before the real receipts exist.

## Focused verification and finite finish line

Use the actual composed compiler/runtime with RAM-only output and mocked
transport/storage/clocks. Cover short labels; old accepted 23-byte and formerly
rejected 24-byte boundaries; the official 27-byte label; exactly 31 accepted and
32 rejected. Exercise complete long-name numeric and text expansion, conditional
flags, distinct long-prefix names, exact duplicates and the sixteen-slot limit.
Preserve collection order, both optional label forms, token boundaries and
nonrecursive semantics. Test exclusions against retained malformed source,
physical diagnostics, zero output before rejection, and unchanged ordinary
variable/function/internal-variable rules.

Use old/new causal controls on the verified DEL parent and candidate. Run
relevant composed regressions and applicable ASan/UBSan/leak checks once final
production bytes are fixed. Reuse unchanged evidence only with explicit source
and receipt bindings. A clean approved Arduino ESP32 3.3.0 target build must
retain committed-source/dependency/profile guards and the inherited release
assertion coverage, with exact source/object/ELF linkage.

Compile the **unchanged pinned official extension** only. Record its actual next
diagnostic after this label fix without editing out dependencies or starting its
runtime. Parser progress is not a detector-success claim. The finish line is a
small bounded label change with meaningful tests, measured fit, guarded target
proof and a hash-verified Mac review ZIP/publication.

## Short later owner acceptance

Only after a separately owner-operated installation, use blank plain-text
TextEdit with the intended input profile and a short focus delay. The package
sheet/fixtures must give these three exact outcomes and actual request statuses:

1. The official 27-byte `#WINDOWS_HOST_REQUEST_COUNT` substituted into harmless
   text emits **`DEFINE27OK`** and reaches matching Completed.
2. The 31-byte `#ABCDEFGHIJKLMNOPQRSTUVWXYZABCD` substituted into harmless text
   emits **`DEFINE31OK`** and reaches matching Completed.
3. A first-line DEFINE using 32-byte `#ABCDEFGHIJKLMNOPQRSTUVWXYZABCDE` rejects
   at **line1, Identifier/code6**, with TextEdit blank.

The markers use constant substitution only; they do not launch a shell, access
credentials, inspect the OS or perform a host probe. Do not execute fixtures
during development or turn them into a broad physical retest campaign. Earlier
DEL owner results and closed H1/right-modifier/wait groups remain preserved.

## OS boundaries and exact recovery

Only the DEFINE-label limitation is addressed. The actual next whole-extension
compile outcome must remain separate from the historical first line50/code6
rejection and earlier isolated dependency probes. Counter event/timing/reset/
overflow/session semantics remain reference-unresolved; OS symbols/constants,
indicator commands, Route B lock save/restore, USB mode/identity/reconnect and
remaining full-extension capacities remain separate. Unknown lock feedback is
not OFF. No mount/report counter, manual OS label or guessed callback hook is
substituted. H1 stays opt-in and experimental, with canonical numeric encoding
unresolved.

The exact source/text-v2 rollback remains **1,413,200 bytes**, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It is older application code without later privacy/dashboard repairs, not a
full-device/filesystem restore. Published DEL/recovery artifacts and private
backups remain untouched. No hardware access, serial operation, real HID output,
flashing, OTA, formatting or automatic owner test is part of this release task.
