# Owner acceptance after separately reviewed installation

Candidate buildId:MAC-CAPS-TIMING-20261019-v1. Existing500ms diagnostic Caps output
and Caps feedback are owner-confirmed on the prior build. New ordinary Caps timing
setting remains physically unverified. Num/Scroll/full frame delivery remain
unverified; Codex performs no device/host tests.

After separately approved install/manual reset, confirm the new buildId and
ordinary harmless typing/STOP first. In the UI's **Ordinary Route B Caps timing**
section select **Mac Caps:500ms**, click **Apply for future runs** once and confirm
Future runs:500ms. It is RAM-only: recheck after reboot. Applying/refreshing does
not start a script. An active request keeps its admitted setting.

Focus an empty TextEdit document within five seconds of explicitly starting this
ONE saved fixture through Route B. Do not press Caps on ANY other keyboard during
this test. Do not use a laptop/Razer light as the acceptance indicator.

```
DELAY 5000
STRING capscheck123
ENTER
CAPSLOCK
DELAY 1000
STRING capscheck123
ENTER
CAPSLOCK
DELAY 1000
STRING capscheck123
ENTER
```

Expected host pattern A/B/A:lower/UPPER/lower or UPPER/lower/UPPER depending on
EvilDuck's starting Caps context. Two successful toggles should return the typed
case to its starting pattern. This is not guaranteed restoration after STOP,
failed output or ambiguous delivery; do not blindly toggle again.

Record execution requestId/effectiveCapsMs500, final phase/reason, buildId,
boot/session, before/after cumulative Caps submissions/completions and accepted
LED report counts. Capture fresh feedback when available; reportAgeUs>5000000 is
historical/stale, not current. Compare trialId==requestId only for the separately
retained one-shot diagnostic; its old record is not the current ordinary run.

Separate results:
A: ordinary CAPSLOCK changed EvilDuck-generated text case in the A/B/A pattern.
B: genuine same-interface Caps OUTPUT was received/routed/accepted with its age.
Local submissions/completions prove neither OS behavior nor host release. Another
physical keyboard remaining independent is expected, not a failed acceptance.
Stop if output, ownership or status is ambiguous. No automatic replay.

The separate0/100/250/500ms one-shot diagnostic stays available. Only500ms has
positive physical evidence; minimum threshold and100/250 are not established.
A409 Already receiving is the finite receiver's state, not execution-admission
busy. Stop receiving explicitly if needed; STOP script is a separate control.

After the ordinary test, the smallest optional Num-channel observation is the
finite two-tap fixture and evidence checklist in feedback-analysis.md. Current
EDR1 requires Num DATA and Caps CLOCK, not Scroll. Do not run a host helper or
claim full message delivery based only on Caps. No logger/reflection completion
is claimed by this package.
