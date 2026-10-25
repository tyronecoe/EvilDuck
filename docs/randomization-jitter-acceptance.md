# Short benign TextEdit acceptance — review only

Candidate `ROUTEB-RANDOMIZATION-JITTER-v1`. Do not install or run this sheet until separately owner-authorized. Keep the accepted uppercase rollback. Use explicit Route B, autorun disabled, blank TextEdit, intended input source recorded, Caps off and no manually held modifier. Keep STOP accessible. One explicit Start per trial; no automatic retries. No LED helper is needed.

## Character groups and jitter

```ducky
STRINGLN aAzZ0123
VAR $n=10
WHILE $n>0
RANDOM_LETTER
$n=$n-1
END_WHILE
ENTER
VAR $n=10
WHILE $n>0
RANDOM_NUMBER
$n=$n-1
END_WHILE
ENTER
VAR $n=10
WHILE $n>0
RANDOM_SPECIAL
$n=$n-1
END_WHILE
ENTER
VAR $n=10
WHILE $n>0
RANDOM_CHAR
$n=$n-1
END_WHILE
ENTER
$_JITTER_ENABLED=TRUE
$_JITTER_MAX=200
STRINGLN aAzZ0123
$_JITTER_ENABLED=FALSE
STRINGLN aAzZ0123
```

Expect four10-character random lines within their specified sets; repeats are valid, no particular sequence is expected. First/final controls must match. The jittered line may look uneven; visual observation does not measure exact jitter distribution or USB latency. Record input source, request and Completed status with screenshot; missing IDs remain unknown. Exhaustive timing/range tests stay automated.

## Numeric branching

```ducky
$_RANDOM_MIN=20
$_RANDOM_MAX=50
VAR $v=$_RANDOM_INT
IF $v>=20 && $v<=50 THEN
STRINGLN RANGE_OK
ELSE
STRINGLN RANGE_BAD
END_IF
$_RANDOM_MIN=7
$_RANDOM_MAX=7
IF $_RANDOM_INT==7 THEN
STRINGLN EQUAL_OK
END_IF
```

Expect exactly RANGE_OK and EQUAL_OK on two lines. No decimal printing or INJECT_VAR inference.

## STOP recovery

```ducky
HOLD SHIFT
$_JITTER_ENABLED=TRUE
$_JITTER_MAX=65535
DELAY 10000
STRING BAD
RELEASE SHIFT
```

Press STOP during the explicit delay; expect Cancelled, blank TextEdit and normal manually typed lowercase afterward. Automated tests cover STOP inside a pending jitter interval without relying on a lucky physical random delay.

## Malformed retained source

```ducky
RANDOM_CHAR extra
STRING BAD
```

Expect compile rejection at line1, TextEdit blank. Record actual diagnostics and request; do not predict IDs. Preserve screenshots and build/app identity. Classify incomplete evidence UNVERIFIED and host-specific limitations PLATFORM-LIMITED. This short sheet does not authorize a broad Caps investigation or any further payload.
