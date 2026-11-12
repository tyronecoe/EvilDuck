# Project state

## Baseline and references

- Workflow baseline (before these documents): `bb20cbe8ebd2be3745bb028220f8c6f0d1c354bf`, branch `work`.
- [README.md](README.md): existing project reference for EvilDuck SD and S3 hardware, advertised features, and software requirements. Feature descriptions are not test evidence.
- [Script library guide](EvilDuckS3/scripts/README.txt): existing examples, upload procedures, and device paths; not a record of test outcomes.
- [TEST_MATRIX.md](TEST_MATRIX.md): compatibility and testing evidence ledger.

## Evidence and open questions

- Verified firmware behavior: no supporting results were located in the limited documentation inspection. This does not establish that testing never occurred.
- Experimental work: no evidence-backed experimental state has been recorded here; do not infer one from example scripts or advertised features.
- Compatibility and blockers: detailed compatibility results and known firmware blockers are not documented in the inspected references. Their status remains unresolved.
- Historical findings without available evidence remain unverified: **Evidence pending reconciliation**.
- Physically installed firmware is unknown. Git history alone cannot establish what is installed on a device.

## Current objective and next task

- Objective: establish a reusable, low-overhead Codex workflow while preserving firmware functionality, history, and verified evidence.
- This change adds workflow documentation only; no firmware builds or tests are performed.
- Next agreed task: none beyond completing this documentation commit. Await a user-defined task; reconcile historical evidence only when supplied or explicitly requested.
