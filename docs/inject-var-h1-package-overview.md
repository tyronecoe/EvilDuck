# H1 experimental Mac package — review only

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING.** This package prepares an owner-reviewable High Sierra test of an EvilDuck convention. It does not establish Hak5 runtime compatibility and does not authorize installation, application boot or payload execution. No physical H1 trial has been supplied.

The candidate is **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**, an existing verified application image of **1,414,080 bytes**, SHA-256 `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd`. It was built with `EVILDUCK_EXPERIMENTAL_INJECT_VAR_H1=1`. Packaging reuses those bytes; it does not rebuild firmware. Its source-stage review commit is `a15b8e218935b2c6a69b71eeac3aaf378c3c0c03`.

H1 interprets a scalar as `(modifier << 8) | HID_usage` within a checked US printable subset: modifier zero or left Shift only, with unsupported pairs rejected. An ordinary variable is required by `INJECT_VAR $name`. Copying stores the scalar; repeated injection reuses it. The six experimental random-keycode getters select once per evaluated reference. These are practical EvilDuck policies, not an independently observed Hak5 numeric contract. Genuine DS3 runtime encoding remains unresolved.

The exact accepted rollback is **ROUTEB-SOURCE-TEXT-PORTABILITY-v2**, **1,413,200 bytes**, SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. Both files are standalone application images, not merged flash/recovery images. Current physical board firmware is **unknown to this package**; the rollback identity describes the accepted recovery target, not a claim that it is currently installed.

The candidate also includes the intervening software-tested bounded lock-wait change, `$_EVILDUCK_LOCK_TIMEOUT`. That inherited delta has not received new owner physical acceptance. This release does not silently promote it to accepted behavior. The accepted v2 application does not implement H1 or this configurable timeout.

Start with the fully offline command from the unpacked package directory:

```bash
python3 preflight.py --directory .
```

Read **INSTALL-MAC.md**, **ROLLBACK-MAC.md** and **OWNER-CHECK.md**. The launcher’s default `check` action is a **device-reading operation**, not this offline check. Offline success means package integrity only; `installed_metadata=NOT_SUPPLIED` and `plan_ready=false` are expected until separately approved current device evidence exists.

Keep all accepted packages and existing backups untouched. No private backups, credentials, owner scripts or NVS data are included. The package has no automatic normal-operation transition, script submission or test replay. EDR1, descriptors, partition geometry and the accepted firmware artifacts remain unchanged. The general-purpose application retains its existing services and storage behavior; this is not a quiescent/read-only firmware profile. No broader key-release, USB retirement, layout or physical compatibility guarantee is made.

`firmware-report.md` and `test-results.json` are preserved **historical source-stage** evidence. Statements there that no package had been produced describe that earlier stage; they are not the publication status of this new ZIP. The 522 native passes and sanitizer receipts are reused evidence, not tests rerun by packaging. Fresh package/mock-installer results are reported separately in the repository packaging report.

## Later owner-test status — October 30, 2026; closeout October 31

The owner has since reported **four scoped physical H1 passes on High Sierra 10.13.6**. See the [later owner-test closeout](inject-var-h1-owner-test-closeout.md) and [structured evidence](inject-var-h1-owner-test-closeout.json) for the successful trials, earlier inconclusive STOP attempt and missing identifiers. This updates the historical pending-test context above without claiming independent Codex hardware/image inspection, a full application readback or genuine Hak5 encoding compatibility. H1 remains experimental; default profiles and the required source/text-v2 `cf42dea0…ba81f02` rollback remain unchanged. The published ZIP and its enclosed overview are not modified.
