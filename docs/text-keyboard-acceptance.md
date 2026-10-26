# Short TextEdit acceptance — review only

Candidate: `ROUTEB-TEXT-KEYBOARD-v1`. No installation or physical testing is authorized by this sheet. Keep accepted `ROUTEB-RANDOMIZATION-JITTER-v1` and its exact rollback package until a separate owner review authorizes installation.

For a future authorized trial: use macOS High Sierra10.13.6, blank TextEdit, intended input source recorded, Caps off, no manually held modifiers and explicit Route B selection. Keep STOP accessible and autorun disabled. One explicit Start per trial; no automatic replay. No LED helper is needed.

## 1. Text-block aliases

```ducky
STRING_PYTHON
    111join
    222done
END_STRING
ENTER
STRINGLN_HTML
333line
444done
END_STRINGLN
```

Expect exactly three lines:

```text
111join222done
333line
444done
```

The language labels do not execute Python or HTML. Associate visible text with the same request's Completed status.

## 2. Inline repetition

```ducky
REPEAT 3 STRINGLN repeat
```

Expect three lines containing exactly `repeat`. The command repeats the inline statement, not a previously executed line.

## 3. RESET and continued execution

```ducky
HOLD SHIFT
STRING abc
RESET
STRINGLN def
```

Expect `ABCdef` on one line and Completed status. Confirm subsequent harmless manual lowercase typing works. This observation does not establish general host-global key-release or USB-retirement guarantees.

## 4. STOP and Shift recovery

```ducky
HOLD SHIFT
DELAY 10000
STRING BAD
RESET
```

Press STOP during the delay. Require Cancelled, blank TextEdit and normal manual lowercase afterward. No later `BAD` may appear.

## 5. Malformed retained source

```ducky
STRINGLN_PYTHON
111BAD
END_STRING
```

Require compile rejection before output, with TextEdit blank. Record actual line/code/request diagnostics rather than predicting them. Exhaustive alias, REPEAT, reset-queue and boundary cases stay automated.

Preserve screenshots, build/package identity, time, input source and available request/boot/session identifiers; leave missing identifiers unknown. Classify missing evidence UNVERIFIED, identified host/tool constraints PLATFORM-LIMITED and demonstrably incorrect behavior only within the tested conditions FAIL. No broad Caps diagnostic campaign is needed.
