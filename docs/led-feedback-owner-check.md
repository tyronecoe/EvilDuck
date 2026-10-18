# One short post-install LED observation

Software preparation does not authorize a write or boot. Use the separately
reviewed Mac package instructions and their app-only checks if installation is
later explicitly authorized. Current exact board image remains unidentified.
The update should visibly show buildId LED-FEEDBACK-BOUNDARY-20261018-v1.

1. With a blank TextEdit document focused, explicitly Run one benign
   `STRING LED BOUNDARY CHECK 123` fixture. Check exact host text and the same
   request's Completed/idle state. Stop if typing or STOP regresses.
2. With NO script running, open LED observations on the dashboard. Do NOT press
   Start receiving. Capture buildId, bootMarker, uptimeUs, USB samples, rawArrivals,
   rawLastInstance/type/id/length/protocol, registration, outputAttempts,
   keyboardDispatches, callbacks, reports, routeReject and receiverOutcome.
3. Set the Mac's PHYSICAL Caps Lock off/on/off, visually checking its keyboard
   light. Refresh promptly after each actual transition, within the5-second
   freshness window. Capture the full new snapshots. A setting already off may
   produce no new report. Do not compare cumulative counts across changed boot
   markers/uptime resets. No host helper, private text or Start receiving is needed.

Interpret ONE set of results:

- Raw stays zero: no arrival at the instrumented SET_REPORT entry. No conclusion
  about packets on the wire or a blanket macOS restriction.
- Raw rises, keyboard callbacks stay zero: inspect type/ID/protocol/registry and
  route rejection. This is the source-routing/descriptor seam.
- Keyboard callbacks rise, accepted reports stay zero: inspect receiverOutcome
  (length/ID/padding/session/configuration/suspend).
- Accepted reports and masks track off/on/off but the display does not: snapshot
  or UI problem. Inspect ledEvidenceValid, freshness and session coherence.

Test EvilDuck's own CAPSLOCK tap separately AFTER this basic feedback observation;
use the Caps queue/completion metadata and exact text, without HOLD/RELEASE.
Do not run blind repeated trials. Only after raw Caps AND Num feedback work on a
chosen host consider the separately reviewed finite17-byte EVILDUCK TEST 123
RAM-only receiver. Missing Num feedback may leave that transport unsupported.
No physical Caps, LED, host release, latency or full compatibility PASS is implied
by software tests or compilation.
