# H1 package reproduction — existing artifacts only

No firmware compilation is part of this packaging stage. Firmware review base: `a15b8e218935b2c6a69b71eeac3aaf378c3c0c03`. The source-stage build and selected post-link checks already completed; their receipts are reused, not claimed as freshly rerun. The package's `source_commit` identifies the packaging tools; `firmware_source_commit` separately identifies that H1 review base. The ELF-derived application is fixed at 1,414,080 bytes / `8a48f3f208165466e579f76a35fb7898fbaf1188e746ca3a0d60e99c576b0ecd`.

The existing local build root is `/workspace/scratch/inject-var-experimental/build-v1`; linked receipt is `/workspace/scratch/inject-var-experimental/linked-final2.json`. The exact receipt SHA-256 is `cf00b9a66e9b9dfb270f10d418e2145af083e7a58a64cc21f2b57842fbe0d4d0`. Its artifact inventory includes the BIN, ELF, map, bootloader and table. The packager verifies all available artifact and generated source hashes, but includes only the two applications and expected table as binary package members. The bootloader/table are not installation targets. Missing or changed evidence stops packaging; rebuilding or substituting an image is outside scope.

From the EvilDuck repository, replace `PACKAGING_SOURCE_COMMIT` with the commit containing these packaging tools and choose new, nonexistent scratch outputs:

```bash
python3 tests/inject_var_h1_package/package.py \
  --source-commit PACKAGING_SOURCE_COMMIT \
  --build-root /workspace/scratch/inject-var-experimental/build-v1 \
  --linked-report /workspace/scratch/inject-var-experimental/linked-final2.json \
  --core /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0 \
  --directory /workspace/scratch/inject-var-h1-package/package \
  --archive /workspace/scratch/inject-var-h1-package/evilduck-routeb-inject-var-h1-experimental-macos-v1.zip
```

Fresh focused verification uses public copies and mocked tool responses only:

```bash
python3 tests/inject_var_h1_package/test_package.py \
  --directory /workspace/scratch/inject-var-h1-package/package \
  --archive /workspace/scratch/inject-var-h1-package/evilduck-routeb-inject-var-h1-experimental-macos-v1.zip \
  --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin \
  --results /workspace/scratch/inject-var-h1-package/package-tests.json
python3 tests/inject_var_h1_package/test_bound_installer.py \
  --directory /workspace/scratch/inject-var-h1-package/package \
  --ota-template /workspace/scratch/led-feedback-isolated-core/data/packages/esp32/hardware/esp32/3.3.0/tools/partitions/boot_app0.bin \
  --results /workspace/scratch/inject-var-h1-package/installer-tests.json
```

Do not overwrite existing output receipts to conceal earlier failures. The installer tests inject every device/tool operation; they do not call an esptool hardware dispatcher. Python 3.8 grammar and Bash syntax checks on Linux are compatibility evidence, not native High Sierra execution or physical recovery proof. ASan/UBSan/leak results belong to the earlier unchanged C++ H1 tests, not these Python package checks.

On the owner's High Sierra Mac, after verifying the externally published ZIP checksum and extracting it into a new folder, the **first fully offline check** is:

```bash
python3 preflight.py --directory .
```

Expected: package integrity PASS; no current metadata, no selected write ranges, no hardware access and no installation authorization. Read INSTALL-MAC.md, ROLLBACK-MAC.md and OWNER-CHECK.md before any separately approved device operation. Never execute the `.txt` fixtures automatically. No native Mac, device or genuine Hak5 experiment was performed by this packaging stage.
