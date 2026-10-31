# Owner correction: inherited lock-wait acceptance is 3/3 PASS

On **October 31, 2026**, the owner explicitly confirmed **three planned inherited lock-wait groups, three scoped passes** on High Sierra with **ROUTEB-INJECT-VAR-H1-EXPERIMENTAL-v1**. The group outcomes are:

1. Settings/default5000, assignment/readback10000, keyboard RESET preservation, and a separate new-run default5000 check: **PASS**, successful Requests **1 and 2**.
2. Passive configured CAPS_CHANGE expiry: **PASS**, Request **3**, correlated waiting followed by Deadline9 / Timeout26 / physical line3 and owner-confirmed blank TextEdit.
3. STOP during the held-Shift wait and manual recovery: **PASS**, Request **6**, correlated waiting then Cancelled2/error0, owner-confirmed blank TextEdit until normal manual lowercase `abc`.

The owner clarified that **attempts 4 and 5 were test-handling mistakes**, not two more planned acceptance tests and not demonstrated firmware failures. They are **excluded from the acceptance count**. There is no outstanding failed group or owner-requested retest for this milestone.

This clarification does not fabricate or replace original evidence. The earlier Request4 record remains inconclusive about entry into the intended wait. Request5 still has no supplied capture/behavior record. Neither is relabeled as a successful execution. The owner's explanation of handling mistakes is an attributed later clarification, while the original logs, screenshots and historical records remain preserved.

See the dated addition to [the lock-wait closeout](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-lock-wait-owner-closeout.md) and its [structured record](https://github.com/tyronecoe/EvilDuck/blob/routeb-h1-right-modifiers-v1/docs/h1-lock-wait-owner-closeout.json), which retains the original evidence and appends the handoff's identity and clarification. These request numbers belong to the inherited lock-wait sequence only. They do not overwrite the separate earlier four-check H1 milestone's inconclusive Request2 or unknown successful STOP ID.

The result remains scoped owner-operated acceptance, not Codex hardware operation, an independent device-image readback, precise timing, all-nine-wait certification or canonical Hak5 numeric encoding. H1 remains experimental, and exact accepted source/text-v2 rollback remains mandatory: **1,413,200 bytes**, SHA-256 `cf42dea0570dcf491c46677aa87dd28bd6347f1617b0eea73ac670b52ba81f02`.

This correction is bundled with the separately authorized right-modifier implementation/build/package work. No repeated physical milestone, firmware installation or new hardware test is authorized by the correction.
