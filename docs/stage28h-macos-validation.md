# Stage28H — disconnected High Sierra host validation

Keep EvilDuck S3 UNPLUGGED throughout. This is a C++ program that checks synthetic bytes in
memory, not a DuckyScript payload delivered to the OS. Do not run any Arduino/upload/firmware
build tools. No USB enumeration, TextEdit automation, keyboard injection, owner scripts, private
backups, network test, downloads or installations are performed by the runner.

1. Transfer/unpack the reviewed stage28h-host-validation-kit source. In Terminal, manually change
   to the unpacked repository root (the folder containing language_preview, docs and tests):

```sh
cd "/path/to/unpacked/EvilDuck-stage28h-host-validation-kit"
```

2. Run ONE command in that root:

```sh
bash tests/stage28h/run_host_smoke.sh
```

The runner is written with Bash3.2-compatible syntax and BSD/POSIX essential utilities. Native
Apple clang++ is preferred when available; otherwise existing c++ can be selected. Optional CXX
is one compiler executable/path, not a command containing flags. No Python, Git history, Arduino,
SDK or package manager is needed for this smoke. No automatic install/update is attempted.
It verifies source files, compiler version and a C++17 compile/link/run probe; creates one private
mktemp directory; compiles approved mock files; compares the compiled manifest to repository JSON;
then executes the traces. Temp files are removed by a constrained cleanup trap. Existing files
are never deleted; no result file is silently written in your project.

3. Read the classification and exit status. Expected successful output includes platform/compiler,
   C++17 probe, manifest match,19 VECTOR lines (eight hex bytes each), and:

```text
PASS trace=repeated_transient_delay_retry reports=7 attempts=10 admissions=3 acks=3 delays=1 terminal=Completed
PASS trace=shared_owner_selective_release_drain reports=9 attempts=13 admissions=4 acks=4 delays=1 terminal=Completed
PASS trace=stale_zero_current_drain reports=3 attempts=5 admissions=1 acks=1 delays=0 terminal=Completed
PASS blocked_preflight cases=4 callbacks=0
PASS host-validation traces=3 blocked_cases=4 assertions=365
PASS runner: host-only mock validation; no hardware or OS input
```

These patterns come from newly executed Linux tests. They are expected on a compatible native
compiler, not an assertion that macOS has passed. Platform/version strings will differ.

| Result | Exit | Meaning |
|---|---:|---|
| PASS runner |0|All current fixture vectors, counters and terminal states matched locally|
| SKIP_ENVIRONMENT |77|Missing/nonexecutable compiler, failed version/C++17/SDK/probe-run or unavailable temp directory|
| FAIL fixture compile/link |Original compiler nonzero|Probe worked; fixture build failed; do not relabel as environment success|
| FAIL fixture execution |Original program nonzero|Actual runtime/assertion fault; report error text|
| FAIL missing source fixture |2|Wrong/incomplete source root; no test executable ran|
| FAIL manifest mismatch / missing receipt |1|Compiled expectations or receipt disagree; no PASS|
| Interrupted |130/143|Cancelled; not PASS; only unique temp directory cleanup|

You can inspect the immediately preceding command's status with `printf 'exit=%s\n' "$?"`.
Do not rerun with weaker expectations, disable warnings, install compilers automatically, or treat
an unexplained failure as SKIP. Older Apple sanitizer/linker support is deliberately not assumed.
GNU -no-pie/-fno-pie are never passed by the portable runner; GCC's preexisting misleading-indent
suppression is added only for the non-clang path. Apple uses common -Wall -Wextra -Werror only.

Optional anonymized transcript (new unique LOCAL file, no upload):

```sh
stage28h_transcript="$(mktemp "${TMPDIR:-/tmp}/evilduck28h-transcript.XXXXXX")"
bash tests/stage28h/run_host_smoke.sh > "$stage28h_transcript" 2>&1
stage28h_status=$?
cat "$stage28h_transcript"
printf 'Runner exit=%s\n' "$stage28h_status"
```

Keep the transcript locally. Before sharing text, review it for personal data. The runner replaces
project, home and created-temp prefixes and hides custom compiler parent paths. This was tested
with synthetic paths; it is not a universal guarantee for arbitrary compiler-emitted text. Share
only platform/compiler version, PASS/FAIL/SKIP, exit and relevant sanitized error/vector lines.
Do not share private backups, usernames, settings or credentials. Nothing uploads automatically.

A source ZIP lacks Git history. The235-file frozen-Git verifier needs immutable historical Git
objects and compatible Python, and is NOT part of this one-command smoke. Do not install Git/
Python or fetch history just to run the smoke. Full cloud regressions/target checks are documented
separately and are not required for the optional owner step.

## Troubleshooting

| Observation | Action / boundary |
|---|---|
| clang++ absent, nonexecutable or C++17/SDK probe fails |Record SKIP_ENVIRONMENT and version/error; no install required|
| Warning treated as error after probe |FAIL fixture build; preserve compiler status and report diagnostic|
| Linux PASS but no native Mac result |Native Mac remains SKIP_ENVIRONMENT; Linux is not an Apple/USB proof|
| Unexpected byte/missing restoration/duplicate ack |FAIL trace/index/expected-vs-actual or counter; report it; do not change engine|
| Retry never resolves / deadline / terminal mismatch |FAIL bounded trace; no hidden sleep or device diagnosis|
| Current drain does not finish |No fresh zero acceptance; FAIL/stop; logical cleanup is not delivery evidence|
| Manifest altered/incomplete project |Restore reviewed source package through owner-controlled preparation; no runner repair|

Native High Sierra/Apple clang/Bash3.2 have NOT been executed in this Linux cloud. Only the owner
can supply that local result. A native PASS proves this compiler and memory-only fixture path,
not USB timing, key delivery, HID OUT, storage, board boot, firmware migration or physical safety.
INJECT_MOD, source modifiers, RESET owner-scope/release-all remain BLOCKED. No Stage28I authorization.
