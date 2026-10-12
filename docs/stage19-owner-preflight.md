# Stage 19 owner-local read-only backup verification (High Sierra)

The owner reports all three SHA256/size checks matched using shasum/wc on macOS10.13.6.
Exact facts/provenance are in stage19-owner-evidence.json. Files were NOT supplied to
Codex. This advances the hash/size evidence gate, not full structural preflight, NVS
compatibility, hardware startup or migration authorization. Keep private files local;
never commit/upload original flash/NVS/filesystem contents to GitHub.

Download this Stage19 source branch. These commands only inspect local files and create
a new local report/temporary verification directories; no serial port/device command.
Run from repository root with Python3.8.10. Do not change the pinned core to2.0.17.

```sh
ED_BACKUPS='/absolute/path/to/the-three-private-backups'
ED_CORE="$HOME/Library/Arduino15/packages/esp32/hardware/esp32/3.3.0"
ED_MKSPIFFS="$HOME/Library/Arduino15/packages/esp32/tools/mkspiffs/0.2.3/mkspiffs"
ED_REPORT='/absolute/path/to/a-new-stage19-preflight-report.json'
python3 --version
wc -c "$ED_BACKUPS/evilduck-16m-backup.bin" "$ED_BACKUPS/partition-table-backup.bin" "$ED_BACKUPS/new-spiffs-0x160000.bin"
shasum -a 256 "$ED_BACKUPS/evilduck-16m-backup.bin" "$ED_BACKUPS/partition-table-backup.bin" "$ED_BACKUPS/new-spiffs-0x160000.bin"
"$ED_MKSPIFFS" --version
python3 tools/deployment_preflight.py --core-dir "$ED_CORE" --backup-dir "$ED_BACKUPS" \
  --mkspiffs "$ED_MKSPIFFS" --output "$ED_REPORT"
```

Do not run an overwrite or replacement when a report already exists; pick a genuinely
new output path. Confirm the actual core/mkspiffs paths, available disk for disposable
extraction/repacking, and executable compatibility. Tool requires tested0.2.3 geometry:
4096block/256page, object-name32 and metadata4 per existing checked_mkspiffs. If the Mac
binary cannot execute or its configuration differs, STOP; do not guess geometry,
substitute an unverified tool or format anything. Python/core partition-tool and native
mkspiffs execution on High Sierra are not newly validated by Linux success. Firmware
CLI/GCC builds on High Sierra remain a separate compatibility gate; read-only preflight
does not require a firmware compiler, isolated core patching or esptool upgrade.

This runs full Stage17 hash/layout/image integrity/SPIFFS extraction/roundtrip/capacity
checks plus Stage19 NVS structural inspection. Output includes nvs_structure.classification
and generic issue locations. No NVS keys/settings/passwords printed. Existing SPIFFS file
inventory is in the private report; keep the report local if its filenames are sensitive.
A successful process means checks completed, not all NVS findings are compatible: read
the classification and issue list. Compatible-within-verified-checks is a bounded subset;
blob relationships, settings semantics and SDK immutability are not proved. Any other
classification requires review; checked migration-plan creation refuses it. Preflight
writes no source backup and never executes a stored script.

Original NVS9000..dfff retained; old SPIFFS290000/170000 -> newE90000/160000 requires
file-level roundtrip, never raw relocation. Seven recorded files/1181payload bytes remain
expected, with original/destination byte equality checked again. app1 relocation means
old OTA metadata is not reused blindly: separately reviewed plan initializes app0 and
writes verified safe image to both new slots. No full-chip erase or merged writer exists.

Optional structural-only local tool (does NOT verify full backup expected SHA/layout):
```sh
python3 tools/nvs_inspect.py --full-backup "$ED_BACKUPS/evilduck-16m-backup.bin" \
  --output '/absolute/path/to/a-new-nvs-structure-report.json'
```
Its nonzero exit flags unresolved findings; do not repair or rewrite NVS. The full
preflight above is required regardless. Preserve original backups in at least two
independent locations. esptool4.12.0/Python3.8.10 remain adequate for separately authorized
ROM read-only operations; none are run or required by this offline procedure.
