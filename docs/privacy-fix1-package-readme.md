# Privacy Fix 1 — High Sierra owner-review candidate

**EXPERIMENTAL — REVIEW ONLY — NOT AUTHORIZED FOR FLASHING.** Downloading or
checking this package does not authorize installation, boot or physical testing.
This is the existing password-disclosure repair; no new scripting or HID feature
is introduced. H1 remains opt-in/experimental and canonical Hak5 encoding remains
unresolved.

Extract into a new directory and open Terminal in that directory. Preserve the
ZIP and verify its published SHA-256. With an existing Python 3.8+ installation,
the first **offline** command is exactly:

```bash
python3 preflight.py --directory .
```

Expect exit 0, `package_integrity: PASS`, `installed_metadata: NOT_SUPPLIED`,
`plan_ready: false`, `selected_write_ranges: []`, `hardware_access: false` and
`installation_authorized: false`. This reads package files only, not USB or the
network. Do not use the installer launcher as the offline check: its default
`check` action reads hardware and needs separate approval.

Read INSTALL-MAC.md, OWNER-CHECK.md and ROLLBACK-MAC.md. The supported preparation
interfaces remain macOS High Sierra 10.13.6, Bash 3.2, Python 3.8+ (owner's known
3.8.10) and esptool 4.12.0. No dependencies are downloaded or installed by this
package. Linux tests do not establish native High Sierra execution.

**The dashboard still reports `ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1`. That
string alone DOES NOT identify this privacy image.** Exact `application.bin`:

- Bytes: **1,415,968**.
- SHA-256: **9e4d3b615d78e87521882a35c4b43ce66403168a15b6b39bcebc81bb32a6b96e**.
- Source checkpoint: `93cc8d1a7b162bdda91e239d840a3eee8a70c51c`.
- Target integration: `0380d1508b8f761e30a6a1fb63f67c2850cbc84a`.

These exact existing build bytes were reused, not rebuilt to change a label.
`build-receipt.json` records fresh applicable full H1 link/disassembly verification
and the additional privacy source/header/object/image binding. The normal image
and `rollback-application.bin` are standalone applications, not merged recovery
images.

The rollback is the **older accepted source/text-v2 application, without Privacy
Fix 1**: 1,413,200 bytes, SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.
It is deliberately preserved unchanged, not described as privacy-patched firmware.

The prior four scoped right-modifier passes and three planned lock-wait groups
remain accepted. The historical `rm-*.txt` fixtures are retained unchanged for
provenance only; they are not requested acceptance trials for this privacy update.
Nothing in the package starts a payload automatically. Keep private credentials,
backups and raw device/HTTP captures out of public logs and screenshots.
