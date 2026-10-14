# Optional High Sierra10.13.6 host-only ownership smoke

Keep EvilDuck unplugged. Download the reviewed Stage28F branch source ZIP or checkout its
published commit. Run manually in that source root. No Arduino/Python/USB install, OS input,
private file access, stored payloads or real-time waits are used. Only in-memory vectors.

Read-only environment checks:

```sh
sw_vers
command -v clang++
clang++ --version
```

If native Apple clang lacks C++17 or SDK support, record SKIP_ENVIRONMENT and exact compiler
version/error; do not install anything automatically or weaken bounds. A compiler/source failure
needs investigation. Linux sanitizer/linker options are intentionally absent from this recipe.

```sh
stage28f_smoke_dir="$(mktemp -d "${TMPDIR:-/tmp}/evilduck28f.XXXXXX")"
clang++ -std=c++17 -Wall -Wextra \
  language_preview/core.cpp language_preview/keyboard.cpp language_preview/bridge.cpp \
  tests/stage28f/mac_smoke.cpp -o "$stage28f_smoke_dir/mock-ownership-smoke"
"$stage28f_smoke_dir/mock-ownership-smoke"
```

Expected exit0:

```
PASS host-only ownership smoke: 8 exact mock reports, 4 keyboard acknowledgements, 1 delay
```

Fixed16-report buffer compares8 literal eight-byte vectors: neutral sync, Prepared SHIFT,
HOLD a, virtual DELAY, transient b press/restoration, RELEASE a, repeated RELEASE a, then
explicit neutral drain. SHIFT is the existing mock setup API, not new INJECT_MOD syntax.
No physical host or device behavior is verified. The smoke is smaller than the full suite.

Cloud result: PASS Linux GCC ASan/UBSan/leak smoke. Native macOS / Apple clang is
SKIP_ENVIRONMENT: unavailable in this Linux cloud (clang++ not found). Owner Mac results
have not been supplied. Sanitizer availability on High Sierra is not assumed.
