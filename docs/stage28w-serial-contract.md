# Stage28W bounded serial and owner progress

In the enabled candidate only, `cli::update` checks the bound owner task, rejects
reentry, and makes at most64 read attempts per invocation. LF frames a command;
CR is ignored but still consumes work budget. Negative read returns early. Partial
input is carried in a static513-byte array: at most512 data bytes plus terminator.
The513th data byte or embedded NUL discards the **entire** command until LF, emits
one rejection at that LF, and resets framing. No truncated prefix executes. There
is no unbounded String growth for an incomplete serial line.

Each actual operational loop first progresses duckscript/com, then consumes this
serial budget, then returns through the existing loop delay. Continuous available
input cannot cause this CLI drain to stay in its while loop indefinitely. Actual
native loop tests run the enabled setup/loop and real compiler/scheduler with an
always-available serial fake and demonstrate completion. They prove work/owner
turn progress in that fixture, not physical wall-clock latency or RTOS fairness.
A completed idle legacy command can still perform existing synchronous work; this
change does not make all legacy filesystem/CLI operations constant-time.

STOP publication retains its priority flag outside the ordinary four-entry queue.
It cannot jump ahead of unread serial bytes or an incomplete/overlong frame. With
128 backlog bytes plus LF then STOP in the fixture, consumption takes three turns.
An endless frame without LF never becomes STOP; the framing policy is explicit.
After STOP/loss is published, the owner polls before its next source tick as in U/V.
An authenticated HTTP STOP also needs a safe authentication snapshot; contention
fails closed rather than falsely authorizing it. There is no instantaneous-stop
or host-release promise.

`routeb <path>` still publishes a copied95-byte path; ordinary run stays legacy.
Only the owner opens/captures/verifies/compiles/executes. The8,192-byte source cap,
32-byte reads, second byte comparison, explicit volume selection and MSC/stream
refusals are unchanged. Once verified bytes are owned by the Adapter, Runtime
executes memory; changing media is not reread for execution. This is not a physical
snapshot guarantee against outside writers. Pending/clearing states remain busy;
ambiguous called-false/loss permanently quarantines the session, with no retry.

The negative control changes the **actual scratch CLI budget** to65 and runs the
same W10 assertion. It fails with the budget diagnostic; no artificial final
assert, sanitizer suppression or unbounded/watchdog-killed loop is used. Default-
off keeps its original String/serial/WS/file-response policy and is separately
regression-tested and clean-linked. No grammar or new automatic arming is added.
