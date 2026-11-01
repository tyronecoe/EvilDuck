# Reproduce verification and packaging — no rebuild

This package uses the existing clean privacy application/ELF identified in
README.md. Missing or mismatched artifacts are a blocker, not permission to
recompile or substitute another image.

The privacy-specific release verifier adapts only final live-candidate expected
hashes for the three reviewed privacy filenames while running the pinned frozen
H1 verifier chain. The independent privacy compiled-input/header/object binding
also runs. Use fresh evidence paths and preserve earlier attempts.

```bash
python3 -B tests/privacy_fix1/verify_release.py \
  --build-root /workspace/scratch/privacy-fix1-integration/build-v2 \
  --output /workspace/scratch/privacy-release-reproduction.json
```

The packaging entry point is `tests/privacy_fix1/package.py`; it requires the
exact application, ELF and verified receipt hashes and a committed packaging
source revision. It forwards the immutable H1 packager's image/layout checks,
installer generation and rollback behavior, adding privacy-only identities and
documents. Its `--help` lists required input paths; it has no build, device,
network, upload or automatic execution interface.

Historical package checks and injected mock-installer checks run against the
extracted new package. Additional privacy metadata tampering is rejected by the
new preflight. The public ZIP is extracted to a fresh directory and its actual
README offline command is executed before publication; published bytes are
downloaded and compared with the application and rollback identities.

The owner only needs the files in the ZIP for the initial offline check:

```bash
python3 preflight.py --directory .
```

No Git, Arduino toolchain or new dependency download is required for that check.
Linux checks do not claim physical High Sierra or firmware execution.
