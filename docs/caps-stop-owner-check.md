# Human-controlled High Sierra / iPhone diagnostic checklist

New trace application is physically UNVERIFIED. This document is a proposed lab
check, not authorization to install, boot, send HID or run an unattended payload.
Keep the working package and exact rollback accessible. No need to upload backups,
credentials, typed text or ordinary key logs. Never use a shell/prompt as the target;
use an empty harmless TextEdit document with deliberate focus.

1. After separately approved installation, record buildId, app SHA and boot marker.
   Expected new ID CAPS-STOP-TRACE-20261019-v1. Record built-in LED, physical Caps state,
   global observer state and EvilDuck LED-feedback mask separately. They may differ.
2. From authenticated iPhone dashboard while idle: enable/reset bounded trace. Read
   next events manually as needed. Ring128/8perpage/120seconds; note any overwritten,
   sequence gaps or clock errors. Enable is not Start. Do not refresh/reset while
   active. HTTP errors are inconclusive, not successful STOP/idle.
3. Select default5ms or opt-in500ms for a **future** ordinary Route B run. Record
   captured requestCapsMs, run ID and setting. One start only; no automatic replay.
4. Minimal fixture, supervised: DELAY2000, CAPSLOCK, DELAY1000, each on its own line.
   With baseline recorded and focus in TextEdit, separately test STOP before press,
   during500ms dwell, between two deliberately spaced toggles and after completion.
   For text case evidence use only the reviewed alternating abc fixture from the
   owner handoff, one finite invocation at a time. Do not use a loop.
5. Separate receipt202/http202-prepared, stop-published, stop-observed, neutral
   submission/completion and terminal(reasonCancelled). Record phase/queue/error and
   new admissions. An already accepted transfer may complete after STOP. No new
   Caps/other-key submission should follow owner-observed cancellation, except
   admitted future runs. Neutral cleanup is expected; it does not undo latched Caps.
6. Observe first while the Mac is otherwise idle; then, in separate captures, use
   physical ordinary letters or physical Caps. Record physical case/LED visually;
   optional bounded host observer captures only Caps/modifier changes by service.
   No global flag or SDK callback alone proves host delivery or device attribution.
7. If unexpected transitions continue, preserve trace before overwrite; record
   whether any backend attempt/accepted Caps occurs, a new admission, LED OUTPUT,
   delayed completion, or only polled host flags. With no complete/gap-free capture,
   leave source UNKNOWN. Do not repeatedly Start to compensate for missing output.
8. STOP once, observe terminal/current generation. If active/ambiguous or unwanted
   output persists, physically unplug as the owner-controlled safety action, stop
   testing and review finite logs. Reconnect only under separate deliberate control;
   do not assume a disconnected host received release. Trace/in-RAM setting reset
   at boot. Use deliberate rollback if an authorized update fails acceptance.

Expected software behavior:default5ms, captured500ms opt-in, no additional key worker
at idle, no replay on reconnect, bounded logging, unrelated typing/shortcuts intact.
Do not promise the built-in Apple LED follows EvilDuck or claim Caps synchronization.
Requested evidence:buildId/SHA, trace JSON with gaps/header, sanitized optional host
Caps/modifier output and timing, visual physical LED/case observations, run/STOP
reasons. No private values. The suspected physical cause remains unresolved until
this discrimination is actually performed.
