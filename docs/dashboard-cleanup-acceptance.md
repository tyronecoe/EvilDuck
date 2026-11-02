# Dashboard cleanup — short owner review

Candidate: **ROUTEB-DASHBOARD-CLEANUP-v1**. This sheet does not authorize
installation, flashing, payload execution or a diagnostic trial. Only perform
browser observations against this candidate after a separately authorized owner
installation. Preserve the previous packages and any existing private backups.

1. On the High Sierra Mac's Chrome and the iPhone's existing dashboard browser,
   open Home and authenticate as usual. Record actual OS/browser versions and
   the displayed build ID. Home should lead with STOP/execution status, compact
   activity evidence, the five tabs, and Status; diagnostic cards should not
   precede these controls. Check scrolling and readable navigation at phone width.
2. Open Dashboard, Scripts, Library, Logs and Diagnostics, then expand/collapse
   its three panels. Existing diagnostic controls should be present; navigation
   alone must not start a trial/receiver, enable a trace, cancel execution, clear
   a result or change timing. Do not press their action buttons for this review.
   STOP remains reachable. A timestamped last observation is not continuous proof
   of current device state. Script STOP does not stop fixed-message receiving.
3. Open Settings. Confirm the two password replacement fields are blank and
   labelled leave-blank-to-keep. Inspect Keyboard timing: its displayed selection
   should match the existing RAM setting; refresh only reads it. Changing the
   dropdown without pressing **Apply for future runs** must not save it. Reload
   the page to discard that unsaved selection. Do not replace passwords or apply
   timing merely to review the layout. RAM timing resets on reboot as before.
4. If authentication is missing/rejected, the new status/diagnostic/timing views
   should give a concise HTTP 401 message, not imply an interpreter failure or
   successful action. Enter the existing dashboard password on Home, never in a
   screenshot or shared URL. Do not change credentials to exercise this check.

Preserve a short note and nonsecret screenshots of Home, Diagnostics and Settings,
including actual browser/OS and build ID. Missing physical evidence is UNTESTED,
not FAIL. A visible issue should be reduced to that page/action; no repeated
keyboard, Caps or lock-wait campaign is requested. No new candidate physical PASS
is claimed by the Linux browser fixtures.

Only browser/layout observations are needed here. No script, HID output, live
receiver/trace/Caps trial, format, reset or settings write is required. Earlier
accepted right-modifier, three lock-wait groups and scoped privacy milestones
remain closed with their original evidence limits.
