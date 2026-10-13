# Stage28A exact fresh test results

| Group | Case | Result | Assertions |
|---|---|---|---:|
| new_expression_calls | required_fixture | PASS | 7 |
| new_expression_calls | assignment_forward_nested_arithmetic | PASS | 8 |
| new_expression_calls | return_of_call_and_boolean | PASS | 8 |
| new_expression_calls | if_else_if_selected_calls_only | PASS | 6 |
| new_expression_calls | while_reevaluation_zero_iteration | PASS | 8 |
| new_expression_calls | left_to_right_capture_eager_power | PASS | 14 |
| new_expression_calls | delay_call_single_timing_owner | PASS | 12 |
| new_expression_calls | static_void_unknown_arity_zero_output | PASS | 52 |
| new_expression_calls | runtime_void_no_stale_return | PASS | 19 |
| new_expression_calls | depth_limit_cycles_and_frames | PASS | 32 |
| new_expression_calls | arithmetic_results_and_source_mapping | PASS | 31 |
| new_expression_calls | cancellation_stop_suspended_and_restart | PASS | 21 |
| new_expression_calls | retry_failure_timeout_and_budget_during_call | PASS | 26 |
| new_expression_calls | bounded_work_cooperative_and_reentrant | PASS | 27 |
| new_expression_calls | expression_function_token_limits | PASS | 21 |
| new_expression_calls | operators_with_function_operands | PASS | 144 |
| new_expression_calls | standalone_inside_value_call_no_leak | PASS | 8 |
| new_expression_calls | cancel_called_delay_and_restart_same_program | PASS | 17 |
| new_expression_calls | static_invalid_inactive_and_void_control_flow | PASS | 18 |
| new_expression_calls | define_call_and_mixed_function_control | PASS | 10 |
| new_expression_calls | suspended_clock_timeout_and_sink_exception | PASS | 14 |
| new_expression_calls | static_truth_facts_preserve_eager_calls | PASS | 18 |
| new_expression_calls | no_heap_multiple_continuations | PASS | 5 |
| fresh_stage27b_regressions | harmless_fixture_files | PASS | 13 |
| fresh_stage27b_regressions | empty_comments | PASS | 30 |
| fresh_stage27b_regressions | line_endings_whitespace | PASS | 24 |
| fresh_stage27b_regressions | all_numeric_operators | PASS | 168 |
| fresh_stage27b_regressions | precedence_and_grouping | PASS | 88 |
| fresh_stage27b_regressions | variables_global_redeclaration | PASS | 43 |
| fresh_stage27b_regressions | constants_replacement | PASS | 48 |
| fresh_stage27b_regressions | if_else_chains | PASS | 30 |
| fresh_stage27b_regressions | while_and_mixed_flow | PASS | 16 |
| fresh_stage27b_regressions | inactive_side_effects | PASS | 8 |
| fresh_stage27b_regressions | functions_and_returns | PASS | 29 |
| fresh_stage27b_regressions | named_key_event_order | PASS | 18 |
| fresh_stage27b_regressions | delay_clock_and_wrap | PASS | 13 |
| fresh_stage27b_regressions | retry_does_not_duplicate | PASS | 9 |
| fresh_stage27b_regressions | cancellation_and_sink_errors | PASS | 32 |
| fresh_stage27b_regressions | budgets_and_no_progress | PASS | 21 |
| fresh_stage27b_regressions | clean_sessions_and_borrowing | PASS | 24 |
| fresh_stage27b_regressions | reentrant_callbacks | PASS | 10 |
| fresh_stage27b_regressions | malformed_structure_zero_events | PASS | 64 |
| fresh_stage27b_regressions | arithmetic_and_syntax_failures | PASS | 139 |
| fresh_stage27b_regressions | unsupported_explicit_rejection | PASS | 67 |
| fresh_stage27b_regressions | source_and_table_limits | PASS | 99 |
| fresh_stage27b_regressions | nesting_and_expression_boundaries | PASS | 46 |
| fresh_stage27b_regressions | deterministic_source_mutations | PASS | 1500 |
| fresh_stage27b_regressions | no_core_heap_allocations | PASS | 4 |

Total: 48 PASS, 0 FAIL; 3069 assertions.
ASan/UBSan and leak detection clean. All Stage27B preview regressions actually rerun on the
changed core. Historical other-stage results/XPASS/XFAIL were not rerun or relabeled. The500
seeded mutation checks remain one safety group, not500 compatibility features. Former call
rejection vectors moved into genuine positive coverage; old results remain historical.
