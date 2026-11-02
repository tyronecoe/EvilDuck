# Dashboard diagnostics cleanup — owner-review candidate

**GO for software/package review. Physical candidate behavior remains UNTESTED.**
This task adds presentation/navigation and an identity-only build label. It adds
no scripting, HID, LED-protocol or host-control capability. No hardware, owner
scripts, private backups or credentials were accessed; no flashing, OTA, real HID
output or payload execution occurred.

## Baseline and source identity

The new isolated branch is `routeb-dashboard-diagnostics-cleanup-v1`, starting at
Privacy Fix 1 publication `70d08e9f789c187c5e27350a66f4d0d52992964b` (packaging
source `48ed7c9dc694316d8f1d194c0bbf4efe492186f9`). The worktree was clean. Remote
refs were independently snapshotted before changes; no later closeout branch was
found in that snapshot. Historical sources, reports, builders and packages are
retained. The owner handoff's accepted right-modifier, three lock-wait groups and
scoped privacy milestones remain closed; missing historical identifiers stay
unknown. No repeat acceptance campaign is requested.

Firmware implementation commit: **`0db1f980e0ed05390d71fe9e92178304d7a3bc24`**.
Distinct actual runtime BuildId: **`ROUTEB-DASHBOARD-CLEANUP-v1`**. Historical nested
source-stage IDs remain historical; the linked image and new package carry the
new actual identity. H1 remains explicitly selected and experimental. Canonical
Hak5 numeric encoding remains unresolved.

The maintained [patch](../tests/dashboard_cleanup/application.patch) and
[source manifest](../tests/dashboard_cleanup/source-manifest.json) compose the
existing H1 and Privacy Fix 1 layers once, then apply a zero-fuzz dashboard delta.
A fresh independent clean-base replay matched all **201** files. Exactly
`webfiles.h` (UI) and `caps_trial.h` (BuildId literal only) change relative to
Privacy Fix 1; **199** files are unchanged. The cumulative original-H1 delta is
four files (`cli.cpp`, `webserver.cpp`, `webfiles.h`, `caps_trial.h`), **197**
unchanged. The earlier privacy **3/198** inventory remains a parent layer, not the
final candidate inventory. No root/uncomposed firmware file was edited.

## Everyday UI and controls

- Home starts with a sticky STOP/execution strip, compact diagnostic activity
  evidence and Dashboard / Scripts / Library / Logs / **Diagnostics** navigation.
  Status and everyday controls appear before historical test content.
- Diagnostics contains the existing fixed-message LED receiver, one Caps-duration
  trial and bounded HID/STOP trace in collapsed panels. IDs, explicit controls,
  endpoints and backend implementation are retained. Opening/navigating/expanding
  does not act on the device.
- The existing 5 ms / 500 ms Mac Caps timing selector lives in Settings. Initial
  load/refresh is GET-only; **Apply for future runs** is the sole timing write.
  A pending GET cannot overwrite a newer unsaved dropdown choice. The setting
  remains RAM-only until reboot; an active run retains its captured value.
- Home's compact activity text performs at most one sequential read cycle per
  five seconds while visible, skipped during a pending Run/STOP. Three existing
  endpoints are read; trace polling uses `after=4294967295` without changing its
  manual cursor or enabling/resetting capture. Detailed JSON remains manual.
  Hidden Logs do not poll. Each fetch/body read is bounded by the existing
  control-fetch deadline; execution status and STOP have independent progress.
- Activity is explicitly a **timestamped last observation**, not an atomic or
  continuously current snapshot. Errors/401 produce unknown activity, not false
  inactivity. Script STOP does not stop fixed-message receiving.
- Home and Settings retain reachable STOP and correlated execution status. New
  status/diagnostic/timing failures show concise authentication/error text rather
  than a raw HTML error page. Existing authentication and credential storage are
  unchanged; no new password persistence is introduced.
- Privacy Fix 1 remains intact: replacement fields blank/write-only; blank or
  omitted credentials preserve stored passwords; unrelated saves omit secrets.
  This task does not claim to address the separate URL-authentication, browser
  retention, diagnostic retention or non-atomic settings-persistence findings.

## Fresh verification and honest limits

