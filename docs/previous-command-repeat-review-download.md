# Previous-command REPEAT v1 — review download

**REVIEW ONLY. Installation and hardware testing are not authorized by this download.**

[Download the review ZIP](../downloads/evilduck-routeb-previous-command-repeat-h1-macos-review-v1.zip?raw=true)
onto the **Intel Mac running macOS High Sierra 10.13.6**, rather than the iPhone.
This publication copies the existing verified archive byte-for-byte. No firmware
rebuild, repackaging, new payload execution or hardware operation is involved.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| ZIP | 2,605,305 | `9ab478df75fcec25648572320229ed9b31b167fa4f1af4f18ea200f2b97f4fbb` |
| Application | 1,437,888 | `13cec88262afdfa641eb0fb4927fe7903abf2863295344ff316418707ba49b7f` |
| Exact older source/text-v2 rollback application | 1,413,200 | `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02` |

Build ID: `ROUTEB-PREVIOUS-COMMAND-REPEAT-v1`.
Firmware checkpoint: `820a575a45e5a4f644921d663a650110667a6ab2`.
Packaging checkpoint: `fe6a6c4fcfca4fdf64023c998975cb3f7eb05e13`.
The ZIP contains `OWNER-CHECK.md`, `manifest.json`, `preflight.py` and the guarded
Mac installer/rollback guides. The corrected publication handoff's checksum
matches the archive and prior verification receipts exactly.

## Offline review on High Sierra

Disconnect/unplug EvilDuck. Do not run the installer launcher or connect to the
dashboard for this stage. Use the Mac's existing Python 3.8+ installation.

Assuming the ZIP was saved in Downloads, open Terminal and verify it first:

```bash
cd "$HOME/Downloads"
shasum -a 256 evilduck-routeb-previous-command-repeat-h1-macos-review-v1.zip
```

The output must match the full ZIP checksum above. Stop on a mismatch. Only
after it matches, extract to a **new** folder and run the offline preflight:

```bash
unzip evilduck-routeb-previous-command-repeat-h1-macos-review-v1.zip -d evilduck-repeat-review-v1
cd evilduck-repeat-review-v1
python3 preflight.py --directory .
```

If that extraction folder already exists, choose a new folder name instead;
do not overwrite or mix an older kit. Expect exit 0 and:

```text
package_integrity: PASS
installed_metadata: NOT_SUPPLIED
plan_ready: false
selected_write_ranges: []
installation_authorized: false
hardware_access: false
```

This preflight uses local package files and does not contact the device or
install dependencies. Keep the device unplugged. Read `OWNER-CHECK.md` and the
guides for review; their physical steps require separate authorization.

## Evidence and limits

The [local build/delivery report](previous-command-repeat-release-delivery.md)
and [structured results](previous-command-repeat-release-results.json) preserve
the completed clean-build, native/browser, sanitizer, complete release-chain,
package, extraction and mock-installer evidence, including earlier failed
verifier integration attempts. Publication does not turn these software checks
into physical High Sierra/iPhone acceptance. The 40-member archive and its
application/rollback identities were audited again before publication; no owner
passwords, private backups, NVS/settings dumps or private host logs were identified.

The rollback is an older standalone application without newer privacy and
dashboard/editor repairs, not a full-device or filesystem restore. Preserve all
existing recovery artifacts. H1 remains opt-in and experimental, with canonical
Hak5 numeric encoding unresolved. Bounded standalone REPEAT and existing inline
REPEAT semantics, ownership, STOP, privacy and release safeguards are unchanged.

Flashing, installation, OTA, dashboard/HID testing or any writing to the device
requires **separate owner authorization**. This publication creates no GitHub
Release, tag or merge and authorizes no automatic script execution.
