# DEL review: two TextEdit checks

**PUBLISHED FOR REVIEW - NOT INSTALLED - DEL HARDWARE ACCEPTANCE PENDING**

Candidate: `ROUTEB-DEL-ALIAS-H1-v1`, application SHA-256
`d1571be81619e464ee997d0ba8ebbf7e7b8a8b4252e4debc9d9144b9ebe6b379`.
The latest owner-recorded installed firmware remains
`ROUTEB-PREVIOUS-COMMAND-REPEAT-v1`, source checkpoint
`820a575a45e5a4f644921d663a650110667a6ab2`. Neither this page nor publication
establishes installation, a live-device readback or DEL hardware acceptance.

DEL is the candidate's alias for DELETE, **forward delete** (keyboard usage
0x4c). It deletes the character to the right of the caret. It is different from
the Mac keyboard's ordinary backward-delete key. The reviewed composition maps
both source spellings to the same existing key/report path.

## First: offline package review

Download the [unchanged review ZIP](../downloads/evilduck-routeb-del-alias-h1-macos-review-v1.zip?raw=true)
and verify the identity in the [download report](del-alias-review-download.md).
Keep EvilDuck unplugged, extract into a new folder, then run from that folder:

```bash
python3 preflight.py --directory .
```

Expect exit 0, integrity PASS, no write ranges, `plan_ready=false`, and
installation/hardware authorization false. Read the existing INSTALL-MAC.md and
ROLLBACK-MAC.md inside the ZIP. This delivery changes neither helper nor its
backup/rollback procedure. No installation or physical execution occurs in this
delivery task; later physical steps are separately owner-operated.

## Later owner-operated comparison

Use the Intel Mac running High Sierra 10.13.6. Prepare **two separate blank,
plain-text TextEdit documents**, with matching **US input** and **Caps Lock off**.
Use the authenticated Route B dashboard on the iPhone. Confirm and record the
actual full running build ID before testing. Keep passwords and private backup
contents out of the test record.

1. **D01 control:** load [D01_DELETE_Control.txt](del-alias-owner-fixtures/D01_DELETE_Control.txt),
   submit once through Route B, and focus the first blank Mac document during
   its five-second initial delay. It types `abc`, moves left once to between
   `b` and `c`, then uses DELETE. Expect **`ab`**, with no remaining `c`, and
   the matching request's successful Completed terminal status.
2. **D02 alias:** load [D02_DEL_Alias.txt](del-alias-owner-fixtures/D02_DEL_Alias.txt),
   submit once, and focus the second blank document during its five-second
   delay. The sequence differs only in using DEL. Expect the same **`ab`** and
   the matching request's successful Completed status.

The fixtures contain only:

```ducky
DELAY 5000
STRING abc
LEFTARROW
DELETE
```

D02 replaces only the final DELETE with DEL. No shell, network operation,
credential access, OS probe, held modifier or file operation is involved.
These fixtures were prepared and checked offline; they were not physically run.

Do not manually erase or repair output before recording it. For each trial,
record filename, full running build ID, actual request ID/terminal status and
visible output. PASS requires both the expected editing and the corresponding
successful terminal status. HTTP acceptance or device completion alone does not
prove what TextEdit received. Leave unavailable session/receipt fields unknown.

If focus was wrong, the result is ambiguous, or output/status disagree, stop and
preserve the observation; do not automatically retry. Dashboard STOP remains
available. No broad Caps, H1, lock-wait or G01-G09 retest campaign is requested.
The original ZIP's longer OWNER-CHECK.md remains unchanged as historical package
content; these two comparisons are the short owner procedure for this delivery.

## Recovery identity

The unchanged source/text-v2 rollback is 1,413,200 bytes, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It is an older standalone application without later privacy/dashboard/editor
repairs; it is not a complete-device/filesystem backup. Preserve all recovery
artifacts and use only the existing guarded rollback instructions if separately
undertaken. Publication does not authorize flashing, OTA or hardware access.
