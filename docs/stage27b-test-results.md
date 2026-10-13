# Stage27B executed test results

Current mock-only core tests; no historical counts are reused.

| Case group | Result | Assertions |
|---|---|---:|
| harmless_fixture_files | PASS | 13 |
| empty_comments | PASS | 30 |
| line_endings_whitespace | PASS | 24 |
| all_numeric_operators | PASS | 168 |
| precedence_and_grouping | PASS | 88 |
| variables_global_redeclaration | PASS | 43 |
| constants_replacement | PASS | 48 |
| if_else_chains | PASS | 30 |
| while_and_mixed_flow | PASS | 16 |
| inactive_side_effects | PASS | 8 |
| functions_and_returns | PASS | 29 |
| named_key_event_order | PASS | 18 |
| delay_clock_and_wrap | PASS | 13 |
| retry_does_not_duplicate | PASS | 9 |
| cancellation_and_sink_errors | PASS | 32 |
| budgets_and_no_progress | PASS | 21 |
| clean_sessions_and_borrowing | PASS | 24 |
| reentrant_callbacks | PASS | 10 |
| malformed_structure_zero_events | PASS | 64 |
| arithmetic_and_syntax_failures | PASS | 139 |
| unsupported_explicit_rejection | PASS | 77 |
| source_and_table_limits | PASS | 99 |
| nesting_and_expression_boundaries | PASS | 46 |
| deterministic_source_mutations | PASS | 1500 |
| no_core_heap_allocations | PASS | 4 |

Total: 25 PASS, 0 FAIL; 2553 assertions.
ASan/UBSan and leak detection enabled and clean. One group includes500 deterministic
source mutations; these are safety checks, not500 separately counted compatibility features.
The no-allocation probe counts C++ new on the tested normal compile/evaluate path. External
sink/vector/exception allocation and physical heap behavior are outside that observation.
Historical XPASS/XFAIL/unsupported observations were not rerun or relabeled.
