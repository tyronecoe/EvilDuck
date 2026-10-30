# Prepared genuine-DS3 reference observation — not executed

This kit is a **prepared experiment**, not an observed Hak5 runtime result, a device-authenticity check or authorization to use hardware. Only synthetic constants and generated key values are involved. It never asks for ordinary host files, credentials, keystroke capture or a complete original loot file. No EDR1/lock-key reflection is needed. A separately authorized genuine official DS3 operator and reviewed compiler/device context are required before physical use.

The existing focused report at `/workspace/outputs/inject-var-focused-validation/REPORT.md` distinguishes compiler bytes from runtime values. Public source evidence is recorded in [this stage's evidence review](inject-var-experimental-evidence.md). Documented `VAR $FOO = 1337` / `EXFIL $FOO` syntax comes from the saved official variable-exfiltration page, section Variable Exfiltration, and captured `handleExfilVar` lines7430–7443. It emits a variable reference, not a runtime observation. Exact random-keycode property names and INJECT_VAR syntax are in that same pinned compiler capture. These review snippets have **not** been run on a device or submitted here through the entire official compiler/UI. Official compilation is a later explicit gate; do not silently alter snippets if it rejects them.

## Gate A — calibrate the synthetic append channel first

Record official device model/generation, any exposed firmware version, authenticity limitations, compiler identifier, selected US language-map SHA256, exact source SHA256, compiled-artifact SHA256, host OS/input source, Caps state and run identifier. Preserve the initial output length/hash and exact appended-region offset. Keep unrelated existing content local and out of the test receipt. Do not delete, reformat or upload existing media/content.

Review and compile the following synthetic-only calibration snippet using the selected official compiler before a separately authorized run:

```ducky
VAR $MARK_A = 0x1234
VAR $MARK_B = 0x00FF
VAR $MARK_C = 0x0100
EXFIL $MARK_A
EXFIL $MARK_B
EXFIL $MARK_C
```

The parser supports **only** a six-byte result matching these three uint16 constants unambiguously in little or big byte order. Expected alternatives are `3412ff000001` and `123400ff0100`. Neither is assumed in advance. Extra headers, padding, missing bytes, alternate width, reordered writes, unexpected append data or a lack of flush/completeness evidence leave framing **UNRESOLVED**. Preserve the observation and stop rather than trim until it fits. A supported six-byte calibration establishes the selected channel's observed framing for that run only, not the keycode encoding. Never inject these constants.

Use `mode="calibration"` in the bounded JSON receipt below. The tool reads only this explicit generated-data receipt. It does not open a device, inspect media or search for loot files. The append offset is owner-recorded provenance, not authenticated by the parser.

## Gate B — capture originals and copies around each injection

Only after Gate A, a separately reviewed finite run may use the same three marker variables and emit their three EXFILs at the start and again at the end. Between marker blocks, execute the following for each property, **once**, in this fixed order:

| Group | Exact property |
|---|---|
| lower | `$_RANDOM_LOWER_LETTER_KEYCODE` |
| upper | `$_RANDOM_UPPER_LETTER_KEYCODE` |
| number | `$_RANDOM_NUMBER_KEYCODE` |
| special | `$_RANDOM_SPECIAL_KEYCODE` |

For each group, use distinct ordinary original/copy variables and this pattern:

```ducky
VAR $ORIGINAL_L = $_RANDOM_LOWER_LETTER_KEYCODE
VAR $COPY_L = $ORIGINAL_L
EXFIL $ORIGINAL_L
EXFIL $COPY_L
INJECT_VAR $COPY_L
EXFIL $ORIGINAL_L
EXFIL $COPY_L
INJECT_VAR $COPY_L
EXFIL $ORIGINAL_L
EXFIL $COPY_L
ENTER
```

Repeat the pattern with unique variable names and the next exact property. Do not resample, wait for a preferred random character, inject guessed numeric constants or automatically replay a failed trial. The four visible pairs can be any characters the getters choose; preserve exact case and punctuation, including unexpected differences. An owner must deliberately focus a blank plain-text editor before the approved injection phase; no host shell command is typed. Record US input source, Caps off and no held keys rather than infer them from output. Obtain screenshots/observations attributable to the same run. Optional specifically scoped HID input-report evidence is stronger than text-derived expectations, but never monitor unrelated typing.

Each group records **six uint16 words / twelve bytes**: original and copy before injection, after the first injection and after the second. This refines the older before/after-pair proposal so mutation after either injection can be localized. The full narrow supported frame is **60 bytes**: six-byte prefix markers + four twelve-byte groups + six-byte suffix markers. This is a **parser-supported format to verify**, not a claim that unexecuted EXFIL necessarily produces it. Recheck both marker blocks; any other result is unsupported evidence, not a reason to discard bytes.

This experiment separates selection, scalar copying, injection and mutation. Matching H1 for these four samples would not settle every printable, firmware version, modifier, language, invalid value or release behavior. An H2, ASCII-like or otherwise inconsistent result must remain a counterexample. Table indices/tags require a separately specified mapping; they are not disproved merely because H1 is convenient.

## Explicit synthetic-only receipt and offline parser

Create a small JSON receipt containing **only the generated appended region**, with these required fields:

```json
{
  "format": "synthetic-ds3-reference-capture-v1",
  "mode": "four-groups",
  "synthetic_data_only": true,
  "append_offset": 0,
  "capture_length": 60,
  "capture_hex": "REPLACE_WITH_EXACT_GENERATED_REGION_HEX",
  "capture_sha256": "REPLACE_WITH_SHA256_OF_THOSE_60_BYTES",
  "metadata": {
    "device_model": "RECORD_ACTUAL_MODEL",
    "device_firmware": "RECORD_EXPOSED_VERSION_OR_UNAVAILABLE",
    "compiler_id": "RECORD_ACTUAL_COMPILER",
    "language_map_sha256": "RECORD_64_LOWERCASE_HEX_DIGITS",
    "source_sha256": "RECORD_64_LOWERCASE_HEX_DIGITS",
    "compiled_sha256": "RECORD_64_LOWERCASE_HEX_DIGITS",
    "host_os": "RECORD_ACTUAL_OS",
    "host_layout": "US",
    "caps_lock": false,
    "authenticity_limitations": "RECORD_WHAT_IS_OWNER_REPORTED_OR_UNVERIFIED",
    "run_id": "RECORD_THIS_RUN"
  },
  "observations": [
    {"group":"lower","property":"$_RANDOM_LOWER_LETTER_KEYCODE","visible_pair":"REPLACE","visible_evidence_id":"RECORD"},
    {"group":"upper","property":"$_RANDOM_UPPER_LETTER_KEYCODE","visible_pair":"REPLACE","visible_evidence_id":"RECORD"},
    {"group":"number","property":"$_RANDOM_NUMBER_KEYCODE","visible_pair":"REPLACE","visible_evidence_id":"RECORD"},
    {"group":"special","property":"$_RANDOM_SPECIAL_KEYCODE","visible_pair":"REPLACE","visible_evidence_id":"RECORD"}
  ]
}
```

The placeholders deliberately fail validation. For Gate A use mode `calibration`, length6 and its exact generated hex/hash; observations can be omitted. Do not invent missing provenance: a required identifier unavailable for a particular device should explicitly say UNAVAILABLE and explain that authenticity limit; required hashes cannot be fabricated. Full-stage review must resolve evidence adequacy even if the structural parser accepts a string identifier.

Run the read-only Python3.8-compatible parser on that explicit receipt:

```bash
python3 tests/inject_var_experimental/reference_results.py --receipt generated-reference-receipt.json
```

It requires bounded regular non-symlink JSON, explicit offset/length/hash, US context, exact calibration and all four group observations. It does not modify input, scan directories or read a raw/private loot file. Output preserves six scalar observations per group and reports copy/mutation differences. H1/H2/ASCII comparisons are hypotheses against text-derived US usage/modifier expectations, **not captured USB reports**. `official_runtime_value` stays null, canonical status stays false, and owner-supplied metadata does not attest device genuineness. Even a parsed capture needs human/source/run review before changing the reference contract.

Synthetic parser tests are run by `python3 tests/inject_var_experimental/test_reference_results.py`. Little/big-endian and H1/H2 examples in those tests are manufactured cases for parser correctness only, not genuine DS3 observations. Corruption, truncation, extra bytes, wrong groups, unsupported host context and missing evidence fail closed. Mutation is preserved as a finding, not normalized away. No test uses private files, real HID or hardware.
