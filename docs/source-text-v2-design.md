# Terminated alias v2 contract

Baseline `1659544f392a0523fa6e598423001e11919370aa`; branch `routeb-source-text-portability-v2`; build `ROUTEB-SOURCE-TEXT-PORTABILITY-v2`. Published source/text v1 is unchanged and was not physically accepted. Rollback remains accepted restart application1,412,688 bytes / `1d4ea6394306885b832619adb3436eaeeccc0a67ce8b73e1f20dd0f9c7d0a060`.

## Supported forms and precedence

For POWERSHELL, BATCH, BASH, JAVASCRIPT, PYTHON, RUBY and HTML:

```ducky
STRING_PYTHON hello END_STRING
STRINGLN_PYTHON hello END_STRINGLN
```

The single final whole matching closing token is syntax for suffixed aliases only. Remove that token and its immediately preceding ASCII space, then use ordinary STRING/STRINGLN operand expansion and delivery. All14 simple space-delimited forms have selected pinned-compiler-function evidence. No official runtime, language execution, scancode contract or USB-delivery equivalence is inferred.

## Explicit ambiguity and whitespace policy

* Ordinary unsuffixed STRING/STRINGLN remain literal, including `STRING hello END_STRING` and `STRINGLN hello END_STRINGLN`. No global stripping is introduced. Use these commands for literal closing-token text.
* Suffixed alias operands may contain at most one raw standalone END_STRING/END_STRINGLN token. It must be final, match the family and have an ASCII-space delimiter. Reject wrong-family, multiple, nonfinal, empty terminated operands and tab-only delimiter separation before output.
* The current leading/trailing horizontal-whitespace normalization and ordinary payload whitespace rules remain. Whitespace variants beyond the verified single-space examples are explicit EvilDuck policy, not exact reference-compiler equivalence. The reference regex accepts a tab case which its argument handler fails; v2 rejects that delimiter form instead of reproducing the error.
* END_STRINGx/END_STRINGLNx are not closing tokens. Never strip matching substrings. Quotes have no special escaping meaning; tokenization remains the existing whitespace-based language policy.
* Determine delimiter grammar from raw source **before DEFINE**. Expand only the resulting operand. A DEFINE value can emit literal END_STRING bytes but cannot create grammar, and expanded text is not reparsed.
* Argument-free aliases keep their accepted multiline behavior with canonical terminators. Inline-looking content inside a block remains literal. Nonterminated aliases without raw closing tokens remain EvilDuck extensions.
* Inline REPEAT uses the same terminated-alias parser, total128IR/count2–128 bounds, shared operand storage and cooperative expansion. Repeated block openers remain unsupported.

The pinned compiler's `replace(" END_STRING", "")` removes its first substring occurrence, including from END_STRINGx. Multiple-delimiter and prefix edge probes reproduce that quirk. V2 deliberately uses a safe final-whole-token subset instead. See the reference receipt for exact observations; do not claim exhaustive official compiler compatibility.

## Preservation

The reviewed BOM contract is unchanged: exactly EF BB BF at raw offset zero, bytes retained within8192raw source limit, split/Retry-safe validation, all other encoding restrictions retained. Preserve ordinary text, blocks, DEFINE, diagnostics, preprocessor exclusions versus retained inactive branches, held merging/rollover, retries, STOP, restart budgets/lease/identity, quarantine, authentication and EDR1. No new locale, USB/partition/core/SDK/settings/PSRAM change. INJECT_VAR stays blocked.
