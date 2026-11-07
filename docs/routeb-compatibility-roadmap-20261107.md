# Route B compatibility roadmap — November 7, 2026

This is the bounded roadmap agreed after the read-only compatibility review.
Only **P1 DEL alias** is the next firmware implementation package. Other items
remain separately scoped follow-ups; they are not merged into this release.
The [consolidated inventory](routeb-current-compatibility.md) separates source,
runtime, USB and owner evidence. The [DEL contract](del-alias-design.md) defines
the first change.

| Order | Current problem and smallest benign reproducer | Boundary, verification and finite finish line |
|---|---|---|
| P0 — inventory | The historical current inventory still calls H1, bounded lock waits and standalone REPEAT unsupported. | Consolidate against the selected201-file composition and later closeouts. Preserve original historical reports. No hardware/build; finish with the supported-profile statement and evidence matrix. |
| P1 — DEL alias | `DEL` rejects while `DELETE` works; the official quick reference lists both. | Exact alias usage0x4c through existing key/report paths, preserving DEL() functions. Composed tests and guarded clean target/review package. Finish with alias parity, no source-behavior regressions and bound artifact identities. |
| P2 — admission diagnostics | Invalid encoding is rejected, but a fresh adapter can return no typed error; a reused adapter can expose an earlier compiler error. Reproducer: prior compiler error, then invalid non-ASCII source on a new request. | Separate adapter-owned reset diagnostic, existing status schema, InvalidSource/code2 at the physical fault line and terminal Error/Capability with zero HID. Test fresh/reused adapters, chunks/Retry/BOM/CRLF, STOP and later valid run. Keep accepted bytes/limits unchanged. Oversized-file classification is deferred; do not silently expand scope. |
| P3 — profile/limits/lifecycle clarity | Alternative linked layout tables and source versus IR bounds can look like support. A non-US device locale is refused by Route B; a short source can still exceed128 IR instructions. | Explain the current US/ASCII contract and actual bounds. Use exact printable fixtures and expected failures; no new locale/Unicode promise or raised limits. Document injection STOP versus a host process already launched. Documentation-only work needs no target build. |
| P4 — synthetic lab evidence | Technique labels can exceed what G10/G11 and fixed EDR1 observed. | Use fake records, fixed local fixtures/hash checks, memory sinks and a visible lab-owned input field only. Preserve G10/G11 scope; no credential collection, global hooks, arbitrary transfer or protocol expansion. Finish at those fixture mechanics, not a whole-laptop security claim. |

P1 depends only on the verified baseline/P0 identity record. P2 is independent
and must explicitly select its baseline rather than making P1 a speculative
prerequisite. P3/P4 need neither canonical INJECT_VAR nor Windows hardware.
Every firmware change needs its own actual-composition tests and guarded target
integration; a documentation-only increment needs neither a rebuild nor a
physical campaign.

The admission diagnostic issue is source-supported. It concerns misleading
reporting, not an observed bypass of retained-source rejection. Relevant old
source tests check rejection/no HID but do not establish exact diagnostics or
cross-request error isolation. This coverage gap does not reopen accepted owner
milestones. A future P2 must distinguish newly executed tests from old receipts.

## Contracts that remain unresolved or excluded

- Canonical INJECT_VAR needs independently established numeric runtime values
  correlated with generated, stored/copied and repeatedly injected keycodes.
  Compiler instructions/selectors/language-table cells and H1 self-consistency
  do not settle this. Preserve all unresolved vectors and completed checks.
  Reconsider a specific authoritative mapping or genuine paired observation;
  do not restart broad searches or expand the decoder to remove a label.
- Checked uint16 arithmetic and eager Boolean evaluation remain project policies.
  Establish primary reference behavior before changing overflow/order/side effects.
- LED reports concern this interface/session. Preserve fresh/unknown/stale
  distinctions, no fabricated OFF, no automatic host-global normalization.
- EDR1 remains the unchanged fixed `EVILDUCK TEST 123` receiver; historical
  acceptance is not general EXFIL/loot compatibility or fresh current-build
  verification. No whitelist, capacity, sender or protocol expansion.
- Dynamic modes/identities, trusted-device impersonation, credential harvesting,
  system-wide input capture, covert transfer and evasion are not work packages.
  Host lab demonstrations do not imply native firmware support or elevated rights.

All future review packages must retain unchanged exact source/text-v2 rollback
`cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`
(1,413,200 bytes). It is older standalone application recovery without later
privacy/dashboard fixes, not restoration of scripts/settings/filesystems.
