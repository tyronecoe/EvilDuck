# H1 inherited lock-wait physical acceptance closeout

**Three planned groups: scoped owner-operated PASS on Intel Mac / macOS High Sierra 10.13.6.** The owner handoff reports four successful executions, **Requests 1, 2, 3 and 6**, in the inherited lock-wait test sequence. The reported terminal timestamps fall on October 31, 2026 UTC; an independent owner-local calendar date is not supplied. Request 4 remains inconclusive; Request 5 is unknown. This closes these specified acceptance groups on experimental H1, without promoting it to the default firmware.

Codex inspected the supplied `EvilDuck-H1-Lock-Wait-Physical-Results-Codex.txt` handoff, **not the original logs or photographs**, which were not supplied to this closeout session. The handoff says another assistant inspected them in the testing conversation. All observations and quoted observer fields below are attributed to that owner-supplied summary. No independent hardware operation or image inspection is claimed. [Structured evidence](h1-lock-wait-owner-closeout.json) records provenance, the handoff's hash and unknown fields.

## Group 1 — settings, RESET preservation and separate new-run default: PASS

**Request 1**, `wait-settings-reset.txt`: the owner reports exactly these three TextEdit lines:

```text
111default
222set
333reset
```

Dashboard: **Request 1 Completed**. Observer terminal: matched request 1, phase **0**, reason **1**, errorCode **0**. Reported terminal `observedUtc`: **2026-10-31T06:32:50.515856+00:00**. Evidence references: `wait-settings-reset-results.txt`, `IMG_EDD5B866-45AC-4CEC-AAA2-33BE0602DD13.jpeg`, `IMG_4140.jpeg`.

**Separate Request 2**, `wait-new-run-default.txt`: exactly **`444newrun`**, dashboard **Request 2 Completed** and matched terminal phase **0**, reason **1**, errorCode **0**. Reported terminal `observedUtc`: **2026-10-31T06:53:13.171802+00:00**. Evidence references: a pasted complete observer log (no filename supplied), `IMG_8D1211AB-8E70-4E4A-A4C9-BCCC956AEE6F.jpeg`, `IMG_4145.jpeg`.

These scoped observations cover default **5000**, assignment/readback **10000**, keyboard **RESET** preserving 10000 and a separately started execution returning to default 5000. Neither fixture contains a lock wait: `waitingObserved=false` is expected and is not an acceptance gap. The summary does not independently establish exact trailing-newline bytes; the visible text/line observations above are retained as reported.

## Group 2 — passive configured 1000 ms CAPS_CHANGE expiry: PASS

**Request 3**, `wait-passive-expiry.txt`: reported waiting capture had **routeBOwned=true**, Running phase **6**, CAPS_CHANGE command **5**, wait session **3** and wait start **2650676 ms**. The matching terminal had phase **0**, **Deadline reason 9**, **Timeout errorCode 26**, physical **line 3**, and **waitingObserved=true**. Reported terminal `observedUtc`: **2026-10-31T07:12:13.529944+00:00**.

Dashboard: **Request 3 Deadline at line 3, code 26**. The owner explicitly confirmed completely blank TextEdit and no unwanted marker. Evidence references: **`Wait-passive-expiry.txt` is an observer transcript**, despite its fixture-like name; it must not be confused with the lowercase `wait-passive-expiry.txt` fixture. Other references: `IMG_4146.jpeg` and the owner's blank-editor confirmation in chat.

This is the intended lock-wait deadline, distinct from the competing whole-run **Runtime reason 6 / Timeout 26**. It is a successful timeout-policy observation, not a firmware failure. Observer sample intervals do not measure a precise one-second expiry or USB timing.

## Group 3 — STOP during a correlated held-Shift wait: PASS

**Successful Request 6**, `wait-held-shift-stop.txt`: reported captures showed **routeBOwned=true**, **routeBWaiting=true**, Running phase **6**, CAPS_CHANGE command **5**, wait session **3** and wait start **5871019 ms**. The observer reported **MATCHED_CAPS_CHANGE_WAIT_OBSERVED** for request 6 and multiple waiting snapshots before cancellation. Their exact count and capture timestamps are not supplied here.

The matching terminal had phase **0**, **Cancelled reason 2**, errorCode **0** and **waitingObserved=true**. Reported terminal `observedUtc`: **2026-10-31T08:05:57.122465+00:00**. Dashboard: **Request 6 Cancelled**. The owner explicitly confirmed TextEdit remained blank until manually typing **`abc`**, which appeared normally in lowercase. Evidence references: `Evil_test.txt`, `IMG_4149.jpeg` and owner confirmations in the testing chat.

