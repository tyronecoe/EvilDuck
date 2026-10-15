# Stage28Y reproducible offline packaging

Exact X source commit134b295deaebcb93f94beb63f2d46f102a7d6555, no firmware changes or
new target links. Materialized its retained ELF/BIN/artifact bytes and verified hashes,
protected core and actual image/table/OTA/FS structures. X's old native/target evidence
is preserved, not counted as newly run. Relevant work is Python/file/tool validation.

The public package contains six distinct binary files representing seven public roles
(one identical app used twice), manifest, README, exact partition generator source,
public EvilDuckS3/tools/historical docs/pins and three Y validation/private/host scripts.
No .git, private NVS/config/binding/receipt, external build tree or owner backup is
included. The source subset supports inspection and private provisioning; full target
rebuild additionally requires the reviewed repository and pinned X environment.

Executed environment: Linux x86_64, Python3.12.14, existing pinned Arduino3.3.0 core/
ESP-IDF5.5 sources, generator0.1.9 and native mkspiffs0.2.3. Generator/source/tree and
filesystem build checks reuse unchanged historical tools. No downloads or global
patches were made. macOS10.13.6 and its native binaries/USB remain untested here.

From reviewed repository root, with NEW external paths:

```sh
python3 tests/stage28h/verify_freeze.py
python3 tests/stage28y/package.py prepare --directory /tmp/stage28y-public --core /workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0 --mkspiffs /workspace/tooling/arduino/data/packages/esp32/tools/mkspiffs/0.2.3/mkspiffs
python3 tests/stage28y/package.py validate --directory /tmp/stage28y-public --mkspiffs /workspace/tooling/arduino/data/packages/esp32/tools/mkspiffs/0.2.3/mkspiffs
python3 tests/stage28y/package.py archive --directory /tmp/stage28y-public --archive /tmp/evilduck-stage28y-public.zip
python3 tests/stage28y/package.py extract --archive /tmp/evilduck-stage28y-public.zip --directory /tmp/stage28y-extracted
python3 /tmp/stage28y-extracted/source/tests/stage28y/host_preflight.py --public /tmp/stage28y-extracted
python3 tests/stage28y/run_tests.py --public /tmp/stage28y-public --core /workspace/tooling/stage26-final-controlled-core/data/packages/esp32/hardware/esp32/3.3.0 --sdk /workspace/tooling/stage19-sdk-source --generator /workspace/tooling/stage19-nvs-generator --mkspiffs /workspace/tooling/arduino/data/packages/esp32/tools/mkspiffs/0.2.3/mkspiffs --results /tmp/stage28y-tests.json
```

Preparation requires the exact retained X artifact paths in its committed artifact
plan. It checks the retained ELF hash and all artifact hashes; no variant is silently
substituted. On another compatible build host, use unchanged tests/stage28x/build_candidate.py
and X reproduction instructions with its exact pinned environment to reproduce those
inputs. A different rebuild digest is a BLOCKER to this pin, not an automatic update:
record/review a distinct identity if bytes differ. Preparing a public package updates
only the NEW Y manifest pin; after reproduction compare it byte-for-byte with Git.
No original Stage26 pin is modified. No owner credentials are needed for public work.

ZIP entries have fixed timestamps/permissions, sorted names and compression level9.
Two archives of the same public inputs were byte-identical on the executed Python/zlib
runtime. Cross-version compressor identity is not asserted; even if ZIP compression
bytes differ, every member must still match the reviewed manifest and source pins.
Final archive/runtime identities are in results and report. Extractor refuses traversal,
absolute/Windows paths, symlinks, duplicates, excessive expansion and existing output;
validated extracted copy is checked again. Local owner-controlled parent and absence
of concurrent hostile filesystem changes are explicit boundaries, not a sandbox claim.

Private commands/schema/permissions are in package README; only a local file path is
passed. Synthetic testing never substitutes an owner final receipt. Receipt parent
must be0700, config0600, output0700/files0600, all outside checkout/public package.
Failures are generic and suppress private values, subprocess output and tracebacks.
Explicit finalization re-generates/compares exact typed NVS and empty FS and binds
public manifest hash, all ranges and both app roles; authorization remains false.

The environment exposes filesystem execution but no attachment-upload, persistent
file publication or release API. Archive is retained locally at
/workspace/outputs/evilduck-stage28y-public.zip; presence there is NOT a verified
ChatGPT download. No download URL is invented. Retrieval alternatives: an operator
with this environment's file-export access can export those exact bytes, or use the
published Y branch source and the verified X build/materialization recipe on a
compatible build host. No release publication is authorized or performed.
