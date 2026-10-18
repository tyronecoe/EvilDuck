# Caps-duration and feedback investigation — software review candidate

Baseline `3e693fbe790af670278716cdf4d64c75485cb097`; new branch
`caps-duration-feedback-trial`. Owner-installed rollback: application
`2c657f0c74f1d12c88aa1e6fa6daf5cc76de36e8e68bc41a325f39b19c9045a7`,
1,386,176bytes. The owner's installation receipt and observed buildId are recorded
as owner evidence, not independently read private bytes. All backups remain
untouched. New buildId: **CAPS-DURATION-20261018-v1**.

## Changes and decision

The selected Route B scheduler's ordinary Caps wait remains5ms. A new authenticated
one-shot UI operation selects baseline/100/250/500ms after a5-second focus delay.
It uses the existing memory-source compiler, single execution owner, backend lease,
cooperative wait, STOP, deadline, cleanup and quarantine. No general HOLD/RELEASE
support, detached timer, automatic replay or global keyboard slowdown is introduced.
A retained per-trial record distinguishes request/trial identity, selected duration,
boot/session, accepted submissions, observed completions and terminal reason.
Normal sync/cleanup can submit neutral reports; these are not extra Caps taps.
Queued admission is not completion and may precede trial-record creation.

See caps-duration-design.md for exact timebase, ownership and diagnostic boundaries.
See caps-duration-feedback-analysis.md and its source/object receipt for the separate
receive investigation. The linked67-byte keyboard descriptor is unchanged,ID1 with
LED OUTPUT. Both inspected successful control and interrupt-OUT routes enter the
same raw callback. No concrete receive defect or ID0 packet has been established;
no descriptor/routing/FEATURE workaround is added. The duration experiment tests
Caps activation; optional read-only Mac HID-service inspection tests recognition.
These enable different decisions and do not promise feedback from High Sierra.

## Executed software validation

| Check | PASS | Unexpected FAIL | Assertions |
|---|---:|---:|---:|
| Actual composed native modules,28 new +147 inherited |175|0|7,097|
| Relevant unchanged backend/diagnostic regressions |63|0|2,650|
| Embedded UI in Node VM |26|0|44|
| Existing additive-core positive/negative guards |14|0|Case-accounted|
| New fixed-state helper allocation probe |1|0|10,000 cycles,0 C++ new calls|
| Actual esptool4.12 parser only |14|0|Case-accounted|

Native and related cases pass ASan/UBSan with leak detection. The helper probe also
passes ASan/UBSan/leaks. C++ counted assertions total9,747; JS assertions44. Python
checks are case-accounted, not invented assertion totals. The allocation probe
executes the actual new helper with stubbed feedback, not a full firmware heap
measurement. Core tests preserve old guard rejection; historical test files and
expectations are not rewritten. The new runner adapts only copied D12's buildId
literal to this candidate. T34/X13/X15 exclusions retain documented prior reasons.
The235-file Stage26 freeze check passed. Package fault-injection37/37 and bound-installer38/38 also passed after archive
creation; esptool parser14/14 remains dispatcher-free. There are368 case-accounted
PASS cases/groups across the listed suites, zero unexpected failures, plus separate
linked descriptor and freeze checks. No physical tests are counted. No historical XFAIL/XPASS is reclassified.

## Clean target build and resources

ArduinoCLI1.3.1, Arduino ESP32 core3.3.0 approved isolated archive-based feedback
profile, Xtensa GCC14.2.0 and177 unchanged SDK archives. PSRAM disabled; existing
16MiB custom geometry, USB-OTG/CDC, CPU and flash settings retained.

| Measurement | Installed baseline build | Candidate | Growth |
|---|---:|---:|---:|
| Compiler program |1,386,023B|1,392,063B|6,040B|
| Application BIN |1,386,176B|1,392,208B|6,032B|
| Static RAM |107,688B|107,768B|80B|
| Free bytes per0x740000 OTA slot |6,216,000B|6,209,968B|-6,032B|

Free slot capacity81.686717%. App SHA256:
`58b0fb93cd39f614109fd3c0079d9e364597c8eb79ee4850955542b8d54caf72`.
ELF SHA256:
`6720c900769ee450cd03c43910625afcf179f1caac2faeffb72dbe795f687d15`.
Core tree `a79b9c7e42e7ea2066815271117eeac23fe0a27e65fa00657dc268b70c22c53a`
is unchanged from the installed baseline composition. Full pins and283 linked
inputs are in caps-duration-build.json. The exact regenerated BIN, source copies,
existing startup guards and actual added call edges are independently checked.
No merged flash image is packaged.

Compiler frame estimates: new HTTP trial1376B, existing LED diagnostics3680B
unchanged; coordinator tick352B vs304B, com update80B unchanged. New helper begin
and session check224B each; other helper methods32B each. Task loop remains8192B;
AsyncTCP's pinned default task stack is16KiB. Estimates are not task high-water
or whole-chain stack bounds. Actual hardware heap, stack, latency, USB delivery,
Caps output and LED feedback are not measured by this task.

## Package and owner boundary

New package name: `evilduck-caps-duration-macos-install-v1.zip`. Source/build commit:
`c868ed8ed66cac9a4bae08d4efb52c17e3d688ec`. ZIP2,204,946bytes, SHA256
`9aba81efcd0a65f1f7bb97073e840786e8d48eb8cfa969ca5f7baab588cd764d`.
Release receipts provide the immutable ZIP commit and actual download verification.
Strict default read-only checks, fresh chip/security/table/OTA checks, NEW private
full backup, typed INSTALL/ROLLBACK, repeat validation and two independent app
comparisons remain. Only0x10000/0x750000 applications are in any proposed write
set. Original nonapplication regions, backups and previous packages are preserved.
The exact2c657f0c rollback is included; no573/c20/de24 substitution.

GO: review verified software/package and select one owner-operated acceptance
trial after separate physical authorization. NO-GO: any cloud hardware operation,
automatic installation/boot/replay or claim of physical Caps/LED success. See
OWNER-CHECK.md in the release for separate output-versus-feedback criteria and
optional minimal read-only High Sierra inspection. Fixed-message reflection
remains gated on physically demonstrated Caps AND Num feedback. No further stage
or unrelated language/USB personality change is started.

File inventory and final remote-ref comparison are recorded in the publication
receipt. This task creates only new docs/caps-duration*, tests/caps_duration and
separately named download artifacts. Historical files, toolchains and profiles
are unchanged. No physical hardware access, flashing, OTA or real HID output occurred.
