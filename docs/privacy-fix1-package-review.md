# Privacy Fix 1 — package review scope

This owner-review package reuses the exact existing privacy application and ELF
from the clean target integration. No firmware recompilation, runtime-ID change,
new HID command, scripting feature, installer redesign or physical operation is
part of packaging.

Application: 1,415,968 bytes, SHA-256
`9e4d3b615d78e87521882a35c4b43ce66403168a15b6b39bcebc81bb32a6b96e`.
ELF SHA-256:
`af7887ceccfe2694738c173c76b3c211b78cb0c7b667d8d7d942a1b0ef317f6e`.

The maintained privacy patch removes routine saved-password readback and settings
echoes. Blank or omitted replacements keep existing values; nonempty invalid
credentials are rejected before setters. The exact 201-file composition has
three privacy changes and 198 unchanged entries; the consumed web header, actual
compiler inputs, linked objects and ELF/BIN remain bound by verification.

The applicable full frozen H1 release/link/disassembly chain was additionally
executed against these existing artifacts. Only final expected hashes for
`cli.cpp`, `webserver.cpp` and `webfiles.h` were narrowly adapted. Historical
source pins, unrelated hashes, selectors and linked-code assertions are retained.
The execution audit in build-receipt.json records the exact adaptations,
generated-unit AST identities and preserved assertion counts. The independent
privacy input-binding verifier also passed. This is software verification, not
execution of the firmware on High Sierra or hardware.

Previously reconciled native evidence is reused: 28 privacy cases / 736
assertions, 558 regressions / 23,901 assertions and 12 embedded JavaScript groups /
221 assertions, with their existing sanitizer/leak results. Those tests were not
rerun just to assemble a ZIP. Package and mock-installer results are recorded in
the separate publication report; mocks do not establish Mac or device operation.

Recorded target resources: program 1,415,827 bytes, application 1,415,968 bytes,
static RAM 113,896 bytes and 6,186,208 bytes free per 7,602,176-byte OTA slot.
No physical heap, timing or stack high-water measurements are claimed.

The dashboard ID remains `ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1`; identify this
privacy image by hash and manifest instead. H1 stays experimental and canonical
Hak5 INJECT_VAR encoding remains unresolved. Existing owner acceptance remains
scoped; no repeated keyboard/lock-wait trial is requested.

Query-password authentication, browser session storage, RAM/trace retention and
other separate privacy findings are unchanged. Settings persistence is still
non-atomic. The rollback is the older source/text-v2 application and does **not**
include this privacy repair. No installation is authorized by this package.
