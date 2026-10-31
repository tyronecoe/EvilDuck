# H1 inherited lock-wait acceptance kit — review only

This is a **helper/fixture-only** kit for the inherited configurable lock-wait behavior on **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**. It contains no application binary, installer, firmware build, native LED helper or automatic execution mechanism. Preparing or downloading it grants no permission to operate the device. Physical use is a later owner-operated step after review.

The intended H1 application is **1,414,080 bytes**, SHA-256 `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd`. The mandatory accepted source/text-v2 rollback remains **1,413,200 bytes**, SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`. Those exact images remain in the preserved H1 application package; neither is included or rebuilt here. An exact full build-ID match checks the reported running build name, **not independently read-back application bytes**.

## First check — fully offline

After verifying the separately published ZIP SHA-256, unpack into a new folder and open Terminal in that folder. Keep the original ZIP unchanged. Run:

```bash
python3 validate_kit.py --directory .
```

This validates the kit's manifest, file inventory and hashes using local files only. It does not contact EvilDuck, inspect USB, request credentials, start a fixture or grant physical-test permission. Stop if the kit is rejected. Do not save logs or test output inside the kit folder; use a new Desktop location and preserve the original files.

Target interfaces: **macOS High Sierra 10.13.6**, **Bash 3.2**, **Python 3.8 stdlib**. No pySerial, compiler, third-party Python module or native LED executable is required. This kit does not download/install dependencies or alter user files automatically. Linux offline tests are not native Mac or hardware validation.

## Contents and intended use

Read **ACCEPTANCE.md** before any separately reviewed physical use. Four exact text fixtures make up three trial groups:

| File | Intended observation |
|---|---|
| `wait-settings-reset.txt` | Default 5000 ms, assignment/readback 10000 ms, RESET preserves 10000 ms; three expected text lines. |
| `wait-new-run-default.txt` | One separate deliberate new run returns to default 5000 ms; one expected text line. |
| `wait-passive-expiry.txt` | Passive 1000 ms CAPS_CHANGE expiry, blank TextEdit, correlated Deadline 9 / Timeout 26 / line 3. |
| `wait-held-shift-stop.txt` | Observe the actual request waiting under held Shift, one owner STOP, Cancelled, absent unwanted marker, scoped manual lowercase recovery. |

`observe_wait.py` is a GET-only observer bound to the **exact full H1 build ID** above. It authenticates via `X-Duck-Password`, checks execution idle, asks for the actual assigned request after a manual Start, and records only reviewed execution fields. It sends no Start, STOP, upload, settings write, LED or HID action. READY is an idle identity preflight result, **not permission to run a fixture**. Never use a clipped prefix or another firmware build to satisfy identity.

Socket-inactivity timeout is not a total network deadline. A slow response may exceed the observation window; late completed responses are rejected as evidence. **Control+C stops observation only, not the device script.** Keep the independent dashboard STOP control accessible. No automatic action or failed-request retry is performed.

For an optional **offline, mocked-only** observer regression run, use:

```bash
python3 test_observe_wait.py
```

This test harness performs no real network/device operations. Its result is software evidence, not physical acceptance. Keep any optional `--results` output outside the kit folder.

## Evidence and compatibility boundary

The [four completed H1 owner checks](https://github.com/tyronecoe/EvilDuck/blob/29cbfae7974abccf513c6d7ff1b7faa5a3fc58c6/docs/inject-var-h1-owner-test-closeout.md) remain closed as scoped owner-reported passes. Request2 remains the earlier inconclusive STOP attempt, and the successful H1 STOP request ID remains unknown. This kit does not request those tests again. These new observations concern the inherited `$_EVILDUCK_LOCK_TIMEOUT` **EvilDuck extension**, which those four H1 checks did not physically certify.

A successful future trial applies to this H1 binary and tested High Sierra setup. It cannot retroactively certify the separate `ROUTEB-LOCK-WAIT-TIMEOUT-v1` binary, establish genuine Hak5 numeric encoding, demonstrate universal key release or promote H1 to the accepted default. Do not reuse an older lock-wait installation receipt as H1 installation evidence. Unknown receipt, session and diagnostic fields stay unknown.

Preserve working firmware, rollback resources, original packages and private backups unchanged. No firmware modification, rebuild, flashing, OTA, settings reset, broad Caps investigation or repeated physical H1 trial is part of preparation. The new inherited lock-wait physical results remain **PENDING OWNER** until supplied.

Original preserved firmware/rollback resource (reference only, no new installation authorization): [commit-pinned H1 application package](https://raw.githubusercontent.com/tyronecoe/EvilDuck/0982baec1d2beda44b1db31aacd373b3f45c1121/downloads/evilduck-routeb-inject-var-h1-experimental-macos-v1.zip). Its ZIP SHA-256 remains `229da835898e6739e31e4a6c08dd1ee9b5d74ded0458c7a0d850c899f5d2c639`. This helper kit does not install, replace or include those images.

## Later owner acceptance — October 31, 2026

The owner has now reported **three scoped inherited lock-wait PASS groups on H1**, comprising successful Requests **1, 2, 3 and 6** on High Sierra 10.13.6. See the [later physical closeout](h1-lock-wait-owner-closeout.md) and [structured evidence](h1-lock-wait-owner-closeout.json). Request 4 remains inconclusive and Request 5 unknown. These IDs belong to the lock-wait sequence and do not change the separate earlier H1 milestone's identifiers. This later report updates the historical pending-owner context above; its original text and the ZIP's enclosed README remain unchanged. H1 stays experimental, canonical Hak5 encoding unresolved, and the exact source/text-v2 rollback mandatory. No new physical operation is authorized by this closeout.
