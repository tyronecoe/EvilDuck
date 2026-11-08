# DEFINE labels: short owner check

**REVIEW CANDIDATE — NOT INSTALLED — DEFINE HARDWARE ACCEPTANCE PENDING.**

Candidate: `ROUTEB-DEFINE-LABELS-H1-v1`. See the
[release report](define-labels-release-delivery.md) for exact application/ZIP
identities and verification. The latest owner-reported installed firmware is
the DEL candidate; its scoped installation/input observations are preserved in
[the closeout](del-alias-owner-closeout.md). These are new-feature checks, not a
request to repeat DEL, H1, lock-wait or earlier accepted milestones.

Download and verify the candidate ZIP, keep EvilDuck unplugged, extract into a
new folder, and run the existing offline checker from that folder:

```bash
python3 preflight.py --directory .
```

Expect integrity PASS, no write ranges, `plan_ready=false`, and no hardware or
installation authorization. Use the unchanged INSTALL-MAC.md/ROLLBACK-MAC.md
inside the kit for any separately owner-operated physical installation. Do not
invent or reuse a stale USB port suffix; retain existing backup safeguards.

For a later authorized owner check on High Sierra 10.13.6, confirm the full
running candidate build ID. Use blank plain-text TextEdit, the US input source
and Caps Lock off. Submit once through authenticated Route B on the iPhone and
focus the intended Mac document during the five-second delay. Use a separate
blank document for each fixture:

1. [D01: official 27-byte label](define-labels-owner-fixtures/D01_DEFINE_27.txt)
   must type exactly **`DEFINE27OK` followed by one newline**, with the matching
   request Completed.
2. [D02: 31-byte boundary](define-labels-owner-fixtures/D02_DEFINE_31.txt)
   must type exactly **`DEFINE31OK` followed by one newline**, with the matching
   request Completed.
3. [D03: rejected 32-byte label](define-labels-owner-fixtures/D03_DEFINE_32_Rejected.txt)
   must compile-reject at **physical line 1, code 6**, leaving TextEdit blank.
   No delay or STRING may execute before retained-source validation succeeds.

The accepted limit is 31 bytes excluding NUL, including `#` when present. These
fixtures only substitute harmless constant text; they do not run a shell, query
the host, access credentials, collect input or probe the OS. No fixture was
physically executed during development or publication.

Record the full build ID, actual request ID/terminal status and unedited visible
output separately. Matching terminal status plus correct visible output defines
PASS; HTTP submission alone does not. Leave missing session/receipt fields
unknown. Preserve unexpected or ambiguous results, use STOP if needed, and do
not automatically retry or repair text before recording it.

The exact source/text-v2 rollback remains 1,413,200 bytes, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It is older standalone application recovery without later privacy/dashboard
repairs, not a full-device/filesystem restore. Existing published kits and
private backups remain unchanged. No hardware access, flashing, OTA or automatic
payload execution is part of this development/publication task.
