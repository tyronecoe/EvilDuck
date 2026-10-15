# Stage28Q executed tests and reproduction

37 native model PASS /0 unexpected final FAIL /419 assertions. No physical certificate or new vendor-model execution. All model cases use explicit synthetic premises except rejection tests; conditional successes are not hardware guarantees.

| ID | Actual model scenario | Assertions |
|---|---|---:|
| Q01 | Full model receipt plus conditional retirement/fences | 19 |
| Q02 | Repeated cancellation; explicit management admission only | 18 |
| Q03 | Raw/CPU pending persists through mask; entered publisher fenced | 21 |
| Q04 | W1C clears selected latched bit, modeled RO/other bits persist | 2 |
| Q05 | Same-bit arrival after acknowledgement: ambiguity | 4 |
| Q06 | Same-bit arrival before acknowledgement: ambiguity | 4 |
| Q07 | ISR/publisher already active at retirement | 17 |
| Q08 | Queued old completion after software enabled-state reset | 9 |
| Q09 | NAK acknowledgement never arrives | 4 |
| Q10 | Disable acknowledgement never arrives | 4 |
| Q11 | Flush acknowledgement never arrives | 4 |
| Q12 | Retained FIFO data blocks before explicit scoped flush | 9 |
| Q13 | Public/incomplete premise profile: no request/certificate | 3 |
| Q14 | Reset/unplug/suspend at every nonterminal phase (42 variants) | 85 |
| Q15 | Full4 queue plus fifth publication: sticky loss | 9 |
| Q16 | Checked lock error: no register writes | 4 |
| Q17 | Contended try-entry consumes bounded budget | 35 |
| Q18 | Equal neutral bytes: deny early reuse; fresh C/Q only after gate | 16 |
| Q19 | Old queued ticket after new admission is dropped | 17 |
| Q20 | Forced old CPU-pending/origin after gate falsifies no-late premise | 18 |
| Q21 | Shared-controller disturbance rejected | 3 |
| Q22 | Active observer prevents reclamation | 4 |
| Q23 | True64-bit identity exhaustion; retirement still possible | 18 |
| Q24 | First fault retained after cancellation then loss | 2 |
| Q25 | Exact32-step exhaustion | 4 |
| Q26 | Exact100-unit deadline exhaustion | 2 |
| Q27 | uint32 wrap deadline arithmetic | 3 |
| Q28 | Ownership failure before mask | 4 |
| Q29 | Missing visibility acknowledgement blocks retirement | 7 |
| Q30 | Each of8 missing certificate premises fails closed | 9 |
| Q31 | Completion raw status reappears after acknowledgement | 3 |
| Q32 | Publisher enters before final gate: refuse | 3 |
| Q33 | Retirement without success cannot accept source | 16 |
| Q34 | Different-bit arrival during W1C persists in either order | 5 |
| Q35 | Failed current receipt cannot accept source | 16 |
| Q36 | Partial current receipt cannot accept source | 16 |
| Q37 | Default hardware schedule does not auto-cooperate | 2 |

Q01–Q37 actual phases/raw/mask/CPU/ISR/queue/identities/outcomes and executed proposed-model function/line counts are recorded in JSON. Q14 loops3 lifecycle inputs×14 phases with checked target phase before invalidation. Q05/Q06 and Q34 explore both acknowledgement orderings. Q30 independently removes every certificate premise. Q20 is an intentionally inconsistent robustness injection, not an interleaving asserted physically permitted under the success premises. Event ticket origin is a supplied immutable publisher lease, not information available in the shipped raw status.

Every conditional success needs all8 ledger certificate premises plus the explicit delayed acknowledgement/publisher/visibility schedule. No request auto-acknowledges in the model. The public/default profile refuses; the synthetic profile without schedule exhausts its budget. No full state-space/model-checker proof or real timing is claimed.

ASan/UBSan/detect_leaks=1 clean for completed37 cases. Native GCC/gcov14.2.0, C++17/O1/debug/Wall/Wextra/Werror, inherited misleading-indentation suppression, frame pointers/non-PIE/gcov; no warning flags weakened. Negative control exits1 separately. The initial retirement-without-success defect reproduction exits1 on preserved pre-fix scratch source; the corrected same reproducer exits0, excluded from primary counts. Q20 initially omitted CPU-pending while trying to enter a masked ISR; the corrected robustness input explicitly supplies it. Development failures are retained in manifest/report rather than counted as final passes.

Unchanged Stage28P runner executed once separately:33 observation PASS/167 assertions;3 expected watchdogs and negative control remain separate. Watchdog-killed processes have no completed coverage/assertion/leak-clean claim. Historical O46/931, baseline20/131 and disabled20/131 remain inherited classifications from P, not newly rerun Q totals. No wide historical or Mac rerun.

## Reproduction

Only existing host GCC/gcov/Python/pdftotext/patch and public references. Fresh external directories; no target/compiler/core installation, firmware link, USB access or private files.

```sh
python3 tests/stage28q/retrieve_references.py --output /tmp/evilduck28q-refs-new
python3 tests/stage28q/run_tests.py --build-dir /tmp/evilduck28q-build-new --results /tmp/evilduck28q-results-new.json
python3 tests/stage28q/verify_scope.py --references /tmp/evilduck28q-refs-new --p-source /tmp/evilduck28p-original-new --output /tmp/evilduck28q-scope-new.json
python3 tests/stage28h/verify_freeze.py
```

The P source path is the exact original tree from its published preparation runner; follow unchanged P reproduction if unavailable. Its unchanged runner can be executed against its exact adapted/only-platform trees as documented there. Q performed that once with fresh native build outputs; actual commands/exits are in its nested P receipt. Reference retrieval checks exact size/SHA at each official URL; if a moving documentation URL changes, stop instead of silently accepting a new version. No large SDK or document dump is committed.
