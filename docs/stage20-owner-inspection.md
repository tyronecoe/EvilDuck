# Stage 20 private owner inspection and shareable summary

## Latest owner-reported result

The owner now reports running both updated Stage20 tools on the actual original local
backups on macOS High Sierra 10.13.6: complete preflight PASS, privacy-safe summary PASS,
NVS `compatible-within-verified-checks` with zero findings, SPIFFS roundtrip true and
migration_authorized=false. The ten older blob findings were no longer reported.
See stage20-owner-extended-preflight-evidence.json. Codex still has neither the binaries
nor the private report; no independent inspection or owner checkout commit was supplied.

This advances owner-reported offline structural evidence only. SDK initialization,
recovery and reads can still modify writable NVS; successful offline checks do not
establish runtime preservation or semantic settings validity. Physical migration stays
NO-GO. The read-only quiescent-profile candidate requires separate review and verified
early-startup coverage. Stage21 has not begun.

## Historical report and repeatable private procedure

Owner confirms local sizes/SHA256 for the three files match Stage19 recorded values.
The owner also reports successfully completing the full Stage19 deployment preflight
on those actual files on macOS High Sierra10.13.6: owner_files_verified=true and
spiffs_roundtrip_verified=true. Its NVS result was insufficient-evidence, with ten
findings: five blob_data_relationships_unverified and five
blob_index_relationships_unverified, all on pages0/1. The owner reported no invalid
or recovery-potentially-required findings and migration_authorized=false.

This is owner-reported local evidence, recorded in
stage20-owner-preflight-evidence.json. Codex has not received the binary files or
private report and has not independently inspected those bytes. The historical
Stage19 hash/size evidence remains unchanged. At the time of that historical report,
no extended blob-relationship run had been reported. The latest report above supersedes
that pending local-run status; independent Codex verification remains unavailable.
Keep backups private and unchanged,
in at least two independent locations. Do not upload NVS/images/private reports to GitHub.
Hash equality is not full structural compatibility or a migration approval.

For an optional future rerun, use the complete file-only procedure in
stage19-owner-preflight.md with the updated Stage20 checkout.
Use new output paths, Python3.8.10 and pinned installed Arduino3.3.0 partition tool. Same
mkspiffs0.2.3 checked geometry4096/256, name32/meta4/magic settings. No firmware compiler,
serial port or esptool operation is required. The prior native preflight/SPIFFS tool
execution succeeded on High Sierra according to the owner; the updated run above is
also now reported successful. These commands remain available for repeat verification.
Linux tests do not prove macOS compiler or USB compatibility.

```sh
ED_BACKUPS='/absolute/path/to/the-three-private-backups'
ED_CORE="$HOME/Library/Arduino15/packages/esp32/hardware/esp32/3.3.0"
ED_MKSPIFFS="$HOME/Library/Arduino15/packages/esp32/tools/mkspiffs/0.2.3/mkspiffs"
ED_PRIVATE='/absolute/path/to/a-new-private-stage20-preflight.json'
ED_SUMMARY='/absolute/path/to/a-new-shareable-stage20-summary.json'
python3 tools/deployment_preflight.py --core-dir "$ED_CORE" --backup-dir "$ED_BACKUPS" \
  --mkspiffs "$ED_MKSPIFFS" --output "$ED_PRIVATE"
python3 tools/deployment_summary.py --private-report "$ED_PRIVATE" --output "$ED_SUMMARY"
```

Both outputs must be new paths; neither command overwrites backups/reports. Preflight
checks exact recorded hashes/sizes/table, original bootloader/application image integrity,
SPIFFS file-level extraction/repack/byte roundtrip/capacity, and bounded NVS structure.
There is no raw SPIFFS170000->160000 relocation, repair, application run or device write.
Temporary repack images are local capacity tests, not replacements for supplied newSPIFFS.

Summary contains only whitelisted generic checks/classification/codes/page/entry locations,
seven-file/1181byte counts and explicit NO-GO boundaries. It excludes NVS keys, namespaces,
values, NVS region digest, dynamic SPIFFS filenames/content and arbitrary report fields.
Input JSON is limited to1MiB; unknown codes/locations/inconsistent flags/identities/layout
are rejected without printing private input. The summary is a projection of a report,
not independent authentication/reinspection of actual binaries. Do not use a hand-edited
or synthetic JSON as owner evidence. Actual backup verification occurs in full preflight.

Interpret nvs_classification:

- compatible-within-verified-checks: only the documented plaintext format subset and
  supported blob-relationship checks passed; not proof of SDK immutability, healthy
  settings, arbitrary unsupported formats or physical startup safety. Do not assign
  this result independently to the owner's backup from hash checks alone. The owner
  now reports this classification from the extended local run.
- recovery-potentially-required: e.g. FREEING, interrupted writes, duplicates or missing
  free page. STOP; no repeated boot, automatic repair or erase.
- invalid: malformed state/CRC/bounds/entry encoding. STOP; retain backups.
- unsupported-format: unverified versions/types/reserved bytes. STOP; no guessed conversion.
- insufficient-evidence: e.g. relationships outside the verified subset or namespace
  resolution. The prior owner's ten blob relationship findings belong to the older
  inspector; the owner now reports zero findings from its extended local rerun.
  Any new insufficient-evidence finding still requires review. Review is
  required, not a compatible pass. No private values need to be shared to discuss codes.

Full preflight exits success when report generation/checks complete; NVS may still have
unresolved findings. The summary deliberately permits exporting these generic findings
while always keeping migration_authorized=false. Existing checked-plan tooling refuses
unresolved classifications. A clean summary cannot close the SDK preservation gate.

Optional share the summary text for review; original binary or private report is not
required for this offline discussion. Preserve raw reports locally for independent
review. Do not create or execute flash/erase/restore/OTA commands from this stage.

Current proposed layout and flags unchanged: NVS9000/5000; OTAE000/2000; app010000/740000;
app1750000/740000; SPIFFSE90000/160000; newcoredumpFF0000/10000. Original SPIFFS290000/170000,
oldapp1150000/140000 and no oldcoredump remain recorded. Owner destination image expected
SHAfea8c95f9a0b49878e69fe9e9afec7472ce52f6b3d7c1b35db43e905470043fe,
size1441792. NVS flagged-readonly experiments were synthetic only; no table change exists.
