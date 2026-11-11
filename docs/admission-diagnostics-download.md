# Admission diagnostics v1: GitHub review download

**Review candidate — not installed or owner-hardware-verified by this work.**

[Download the Mac review ZIP](../downloads/evilduck-routeb-admission-diagnostics-h1-macos-review-v1.zip?raw=1)
and [its SHA-256 checksum](../downloads/evilduck-routeb-admission-diagnostics-h1-macos-review-v1.zip.sha256?raw=1).

The ZIP is **5,614,647 bytes**, with 80 verified members. Exact SHA-256:

```text
05fdff0cdb7a0d4336f8dc219c3a501cc7349c9200f95c2f54a36bb9cccffd81
```

Build: **ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1**. Application: 1,450,944 bytes,
SHA-256 `fce91bca0774181a1be6bc691a1303d47f61caba49e979e89bfa678ef41f60f1`.
Firmware checkpoint: `c9fd36c3e03b2d7ffa318b289398ff7dc1c9fd44`.
Package checkpoint: `0c799d9bb72447409c9f6c23b2f78edaaa849a9a`.

This publication copies the already verified local ZIP without rebuilding or
repacking it. The [development report](admission-diagnostics-report.md) and its
source, test, build and resource receipts remain the historical local-stage
record; the later publication does not claim physical acceptance.

With EvilDuck unplugged, compare the downloaded ZIP hash on the Mac:

```bash
shasum -a 256 evilduck-routeb-admission-diagnostics-h1-macos-review-v1.zip
```

After extraction, from inside its folder, run the offline check:

```bash
python3 preflight.py --directory .
```

Require integrity PASS, `plan_ready=false`, empty selected write ranges and no
hardware/installation authorization. Installation remains a separate deliberate
owner-operated step. Use the included README and short owner checklist.

The exact nested working DEFINE kit remains unchanged (application SHA-256
`167cf5013cd4aa7c0823e5c7391ca9f6d400b7b99df6fe0e46085048fde91a30`).
The outer rollback selects older source/text-v2 (application SHA-256
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`),
which is a distinct recovery role. No hardware operation or payload execution is
part of publication.
