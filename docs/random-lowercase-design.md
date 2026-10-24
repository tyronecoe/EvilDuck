# Route B random lowercase — bounded contract

Baseline: `83c1b7da9ae3aca4fda51fe96f5959a31e3ec9b4`. New isolated profile: `ROUTEB-RANDOM-LOWER-20261024-v1`. This is the separately identified fallback feature; it is **not INJECT_VAR implementation**.

## Primary-reference gate

Read `docs/stage15-inject-var-analysis.md`, `tests/stage15/reference-vectors.json`, and the actual composed compatibility inventory. Fresh primary randomization, quick-reference and variables pages were retrieved; hashes/URLs/times are in `random-lowercase-references.json`. Official randomization establishes `INJECT_VAR $variable` consuming a stored scancode and repeats the selected character on reuse. It explicitly excludes decimal-number printing. The retrieved pages do not specify numeric bit fields, modifier encoding, invalid ranges, locale capture, AltGr/dead-key representation or release behavior for that numeric value. Payload Studio now responds HTTP200 with a login/license page, not an unauthenticated reference compiler; no login or compiler session was attempted. No independent packed numeric vector was obtained. Stage15 null vectors stay unchanged. No claim that no private compiler exists is made.

Consequently INJECT_VAR and the packed-keycode properties remain unsupported. Retained INJECT_VAR statements now fail explicitly with Unsupported before output, including inactive runtime branches and unused functions. Preprocessor-excluded statements retain their distinct nonsemantic exclusion behavior. No invented packing or decimal substitute is introduced.

## Implemented grammar and interfaces

Only exact, argument-free `RANDOM_LOWERCASE_LETTER` is added. Character set: `abcdefghijklmnopqrstuvwxyz`, as listed in the official primary reference. No uppercase/digit/symbol command, random numeric/internal variable, packed-keycode capture, seed control or jitter is added. Invalid retained syntax rejects before any HID output. The keyword is reserved against function shadowing.

A new appended IR opcode and RandomUnavailable diagnostic preserve all previous opcode/error numbers. Runtime exposes a bounded `RandomReader` callback `(void*, uint32_t&) -> bool`, analogous to existing injected device-read callbacks. Its context must remain valid while execution is running. The production adapter binds the pinned SDK `esp_random()` from `<esp_random.h>`; no core/SDK modification, seed file, settings write or cryptographic guarantee. RF/environment influence and physical entropy quality are not measured here.

Each execution of the instruction enters sampler state. A runtime tick invokes at most one provider draw. Values below `floor(2^32/26)*26` select `'a' + raw%26`; the top 22 values are rejected. After at most8 raw draws, failure is explicit and existing cleanup follows. This removes arithmetic modulo bias for a uniform32-bit provider without an unbounded loop. Missing/false/throwing providers fail before sink output; reentrant cancellation is honored.

One selected character is copied to the existing pending Character event. Sink/USB retries reuse the same value, without another draw or duplicate accepted output. No new transport event/backend is introduced. Validation, US translation, modifier merge, held-key collision/seventh-key rejection, STOP cleanup, ambiguity/quarantine and operation identity remain existing paths. Cancel/failure/start clear sampler state; callbacks remain configured dependencies, not per-script values. No per-character allocation or growing queue is added.

Existing source, expression, compile-step, runtime/tick/time and memory limits remain. Runtime state adds only fixed callback/context/flags; actual target memory/frame differences are reported from clean builds. Direct compiler BOM support remains distinct from the unchanged composed ASCII-only admission boundary. EDR1 and LED feedback are unchanged.
