# DuckyScript 3.0 compatibility inventory — keyboard-control release

Inventory revision 1. Starting checkout:
`cb3a147719850a0dc4a4797b401b606ea14c6571`; installed composed application/report
baseline `0803937b9b552fe4b6e6cb6d1dd60f80f098449c`. This inventory reviews the
developed custom firmware, not stock EvilDuck or Pico-Ducky. No compatibility
percentage or blanket Hak5 payload/`inject.bin` compatibility is claimed.

## Evidence and execution-path identity

**Supported** means implemented within stated bounds; **Partial** means a limited
subset or deliberate semantic difference; **Unsupported** means rejected/absent
on that path; **Not yet verified** identifies missing evidence rather than an
implementation failure. Software evidence is not physical host evidence.

The installed composition was inspected from the retained candidate whose 201
source entries are pinned in [caps-stop-build.json](https://github.com/tyronecoe/EvilDuck/blob/cb3a147719850a0dc4a4797b401b606ea14c6571/docs/caps-stop-build.json).
References below beginning **C:** mean paths/line numbers in that composed
`EvilDuckS3` tree, not a claim that the frozen root file is identical. It is
reproduced by the existing `tests/caps_stop/prepare_sources.py` overlay chain.
For example, its `core.cpp` SHA-256 is
`6af6469b224bfc5c494333becd0e00442fbc3a58643206b21fe7555af212c198`,
`adapter.cpp` is
`af95747ed5974a33ab55a6416c348c43f7a094186194aeec605c2c486c692f96`,
and `webfiles.h` is
`2774ff015739423be2959cc22a745816f0b6bc4c38eccd3d3dfc697ebcd3606d`.
These identities distinguish installed-source evidence from the new candidate.

| Selected entry point | Actual inspected path |
| --- | --- |
| Dashboard library Run | C:`webfiles.h:763` calls `runScript`; `runScript:998` sends authenticated `/run?engine=routeb&s=…` and checks a request-correlated 202 receipt |
| Editor Save & Run | C:`webfiles.h:888` runs only after successful save, then uses the same Route B function |
| Explicit HTTP Route B | C:`webserver.cpp:215` validates engine/source, then `route_u::requestStart`; no legacy retry on refusal |
| No-engine HTTP request | C:`webserver.cpp:268` still calls `duckscript::run`; this is not the current dashboard Run request |
| USB CLI | C:`cli.cpp:342` recognizes explicit `routeb <script>`; ordinary `run <script>` at207 remains legacy |
| SPIFFS/SD source | Coordinator/FileSource and storage reference parsing select the actual source; source medium does not silently select a different language engine |

Thus the current composed dashboard **does** explicitly select Route B. Older
generic summaries of ordinary/default web behavior must not override this
inspected UI code. A linked legacy module or successful preview test is not Route
B support. Competing execution, malformed source, unsupported capabilities and
transport uncertainty must remain explicit refusals, without silent legacy fallback.

The earlier [compatibility pass](https://github.com/tyronecoe/EvilDuck/blob/cb3a147719850a0dc4a4797b401b606ea14c6571/docs/compatibility-pass.md) supplies meaningful shared
fixtures and exact engine-specific tests. Its counts are historical, not freshly
rerun totals for this release. New candidate results belong to the keyboard-control
implementation report and its focused receipts. The [owner acceptance note](https://github.com/tyronecoe/EvilDuck/blob/routeb-keyboard-control-v1/docs/keyboard-control-owner-acceptance.md)
records the physically passed EDR1 milestone without extending it to new commands.

Selected Route B bounds are C:`core.h:6`: source8192 bytes, line256 bytes,
128 instructions,4096-byte text arena,32 symbols,16 functions,8-call depth and
nesting16. Runtime budgets at `core.h:9` are10000 steps,100000 ticks and30000ms;
these are protective limits, not measured host throughput. Legacy `config.h:12`
instead permits256KiB sources,512-byte lines,8192 physical lines,16 variables,
control depth8 and call depth8. The independent EDR1 receiver has its own120s
deadline and is not constrained by the script Runtime's30s limit.

## Official-reference provenance

Official categories are the Hak5 USB Rubber Ducky DuckyScript 3.0 reference,
including [keystroke injection](https://docs.hak5.org/hak5-usb-rubber-ducky/ducky-script-basics/keystroke-injection),
[holding keys](https://documentation.hak5.org/hak5-usb-rubber-ducky/advanced-features/holding-keys.md),
[quick reference](https://docs.hak5.org/hak5-usb-rubber-ducky/duckyscript-tm-quick-reference)
and the category URLs recorded in [Stage9 provenance](https://github.com/tyronecoe/EvilDuck/blob/cb3a147719850a0dc4a4797b401b606ea14c6571/docs/stage9-reference-sources.json).
That metadata records saved official Markdown observations from 2026-10-11;
[compatibility-pass references](https://github.com/tyronecoe/EvilDuck/blob/cb3a147719850a0dc4a4797b401b606ea14c6571/docs/compatibility-pass-references.json) and
[Stage28G's contract](https://github.com/tyronecoe/EvilDuck/blob/cb3a147719850a0dc4a4797b401b606ea14c6571/docs/stage28g-reference-contract.md) record the prior checked
snapshots and exact syntax ambiguity. They are not a versioned compiler oracle.

On 2026-10-22 at06:02:22–23 UTC, fresh requests for Holding Keys Markdown,
Keystroke Injection Markdown and current `docs.hak5.org` Keystroke Injection HTML
all returned **HTTP403**. Their raw historical Markdown files were not located in
this workspace, so this pass does not claim a new byte verification of those
snapshots or retrieval of the latest reference. The historical recorded hashes
are `c57852d2f4dad7b64b104c98da910c2a61d229875b9e02b121a1c259920372a3`
(Holding Keys) and `bd13890f5d18777764ba438c9ca70c8dbb5cb29f4f64fb9fe4a8e170e181b16a`
(Keystroke Injection). No reference host-command examples were executed.

Inline `INJECT_MOD WINDOWS` is shown in the recorded reference. Bare
`INJECT_MOD` before modifier HOLD/RELEASE has unresolved scope across intervening
statements and conflicting prefix placement in examples. The owner selected
**inline-only** for the new candidate. Bare prefix remains rejected; direct
modifier HOLD/RELEASE is an explicit EvilDuck extension, not invented canonical
prefix semantics. RESET and packed INJECT_VAR semantics are not inferred here.

## Language and source matrix

Installed Route B status below is the **accepted baseline**, before this release's
new overlay. Candidate differences are isolated in the next section. Preview
means the standalone `language_preview` compiler/runtime/mock Planner/Bridge,
whose success is not proof of real scheduler support.

| Family / meaningful form | Installed Route B | Legacy / standalone preview distinction | Source/test anchor and limit |
| --- | --- | --- | --- |
| `REM text`, `REM_BLOCK [DOCUMENTATION]` … `END_REM` | Supported | Legacy also accepts `//` as extension; preview has bounded REM/block forms | C:`core.cpp:166` skip, `script_parser.cpp:345`; existing source/structure fixtures. Unknown forms are not ignored |
| Inline `STRING`, `STRINGLN` | Supported for bounded US ASCII | Legacy supports US/DE mapping and its text-variable interpolation extension; preview leaves `$name` text literal | C:`core.cpp:241`, `com.cpp:366`; keyboard locale path. Exact lower/upper host text has limited owner evidence, not all printable characters |
| `STRING`/`STRINGLN` multiline blocks | Supported within arena bounds | Shared documented policy: STRING strips leading whitespace/concatenates; STRINGLN removes one leading tab and emits Enter per line; trailing bytes retained | C:`core.cpp:201`, runtime507; Stage7/Stage28B and compatibility fixtures. Formatting reference edges lack independent official-compiler oracle |
| Embedded-language block aliases | Unsupported | Legacy supports BASH/BATCH/HTML/JAVASCRIPT/POWERSHELL/PYTHON/RUBY aliases; they emit literal text and do not interpret host languages; preview unsupported | C:`script_parser.cpp` text opener and raw modes; `core.cpp:305` rejection. Legacy alias tests are not Route B tests |
| DEFINE labels / forward collection | Supported bounded substitution | Legacy and preview have related contracts; no recursive macro engine | C:`core.cpp:176,184`; `tests/compatibility_pass/fixtures/define-prefixes.duck`. Longest match, declaration exemption and delimited bare labels are explicit project rules |
| `IF_DEFINED_TRUE`, `IF_NOT_DEFINED_TRUE`, `ELSE_DEFINED`, `END_IF_DEFINED` | Unsupported | Legacy has fixed-depth preprocessing with structural boundary checks; preview unsupported | C:`script_preprocessor.cpp:34`, parser536; Stage13 tests. Runtime inactive branches are still semantically validated; they are not preprocessing exclusions |
| `EXTENSION`/`END_EXTENSION`, `VERSION` | Unsupported | Legacy supports bounded wrappers/metadata, no arbitrary inclusion/download; preview unsupported | C:`script_parser.cpp:310,318,612`, preprocessor42. Stage13 structural tests |
| Numeric/Boolean `VAR`, assignments | Supported | Legacy additionally has explicit text variables/READ extension; preview numeric-only | C:`core.cpp:228`; global, bounded uint16 variables; prefix-name fixture. Runtime uninitialized variables error rather than silently becoming zero |
| Arithmetic, comparisons, Boolean expressions | Partial official-equivalence evidence | Both use bounded evaluators; legacy wraps uint16 arithmetic while preview/Route B checked overflow errors differ | C:`core.cpp:63` Expression and `duck_expr.cpp`; Stage3/Stage28A tests. Eager Boolean evaluation, precedence/overflow choices are project contracts, not proven official equivalence; Route B unary sign/NOT/complement syntax is not provided by this binary evaluator |
| Canonical `IF … THEN`, `ELSE IF`, `ELSE`, `END_IF` | Supported within bounds | Legacy also retains limited old no-THEN atom/equality grammar; preview/Route B do not inherit it | C:`core.cpp:246`, legacy `script_parser.cpp:44`; mixed-control fixtures |
| `WHILE …`, `END_WHILE`; nested mixed control | Supported within budgets | Legacy and preview implement their own bounded control engines | C:`core.cpp:261`, legacy `duckscript.cpp` control engine; selected Stage5/6 fixtures. Owner observed one finite arithmetic/loop/IF example, not unbounded host testing |
| No-argument `FUNCTION name()`, calls, `RETURN` | Supported bounded integer/Boolean/void behavior | No parameter/local-scope syntax invented; all numeric variables are global | C:`core.cpp:263,271`, Runtime continuations; function-prefix fixture. Calls in expressions suspend cooperatively; 8-call depth. Historical function host trial had an unexplained initial-case discrepancy, not an exact-case pass |
| All-branch preflight and source diagnostics | Supported safety policy | Both engines reject detectable unsupported/malformed inactive code; selected compiler uses physical line/column and bounded source callbacks | C:`core.cpp:305,412`; Adapter loading validates ASCII and exact source size before execution. Runtime-only conditions can still fail later |

## Keyboard, timing and control matrix

| Family / meaningful form | Installed Route B | Legacy / standalone preview distinction | Source/test anchor and limit |
| --- | --- | --- | --- |
| F1–F24, navigation/editing, lock-key usages | Supported named subset | Legacy has broader key vocabulary including keypad names; preview's original named set is narrower than composed shortcut overlay | C:`shortcut_keys.h:11` named map: F1–12 0x3A–45, F13–24 0x68–73. Historical F13 defect fixed; exact mock-report tests. Ordinary standalone CAPSLOCK retains captured5ms/default or500ms/opt-in dwell; chords stay5ms. Not every host interprets every usage identically |
| Left-side chords: CTRL/CONTROL, SHIFT, ALT/OPTION, GUI/WINDOWS/COMMAND | Supported current shortcut overlay | Legacy additionally supports verified right-side names; standalone preview core is not this overlay | C:`core.cpp:283`, `shortcut_keys.h:29`; modifiers combine into an eight-byte report. Modifier-only ordinary spelling is not INJECT_MOD support |
| Right-side modifiers / optional aliases | Unsupported in selected shortcut vocabulary | Legacy RIGHTGUI/RIGHTWINDOWS, RIGHTALT/RALT etc exist. RGUI/RWINDOWS/RCOMMAND/ROPTION remain unsupported optional spellings | Actual composed `shortcut_keys.h:29` versus legacy `duck_keys.cpp`; prior alias-negative fixtures. Do not infer spelling from USB usage values |
| Inline `INJECT_MOD modifier` | Unsupported | Legacy performs modifier-only transient report/restoration; preview unsupported | C:`com.cpp:241` is legacy-only; core rejects before output. First new candidate group below |
| Bare `INJECT_MOD` prefix | Unsupported | Legacy treats it as non-output annotation; this does not establish canonical portable prefix lifetime | C:`com.cpp:242`; Stage28G source-reference ambiguity. Candidate deliberately retains rejection |
| `HOLD key`, `RELEASE key` | Unsupported at real adapter | Preview parses narrow nonmodifier ownership and mock Bridge handles it; legacy has real fixed ownership | C:`core.cpp:276`, `adapter.cpp:74` capability refusal before sync. Parser success is insufficient |
| Modifier HOLD/RELEASE | Unsupported | Legacy directly accepts modifiers as an EvilDuck extension; preview source modifier ownership unsupported | C:`com.cpp:230`, `hid_backend.cpp:433,454`; existing real-backend ownership calls intentionally deny an active Route B lease |
| `DELAY expression` | Supported cooperative delay | Legacy also accepts WAIT alias; preview has same bounded numeric delay event | C:`core.cpp:245,485`, Adapter41; owner physical DELAY+STOP example, no exact latency promise |
| `DEFAULT_DELAY` / `DEFAULTDELAY`, `REPEAT` / `REPLAY` | Unsupported as selected source commands | Legacy supports bounded delay/history operations; these names are not automatically inherited through scheduler linkage | C:`com.cpp:255,259`; core statement inventory rejects. Explicit REPLAY is an extension, not a new canonical claim |
| Random integer/range, random-character commands | Unsupported | Legacy supports inclusive uint16 range and six documented character commands; preview has no RNG environment | C:`duck_random.cpp:37,54`, `duck_vars.cpp:206`; Stage14 deterministic tests. Seed.bin compatibility and random packed keycodes remain unsupported |
| `$_JITTER_ENABLED`, `$_JITTER_MAX` | Unsupported in selected expression registry | Legacy has bounded cooperative jitter; Route B captures/restores shared settings but that is not script-visible support | C:`duck_vars.cpp:174,212`, `seam.inc:31`; no new jitter/timing change in this upgrade |
| `STOP_PAYLOAD`; external STOP | Supported cancellation/local cleanup | Legacy STOP/STOP_PAYLOAD also exist; Route B source bare STOP is not a newly accepted alias | C:`core.cpp:275,538`, Adapter finish, `seam.inc:57`; owner physical STOP_PAYLOAD and external STOP observations; STOP202 means request receipt, not proven host release |
| `RESET` | Unsupported | Legacy clears HID ownership without rebooting; preview/Route B reject release-all semantics | C:`com.cpp:224`; canonical keyboard clear must not be confused with board reset, reboot or reflashing |
| `RESTART_PAYLOAD` | Unsupported | Neither engine implements the required lifetime contract | Parser/core unknown-command paths; restart/preprocessor/feedback state requires a separate reviewed design |
| `INJECT_VAR`, packed random scancodes | Unsupported | Decimal interpolation is not the canonical packed-scancode contract | Core/parser reject; historical Stage15 encoding analysis. No guessed byte ordering or locale/dead-key encoding |

## Feedback, hardware and data matrix

| Family / meaningful form | Installed Route B | Legacy / standalone preview distinction | Source/test anchor and limit |
| --- | --- | --- | --- |
| Lock variables `$_CAPSLOCK_ON`, `$_NUMLOCK_ON`, `$_SCROLLLOCK_ON`, reply indicator | Unsupported in selected expressions | Legacy fixed registry reads observed interface state and rejects unknown values; preview has no device-backed registry | C:`duck_vars.cpp:215,222`; registry names being linked does not make them Route B symbols. Passed Caps/Num EDR1 is a hardware prerequisite, not these source variables |
| `WAIT_FOR_{CAPS,NUM,SCROLL}_{ON,OFF,CHANGE}` | Unsupported | Legacy cooperatively waits with default5000ms bounded policy and USB-session checks | C:`duck_vars.cpp:177`, `com.cpp:202`, LockWait state. New Route B freshness/transition semantics need a coherent subsequent release |
| `SAVE_HOST_KEYBOARD_LOCK_STATE`, saved variables | Unsupported | Legacy saves only known observed state; restore requires released ownership and coherent current/saved session | C:`com.cpp:205`, `duck_vars.cpp:215`; physical global-state equivalence is not established |
| `RESTORE_HOST_KEYBOARD_LOCK_STATE` | Unsupported | Legacy implements bounded feedback-confirmed toggle procedure; not evidence another keyboard's LED was restored | C:`com.cpp:211`, LockRestore and Phase::Press guards. Must remain separately reviewed before any Route B port |
| Other native/internal variables | Unsupported except ordinary user variables | Legacy reserves all recorded names, implements a subset and rejects unsupported reads/writes rather than accepting fake device settings | C:`duck_vars.cpp:159,168,203`; read-only storage/request/failure distinctions are EvilDuck-specific extensions |
| `WAIT_FOR_BUTTON_PRESS`, BUTTON_DEF, ENABLE_BUTTON, DISABLE_BUTTON | Unsupported | No verified application button-runtime integration; do not invent GPIO wiring from a boot switch | Parser/core rejection and Stage9 inventory. Board-specific behavior needs independent hardware evidence |
| `LED_R`, `LED_G`, `LED_OFF` | Unsupported as selected commands | Legacy maps to one supported RGB indicator, obeys LED-disable setting; no independent dual-LED hardware claim | C:`com.cpp:274`, parser390; LED RGB syntax is an extension. Automatic Hak5 LED-policy flags remain unsupported |
| Layout selection / arbitrary Unicode | Partial: selected Route B requires US locale and ASCII input | Legacy US/DE translation exists, including bounded dead keys; unsupported characters may be skipped with warning there; preview is US ASCII only | C:`seam.inc:24`, Adapter input check67, `keyboard_locale.cpp`; arbitrary Unicode is unsupported. High Sierra layout assumptions must be recorded |
| `ATTACKMODE` HID/STORAGE/OFF | Unsupported in selected source | Legacy accepts restricted logical modes with truthful requested/preparing/failed storage states; this does not implement arbitrary USB re-enumeration | C:`com.cpp:327`, parser452, Stage10 MSC tests. VID/PID/manufacturer/product/serial options and random identities unsupported |
| Host OS detection / enumeration counters | Unsupported | `$_OS` may be extension-defined, not a native reliable host detector; native reserved counter has no supported binding | C:`duck_vars.cpp:159,232`; no macOS/Windows identification is inferred from lock replies |
| Storage activity waits / HIDE_PAYLOAD | Unsupported | Separate backing image and plain-script files differ from Rubber Ducky shared inject.bin/media semantics | Parser/core rejection, Stage9 storage inventory; filesystem read/write extensions are not host MSC activity evidence |
| `READ`, `SAVE`, `APPEND` file operations | Unsupported selected source | Legacy has bounded EvilDuck storage extensions, not full canonical data/reflection compatibility | C:`com.cpp:306,317,322`; no private files used in audit/tests |
| Full keystroke reflection / exfiltration flags / loot.bin | Unsupported | Existing EDR1 receiver is not a general-purpose reflection or logging implementation; reserved flags do not implement it | C:`led_receiver.cpp`, `duck_vars.cpp:159,232`. Requires a distinct privacy/data-format/hardware design, not expansion of this release |
| EDR1 fixed-message LED return | Supported custom protocol; owner physically passed on High Sierra | Independent authenticated receiver/host tool, not a DuckyScript command or Hak5 wire-compatible interface | [Owner acceptance](https://github.com/tyronecoe/EvilDuck/blob/routeb-keyboard-control-v1/docs/keyboard-control-owner-acceptance.md): exact17-byte message, Caps clock/Num data, CRC, RAM bounds and explicit arming. Windows and Scroll remain unverified |

## New candidate boundary

| Keyboard feature | Installed baseline | New review candidate |
| --- | --- | --- |
| Inline `INJECT_MOD modifier` | Unsupported on Route B | Supported within left-modifier vocabulary; production-source tested, physical acceptance pending |
| `HOLD key` / `RELEASE key` | Adapter capability refusal before output | Real lease-bound scheduler/backend implementation;37 focused cases pass |
| Direct modifier HOLD/RELEASE | Unsupported on Route B | Implemented as an explicitly labeled EvilDuck extension |
| Bare `INJECT_MOD`, RESET, restart | Unsupported | Still rejected; no guessed prefix/reset contract |

This release targets only inline modifier taps and real Route B HOLD/RELEASE with
STOP/terminal cleanup. Its implementation and actual fresh verification are
recorded in the release report; this baseline inventory does not promote a new
command to installed or physical support merely because the upgrade is planned.
The installed image remains unchanged until a separately authorized installation.

Candidate contract: one execution owner; eight modifier bits/six physical usages;
duplicate HOLD and absent RELEASE are logically idempotent with fresh correlated
operation acknowledgement; aliases share one physical usage; seventh distinct key
refuses atomically. Held modifiers merge with transient text/chords, followed by
restoration of held state. A tap of an already-held usage rejects rather than
inventing a key edge. Bare INJECT_MOD and RESET remain rejected. Direct modifier
ownership is labeled an extension. Local API acceptance/completion/neutral cleanup
does not prove host release or reset a latched Caps state.

## Ranked follow-up backlog and practical validation

| Rank | Coherent work group / usefulness | Regression risk and dependency | Mac / later Windows evidence |
| --- | --- | --- | --- |
| 1 | Finish this lease-bound keyboard group: broadly useful holds, selective release and modifier taps | Medium/high: scheduler, backend ownership, STOP and ambiguity quarantine must remain intact; real composed tests and link guards required | Short supervised TextEdit held-Shift/literal-text/selective-release and STOP-while-held checks after separate installation approval. No global Caps-mirroring criterion |
| 2 | Route B lock variables, reply flag, bounded ON/OFF/CHANGE waits; save separate from restore | Medium: fixed device registry integration, freshness/unknown/session semantics and cooperative cancellation. Restore is a subsequent reviewed contract | Use actual interface report diagnostics and direct observation. Caps/Num path prerequisite now passed. Scroll and host-specific toggle/report behavior remain unverified; bookmark Windows rather than blocking unrelated work |
| 3 | High-value source compatibility from actual intended scripts: preprocessing/extension wrappers and text aliases | Medium: inclusion order, diagnostics, literal bodies, bounded compile passes. Preserve current all-branch preflight policy | Primarily deterministic native source tests; short harmless text fixtures on Mac. No host-shell examples are needed |
| 4 | Route B random integers/characters and cooperative jitter | Medium: exactly-once expression evaluation, clock budgets, backpressure and STOP. Reuse legacy lessons, not its execution state | Deterministic injected entropy/clock tests first; short Mac text checks. Native timing is not physical latency evidence; Windows later if needed |
| 5 | Layout expansion and script-requested text edge cases | Medium/high: physical usages versus characters, AltGr/dead-key sequencing and unsupported Unicode policy | Explicit matching host-layout selection; harmless TextEdit output. Windows layout behavior must be validated separately; do not claim arbitrary Unicode |
| 6 | RESET and payload restart | High: ownership/drain, variable/preprocessor/RNG/feedback lifetimes and progress budgets | Source/state-machine tests before any physical proposal; no board reset interpretation |
| 7 | Button/indicator commands useful on this exact board | Low/medium for verified existing RGB actions; high/blocked for unverified button wiring | No guessed GPIO/button capabilities. Owner observation of supported indicator only when separately approved |
| 8 | USB identity/modes, host detection, storage activity and broader data features | High/separate design: descriptors, host-visible media, recovery and privacy contracts | Separate build/hardware plan and owner approval. Neither EDR1 success nor keyboard tests validate these features |

No row requires waiting indefinitely for Windows11 hardware. A Mac-only limitation
is recorded as platform-limited or unverified unless evidence isolates a firmware
defect; it is not a universal failure. Useful independent software work can proceed
after the relevant roadmap group is reviewed. No automatic payload execution,
pause/resume feature, speculative Caps correction or firmware installation is
authorized by this inventory.
