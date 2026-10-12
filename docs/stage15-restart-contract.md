# RESTART_PAYLOAD contract investigation and proposal — NOT implemented/approved

Official payload-control/quick-reference prose establishes cease current execution,
restart from the beginning and never reach the following line. RESET clears keyboard
buffer and continues; it is not restart or hardware reboot. No independently available
reference compiler/device defines the remaining lifetime contract. Fresh encoder/docs
retrieval is unavailable (HTTP403); prior provenance-verified snapshots are retained.

| State | Reference-backed fact | Proposed EvilDuck policy, requires review |
| --- | --- | --- |
| Program counter | Restart from beginning | Cooperative rewind, no recursive run() or hardware reboot |
| User variables/functions | Globals, ordinary declaration/call semantics | Clear runtime values, calls, suspended expressions, IF/WHILE frames; retain validated function metadata only for unchanged source |
| Mutable internal controls | Individual defaults documented, restart lifetime unspecified | Reset random bounds0/9, jitter off/MAX20, default delay/history/lock timeout; no assertion of Hak5 equivalence |
| RNG/seed | seed.bin PRNG described; algorithm/layout unresolved | Keep native device source stream, do not invent reseeding or reset seed files |
| Keyboard ownership | RESET clears buffer; restart ownership unspecified | Clear immediately, prioritize zero release; no new press before pending release accepted, no ACK while disconnected |
| Preprocessing | Inclusion is precompile, no runtime flag mutation | Retain frozen membership/constants only if same source snapshot verified |
| Lock evidence | Observed host state tied to USB session | Preserve current/saved evidence if same session; disconnect invalidates; no new synthetic state |
| USB/storage | Canonical attackmode reset unspecified | Preserve active local media/USB session; cancel pending preparation safely; never detach/format/truncate as a restart side effect |
| Locale/LED | Compiled keyboard mapping; restart LED lifetime unclear | Preserve selected locale; reset execution LED override/default status, retain existing error priority |
| STOP/progress | STOP ceases execution; indefinite restart example | STOP preempts every bounded phase; explicit reviewed progress/restart budgets are a safety divergence |

Proposed state machine: REQUEST → CLEAR/RELEASE → VERIFY_SOURCE → REWIND/RESET →
RESUME. Each phase is serviced within one existing update budget. Cancellation clears
pending restart and release remains prioritized. A5-second release deadline would
report inability to resume, retaining the pending zero obligation; it would not claim
host receipt. No repeated begin/end of USB or allocation of a new whole-file parser.

Progress policy proposal: restart requests without any accepted meaningful runtime
output/state change since the prior restart increment a streak; reject boundary+1
after a conservative reviewed limit (suggested3). Timers alone are not evidence of
host progress. A shared total restart ceiling (suggested1000/run) also bounds deliberate
output/restart loops, explicitly differing from Hak5's infinite example. Define exactly
which accepted HID/storage/LED/variable actions count, idempotent HOLD behavior and
repeat/error cases before coding; counters use bounded unsigned arithmetic. Neither
constant is implemented or presented as a documented DuckyScript rule.

Source immutability is a prerequisite: existing streamed preflight does not guarantee
against same-size external mutation. A future restart implementation must reject
active-source edits or verify a bounded fingerprint across passes/restarts, not merely
compare byte count. No filesystem mutation policy or fingerprint was silently added
in Stage15. Metadata can only be retained on verified unchanged input; changed/read/
seek failure stops before further HID.

Acceptance specifications: restart inside functions/WHILE/IF/text and after pending
jitter; held modifiers and queue refusal; unchanged versus changed source; exact budget
and budget+1; STOP during each phase; current/saved lock session; randomized values and
settings lifetime; SD errors; live/web ownership and simultaneous storage preparation;
no hidden key output from preparation failures. These are proposed cases, NOT tests
of implemented restart. Production continues to reject RESTART_PAYLOAD preflight.
