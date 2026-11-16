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
