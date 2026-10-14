# Stage28G optional native High Sierra10.13.6 smoke

Keep EvilDuck unplugged. Download this reviewed branch source ZIP or checkout its exact commit.
This is memory-only C++17: no USB endpoint/enumeration, real keyboard, OS input, private backups,
stored scripts, Arduino, Xtensa, network or actual delay. No installations required/authorized.

Read-only environment checks, manually in Terminal:

```sh
sw_vers
command -v clang++
clang++ --version
```

If native Apple clang cannot support C++17/SDK, report SKIP_ENVIRONMENT with version/error.
Do not install/upgrade automatically, alter bounds or claim PASS. Source failures require review.
Do not reuse Linux -no-pie or sanitizer flags blindly; native sanitizer availability not assumed.

```sh
stage28g_smoke_dir="$(mktemp -d "${TMPDIR:-/tmp}/evilduck28g.XXXXXX")"
clang++ -std=c++17 -Wall -Wextra \
  language_preview/core.cpp language_preview/keyboard.cpp language_preview/bridge.cpp \
  tests/stage28g/mac_smoke.cpp -o "$stage28g_smoke_dir/mock-contract-smoke"
"$stage28g_smoke_dir/mock-contract-smoke"
```

Expected exit0 and:

```
PASS host-only ownership smoke: 8 exact mock reports, 4 keyboard acknowledgements, 1 delay
```

Uses the same fixed16-report fixture as Stage28F: sync, Prepared SHIFT, nonmodifier source HOLD,
virtual Delay, transient b/restoration, repeated source RELEASE, then explicit neutral drain.
It checks8 literal vectors. There is no new source modifier grammar. This smaller smoke does
not execute the entire regression or demonstrate host keyboard interpretation.

Fresh cloud Linux GCC ASan/UBSan/leak run PASS. Native macOS/Apple clang SKIP_ENVIRONMENT: Linux
cloud lacks Apple/macOS and clang++; owner-native results not supplied. Report compiler/version,
exit code and stdout/errors only, without credentials or private files. No device permission.
