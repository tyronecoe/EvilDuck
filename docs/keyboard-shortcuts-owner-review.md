# Owner review and future editor-only trial

No hardware operation is executed or authorized by this document.
Keep the installed Stage28X image and its known public package available.
The October 16 owner handoff is limited physical evidence for X on that board
and macOS 10.13.6. It is not new-candidate evidence. The earlier `Functiondone`
versus `functiondone` discrepancy remains unresolved; the later mixed-case pass
does not explain it. Local clearSubmitted never establishes host key release.

Review source delta, reports, hashes, current configuration, recovery ability and
candidate identity before separately deciding whether to authorize any installation.
No flashing/OTA commands are provided here. Do not reuse the Stage28Y X manifest
with the changed application: a new reviewed artifact binding would be required.

Only following separate installation and trial authorization, a possible short
manual test is `tests/keyboard_shortcuts/fixtures/editor-only.duck`. Its intended
result in a new, empty, plain-text editor document is:

```
abZ
done
```

The owner must explicitly select that disposable empty document, review editor
capitalization/substitution settings, verify saved fixture bytes, explicitly select
Route B, allow the focus countdown, and permit exactly one Start. This document
is not an auto-run helper. COMMAND a selects all current editor content; never use
an existing document. No shell, credentials, network payloads or host commands.

Capture the actual source/build identity, final status/reason, local diagnostics,
observed editor text/case and any stuck modifier symptoms. Distinguish visual
host checks from device counters. If anything is ambiguous, stop and reduce to
one benign shortcut before changing firmware. Do not automatically replay, enable
autorun or infer that ordinary web Run selected Route B.

The owner reported a newer retained backup SHA
`67c1a1474f1c0814f6267d1ad811221ab623e8b3e4126a9108cafddfdabba4eb`.
No bytes were supplied or inspected here. Historical backup identities remain
historical records; this task neither overwrites them nor resolves their distinct
file identities. Original-data preservation is not required; existing backups
must remain untouched. Stock firmware availability is OWNER CONFIRMED externally.
