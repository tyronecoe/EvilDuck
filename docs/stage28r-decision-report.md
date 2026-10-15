# Stage28R transport decision and language-engine roadmap

**GO: review the decision package. Recommendation: B, an opt-in Runtime-to-existing-scheduler route with explicitly local completion semantics, pending owner selection. Strict real endpoint retirement remains UNRESOLVED. NO-GO: integration/deployment, dependency changes, target/SDK/firmware builds, device/live USB/HID, flash/boot/OTA or automatic Stage28S.**

Exact clean starting commit `9afdeabffae32186e56fe7012cf5f639bb88dec9` on Stage28Q was verified before changes. New branch `stage28r-transport-decision-language-roadmap`. Only nine new `docs/stage28r-*` files; no historical edits or new runtime code. Protected source inventories are independently compared to actual Git blobs, not only old reports.

## Findings and decision still needed

- Q's public-document blocker applies to the additional strict L contract, not to all ordinary HID operation or language work. Q's conditional green model does not prove retirement.
- Production uses `com` cooperative scheduling over backend ownership/submission, not a ready-made preview Bridge sink. `tud_hid_n_report` copies to class-owned storage and reports stack/DCD submission status; shared core semaphore is not per-transfer correlation.
- B can reuse local press/dwell/restoration and cancellation policies without rewriting USB transport, provided a future exclusive, typed scheduler admission/result seam is verified. It cannot offer L's correlated retirement guarantee. Current void script APIs/global callbacks, single held-state ledger, numeric divergence, locale and capacity differences prevent plug-in substitution.
- C public raw report adaptation is different but duplicates existing scheduler work and still lacks strict correlation/retirement. A remains a valuable separately blocked option. Neither weaker route authorizes blind retries, competing producers or neutral/host-delivery claims.
- Production already has broader language/device extensions than preview. Next useful implementation is an opt-in ownership-free subset with actual scheduler/native tests; independent numeric/text/preprocessing fixtures can proceed without vendor retirement answers. No full compatibility claim.

Owner needs to select the acceptance contract/subset and separately authorize the next implementation scope. This package makes no selection and does not move previous approval cells. No recurring design-only stage is recommended: implement the narrowly specified native scheduler seam next if B is selected, or resolve A's named missing premise first if strict transport remains mandatory.

## Support packet and reference limits

`stage28r-espressif-support-draft.txt` is **UNSENT**. It requests device IN disable/NAK, endpoint/FIFO mapping, W1C/CPU pending, no-late buffer/IRQ, visibility/affinity, active publisher fencing and supported APIs. Official current ESP-IDF Resources page was retrieved HTTP200 and confirms community support route; live technical-inquiry pages returned403. Exact URLs/status/hashes are in evidence JSON, alongside the pinned official TRM's Technical Enquiries routing. No ticket/post/email, account request or NDA acceptance occurred. Live Hak5 pages returned403; four saved official snapshots were freshly hash-verified to existing provenance. No claim current online syntax or compiler oracle was obtained.

## Actual Stage28R verification

Documentation/source/hash/diff/consistency checks only: exact parent and clean initial tree; all1,155 historical tracked bytes/paths/modes; all235 frozen Stage26 files; source span hashes; protected installed core/SDK source guard; cached official reference hashes; allowed new-file scope; document links and required decision/gate consistency. Remote snapshot42 refs before publication; compare every one after publishing only R. Integrity JSON is explicitly PRECOMMIT with self-hash excluded. Final exact commit and post-push publication checks are external to avoid a self-referential receipt.

**New runtime groups=0; new runtime assertions=0. Runtime/sanitizer/regression reruns=none.** Q37/419 and P33/167 are inherited evidence, not fresh results. Preserve P's three expected watchdog observations, historical negative controls, production language XPASS/USB XFAIL and all prior classification boundaries. No new sanitizer-clean claim; no native Mac rerun. Prior H/J187/579622 and M/O/N results are not added to fresh totals.

