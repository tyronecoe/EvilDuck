# Owner-operated Caps evidence — 18 October 2026, America/Vancouver

Recorded from Tyrone's supplied handoff. Codex did not operate the board, inspect
private flash bytes, or independently analyze the original video/photo here.
Baseline report commit:baddb8f2d3bb6060e0f72e6cbe58377c894c86bb; source/build
c868ed8ed66cac9a4bae08d4efb52c17e3d688ec; package
bb9a2041f9bad6882c4fa8cf73f97ce6c9798816. Expected observed buildId:
CAPS-DURATION-20261018-v1. Prior application1,392,208bytes,
SHA25658b0fb93cd39f614109fd3c0079d9e364597c8eb79ee4850955542b8d54caf72.
The pinned public package and exact application bytes were downloaded and checked
again for this task; this is artifact verification, not live-board readback.

Environment: owner's EvilDuck S3, macOS10.13.6 laptop, iPhone controlling the UI,
and a Razer BlackWidow-family USB keyboard. Exact Razer variant is unconfirmed;
two leads/passthrough do not establish V3 or global keyboard-state forwarding.

Between STRING-only script runs, the owner explicitly clicked the separate500ms
Caps trial. The supplied account of TextEdit photo
IMG_F8EF7EB3-9CD6-42DA-A5DF-A186D37D16D5.jpeg shows:

```
capscheck123
CAPSCHECK123
capscheck123
CAPSCHECK123
```

Owner explicitly attributes the toggles to the trial, not STRING. The laptop's
Caps state/light and laptop-typed case remained independent. Razer Caps affected
its own case/indicator without the laptop indicator. This is positive evidence
for EvilDuck's own Caps context, not failure because a different light stayed off.

Owner's narrated-video account (RPReplay_Final1792378998.mp4): build above,
boot415f2d960ee4efc9, feedbackSession3. Trial8: observed mask0/Capsfalse/reports8;
trial9: observed mask2/Capstrue/reports9; ledEvidenceValidtrue and rejected0 for
both. Raw OUTPUT was routed and accepted through the existing prefixed-ID path.
Initial missingRoute for ID0 followed by successful routing is not a lost report.
Trial8 queue-return down/up433414997/433916956us:501.959ms. Trial9
451535989/452037955us:501.966ms. These are local accepted-submission intervals,
not measured wire dwell or host-release proof. Cumulative completion totals reach
8/9 respectively; they are not substituted for per-request timing records.

Later stale samples are older than the5-second freshness window, not absence of
received feedback. Retained trial attribution requires requestId==trialId plus
matching boot/session; a new queue admission may initially expose an older trial.
HTTP409 Already receiving belongs to the separate fixed-message receiver, not
execution-admission busy.

Confirmed by this owner evidence:500ms diagnostic Caps activation and genuine Caps
LED OUTPUT to EvilDuck. Not established: minimum interval,100/250ms success,
ordinary Caps using the new opt-in setting, every channel/keyboard/OS, host key
release, full decoded fixed-message delivery or capture of another keyboard.
Historical reports remain unchanged; this document supersedes their old laptop-
manually-typed-abc acceptance criterion for new testing.
