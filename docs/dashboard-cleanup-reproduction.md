# Dashboard cleanup — reproduction and evidence scope

Run the first package check from its extracted directory, with EvilDuck unplugged:

```bash
python3 preflight.py --directory .
```

This is the first offline Mac command. It validates package/image/provenance
identities and does not inspect or operate a USB device. Do not use install or
rollback launchers during this review. The package retains Bash 3.2 launchers,
Python 3.8-compatible source and the established esptool 4.12 workflow; native
High Sierra execution of this candidate remains untested.

Repository checks below are developer offline operations; paths assume the
recorded Linux workspace. They do not flash or link anything unless the explicitly
labelled target-build command is run. Browser fixtures intercept an exact inert
HTTP route/method allowlist and abort unknown requests; no device is contacted.

```bash
python3 -B tests/dashboard_cleanup/test_browser.py \
  --source /workspace/scratch/dashboard-cleanup/build-v1/candidate/EvilDuckS3/webfiles.h \
  --output-dir /workspace/scratch/dashboard-cleanup/browser-reproduction
node tests/led_return/test_stop_ui.cjs \
  /workspace/scratch/dashboard-cleanup/build-v1/candidate/EvilDuckS3/webfiles.h
python3 -B tests/dashboard_cleanup/test_verify_release.py
```

The first browser run used the identical verified scratch candidate header before
compilation. The target verifier subsequently binds those exact header bytes to
the compiled source dependency/object and linked image. Output directories must
be fresh; preserve earlier receipts, including intermediate harness failures.

Clean target build, using the committed new overlay and the existing approved
isolated archive-based profile:

```bash
python3 -B tests/dashboard_cleanup/build_candidate.py \
  --output-dir /workspace/scratch/dashboard-cleanup/build-v1 \
  --config /workspace/scratch/led-feedback-isolated-core/arduino-cli.json \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 4
python3 -B tests/dashboard_cleanup/verify_release.py \
  --build-root /workspace/scratch/dashboard-cleanup/build-v1 \
  --output /workspace/scratch/dashboard-cleanup/release-checks.json
```

These are compile/verification commands, without any port/upload interface. The
builder rejects changed/uncommitted implementation inputs, partial composition,
wrong guards and nonfresh builds. Do not change the historical builders or global
Arduino/SDK installation. Arduino ESP32 3.3.0 / ESP-IDF 5.5, ESP32-S3, 16 MiB flash,
PSRAM disabled, existing USB/CDC and production partition identity are retained.
The package contains application images, not bootloader/partition/filesystem
replacement images.

Browser environment: Debian 13, Chromium 151.0.7922.173, Playwright 1.62.0,
1280×900 desktop and 320×640/390×844 touch emulation. Other native OS/browser engines
are untested; see [platform matrix](dashboard-cleanup-platforms.md). Python/Node/
compiler versions, hashes and actual target commands are recorded in the receipts.
No timing/heap/stack-high-water measurements or physical USB evidence are inferred.