No target object, linked ELF/BIN, OTA, firmware resource or physical measurements. Historical target Program6936B +CompileSession2408B +Bridge5020B=14364B includes Runtime/Planner inside Bridge; not measured anew or production headroom. B's alternative Runtime-only composition requires future peak/ABI/stack checks; no inferred memory savings or timing guarantee.

## File inventory

- `docs/stage28r-owner-scope.md`
- `docs/stage28r-blocker-summary.md`
- `docs/stage28r-espressif-support-draft.txt`
- `docs/stage28r-transport-options.md`
- `docs/stage28r-language-capability-map.md`
- `docs/stage28r-implementation-roadmap.md`
- `docs/stage28r-decision-report.md`
- `docs/stage28r-source-evidence.json`
- `docs/stage28r-integrity.json`

Full transport choices, capability map and next milestone acceptance/stop conditions are in the named companion files. Existing profiles, pins, preview grammar/APIs/caps, K01 barrier and conservative E-capacity status remain unchanged. Existing backup files and owner payloads were not read. Original firmware availability stays owner-confirmed externally. No hardware access, real HID output or firmware generation occurred; Stage28S not started.

## Reproduce the documentation checks (no builds or runtime tests)

From the reviewed repository root with existing Python3 and Git:

```sh
git status --short
git rev-parse HEAD
git diff 9afdeabffae32186e56fe7012cf5f639bb88dec9 --name-status
python3 tests/stage28h/verify_freeze.py
git diff --check
```

The following read-only check compares historical bytes/modes directly to Git and verifies all repository source/report hashes. It does not use old test counts as fresh results:

```sh
python3 - <<'PY'
import hashlib,json,pathlib,stat,subprocess
base='9afdeabffae32186e56fe7012cf5f639bb88dec9';root=pathlib.Path('.')
def git(*a):return subprocess.check_output(['git',*a])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
n=0
for row in git('ls-tree','-rz',base).split(b'\0'):
    if not row:continue
    meta,name=row.split(b'\t');mode,kind,oid=meta.split();p=root/name.decode()
    assert kind==b'blob' and p.read_bytes()==git('cat-file','blob',oid.decode())
    assert bool(p.stat().st_mode&stat.S_IXUSR)==(mode==b'100755');n+=1
assert n==1155
m=json.loads((root/'docs/stage28r-source-evidence.json').read_text())
for row in m['source_spans']:
    if row['file'].startswith(('tinyusb/','builder/','protected-core/')):continue
    p=root/row['file'];assert digest(p)==row['sha256']
    lines=p.read_bytes().splitlines(keepends=True)
    assert hashlib.sha256(b''.join(lines[row['first']-1:row['last']])).hexdigest()==row['span_sha256']
for row in m['prior_reports']:assert digest(root/row['file'])==row['sha256']
print('PASS historical inventory and repository evidence')
PY
```

Six dependency spans additionally checked here against existing pinned scratch sources: `tinyusb/` aliases Stage28P original `src/`; `builder/` aliases its builder directory; `protected-core/` aliases the verified isolated Arduino3.3.0 core root. Whole-file/span SHA values and pins are in source-evidence JSON. Recheck with that mapping when those sources exist; absence is missing dependency evidence, never a fresh PASS. No install/retrieval/build is required for repository-only checks. The installed protected-core/SDK guard was run read-only using existing `tools/patched_core.py check_sources(...,patched=True)`; no global source was patched. Source-span preparation initially caught three overlong citation endpoints (com header, execution guard, preprocessor); citations were corrected against actual line counts before the final check. No production defect or runtime test outcome was involved.

Publication verification: save `git ls-remote --refs origin` before push outside the checkout, push ONLY `HEAD:refs/heads/stage28r-transport-decision-language-roadmap` without force, save the same read-only snapshot after. Require every old ref/hash identical and exactly one new ref at final HEAD. Final publication evidence belongs outside the self-referential committed receipt and is reported with the delivered SHA. These Git operations publish documentation only; no firmware upload or hardware operation occurs.
