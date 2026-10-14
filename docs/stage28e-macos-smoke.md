# Owner Mac High Sierra10.13.6 — host-only smoke recipe

Optional local verification. Keep EvilDuck disconnected. No upload/flash/OTA, keyboard/OS input,
USB enumeration, private backups or stored owner scripts. Open Terminal manually if needed;
this recipe never opens windows through DuckyScript. The fixture produces in-memory bytes only.

Download this reviewed branch's source ZIP or checkout its exact published commit. In its root,
read-only environment checks:

```sh
sw_vers
command -v clang++
clang++ --version
```

Use native Apple clang++ only if it supports C++17 and these source files. No Arduino, Xtensa,
Python, USB driver or compiler installation is required by this recipe. If clang++ is missing or
C++17/SDK support unavailable, record SKIP / ENVIRONMENT BLOCKER with version/error text; do not
install/upgrade automatically or weaken compile-storage bounds. An unexplained source build
failure or nonzero test exit needs investigation, not an automatic PASS or environmental dismissal.

Compile into a new temporary directory, without Linux linker or sanitizer assumptions:

```sh
stage28e_smoke_dir="$(mktemp -d "${TMPDIR:-/tmp}/evilduck28e.XXXXXX")"
clang++ -std=c++17 -Wall -Wextra \
  language_preview/core.cpp language_preview/keyboard.cpp language_preview/bridge.cpp \
  tests/stage28e/mac_smoke.cpp -o "$stage28e_smoke_dir/mock-bridge-smoke"
"$stage28e_smoke_dir/mock-bridge-smoke"
```

Expected exit0 and exactly:

```
PASS host-only bridge smoke: 9 exact mock reports, 4 keyboard acknowledgements, 1 delay
```

The smoke uses fixed16-report memory storage and explicitly compares9 eight-byte vectors.
It runs neutral sync, two separate lowercase a actions, a virtual delay, shifted A and ENTER.
It does not send keys anywhere or actually sleep. It is a small smoke check, not the full suite.

Do not reuse Linux run_tests.py flags (-no-pie/-fno-pie) blindly on Apple clang. No ASan/UBSan/
leak support is assumed on High Sierra. A later separately reviewed local sanitizer recipe can
check available runtimes; absence is SKIP, not a claim that Linux sanitizer proof covers macOS.
The read-only freeze checker additionally needs compatible Python3 and Git history containing
its immutable baseline; a source ZIP alone lacks Git history. Do not run production build/upload
scripts or download toolchains for this smoke.

Cloud evidence: native Apple clang and macOS were unavailable, so native Mac execution is SKIP.
The same portable smoke source passed Linux GCC ASan/UBSan/leak checks. That result proves only
its Linux synthetic path and does not prove High Sierra host USB/input behavior. Please report
local compiler version, exit status and stdout/error, without personal data or private backups.
