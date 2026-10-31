# Right-modifier candidate compatibility

Target: **ROUTEB-RIGHT-MODIFIERS-H1-EXPERIMENTAL-v1**, actual composed Route B. This additive candidate extends the tested H1 composition; the older root, legacy interpreter and standalone preview do not establish support in this profile. The accepted-default inventory remains historical evidence and is not silently promoted to H1.

| Capability | Candidate status and evidence boundary |
|---|---|
| `RCTRL`, `RSHIFT`, `RALT`, `RGUI` through chord, inline INJECT_MOD, HOLD/RELEASE | Added source names, documented **EvilDuck extensions**. Exact mapping is standard keyboard modifier bits `0x10/20/40/80`; production-source native tests and linked source evidence support software behavior. Physical results pending owner acceptance. |
| Left modifiers and aliases | Existing meanings and duplicate-physical-bit policy preserved. Left/right pairs remain distinct. |
| Persistent/transient reports, STOP, RESET, restart, error cleanup | Existing lease, operation correlation, restoration, refusal and neutral cleanup paths reused. New tests cover right-side interactions; no general host-release guarantee follows. |
| H1 stored-keycode INJECT_VAR | Existing opt-in experiment only, finite US-printable modifier zero/left-Shift whitelist. Right-side source names do **not** broaden numeric decoding. Genuine Hak5 encoding remains unresolved. |
| H1 owner milestones | Prior four-check H1 milestone unchanged. Inherited configurable lock waits are now **3/3 planned owner PASS groups** on High Sierra per owner clarification; attempts 4/5 are handling mistakes outside acceptance count, not outstanding failed groups. |
| Earlier language/text/randomization features | Inherited preprocessing, aliases, functions, HOLD/RELEASE, inline INJECT_MOD, randomization/jitter, RESET/restart and BOM policies retained. Relevant actual-composition regressions provide software evidence, not exhaustive language certification. |
| Lock feedback / EDR1 / USB infrastructure | Existing interface-specific evidence, wait semantics, fixed-message protocol, authentication, report IDs and descriptors preserved. No fresh physical certification of every lock/wait variant or platform. |
| Right Alt / international behavior | Right Alt bit is supported; generalized AltGr, dead keys, Unicode, new locale support or arbitrary host/layout behavior are not established. |
| Other firmware profiles | Default non-H1 builders and accepted source/text-v2 rollback remain unchanged. No automatic switch into this experimental candidate. |

See [the design contract](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-right-modifiers-design.md), source/test/build receipts in the release report and [the short acceptance sheet](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-right-modifiers-acceptance.md). Linux software checks and successful compilation do not constitute physical High Sierra validation. The next physical checks exercise only these new source names and right-side cleanup; no repeated broad Caps or H1 encoding investigation is required.
