# Offline reproduction and owner review gates

Existing verified cloud workflow reused: Python3.12.14, GCC14.2.0, Node24.19.0,
Arduino CLI1.3.1, pinned Xtensa14.2.0/Arduino3.3.0/ESP-IDF5.5. No setup installation
or environment-config changes were needed. No native Windows/.NET or Apple SDK
is available; do not classify their unexecuted tests as PASS.

All commands run from repository root, device disconnected. Use new disposable
output paths outside Git; the runners reject existing directories. Reuse the
verified isolated core; never globally patch Arduino/SDK. These commands compile,
inspect public sources and run mocks only. No port/upload/flash interface is used.

```sh
python3 tests/led_return/run_tests.py --build-dir /workspace/tooling/stop-led/repro-native --results /workspace/tooling/stop-led/repro-native.json
python3 tests/led_return/run_related.py --native-results /workspace/tooling/stop-led/repro-native.json --build-dir /workspace/tooling/stop-led/repro-related --results /workspace/tooling/stop-led/repro-related.json
python3 tests/led_return/build_candidate.py --output-dir /workspace/tooling/stop-led/repro-link --config /workspace/tooling/stage26-final-controlled-core/arduino-cli.json --baseline-build /workspace/tooling/arduino/build/stage26-final-controlled --arduino-cli /workspace/tooling/arduino/bin/arduino-cli --jobs 2
python3 tests/led_return/verify_link.py --build-root /workspace/tooling/stop-led/repro-link --output /workspace/tooling/stop-led/repro-checked.json
node tests/led_return/test_stop_ui.cjs /workspace/tooling/stop-led/repro-link/candidate/EvilDuckS3/webfiles.h
node tests/led_return/test_ui.cjs /workspace/tooling/stop-led/repro-link/candidate/EvilDuckS3/webfiles.h
python3 tests/http_snapshot/test_verifier_controls.py --build-root /workspace/tooling/stop-led/repro-link --output /workspace/tooling/stop-led/repro-verifier-controls.json
python3 tests/host_capture/run_checks.py --candidate-sources /workspace/tooling/stop-led/repro-link/candidate/EvilDuckS3 --output-dir /workspace/tooling/stop-led/repro-host-checks
python3 tests/stage28h/verify_freeze.py
```

Actual final output names were b-native-verified/b-results-verified,
b-related-fixed/b-related-fixed.json, linked-final/linked-final-checked.json,
c-checks-delivery and their recorded logs/results. Related tests preceded the final
JS-only response-body timeout fix; relevant C++ sources are identical and the final
103-case native suite and JS tests used final assets. Initial compiler/harness/
fixture failures and their corrections are documented, not converted to passes.
All final target artifact hashes belong to that exact path/time build; a reproduction
must check its own ELF/BIN provenance rather than assume identical bytes.

Owner checklist (future activity requires its own approval):

1. Review the separate A/B/C commits, source manifests, receiver protocol and host
   limitations. Keep the installed working package and backups untouched.
2. Compile the host-only helpers locally using the README's normal tools and
   permissions, with EvilDuck unplugged. No need to grant capture permission or
   run a helper merely to compile it. Native build failures are blockers to fix.
3. Before any application installation, separately review actual installed partition
   table/OTA target and new artifact identity. The existing package pins a different
   application hash and must not be bypassed or silently replaced. No new physical
   installation plan or automatic updater is authorized here.
4. After a future approved app-only update, hard-refresh the embedded home page
   on Mac/iPhone. No SPIFFS replacement/format, settings reset or bundled examples
   are needed. Confirm STOP access independently of status polling.
5. Only under a separately authorized harmless trial: check STOP admission/errors,
   request-correlated terminal state and local report cleanup; host release remains
   independently observed. Programs already launched require their own Stop/Exit.
6. Observe actual lock reports first, then a single bounded fixed-message roundtrip.
   No Caps+Num evidence means no supported two-bit sender. Keep unknown/stale explicit.
7. Only after supported transport evidence: separately test a manually typed fake
   phrase in a second ordinary editor, verify the helper stops and review the local
   fake result before deliberate sending. Fill the sanitized record template; leave
   all unperformed cells NOT TESTED. No credentials/private input or automatic upload.
