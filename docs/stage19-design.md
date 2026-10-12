# Stage 19 decisions recorded before production changes

Baseline: 07864bb151ed4b38cc22b02ea1ea9569cc78c78b. No SDK binary patch,
read-only flag substitution, flash-write interception or new NVS repair is authorized.
Keep the exact Stage18 dependency pin and protection unchanged. Strict SDK immutability
is not established; migration stays NO-GO.

## Settings compatibility decision

Existing load ignores Preferences::begin and getter errors; all failures can become
default values, and storage/HID start before validation. Replace only settings loading
with typed, read-only NVS calls and add a readiness query. A genuinely absent namespace
or key uses in-memory defaults without writing. Type mismatches, I/O failures and invalid
stored settings fail closed. Strings have a bounded 4000-byte maximum (SDK single-page
string limit), SSID 1..32, AP password 8..63, channel 1..13, RGB <=0xffffff, Boolean
values 0/1, delay minimum <= maximum. Enabled autorun requires a nonempty script name.
Previously invalid persisted settings silently normalized; they will now disable startup
rather than be silently replaced. Valid settings and explicit normal-operation save/reset
commands retain their interfaces. Loading publishes values only after all reads succeed.
No credential or value is logged. Save is refused after failed load.

Normal setup validates settings before LED/HID/locale/attackmode/filesystem/web/CLI
activation. A settings failure is latched for this boot, logs an error code only and
runs only the existing yielding diagnostic loop. Safe-start never loads settings and
remains quiescent. No automatic retry or arming. Runtime save atomicity, later Wi-Fi NVS
writes, and SDK recovery before setup remain outside this guarantee.

## Offline inspection contract

Inspect exactly five 4096-byte plaintext NVS pages at 0x9000/0x5000, never execute or
write owner inputs. Verify header/entry/data CRCs, bitmap/span consistency, supported
versions/types, namespaces and duplicate records where possible. Output only structural
counts, page/entry indices and generic issue codes: no keys, namespaces, credentials
or values. Complex cross-page blob relationships not fully proved are insufficient
evidence, not a compatibility pass. Report compatible-within-checks, invalid,
recovery-potentially-required, unsupported-format or insufficient-evidence. A clean
structural result is not an SDK immutability certificate or migration authorization.

Owner hashes/sizes are owner-verified locally, not Codex-inspected. Full owner preflight
must still run privately on the Mac. Synthetic SDK source execution is distinguished
from execution of the actual Xtensa archive and from physical startup.
