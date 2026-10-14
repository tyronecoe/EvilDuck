# Stage28K safe reproduction — memory only

Reuse the existing environment; do not install/patch a core, SDK, compiler or service. Observed Linux tools: Python 3.12.14, GNU Bash 5.2.37, Debian g++ 14.2.0-19. Existing target compiler GCC 14.2 and Arduino ESP32 3.3.0 / ESP-IDF 5.5 pins stay unchanged. Source baseline `dce42b8664c2964019cf4b488388d08b2b7fc2d0`. No device, private image or payload file is needed.

From repository root, fresh external directories/results only:

```sh
python3 tests/stage28k/run_tests.py \
  --build-dir /tmp/evilduck28k-build-new \
  --results /tmp/evilduck28k-results-new.json
```

Runner compiles the unchanged preview and new wrapper/test files with C++17/O1/debug, `-Wall -Wextra -Werror`, existing GCC misleading-indent suppression, ASan/UBSan, frame pointers and Linux non-PIE flags. `ASAN_OPTIONS=detect_leaks=1`, `UBSAN_OPTIONS=halt_on_error=1`. It executes 37 new groups, parses every receipt and all 18 mandatory traces, checks duplicate IDs/acks and accepted action-to-intent totals, then separately requires a deliberate negative build to exit 1 and the healthy non-sanitized C++ new probe to report zero. Repeated negative/probe assertions are not added to primary totals. Missing compiler stops the gate as an environment prerequisite; real compile/assertion/sanitizer/receipt errors are not silently downgraded to SKIP. No tests use network or OS keyboard APIs.

Actual final execution used `/workspace/tooling/stage28k-delivery-tests` and `/workspace/tooling/stage28k-delivery-results.json`. The source-result receipt includes full commands/versions/flags, per-case attempts, admissions/acks, accepted snapshots and identities. Earlier development runs remain separate observations, not extra PASS totals.

Fresh unchanged legacy suites:

```sh
stage28k_legacy="$(mktemp -d /tmp/evilduck28k-legacy.XXXXXX)"
for stage28k_suite in stage27b stage28a stage28b stage28c stage28d stage28e stage28f stage28g stage28h; do
  python3 "tests/$stage28k_suite/run_tests.py" \
    --build-dir "$stage28k_legacy/$stage28k_suite-build" \
    --results "$stage28k_legacy/$stage28k_suite.json" || exit 1
done
python3 tests/stage28h/verify_freeze.py
```

Cloud execution used fresh `/workspace/tooling/stage28k-<suite>` outputs and three concurrent suite processes. Existing runners/flags/expectations were untouched. `stage28k-legacy-results.json` records actual independent 187 PASS groups / 579,622 assertions; do not combine them with repeated probe counts or owner-local figures.

Pinned preview OBJECT-ONLY check, no firmware link:

```sh
python3 tests/stage28h/target_check.py \
  --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled \
  --original-core /workspace/tooling/arduino/data/packages/esp32/hardware/esp32/3.3.0 \
  --output-dir /tmp/evilduck28k-target-new
```

The existing checker validates the original/protected core, SDK config/archive/compiler and source before four unlinked objects. No new firmware is produced. If these exact prerequisites are absent, stop target evidence rather than change pins or install tools. The following optional metadata-only extension reproduces wrapper target sizeof from that fresh verified report; it does not compile/link wrapper runtime or firmware:

```sh
python3 - <<'PY'
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
root=Path('.').resolve()
p=json.loads(Path('/tmp/evilduck28k-target-new/report.json').read_text())
assert p['status']=='PASS'
cmd=p['commands'][0].copy()
compiler=Path(cmd[0])
assert hashlib.sha256(compiler.read_bytes()).hexdigest()==p['compiler_sha256']=='d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3'
# Use only the fresh local checker-generated command, never a downloaded receipt.
with tempfile.TemporaryDirectory(prefix='evilduck28k-layout-') as directory:
    out=Path(directory)
    cmd[cmd.index(str(root/'language_preview/core.cpp'))]=str(root/'tests/stage28k/object_layout.cpp')
    cmd[cmd.index('-o')+1]=str(out/'layout.o')
    subprocess.run(cmd,check=True)
    objcopy=compiler.with_name(compiler.name.replace('g++','objcopy'))
    subprocess.run([str(objcopy),'-O','binary','--only-section=.stage28k_sizes',str(out/'layout.o'),str(out/'layout.dat')],check=True)
    raw=(out/'layout.dat').read_bytes()
    assert len(raw)==32
    print(dict(zip(['Driver','Record','IntentRecord','Request','Diagnostic','Counters','Work','MemoryReader'],struct.unpack('<8I',raw))))
PY
```

The actual layout receipt additionally records exact source/header/object SHA-256 and compile/extract commands (`stage28k-object-layout.json`). Binary section bytes are sizeof metadata, not an application image or flash bundle.

Read-only scope/source check requires Git history and existing dependency sources (cloud Python, not a Mac prerequisite):

```sh
python3 tests/stage28k/verify_scope.py \
  --protected-core /workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --sdk /workspace/tooling/arduino/data/packages/esp32/tools/esp32-arduino-libs/idf-release_v5.5-b66b5448-v1/esp32s3 \
  --results /tmp/evilduck28k-scope-new.json
```

It compares all baseline Git files/modes, 47 inherited source spans, frozen 235 files and receipt classifications; rejects additions outside Stage28K docs/tests. Static scope checks are not extra runtime assertions. A source ZIP lacks history needed for freeze verification.

Git publication alone uses network: snapshot `git ls-remote --refs origin` before/after, use unchanged `tests/stage28h/verify_freeze.py --remote-before <before> --remote-after <after>`, then assert only the new branch appeared at exact HEAD. Never merge/rebase/force-push previous refs. The committed publication receipt precedes the commit to avoid self-referential SHA; final exact SHA/post-push receipt is reported at delivery.

Owner-native E–H smoke evidence is already recorded with compiler/version and exit. No automatic rerun, local compatibility editing, upload or tool installation is requested. Stage28K has not been run on macOS. No flashing, boot, OTA or real HID command is provided.
