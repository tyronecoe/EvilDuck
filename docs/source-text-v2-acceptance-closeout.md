# Source/text v2 acceptance closeout

**ROUTEB-SOURCE-TEXT-PORTABILITY-v2 is the latest owner-accepted baseline on macOS High Sierra 10.13.6.** The owner reports four scoped physical passes and the expected dashboard build ID. Codex has not operated the board or independently inspected the original physical screenshots, script readback files or serial transcript for these trials.

This documentation-only closeout follows release `789815a70544e0b8f3967f8ab68d9f4f1f4e5f62`. It supersedes older *current-status descriptions* without changing historical reports, builders, packages or evidence. See the [accepted-baseline record](source-text-v2-accepted-baseline.json), [unaltered supplied handoff](source-text-v2-acceptance-handoff.txt), [current compatibility inventory](routeb-current-compatibility.md) and [next-release recommendation](routeb-next-release-recommendation.md).

## Scoped owner-operated results

| Trial | Classification | Supplied observations |
|---|---|---|
| Terminated aliases | OWNER-REPORTED PASS | Includes the planned ordinary literal closing-token and multiline-block comparisons. Representative workflows, not all fourteen physical alias variants. |
| Restart and held Shift | OWNER-REPORTED PASS | Restart, held-Shift recovery and STOP passed. |
| Malformed source | OWNER-REPORTED PASS | Rejection passed. Request, physical line and diagnostic code were not supplied. |
| Leading BOM via stored-file Route B | OWNER-REPORTED PASS | All **30 source bytes**, including initial **EF BB BF**, survived upload/download comparison. Control + J submitted the explicit Route B command; console printed **Queued Route B**; TextEdit displayed exactly one **111bom**; dashboard reported **Request 1: Completed**. |

Physical test date/time, boot/session identifiers, original receipt/screenshot/transcript associations, BOM fixture filename and readback SHA-256 remain **unknown**. Only the BOM trial's request ID is supplied. Do not borrow identifiers from older releases or calculate an expected fixture hash and present it as an observed readback. The handoff itself is preserved and hashed; it is not a substitute for the absent original physical artifacts.

The BOM observation covers the complete reported HTTP save/readback → stored source → explicit Route B → TextEdit workflow. It is more specific than editor paste or direct compiler testing. Script-source readback is distinct from an installed application readback; no new application readback is claimed.

These observations accept the exercised configuration. They do not establish exhaustive DuckyScript 3.0 compatibility, every delimiter edge, arbitrary Unicode, universal layouts, precise timing, general USB/host-state or key-release guarantees, or Windows compatibility. Missing physical identifiers do not require repeating the successful acceptance campaign merely to begin the approved documentation work.

## Frozen artifact and future rollback

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Accepted v2 `application.bin` | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |
| Unchanged published v2 ZIP | 2,395,166 | `589c277b48838777a9333304e29ba7c1052a0a022558fa5f2bf0a1ffe7d2f1d0` |
| Older restart application already included as rollback in v2 | 1,412,688 | `1d4ea6394306885b832619adb3436eaeeccc0a67ce8b73e1f20dd0f9c7d0a060` |

The accepted application's exact bytes are available in the [commit-pinned public ZIP](https://raw.githubusercontent.com/tyronecoe/EvilDuck/d241a1da070bc7bd447904cd6b762f73385487c4/downloads/evilduck-routeb-source-text-portability-macos-v2.zip). This closeout independently rehashed the repository ZIP, downloaded that URL, compared the complete bytes and checked the contained application, older rollback and partition table. It does **not** manufacture rollback by rebuilding the accepted source.

**Every future candidate package must bind its rollback to the accepted v2 application above.** Do not instead select `rollback-application.bin` from the existing v2 ZIP: that member remains the older restart image. Do not regenerate v2 to replace its historical rollback. Existing historical builders retain their original pins; a future approved candidate needs a separate additive package binding.

This is a standalone application, not a merged/full-flash recovery image. Its build receipt targets ESP32-S3, 16 MiB flash, the existing custom geometry, PSRAM disabled and the established USB-OTG/TinyUSB/CDC profile. The expected partition table remains SHA-256 `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`. Application-only recovery still depends on separately verified chip/security, installed partition/OTA/image compatibility and recovery access. It does not restore NVS or filesystem contents. Original firmware is **OWNER CONFIRMED: AVAILABLE EXTERNALLY**, not an availability blocker or proof of physical recovery.

