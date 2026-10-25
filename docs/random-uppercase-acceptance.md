# Benign uppercase TextEdit acceptance — review only

Keep accepted `ROUTEB-RANDOM-LOWER-20261024-v1` installed until a separate owner review explicitly authorizes candidate installation. This sheet does not authorize hardware access, flashing, OTA or automatic script execution. No LED helper is needed; the existing helper v4 and EDR1 path remain unchanged.

For a future owner-authorized trial, verify candidate `ROUTEB-RANDOM-UPPER-20261025-v1` and package identity, disable autorun, use blank TextEdit, confirm Caps Lock off and no physically held modifiers. Select the intended Canadian or US input source and record it. Use explicit Route B Run or CLI `routeb`; do not assume a legacy Run path selects the same engine. Keep STOP accessible. One explicit Start per trial; no automatic replay.

## Mixed-case controls and ten random uppercase letters

```ducky
STRINGLN aAzZ0123
STRING BEGIN-
VAR $n=10
WHILE $n > 0
RANDOM_UPPERCASE_LETTER
$n=$n-1
END_WHILE
STRINGLN -END
STRINGLN aAzZ0123
```

Require the first and third lines to be exactly `aAzZ0123`. Require the middle line to contain `BEGIN-`, exactly ten A–Z letters, then `-END`. Repeated letters are valid; no particular sequence or uniqueness is required. Associate visible text with the same request's Completed status. Preserve screenshots, build/package identity, timestamp, host/input source and available request/boot/session identifiers. Missing identifiers remain unknown. Canadian/US lowercase PASS observations are recorded separately; they do not establish this candidate's physical acceptance or universal layout compatibility.

## STOP and Shift recovery

```ducky
HOLD SHIFT
DELAY 10000
RANDOM_UPPERCASE_LETTER
RELEASE SHIFT
STRING BAD
```

Press STOP during the delay. Require Cancelled, no random letter or `BAD`, and harmless manually typed lowercase afterward. Preserve evidence. Cleanup submission alone does not establish all host-global key-release or USB-retirement guarantees.

## Malformed retained source

```ducky
RANDOM_UPPERCASE_LETTER extra
STRING BAD
```

Require compile rejection before output, with TextEdit blank. Record the actual request, physical line and diagnostic code; do not infer them from a previous release. The same malformed command in a retained `IF FALSE` branch must also reject. Preprocessor-excluded text has its existing separate semantics.

Classify missing or ambiguous physical evidence UNVERIFIED, identified host/tool/environment limitations PLATFORM-LIMITED, and demonstrated incorrect behavior only within the tested conditions FAIL. Windows 11 remains later platform coverage; no claim is made before physical testing.
