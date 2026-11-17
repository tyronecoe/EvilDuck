# DEFINE H1 physical acceptance evidence closeout

## Owner-reported Intel Mac / High Sierra 10.13.6 observations

Provenance: owner narrative supplied in the closeout request, not Codex-executed
hardware tests. The DS01–DS04 screenshots are not available in this environment;
direct screenshot verification is PENDING. Test date/time and exact uploaded
script bytes were not supplied. Scripts below preserve the supplied visible text.
The owner reports the firmware installed and the captured build ID as
ROUTEB-DEFINE-STATEMENTS-H1-v1. This is not installed-image byte readback or an
independently verified installation receipt. Earlier NOT INSTALLED / NOT PERFORMED
statements below describe the original package stage, not the later owner report.

| Case | Owner observation | Closeout classification |
| --- | --- | --- |
| DS01 statement-valued DEFINE | TextEdit displayed ROUTEB_DEFINE_PASS once; Request 1: Completed; no active diagnostics; build-ID capture confirmed ROUTEB-DEFINE-STATEMENTS-H1-v1 | Owner-reported PASS |
| DS02 generated DELAY cancellation | Request 2: Cancelled; TextEdit blank; no active diagnostics | Owner-reported PASS, conditional on confirming the observation period after STOP extended past the original generated delay |
| DS03 recovery | TextEdit displayed recovery_ok once; Request 1: Completed; no active diagnostics | Owner-reported PASS |
| DS04 unsupported DEFINE | Request 2: Compile failure; diagnostic line 4, code 14; TextEdit blank; no active diagnostics afterward | Owner-reported PASS for rejection/no visible text ONLY; diagnostic line mapping unresolved |

Request numbers are reproduced exactly. They do not establish a continuous
request sequence or a numbering defect. No exact STOP latency, report bytes,
zero cleanup reports, internal HID release, or general host delivery is inferred.

### Supplied scripts

DS01:

```text
DELAY 5000
DEFINE #STEP $count = ($count + 1)
DEFINE #MARK STRINGLN ROUTEB_DEFINE_PASS
VAR $count = 0
#STEP
IF ($count == 1) THEN
#MARK
END_IF
```

DS02:

```text
DELAY 5000
DEFINE #WAIT DELAY 10000
#WAIT
STRINGLN UNEXPECTED
```

DS03:

```text
DELAY 5000
STRINGLN recovery_ok
```

DS04:

```text
DELAY 5000
DEFINE #BAD VAR $x = 1
#BAD
```

### DS04 read-only diagnostic reconciliation

The supplied script has three visible lines; the owner reports line 4. The
original acceptance instructions below expect invocation line 3. Neither is
silently changed. The merged [DEFINE overlay](../../tests/define_statements/application.patch)
rejects generated declarations with ErrorCode::Unsupported; the composed core.h
enumeration assigns Unsupported code 14. In the authenticated candidate core.cpp,
Compiler::fail stores line_ without adding an offset, line_ starts at 1, and the
Line phase increments it only after successful line processing. adapter.cpp copies
compiler_.error() into diagnostic_. These inspected paths do not establish why
the dashboard displayed 4. Exact submitted bytes (including possible blank lines),
raw diagnostic response and screenshot are unavailable. No cause is assigned;
end-to-end line mapping is NOT VALIDATED. No firmware or test was changed/run.

### Distinct identities and existing evidence

- Authoritative branch: routeb-admission-diagnostics-v1; inspected remote HEAD
  and PR #8 merge: 8515c6d6a8f04becc9c8efd4779c9d5aef4b23c4.
- Firmware build ID: ROUTEB-DEFINE-STATEMENTS-H1-v1; firmware source:
  de683669135fe5ccc5922f9883709194400672e5.
- Verifier preservation: 5a5894effe44bdacb79f1c17f594e156cff20456;
  packaging source: 4490d6c46dc2bd72bd464939f6c6d3af37c780b2;
  publication: 717957b6120c17770b57c12a21bb759994cc4a28.
- Application: 1,451,184 bytes; SHA-256
  524805fbde1af49b908b156e0eb50de48393b8e2810efcf0eaddba931408012e.
- ELF SHA-256: cd82758717bf0e6e78aa8a582dff7b01de99ac14a62923b12cd104de8c56f490.
- [Original Mac ZIP](../../downloads/evilduck-routeb-define-statements-h1-v1-independent-owner-review-v1.zip):
  5,531,756 bytes; SHA-256
  385dc473abc5ada4360ea6ffa3746ef51b78b622db919a0480971ab7db079d4c.
- [Working DEFINE return](RETURN-WORKING.md): kit SHA-256
  b91946bec818616f35a469edd6c2efa525eea01276d238b42ed1b26dea3558ed;
  application 167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30.
- [Older source/text-v2 rollback](ROLLBACK-MAC.md): application SHA-256
  cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02.
- Admission-diagnostics predecessor package SHA-256:
  05fdff0cdb7a0d4336f8dc219c3a501cc7349c9200f95c2f54a36bb9cccffd81;
  see [historical download](../admission-diagnostics-download.md).
