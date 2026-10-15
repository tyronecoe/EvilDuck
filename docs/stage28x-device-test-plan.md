# Stage28X future controlled device-validation plan

**EVERY PHYSICAL TRACE BELOW: NOT EXECUTED.** This is review material, not permission
to connect, interrogate, install, boot, access serial/USB or inject keys. No automated
flasher or install hook is supplied. Strict Route A/USB retirement remains unresolved.
A linked Route B candidate establishes only local scheduler/submission contracts.

Before authorization, owner must choose: exact computer/OS and keyboard layout;
controlled X diagnostics-enabled image identity; fresh credentials prepared privately;
exact new-layout complete artifact set and independently verified recovery package;
acceptable provisional telemetry limits; approved observation channels and maximum
session length. No broad repeated request for old firmware or private files is needed.

| Gate | Preconditions and bounded future action | Expected evidence / stop / recovery |
| --- | --- | --- |
| A: prerequisites/install | Separate owner-approved deployment review authorizes the exact image/range set, fresh NVS/SPIFFS replacement and first boot. Confirm target/layout/security, ROM entry/data cable/power, current tool support and restorable package before any write. | Check hashes/headers/table/readback under that authorization. Missing/mixed image, wrong geometry, unstable connection or partial operation =>stop in ROM; use separately approved recovery, no guessed offset/full-chip erase. Installation steps are not executed or provided as a runnable command here. |
| B: idle, no script | After approved installation/boot, leave Route B unselected; observe startup and new diagnostics via authenticated HTTP or local CLI. Suggested60s idle with one status/sec, not concurrent floods. | Controlled-start marker, strict settings/mount success, no format/examples/autorun, ticks advancing, resource flags known for heap/loop, AsyncTCP unknown. Record max observed intervals/work, low-water stack, free/min/largest8 and refusals. Any critical startup error, unexpected script/key activity, loss/quarantine or absent progress =>no later tests; stop/recover under authorization. |
| C: prepare/cancel/refusal, no output | Later authorization permits saving only a reviewed benign Delay-only fixture (finite long delay) through an admitted synchronous path while idle. Explicit Route B selection/manual Start only. Cancel during capture/verify and separately during Delay; try one competing service request and one competing Start. Each trial <=10s, entire group<=2min. | Copied request/capture phase then STOP observation, clean local cancellation/clearing or conservative fault/quarantine. Competing service/Start refuses before side effects. No visible text expected. Capture can finish before a polling request sees it: report this as unobserved, not a passed cancellation point. No artificial media removal in this gate. |
| D1: tiny text | **Separate explicit HID-output authorization**, owner-controlled computer, correct US/DE layout selected, deliberately focused empty text editor; no terminal or sensitive application. Manually start a reviewed fixture containing only one tiny literal STRING, e.g. `STRING test`. Trial<=10s. | Observe exactly `test`, compare localKind/sequence separately. Unexpected focus/characters/held keys =>stop; do not promise unplug releases host state. No shell commands, credentials, automatic payload or owner scripts. |
| D2: bounded timing/STOP | Only after D1 review, finite small loop supported by unchanged preview subset, literal text plus short Delay; validate fixture offline before saving. One competing status/Start and separately STOP during Delay. Each<=10s. | No replay after ambiguous submission; cancellation prevents further admissions when observed. Visible editor text and local report submissions recorded separately. No endpoint completion/host-release guarantee inferred. Existing limits remain; unsupported HOLD/INJECT_MOD/RESET are not test substitutions. |
| E: review/optional loss | Compare agreed samples after each trial, entire session<=5min initially. USB unplug/loss/reconnect only in a separately specifically approved subtest with harmless focus, no modifier chord and known host escape/recovery plan. | Loss =>permanent quarantine/no automatic replay or rearm. Record actual visible host state independently. Diagnostic gap or disconnected channel cannot certify release. No arbitrary physical fault injection, no live media write interruption. |

Provisional abort criteria for owner review: no owner tick advancement in two
successive1s observations while observation transport is responsive; maximum observed
interval/work exceeding250ms; loop minimum remaining stack<2048B; free8<32768B;
largest8<16384B; any clockErrors increment, queue/repeated refusal without progress,
quarantine/loss, mount/configuration error, unexpected text or non-idle startup.
These are conservative proposed trial limits, not measured safe margins or real-time
requirements. Low min8 is a sum of region histories, not a simultaneous measurement;
compare trends as well. AsyncTCP stack is unavailable, so loop success does not prove
network stack sufficiency. Review may tighten limits before authorizing a trial.

STOP publication/observation cannot bypass bytes not yet parsed by CLI. With64 reads
per loop, a known finite backlog requires at least ceil(bytes-through-LF/64) turns;
arbitrary continuous backlog has no finite STOP arrival guarantee. Do not spam the
serial input. HTTP STOP can fail authentication snapshot/admission during execution
mutex contention;401/409 means retry after contention or use a separately available
local path. An unresponsive serial/network channel is itself an abort, not evidence
that a STOP or release arrived. No busy-spin retry or repeated HID replay is allowed.

Capture only sanitized numeric diagnostic records, build identity and explicit harmless
visible-text result; no credentials, SSID, script contents beyond reviewed literal,
filesystem inventory or owner data. Local scheduling, local clear submission, visible
text, and strict USB transfer retirement are four different evidence levels. Actual
RTOS timing, physical heap/stack/media, High Sierra compatibility and USB delivery
remain pending. Stage28Y is not authorized by this plan.