## High Sierra / GNU Screen observation

On the owner's tested 115200-baud High Sierra/GNU Screen setup, **Control + J** submitted the command when ordinary Return appeared ineffective. The hash-verified composed `EvilDuckS3/cli.cpp:342–344` recognizes explicit `routeb ` and prints `Queued Route B` on accepted admission; `:373–380` ignores CR and submits on LF. This is consistent with the workaround but does not establish Screen's Return configuration or prove a firmware defect. No console parsing change is proposed.

For a later separately approved connection/trial:

1. Rediscover the current ports using `ls /dev/cu.usbmodem*`; the suffix can change after reconnect/reset. No match means stop and identify the connection rather than reuse an old suffix. Verify the current EvilDuck device/port; a filename alone is not identity proof.
2. Open the verified current port at **115200** with the existing Screen procedure. A command template is `screen /dev/cu.usbmodemCURRENT 115200`; replace the placeholder with the freshly verified path.
3. Enter the intended `routeb <actual-stored-fixture-name>` once. On this tested setup use **Control + J once** to submit, then correlate the assigned dashboard request and completion. Do not send Return followed by repeated submissions or assume another engine path is equivalent.
4. Preserve available output/status with its actual identifiers. Reconnect only deliberately; rediscover the port afterward. These instructions do not authorize a new physical trial or replay.

## Verification and scope

[Fresh verification receipt](source-text-v2-closeout-verification.json) distinguishes read-only checks from historical test results. The current composed source tree was checked against all **201** files in the v2 build receipt. All **2,156** baseline repository files/modes and **235** frozen Stage26 files were checked unchanged. The public ZIP was downloaded and verified again. Documentation JSON, relative links and source anchors are checked without a firmware build.

Historical v2 receipts remain **457 native PASS / 0 FAIL / 17,612 assertions**, **46 package checks** and **38 mock-installer checks**, with recorded ASan/UBSan/leak results. Those suites were **not rerun** for this documentation-only closeout; they are not new results. Historical classifications and the documented V14 provenance correction remain untouched.

Reproduce the key read-only checks from the repository root:

```bash
python3 tests/stage28h/verify_freeze.py
python3 - <<'PY'
import hashlib, json, os, pathlib, subprocess, zipfile
root = pathlib.Path('.')
baseline = '789815a70544e0b8f3967f8ab68d9f4f1f4e5f62'
tree = subprocess.check_output(['git', 'ls-tree', '-r', '-z', baseline])
count = 0
for entry in tree.split(b'\0'):
    if not entry:
        continue
    metadata, name = entry.split(b'\t', 1)
    mode, kind, oid = metadata.decode().split()
    path = root / os.fsdecode(name)
    assert kind == 'blob'
    contents = os.fsencode(os.readlink(path)) if mode == '120000' else path.read_bytes()
    actual = hashlib.sha1(('blob %d\0' % len(contents)).encode() + contents).hexdigest()
    actual_mode = '120000' if path.is_symlink() else '100755' if path.stat().st_mode & 0o111 else '100644'
    assert actual == oid and actual_mode == mode, str(path)
    count += 1
assert count == 2156
record = json.loads((root / 'docs/source-text-v2-accepted-baseline.json').read_text())
package = root / record['package']['file']
data = package.read_bytes()
assert len(data) == record['package']['bytes']
assert hashlib.sha256(data).hexdigest() == record['package']['sha256']
with zipfile.ZipFile(package) as archive:
    assert archive.testzip() is None
    application = archive.read('application.bin')
assert len(application) == record['application']['bytes']
assert hashlib.sha256(application).hexdigest() == record['application']['sha256']
handoff = record['owner_evidence']['handoff']
assert hashlib.sha256((root / handoff['preserved_file']).read_bytes()).hexdigest() == handoff['sha256']
print('PASS 2156 baseline files/modes, accepted artifact and preserved owner handoff')
PY
```

The source receipt plus named composition patches provide public source identity; the local generated tree is not assumed to exist on every reviewer's machine. No re-generation or build is required simply to review acceptance. The [publication receipt](source-text-v2-closeout-publication.json) records the documentation commit and before/after remote refs. Only the new documentation branch is published; no previous ref is moved.

**GO:** accept the scoped owner results, preserve the exact release bytes, and review the next-release proposal. **Not authorized:** implementing that proposal, firmware builds, new installation packages, hardware access, HID execution, flashing, OTA, settings resets or automatic execution. No such actions occurred during this closeout.
