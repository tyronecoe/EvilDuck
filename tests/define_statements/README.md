# Bounded DEFINE statements

Additive, core-only overlay on publication `2ad87593bfde79d854c03045a68fe70d2ac49f72`
(firmware checkpoint `c9fd36c3e03b2d7ffa318b289398ff7dc1c9fd44`).
Historical sources, preparers, build selection and release identities are unchanged.
This directory is not an installable firmware or release.

A standalone, optionally indented constant label can now supply one ordinary
`$variable = expression`, nonempty inline `STRING`/`STRINGLN`, or `DELAY expression`.
Existing recognized commands/functions retain priority. Labels take no arguments.
Both bare and hash labels work; forward definitions remain available. The stored
replacement is parsed once, without substituting any constants inside it.
Assignments require an ordinary declared variable and retain initialization checks.

Example:

```text
DEFINE #STEP $count = ($count + 1)
VAR $count = 0
#STEP
IF ($count == 1) THEN
    STRING PASS
END_IF
```

Generated declarations, internal-setting assignments, blocks, functions, comments,
preprocessing and other commands reject. `#STEP argument`, recursive aliases and
`+=` reject. Existing constant/line/source/IR limits and checked arithmetic remain.
Malformed invocations in retained inactive branches or unused functions fail
preflight. Preprocessing exclusions remain separate. Macro invocations remain
barriers to standalone REPEAT, as previously unrecognized source was ineligible.
Diagnostics refer to the invocation's physical line. No public ABI/IR change.

Hak5's [constants documentation](https://documentation.hak5.org/hak5-usb-rubber-ducky/attack-modes-constants-and-variables/constants.md)
permits any DuckyScript syntax as a constant value; this implements only the leaf
subset above. It does not claim full DEFINE or DS3 conformance.

## Composition and focused checks

`prepare_sources.overlay(source)` applies the unchanged admission-diagnostics
parent chain then this patch and verifies all 201 production hashes.
`delta(source)` accepts only the exact parent core. `verify_final(source)` checks
the complete resulting inventory. Nothing redirects the canonical firmware builder.

Run from repository root with a fresh external directory:

```sh
python3 tests/define_statements/run_tests.py --output-dir /tmp/evilduck-define-statements
```

The runner reconstructs core.cpp/core.h/shortcut_keys.h and checks all three against
the pinned final admission inventory before applying the new patch. It compiles
only a Linux native test executable with ASan/UBSan and leak detection, then uses
an in-memory event sink with retry injection. No historical case is executed.
This is exact composed-module evidence, not full adapter/coordinator integration,
physical HID delivery, firmware compilation or hardware acceptance.

## Owner check (pending separate firmware/hardware authorization)

Manually focus a blank TextEdit document on High Sierra, select Route B, and use:

```text
DEFINE #STEP $count = ($count + 1)
DEFINE #MARK STRING ROUTEB_DEFINE_PASS
VAR $count = 0
IF FALSE THEN
    STRING FAIL
ELSE IF ($count == 0) THEN
    #STEP
ELSE
    STRING FAIL
END_IF
IF ($count == 1) THEN
    #MARK
END_IF
```

Require exactly `ROUTEB_DEFINE_PASS`, no `FAIL`, and request `Completed`; record
running build and request IDs. No shell, OS detection or STOP trial is involved.
This test has not been performed.

Rollback source identity is the publication/checkpoint above; remove this overlay.
Baseline build is `ROUTEB-ADMISSION-DIAGNOSTICS-H1-v1`, published application SHA-256
`fce91bca0774181a1be6bc691a1303d47f61caba49e979e89bfa678ef41f60f1`.
No installation or rollback operation is authorized or performed here.