**Earlier Request 4 remains INCONCLUSIVE.** Its transcript/dashboard reportedly show cancellation with error 0, but every supplied snapshot had **routeBWaiting=false**, and the terminal had **waitingObserved=false**. Those observations do not establish the intended waiting or held-Shift interval. References: `Mac-test.txt`, `IMG_4148.jpeg`. It is neither a successful instance of this test nor a demonstrated firmware failure.

**Request 5 remains UNKNOWN.** No evidence was supplied; its behavior or even a particular execution must not be inferred from later numbering.

## Keep the two H1 milestones distinct

The identifiers above belong only to this inherited lock-wait sequence. Its successful **Request 2** must not overwrite the separate earlier H1 milestone's **inconclusive Request 2**, and successful lock-wait **Request 6** must not fill the earlier milestone's **unknown successful STOP request ID**. The [earlier four-check H1 closeout](inject-var-h1-owner-test-closeout.md), commit `29cbfae7974abccf513c6d7ff1b7faa5a3fc58c6`, remains closed and unchanged.

The reviewed acceptance contract and original fixtures remain in [the acceptance sheet](h1-lock-wait-acceptance.md) and [the pinned kit source directory](https://github.com/tyronecoe/EvilDuck/tree/b28f692bb255a44345f3b757b2324983863cb36e/tests/h1_lock_wait). These reported results certify only the three specified groups on H1, not the separate older `ROUTEB-LOCK-WAIT-TIMEOUT-v1` binary or all nine physical wait variants.

## Artifact identity and evidence limits

The handoff reports the full observer build ID **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**. The tested kit is bound to tools commit `c7531e2792e1f396ba07fc9c69313a21ae9d9949`; kit report commit `b28f692bb255a44345f3b757b2324983863cb36e`; downloadable ZIP commit `4575a23f02c4a0e56b9a25d22c296f676990b642`.

| Preserved artifact | Bytes | SHA-256 |
|---|---:|---|
| `evilduck-h1-inherited-lock-wait-high-sierra-v1.zip` | 24,304 | `faf26f64212fad199e4f34b822f9ea4d684da99540ce2d5c3d50d35932d56211` |
| Intended H1 application | 1,414,080 | `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd` |
| Mandatory accepted source/text-v2 rollback | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

The original H1 application package retains both exact images; they are not included in the helper kit or rebuilt by this closeout. Offline artifact hashes and a full build-name check are **not independent device-image readbacks**. These trials provide no new installation-comparison receipt, source-file readback hash or complete boot-marker correlation. Wait session **3** is not proof of complete boot continuity. Reported UTC values are observer-log timestamps, not independently verified device-clock times. Other unsupplied identifiers and diagnostics remain unknown.

Idle terminal snapshots with the stated reason/error values are scoped observations. They do not establish universal absence of faults/quarantine, global host-key release or USB endpoint-retirement guarantees. No precise timing, arbitrary host/layout compatibility, all-nine-variants certification or general recovery guarantee is inferred.

**H1 remains experimental; canonical Hak5 INJECT_VAR numeric encoding remains UNRESOLVED.** This lock-wait milestone supplies no genuine DS3 runtime encoding reference. Default builders, canonical compatibility inventories and the exact source/text-v2 rollback requirement remain unchanged.

## Documentation-only verification and publication

[Fresh verification](h1-lock-wait-owner-verification.json) records JSON/evidence consistency, links, artifact identities, allowed scope and historical file/mode preservation. The original **46 observer / 31 package PASS** receipts in [kit test evidence](h1-lock-wait-test-results.json) remain historical software evidence; neither suite was rerun here. Firmware/build/native/sanitizer receipts were also reused without a test sweep or new success claims.

Only new closeout documentation/receipts and a dated link appended to the repository kit README are permitted. Its original text remains a byte-identical prefix, and the published ZIP's enclosed README, frozen reports, logs/screenshots, tests, observers, fixtures, profiles, application/kit packages and earlier refs remain unchanged. Publication/download and ref verification are recorded after push.

**GO: close these three scoped owner-operated inherited lock-wait acceptance groups on H1.** No new firmware, package, installation, hardware operation or physical repetition is requested or performed. Further development or physical testing requires a separate instruction.
