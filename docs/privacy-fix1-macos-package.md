# Privacy Fix 1 — High Sierra owner-review package

**Software verification PASS; physical candidate acceptance remains unverified.**
No firmware was rebuilt, hardware accessed, payload executed, flashed or updated
over OTA during this packaging task. No new HID/scripting capability is added.

The packaging source commit is `48ed7c9dc694316d8f1d194c0bbf4efe492186f9`.
It descends from source checkpoint `93cc8d1a7b162bdda91e239d840a3eee8a70c51c`
and target integration `0380d1508b8f761e30a6a1fb63f67c2850cbc84a`.
The final artifact commit adds the ZIP and verification receipts separately.

## Exact immutable artifacts

[Public ZIP](../downloads/evilduck-privacy-fix1-h1-macos-review-v1.zip):
**2,471,979 bytes**, SHA-256:

```text
6fff7825d25df3288beb8975abbd56f464bf5ccc81a5c680fa6f5ccf7b2940cf
```

| Member | Bytes | SHA-256 |
|---|---:|---|
| `application.bin` | 1,415,968 | `9e4d3b615d78e87521882a35c4b43ce66403168a15b6b39bcebc81bb32a6b96e` |
| `rollback-application.bin` | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

The application is the existing clean privacy image. The preserved ELF SHA-256 is
`af7887ceccfe2694738c173c76b3c211b78cb0c7b667d8d7d942a1b0ef317f6e`;
the ELF is not included in the app-only ZIP. The rollback is the older accepted
source/text-v2 image **without Privacy Fix 1**, not a privacy-patched recovery.
Rollback replaces application code, not settings or filesystem snapshots.

The dashboard still displays `ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1`.
That string does not distinguish this privacy build. Use the exact application
hash, [package manifest](privacy-fix1-package-manifest.json) and actual installer
comparison evidence when a future physical operation is separately approved.
No installed-image proof or bit-for-bit cross-build reproducibility is claimed.

## Fresh release verification

The applicable full frozen H1 verifier chain ran against the exact existing
ELF/BIN. Only final live-candidate expected hashes for `cli.cpp`, `webserver.cpp`
and `webfiles.h` were adapted to the reviewed privacy manifest. No historical
verifier or firmware source was edited. A lookup containing only those three
filenames preserves the original expected value for every other source.

Six executable verifier units retained all **190 static Assert nodes**; these
are static audit counts, not a claim of 190 separately executed test cases.
Eight candidate-hash comparison sites were adapted. Historical source-pin/before,
compiled-copy, SDK/core, selector, startup, NVS, USB and linked-code predicates
remain executable. Fresh checks covered the keyboard/lock-feedback, preprocessing,
text/restart/timeout, H1 decoder, right modifiers and STOP/cleanup disassembly
requirements. The execution audit records generated AST identities and each
adapted expression. The independent privacy input/header/object binding passed
both before and after this chain, preserving the exact 201-file, 3/198 composition.

The fresh closure records 284 linked-input entries, three response files,
13 linker scripts, 177 SDK archive pins and 88 compiled-source-copy checks.
Three focused adapter-policy unit groups also passed. See
[release-check evidence](privacy-fix1-release-checks.json); the full exact receipt
is the ZIP's `build-receipt.json`, SHA-256
`77b2787b0f72d92b0a8573da57419ccc362106ba0d7330e5c0da00efa95da908`.

## Fresh package checks

| Executed suite | PASS | FAIL |
|---|---:|---:|
| Unchanged historical H1 package checks | 83 | 0 |
| Unchanged historical bound-installer mocks | 38 | 0 |
| Additional privacy-specific semantic checks | 36 | 0 |

Additional privacy cases rehash modified support metadata on disposable public
copies, so the semantic checks cannot pass merely because generic file integrity
fails first. They cover identities, false compatibility/rollback claims, full-chain
proof, three-file composition and consumed CPP/header/link binding. Original
package files remain unchanged. Device contents and esptool outcomes are simulated;
no dispatcher was used against a real device.

All 29 ZIP members were CRC/member/byte-checked, then extracted into a fresh
directory. The exact README command below exited 0 on Linux Python **3.12.14**,
returning integrity PASS, no selected write ranges, `plan_ready: false`,
`hardware_access: false` and `installation_authorized: false`. Python 3.8 syntax
checks and unchanged Bash launcher checks passed in the inherited suite.
**Native High Sierra/Python 3.8 execution was not performed in this environment.**
See [package results](privacy-fix1-package-results.json) for receipt hashes.

The prior 28 privacy cases / 736 assertions, 558 regressions / 23,901 assertions
and 12 embedded JavaScript groups / 221 assertions, plus their sanitizer/leak
results, were reused because application source is unchanged. They were not
newly executed during packaging. No fresh target sanitizer execution is claimed.

## First offline command on the Mac

Preserve the ZIP, verify its published checksum, extract to a new directory and
open Terminal in that directory. With an existing Python 3.8+ installation:

```bash
python3 preflight.py --directory .
```

This command reads package files only. The installer launcher's default `check`
instead reads hardware and is outside this initial offline step. Existing
High Sierra 10.13.6 / Bash 3.2 / esptool 4.12.0 interfaces are preserved; no
dependency download or installation is automatic.

The installer body is unchanged from H1 except the required generated preflight
hash binding. Both shell launchers are unchanged. Existing chip/security,
partition/OTA-state, fresh-identity, private-backup, explicit confirmation,
rounded application-sector and two-slot comparison guards remain. Bootloader,
table, NVS, OTA metadata, SPIFFS and coredump stay outside the installer write plan.
No automatic retry, reboot or payload Start is added.

## Owner acceptance and limits

[OWNER-CHECK source](privacy-fix1-package-owner-check.md) requests only narrowly
scoped future checks: blank secret-replacement display/readback, unrelated saves
retaining credentials and optional `settings` output on an independently identified
candidate. It avoids credentials in shell commands, logs and screenshots, warns
that older firmware can disclose secrets, and labels direct empty-HTTP behavior
as software-tested rather than physically exercised by the UI.

Intentional web-password replacement requires reauthentication; settings saves
remain non-atomic. Query-password authentication, session storage and other
separate privacy findings are unchanged. The four scoped right-modifier passes
and three planned lock-wait groups remain closed; historical fixture files are
retained for provenance, with no repeat campaign requested.

H1 stays opt-in/experimental and canonical Hak5 encoding unresolved. This is an
owner-review candidate, not a hardware-validated release. Existing releases,
rollback bytes and private backups remain unchanged. Publication is confined to
the isolated review branch and new ZIP path; the final delivery reports the
commit-pinned download and remote-ref comparison after publication.