- Private transfer commit c164712d8990c5d45772268d416ff1e5b8f61548 identifies
  evidence transport, not firmware. Original engineering archive: 898942569 bytes;
  SHA-256 5a4836a05949dd824a08f240e4102c61b1e0c0c20d2d22b98ea850d4c41c9a87.
  Owner subsequently reported restore PASS and checksum OK on the Mac in this
  conversation. The temporary transfer branch was subsequently deleted by explicit
  owner request in earlier work; no deletion or private publication occurs here.

Repository/package facts were inspected and existing ZIP/BIN/ELF/archive hashes
rechecked during closeout. Existing receipts remain unchanged:
`/workspace/artifacts/DEFINE-STATEMENTS-H1-v1-PACKAGING-REPORT/summary.json`,
`/workspace/artifacts/DEFINE-CANDIDATE-INDEPENDENT-v1-PROVENANCE-v2/summary.json`,
`/workspace/artifacts/DEFINE-PRIVATE-GIT-TRANSFER-RECEIPT/summary.json`.
These are workspace locations, not promises of permanent links. Their original
stage-specific PENDING/NOT INSTALLED fields are not rewritten. Later Mac restore
and branch-deletion outcomes are owner/conversation provenance, distinct from
those original receipts. The archived evidence predates these new physical reports.

Independent software/artifact gate PASS remains separate and was not rerun.
Original historical DEL gate remains BLOCKED / EXACT HISTORICAL INPUT UNAVAILABLE.
Runtime peak stack, complete HID-level validation, exact STOP latency, installed
byte identity, broad DS3 compatibility and overall firmware release acceptance
are NOT established. Firmware attempts remain ONE; auxiliary invocations TWO.

### Acceptance change log

Documentation-only closeout: added the four owner reports, conditional DS02 timing,
DS04 line discrepancy and distinct identity/evidence provenance. Retained the
original acceptance procedure and earlier stage evidence below unchanged. Next
engineering milestone: reconcile existing DS02 observation timing and DS04 submitted
bytes/raw diagnostic evidence before proposing any narrowly scoped follow-up.
No additional physical testing is initiated or authorized by this record.

---

## Original package-stage acceptance procedure (preserved)

# Harmless TextEdit acceptance — NOT PERFORMED

REVIEW CANDIDATE / NOT INSTALLED. These are later owner tests on macOS High Sierra
10.13.6 after separate installation/physical-test authorization. No test is run
by preflight or package creation. First keep EvilDuck UNPLUGGED and run only:

    python3 preflight.py --directory .

Before later tests, confirm the exact running build ID ROUTEB-DEFINE-STATEMENTS-H1-v1
and the installed-image evidence available to the owner. A displayed ID alone is
not installed-byte readback. Use blank local TextEdit in plain-text mode with no
shell, terminal or privileged application focused. Use fresh script filenames;
never overwrite owner files. Check fixture bytes with FIXTURE-SHA256.txt and
choose explicit Route B. Record actual request IDs and terminal status alongside
visible text. Do not run historical rm-* fixtures or use OS-detection payloads.

1. DS01_STATEMENTS.txt: during the initial five-second delay focus blank TextEdit.
   Expect exactly ROUTEB_DEFINE_PASS followed by newline, once, and Completed.
   It exercises a statement-valued assignment and inline text label.
2. DS02_DELAY_STOP.txt: after the first five seconds, request STOP during the
   generated ten-second DELAY. Expect terminal cancellation for that request,
   no text, and no UNEXPECTED output after waiting past the original delay.
   Neutral synchronization/cleanup reports may exist; do not infer failure from
   a nonzero report count or claim physical release from software counts.
3. DS03_RECOVERY.txt: run separately after confirmed idle; focus blank TextEdit
   during its five-second delay. Expect recovery_ok plus newline and Completed.
4. DS04_REJECT.txt: expect Unsupported (code 14), invocation line 3, terminal error
   before any text. Whole-script compilation must fail before even the first
   delay executes. Generated VAR declarations are intentionally unsupported.

Stop criteria: wrong running identity, unexpected text, stuck key/modifier,
missing/wrong request status, disconnect, quarantine/error or mismatched output.
Stop the active request; if status/release is ambiguous, do not resubmit it.
Do not perform automatic retries. Close the test document without saving if
needed. Disconnect EvilDuck if unexpected typing continues; use the physical
keyboard only after verifying normal local key state. Cooperative STOP/cleanup
software proof is not a guarantee of host-wide state or precise physical latency.

Recovery: preserve observations and private backups. Remain disconnected until
review. RETURN-WORKING.md identifies the distinct original working DEFINE kit;
ROLLBACK-MAC.md identifies the older source/text-v2 image. Only a later deliberate
owner operation through the appropriate unchanged guarded kit may install either.
No reset/erase-all/format, automatic rollback or speculative reflashing is advised.
Runtime peak stack, physical timing and general host compatibility remain unknown
until appropriate owner evidence exists. This sheet contains no physical PASS.
