# Route B random uppercase — bounded contract

Source baseline: `485d1a31c7d1ef868aef99c92c15ebd9b75994b5`. Isolated branch: `routeb-random-uppercase-v1`. Candidate build ID: `ROUTEB-RANDOM-UPPER-20261025-v1`.

## Reference-backed grammar

The official Hak5 [randomization reference](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/randomization.md), “Random Keystroke Injection”, lists `RANDOM_UPPERCASE_LETTER` with the exact character set `ABCDEFGHIJKLMNOPQRSTUVWXYZ`. Only the exact, argument-free command is added. The command is reserved against function shadowing. Extra operands in retained source reject during compilation, including inactive runtime branches and unused functions. Preprocessor-excluded source retains its distinct existing exclusion semantics.

No digit, symbol, mixed-letter, numeric RNG, seed, jitter or packed-keycode group is implemented. INJECT_VAR remains explicitly unsupported; its original investigation and unresolved vectors are unchanged and are not re-investigated in this stage.

## Selection, output and lifetime

The uppercase instruction reuses the existing bounded 26-way sampler and injected `RandomReader` dependency. The SDK production source remains `esp_random()`; no SDK/core change, persisted seed or cryptographic claim is introduced. Each runtime tick draws at most once. Raw values below `floor(2^32/26)*26 = 4294967274` select `A + raw % 26`; the top 22 uint32 values are rejected. Eight rejected samples terminate with the existing explicit RandomUnavailable error. These arithmetic rules avoid modulo bias for a uniform provider without claiming measured device entropy quality.

A successful selection becomes the ordinary pending Character event. Retries reuse that value; they do not resample or duplicate accepted output. Lowercase continues selecting `a + raw % 26`. Start, cancellation and failure clear per-operation sampler state. The existing callback/context lifetime contract, runtime budgets, source/expression limits and cooperative scheduling remain.

Existing uppercase character translation supplies Shift. Persistent modifiers and nonmodifier keys merge through the existing backend; the transient release restores the persistent held report. Held-usage collisions and seventh-key rollover remain explicit refusals. Existing ownership, STOP/error cleanup, disconnect, ambiguity/quarantine and subsequent-run isolation remain in force. No automatic Caps normalization or host-lock manipulation is added.

The new layer and its build selector are separately pinned. Existing lowercase and earlier overlays, source trees, verifiers, packages and diagnostics are historical inputs. The target build and post-link verifier must identify the exact new composed source and preserve inherited USB/NVS/startup/archive checks.