| Executed check | Observed result |
|---|---|
| Actual embedded HTML/JS in inert Chromium fixtures | **9 PASS groups / 207 assertions / 0 final FAIL** |
| Existing LED-return STOP UI regression, unchanged runner | **10 PASS groups / 21 assertions / 0 FAIL** |
| New release-adapter policy unit tests | **5 PASS / 0 FAIL** |
| Fresh clean-base composition | **201/201 exact files**, 2/199 final delta, identity-only header |
| Repeated delta application negative control | Rejected before patching |
| Clean target compile and final input/header/object/image binding | PASS |
| Full frozen inherited H1 release chain against new ELF/BIN | **6 layers PASS; all 190 static Assert nodes retained** |

The 190 count is an AST audit count, not 190 independent runtime tests. The chain
retains linked ownership, STOP, cleanup, keyboard/lock feedback, preprocessing,
text/restart/timeout, H1/right-modifier, USB, NVS, SDK/core and startup guards.
Only four final candidate source-hash expectations and actual-ELF build-label
checks are narrowly adapted; historical source-pin identities are preserved.
The target verifier additionally binds the new header via the actual
`caps_trial.cpp.d`, compiled copy, pinned compiler command, object, link map and
ELF marker. Compiler-inserted source directives are normalized under the inherited
source-copy policy. No image is substituted or rebuilt during release verification.

Full receipts: [browser](dashboard-cleanup-browser-results.json),
[software checks](dashboard-cleanup-software-checks.json),
[composition](dashboard-cleanup-composition-checks.json),
[guard audit](dashboard-cleanup-guard-audit.json),
[target binding](dashboard-cleanup-target-checks.json),
[build](dashboard-cleanup-build.json), and
[release verification](dashboard-cleanup-release-checks.json).

An intermediate browser-v2 run recorded 8 PASS/1 harness FAIL: a locator matched
two existing Refresh buttons. The corrected scoped locator then passed v3; both
receipts remain in scratch. Earlier v1 passed 9 groups/206 assertions. The final
v3 count is used once, not accumulated across runs.

The earlier `tests/stop_ui/test_ui.cjs` was also tried unchanged: it FAILS on both
the unchanged privacy base and this candidate because its `text()` mock returns
`String(object)`, whereas the existing control code parses JSON response text.
That baseline-incompatible runner is recorded, not silently called PASS or
weakened. The later unchanged `tests/led_return/test_stop_ui.cjs` uses the actual
response contract and passes; the new real-browser fixtures independently cover
correlation, authentication, no retries and STOP progress under delayed reads.

The unchanged native/backend Privacy Fix 1 evidence (28 privacy cases/736
assertions, 558 regressions/23,901 assertions, clean ASan/UBSan/leak checks) is
**historical, not freshly rerun**. Only UI strings/JS/CSS and one identity literal
changed, so those unchanged C++ runtime suites were reused. No new native memory
logic or claim of fresh sanitizer execution is introduced. Browser fixtures use
inert HTTP only; no host input, OS injection or real diagnostic action occurs.

## Target build, resource comparison and provenance

Approved isolated archive-based Arduino ESP32 **3.3.0**, ESP-IDF **5.5** profile;
ESP32-S3, 16 MiB, PSRAM disabled, existing USB-OTG/CDC, partition geometry,
authentication and controlled startup. No global installation or historical guard
is modified. Compiler: Xtensa GCC **14.2.0**, Arduino CLI **1.3.1**. Actual commands,
linked archives, object hashes and all dependency pins are in the receipts.

| Metric | Privacy Fix 1 | Dashboard cleanup | Change |
|---|---:|---:|---:|
| Compiler program bytes | 1,415,827 | **1,428,067** | +12,240 |
| Application BIN bytes | 1,415,968 | **1,428,208** | +12,240 |
| Static RAM bytes | 113,896 | **113,896** | 0 |
| OTA slot capacity | 7,602,176 | **7,602,176** | 0 |
| Free bytes per OTA slot | 6,186,208 | **6,173,968** | -12,240 |

