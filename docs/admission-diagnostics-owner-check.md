# Admission diagnostics v1: review-only owner check

**NOT INSTALLED OR PHYSICALLY VERIFIED BY THIS DEVELOPMENT STAGE.**

Candidate identity: `ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1`. Software checks establish
request-owned diagnostics and zero mocked HID output for rejected requests;
they do not establish installed bytes or physical USB behavior. No broad
DEFINE/DEL/H1/lock-wait/LED campaign or OS probe is required for this correction.

First, keep EvilDuck unplugged and run from the extracted review folder:

```bash
python3 preflight.py --directory .
```

Require offline integrity PASS with no ready write plan, no selected write ranges,
and hardware/installation authorization false. Stop if any identity check fails.
Installation is a separate deliberate owner step using the original guarded
application-only procedure; this sheet does not perform or authorize it.

## Optional later focused observations

After a separately authorized installation, confirm the full running build ID.
Use a blank plain-text TextEdit document with the normal tested input source.
Do not launch a shell, host query, lock probe or helper payload.

1. A raw-byte invalid-encoding fixture on physical line 3 should fail before
   output with existing error code **2**, line **3**, and Capability reason.
   Use the package's byte fixture (valid UTF-8 C3 A9, outside Route B's ASCII
   subset), the existing authenticated `POST /script` name/content save and
   `GET /script?s=...` readback, then explicit Route B launch. Require matching
   readback bytes/hash first. The separate `/upload` route is disabled; do not
   use it. Editor paste is not a byte-preserving fixture transport. If the
   existing save path refuses the bytes, record that boundary and stop this
   observation; do not bypass it or change firmware validation.
2. A subsequent independent valid request can use the benign source below. Expect
   `ADMISSION_OK` plus one newline, matching successful request status and no
   retained code 2/line 3. Focus the intended TextEdit document during the delay.

```ducky
DELAY 5000
STRINGLN ADMISSION_OK
```

These optional observations do not replace the exhaustive mocked byte/ownership
checks. No report of a physical pass is assumed; unavailable request/session
identifiers stay unknown. STOP retains its existing injection-cleanup meaning.
Do not retry automatically or repair unexpected output before recording it.

## Recovery

The nested original working DEFINE kit restores application
`167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`.
Extract it separately, preflight unplugged and use its own guarded install action
if a later owner return is chosen. The outer rollback selects older source/text-v2
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`,
not DEFINE; it lacks later privacy/dashboard fixes. Preserve every private backup.
Rediscover the USB port after reconnecting; never assume a previous suffix.
