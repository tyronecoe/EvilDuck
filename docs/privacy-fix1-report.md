# Privacy Fix 1 — local source and software verification

Implemented locally on `routeb-privacy-fix1`, based on the unchanged owner closeout
`a04e54309c9c73bae17ef23c48283828dfebc0ad`. No commit, push, target firmware build,
package or device operation was performed. The accepted installed firmware has
not been changed by this work.

## Source diff and behavior

[The reviewable source patch](../tests/privacy_fix1/application.patch) changes only
`cli.cpp`, `webserver.cpp` and `webfiles.h` in the actual composed right-modifier H1
tree. It is a new additive, hash-pinned layer over the historical H1 preparer;
historical patches, preparers, verifiers and source files remain unchanged.
[The source manifest](../tests/privacy_fix1/source-manifest.json) pins all 201
baseline files: three changed, 198 byte-identical. The default delta verifies all
201 files; its explicit native mode checks the three touched files because the
historical native harness substitutes platform headers. The native hook also
checks the unchanged keyboard, runtime, settings, coordinator and LED sources.

| Interface | New contract |
|---|---|
| Authenticated GET `/settings` | Omits `password` and `web_password`; returns boolean `password_configured` and `web_password_configured` instead. Other settings remain available. |
| POST `/settings` | Each omitted or empty password field independently preserves its existing value. A nonempty replacement is write-only and validated before any setter. There is no password-clear operation. |
| Replacement validation | AP: 8–63 bytes, with existing controlled-start rejection of the legacy default. Web: 1–3999 bytes. Both reject embedded NUL, CR and LF. These preserve the composed controlled-profile credential rules. |
| Settings page | Never populates saved passwords. Blank replacement fields are omitted from submissions. Labels explain blank means unchanged; successful saves clear replacement inputs, while unsuccessful saves retain them for owner review. |
| USB CLI `settings` | Reports only nonsecret configured indicators for passwords. |
| CLI settings writes | Both the explicit acknowledgment and optional public `parse(..., true)` echo omit setting values. Redaction applies to all settings writes, including malformed `set` input. Empty password replacements explicitly leave passwords unchanged without writing NVS. |

Authentication, request/lease ownership, STOP, keyboard reports, execution limits,
lock feedback, the fixed-message LED protocol and storage/USB safeguards are not
modified. H1 remains opt-in and experimental. Canonical Hak5 encoding remains
unresolved. No new firmware identity or deployable image is created by this
source-only layer; historical builders are not silently changed to select it.

## Fresh verification

| Executed verification | PASS | Unexpected FAIL | Assertions/checks |
|---|---:|---:|---:|
| New privacy native cases PF01–PF28 | 28 | 0 | 736 assertions |
| Existing composed regressions, including right modifiers, STOP, lock feedback and EDR1 | 558 | 0 | 23,901 assertions |
| Actual embedded settings JavaScript with mocked DOM/HTTP | 12 groups | 0 | 221 assertions |
| Inherited core edge probe | PASS | 0 | 2 checks, separate from native totals |

The native total is **586 cases / 24,637 assertions**. ASan, UBSan and leak detection
were enabled; all completed native cases had empty stderr. The unchanged baseline
UI was separately rejected for preloading a saved password by the new write-only
UI assertion. That is an intentional negative control, not a candidate failure.
Altered source input and repeated patch application were also rejected.

The new cases execute the actual composed settings/HTTP/CLI bodies. The recording
typed-NVS mock verifies both persisted values and reload through actual
`settings::load()`: unrelated successful and failed saves retain both passwords;
AP-only, web-only and combined replacements preserve the other field; blank and
omitted fields preserve values. Tests cover authentication refusal, valid limits,
invalid inputs before mutation, actual bounded serial handling, both public CLI
echo modes, failed opens/sets/commits and explicit error responses. Privacy cases
assert no HID output or execution request. All credentials are synthetic fixtures.

This does not execute ESP-IDF flash recovery, a native browser, High Sierra or
physical USB. The previous closeout's 36 integrity checks remain historical and
are not counted here. Two development setup errors occurred before any cases ran:
an unchanged header was not in native scratch, and the new test driver initially
omitted `nvs.h`. Both were corrected without changing production expectations;
their original logs remain in the scratch evidence directory. An initial negative
control verifier read stderr instead of the UI runner's structured stdout; its
corrected check requires the exact password-preloading failure.

See [machine-readable results](privacy-fix1-results.json) for commands' receipt
locations, hashes, tool versions, per-group UI results and development notes.
Full fresh native receipt: `/workspace/scratch/privacy-fix1/native-v3.json`.

Reproduce using a **fresh** output directory, with the existing pinned isolated
core available for read-only source checks:

```bash
python3 -B tests/privacy_fix1/run_tests.py \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --build-dir /workspace/scratch/privacy-fix1-native-reproduction \
  --results /workspace/scratch/privacy-fix1-native-reproduction.json
```

This invokes only host `g++` software-test compilation and Node; it does not invoke
Arduino/Xtensa compilation or produce firmware. Observed versions: GCC 14.2.0,
Node v24.19.0 and Python 3.12.14. The embedded script is tested with mocks; no new
claim of Safari/High Sierra physical verification is made.

## Preservation and remaining boundaries

All previously tracked repository files are unchanged relative to the closeout.
Local remote-tracking refs and tags match the initial snapshot; no remote server
ref query or push was performed. Only new privacy source/test/report files exist.
The existing public right-modifier ZIP is unchanged:
`9a3593735799d36d1db949c2982558a384dc5f6de43f2d3f804c4bfb15fc113e`.
Its rollback member was read and SHA-256 verified without extracting or rewriting:

- Bytes: **1,413,200**.
- SHA-256: **cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02**.

Settings persistence remains non-atomic. A failed explicit credential replacement
can leave RAM or a persisted prefix changed; error messages retain the existing
partial-persistence warning. This patch does not promise transaction rollback or
change unrelated validation sequencing. Changing the dashboard password requires
reauthentication with the new password; existing browser authentication storage
is not automatically migrated.

Query-password authentication, browser session storage, trace/RAM retention,
backup consent and other privacy-review findings are outside Fix 1 and remain
unchanged. No secure-erasure, TLS, device attestation or physical readiness claim
is made. The four accepted scoped owner reports and earlier lock-wait milestones
remain untouched; no new acceptance test or receipt checker is requested here.
