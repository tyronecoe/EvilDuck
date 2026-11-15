# Codex workflow

- Read [PROJECT_STATE.md](PROJECT_STATE.md) first, then only the existing documentation relevant to the task. Consult [TEST_MATRIX.md](TEST_MATRIX.md) when compatibility or test evidence matters.
- Keep inspection and changes task-scoped. Reuse documented findings; avoid repository-wide investigations and repeating earlier work without a concrete reason.
- Preserve verified firmware functionality, historical evidence, and rollback checkpoints. Do not rewrite history or remove records to simplify a task.
- Prefer verification targeted to the changed behavior when appropriate. Documentation-only changes do not automatically require firmware builds, regression suites, or release packages.
- Claim physical hardware testing only when actual evidence supports it. Separate documented claims, verified results, experimental work, and unresolved compatibility.
- Update state only after meaningful changes, and the test ledger only when evidence changes. Do not update all documentation automatically after trivial edits.
