# Benign TextEdit acceptance — review only

Keep the accepted preprocessing firmware installed until a separate owner review explicitly approves a candidate installation. No hardware, flashing, OTA or automatic script execution is authorized by this document. No LED helper is needed; existing v4 remains unchanged and bound to its own lock-feedback build.

For a future approved trial: confirm `ROUTEB-RANDOM-LOWER-20261024-v1`, correct US input source, Caps Lock off by ordinary owner observation, no held modifiers, autorun disabled, and a blank TextEdit document. Use explicit dashboard Route B Run or CLI routeb, never assume legacy run selects this engine. Keep STOP accessible.

```ducky
STRING BEGIN-
VAR $n=10
WHILE $n > 0
RANDOM_LOWERCASE_LETTER
$n=$n-1
END_WHILE
STRINGLN -END
```

Require `BEGIN-`, exactly 10 letters in a–z, and `-END` on the same line, followed by Enter, with the same request's Completed status. Letters are intentionally unpredictable; no particular sequence or uniqueness is required. Preserve exact visible text, request/boot/session if available, timestamped device status/build, screenshots and package identity. Do not conflate an uppercase result under host Caps/Shift settings with a demonstrated sampling error without isolating host state.

Separate bounded STOP fixture (one explicit Start):

```ducky
HOLD SHIFT
DELAY 10000
RANDOM_LOWERCASE_LETTER
RELEASE SHIFT
STRING BAD
```

Use STOP during the delay. Require Cancelled, no later random/BAD output and harmless manually typed lowercase afterward; retain evidence. No automatic replay. Local cleanup alone does not prove all host release or USB-retirement behavior.

A separate malformed source `RANDOM_LOWERCASE_LETTER extra` must reject before text, including if placed in a retained IF FALSE branch. INJECT_VAR remains rejected; this is not its acceptance test. Windows 11 is future platform coverage, not required to begin offline work. Missing/ambiguous physical evidence is UNVERIFIED; an identified host limitation is PLATFORM-LIMITED rather than universal failure.