Application SHA-256:
`e0ae270554c28dbc7f5634a5879c4ea56dd39b60e37b4c2de5cb9493520b97d1`.
ELF SHA-256:
`39c5003af0006cf6e74297a4cbc135bae771a5d3592a553cc485d159bb3977b4`.
Unchanged production partition table SHA-256:
`b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.
Compiler SHA-256:
`d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3`.
SDK NVS archive SHA-256:
`a1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e`.

Compiler stack estimates remain estimates: setup 80 B, loop 32 B, loopTask 32 B;
largest recorded static frame 4,224 B in Program::compile. They are not task-stack
high-water, physical heap, latency or hardware stability measurements. JavaScript
adds browser-side state and bounded GET traffic; its physical network impact is
unmeasured. Static RAM equality does not prove unchanged dynamic heap behavior.

## Package and owner boundaries

One distinct Mac application-only review ZIP is prepared from these exact verified
bytes, with independently checked extracted offline preflight, frozen package and
mock-installer tests. Packaging and publication receipts record exact archive
identity and new source/publication commits; see `dashboard-cleanup-package.json`
and `dashboard-cleanup-publication.json` after publication. The application is not
a bootloader, merged-flash or filesystem image. No bit-for-bit cross-build
reproducibility or installed-device identity is inferred from a successful build.

Mandatory rollback remains the exact **1,413,200-byte** source/text-v2 application:
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It is older firmware **without Privacy Fix 1 or this UI change**. Rollback does not
restore settings, filesystem data or deleted contents. Existing installer behavior
remains bounded to the two application slots, with current layout/security/OTA
checks, explicit owner confirmation, private full-flash backup and verification;
it does not rewrite data partitions or automatically reboot. Backup creation
precedes final write confirmation and can retain secrets even if writing is
cancelled. Preserve existing backups and do not upload private receipts.

The first offline Mac command is `python3 preflight.py --directory .` from the
extracted directory, with EvilDuck unplugged. See the [reproduction guide](dashboard-cleanup-reproduction.md)
and [short acceptance sheet](dashboard-cleanup-acceptance.md). Installation,
flashing, boot and physical testing remain separate owner-authorized actions.

The [platform matrix](dashboard-cleanup-platforms.md) distinguishes dashboard,
USB input and installation for High Sierra, newer macOS, Windows 10/11, Linux,
Android and iOS. Actual new evidence is Debian 13 Chromium 151.0.7922.173 /
Playwright 1.62.0, desktop and 320/390px touch emulation. Native High Sierra/iPhone,
Firefox/WebKit and all other physical targets are UNTESTED, not FAIL. No generic
USB-driver documentation, Linux PASS or Wi-Fi iPhone observation proves another
surface. No Windows/Linux/mobile installer support is advertised.

Next action: review this bounded UI candidate, then separately authorize any
owner installation. After that, use the short page-navigation/settings-display
check; no new keyboard test or live diagnostic is needed for this presentation
milestone. No further feature or privacy stage is begun here.

## Final packaged-byte checks

Packaging source: `be559301ab01a608396073f8656d05e4f59921e7`. Final ZIP:
[evilduck-dashboard-diagnostics-cleanup-h1-macos-review-v1.zip](../downloads/evilduck-dashboard-diagnostics-cleanup-h1-macos-review-v1.zip),
**2,497,152 bytes**, SHA-256:
`f9221d2f8bd397cbcaf9166126026f4712fc17fd0ae883fe05115cc33578142c`.

The final archive passes **83 package checks, 38 bound-installer mocks and 44
dashboard-specific semantic checks**, all with zero final failures. Six packaging
policy unit checks also pass. These are separate from browser and release-layer
counts. Extracted offline preflight exits 0 with plan_ready=false, no selected
write ranges and installation_authorized=false. Python 3.8 AST grammar and Bash
syntax pass on Linux; this is not native High Sierra execution.

The first draft package's frozen guide check recorded 82 PASS/1 FAIL because
the new guide abbreviated the future install command and omitted the historical
H1 label. Only documentation generation was corrected; final firmware bytes and
test expectations remain unchanged. A first invocation with symbolic HEAD was
rejected before construction; the required full packaging commit was then used.
Original failed receipts/draft archives remain local; only the verified final ZIP
is published. Final package receipts are linked in
[package identity](dashboard-cleanup-package.json),
[83 package checks](dashboard-cleanup-package-checks.json),
[38 installer mocks](dashboard-cleanup-installer-checks.json),
[44 semantic checks](dashboard-cleanup-package-semantic-checks.json), and
[extracted offline preflight](dashboard-cleanup-offline-preflight.json).
The ZIP's firmware-report.md is the packaging-source checkpoint report; these
subsequent packaging/publication results are supplied alongside it in the repository.
