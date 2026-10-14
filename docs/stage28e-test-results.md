# Stage28E fresh executed results

Six fresh suites compile current modules with ASan/UBSan and leak detection.
Historical firmware XPASS/XFAIL/observations remain unchanged and are not counted as new passes.

| Suite | PASS | FAIL | Assertions |
|---|---:|---:|---:|
| stage27b_regression | 25 | 0 | 2543 |
| stage28a_regression | 23 | 0 | 526 |
| stage28b_regression | 26 | 0 | 4733 |
| stage28c_regression | 17 | 0 | 390573 |
| stage28d_regression | 21 | 0 | 14989 |
| stage28e_new | 24 | 0 | 109591 |
| Total | 136 | 0 | 522955 |

Counts include per-step/report/source invariants, not522955 supported features. No skipped/XFAIL/XPASS in these preview suites.
Rejection tests prove safety behavior, not support for rejected syntax or hardware.

Separate portable smoke: PASS on Linux GCC ASan/UBSan/leak,9 exact reports/4 keyboard acks/1 Delay.
Native Mac/Apple clang: SKIP_ENVIRONMENT, unexecuted; not included in group/assertion totals.

## stage27b_regression

| Exact group | Status | Assertions |
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
| unsupported_explicit_rejection | PASS | 67 |
| source_and_table_limits | PASS | 99 |
| nesting_and_expression_boundaries | PASS | 46 |
| deterministic_source_mutations | PASS | 1500 |
| no_core_heap_allocations | PASS | 4 |

## stage28a_regression

| Exact group | Status | Assertions |
|---|---|---:|
| required_fixture | PASS | 7 |
| assignment_forward_nested_arithmetic | PASS | 8 |
| return_of_call_and_boolean | PASS | 8 |
| if_else_if_selected_calls_only | PASS | 6 |
| while_reevaluation_zero_iteration | PASS | 8 |
| left_to_right_capture_eager_power | PASS | 14 |
| delay_call_single_timing_owner | PASS | 12 |
| static_void_unknown_arity_zero_output | PASS | 52 |
| runtime_void_no_stale_return | PASS | 19 |
| depth_limit_cycles_and_frames | PASS | 32 |
| arithmetic_results_and_source_mapping | PASS | 31 |
| cancellation_stop_suspended_and_restart | PASS | 21 |
| retry_failure_timeout_and_budget_during_call | PASS | 26 |
| bounded_work_cooperative_and_reentrant | PASS | 27 |
| expression_function_token_limits | PASS | 21 |
| operators_with_function_operands | PASS | 144 |
| standalone_inside_value_call_no_leak | PASS | 8 |
| cancel_called_delay_and_restart_same_program | PASS | 17 |
| static_invalid_inactive_and_void_control_flow | PASS | 18 |
| define_call_and_mixed_function_control | PASS | 10 |
| suspended_clock_timeout_and_sink_exception | PASS | 14 |
| static_truth_facts_preserve_eager_calls | PASS | 18 |
| no_heap_multiple_continuations | PASS | 5 |

## stage28b_regression

| Exact group | Status | Assertions |
|---|---|---:|
| official_fixture_files | PASS | 14 |
| inline_commands_unchanged | PASS | 12 |
| empty_blank_adjacent | PASS | 24 |
| whitespace_preservation | PASS | 18 |
| source_endings_bom_eof | PASS | 33 |
| raw_commands_not_declarations | PASS | 24 |
| terminator_lookalikes_literal | PASS | 12 |
| malformed_structure_zero_events | PASS | 69 |
| forward_constants_boundaries_literal_hash | PASS | 24 |
| if_else_selection_and_inactive | PASS | 12 |
| while_zero_one_many | PASS | 18 |
| forward_nested_expression_function_blocks | PASS | 26 |
| source_line_arena_code_exact_limits | PASS | 46 |
| constant_expansion_exact_overflow_locations | PASS | 21 |
| compact_instruction_and_blank_metadata_limits | PASS | 13 |
| retry_character_and_enter_exactly_once | PASS | 7 |
| cancellation_at_every_output_boundary | PASS | 54 |
| stop_after_block_and_inactive_stop | PASS | 12 |
| sink_failure_exception_body_locations | PASS | 28 |
| reentrant_and_cancel_inside_callback | PASS | 13 |
| borrow_simultaneous_restart_revision | PASS | 17 |
| clock_wrap_stuck_tick_timeout_steps | PASS | 22 |
| one_attempt_per_tick_large_loop_text | PASS | 3274 |
| nested_structure_and_call_boundaries | PASS | 24 |
| bounded_seeded_block_mutations | PASS | 911 |
| no_heap_block_and_suspended_expressions | PASS | 5 |

## stage28c_regression

| Exact group | Status | Assertions |
|---|---|---:|
| memory_mock_chunk_equivalence | PASS | 4250 |
| empty_eof_bom_crlf_boundaries | PASS | 859 |
| source_line_expansion_boundaries | PASS | 168494 |
| table_and_arena_boundaries | PASS | 39951 |
| read_errors_pass_one_two_seek_exception | PASS | 1510 |
| zero_progress_retry_invalid_counts | PASS | 177 |
| cancel_every_phase_and_restart | PASS | 2552 |
| partial_line_block_cancel_boundaries | PASS | 800 |
| incremental_inventory_validation_work | PASS | 670 |
| reentrancy_and_callback_cancellation | PASS | 140 |
| runtime_borrow_multiple_sessions_destructor | PASS | 106 |
| stable_source_contract_and_failed_reuse | PASS | 397 |
| reader_lifetime_release_after_terminal | PASS | 95 |
| invalid_api_budgets_and_full_retry_limit | PASS | 131087 |
| seeded_chunk_mutations | PASS | 39169 |
| atomic_line_and_expression_worst_bounds | PASS | 313 |
| no_heap_compiler_read_and_inventory | PASS | 3 |

## stage28d_regression

| Exact group | Status | Assertions |
|---|---|---:|
| empty_sync_and_exact_single_key | PASS | 18 |
| all_modifier_bits_and_combinations | PASS | 8192 |
| two_owners_shared_keys_and_modifiers | PASS | 27 |
| idempotence_unmatched_invalid_usage_owner | PASS | 1035 |
| six_keys_seventh_reject_and_recovery | PASS | 43 |
| single_owner_capacity_and_reordering | PASS | 42 |
| persistent_transient_shift_and_lowercase_conflict | PASS | 28 |
| us_printable_mapping_reference_vectors | PASS | 1692 |
| unsupported_bytes_and_held_tap_policy | PASS | 40 |
| named_function_navigation_key_usage_vectors | PASS | 119 |
| retry_press_and_release_without_replay | PASS | 39 |
| cancel_all_phases_and_explicit_neutral_drain | PASS | 53 |
| failure_exception_and_uncertain_release | PASS | 51 |
| drain_retry_failure_and_retry_exhaustion | PASS | 25 |
| wrap_timeout_and_stuck_clock | PASS | 19 |
| reentrant_cancel_accepted_report_is_retained | PASS | 22 |
| queue_single_action_and_restart_isolation | PASS | 26 |
| budget_validation_and_noop_deduplication | PASS | 52 |
| seeded_ownership_property_ordering | PASS | 3005 |
| hostile_cancel_retry_throw_and_one_attempt_bound | PASS | 458 |
| zero_heap_planner_hot_path | PASS | 3 |

## stage28e_new

| Exact group | Status | Assertions |
|---|---|---:|
| initial_sync_and_identical_neighbors | PASS | 141 |
| mixed_us_punctuation_exact_vectors | PASS | 298 |
| multiline_blank_tabs_and_enter_order | PASS | 146 |
| function_continuations_and_control_flow | PASS | 158 |
| source_ack_waits_for_restoration | PASS | 46 |
| press_release_long_retry_no_replay | PASS | 427 |
| delay_timing_zero_and_two_segments | PASS | 89 |
| wrap_and_stalled_delay_clock | PASS | 100041 |
| persistent_modifier_restore_and_completion_cleanup | PASS | 61 |
| invalid_event_boundaries_and_bad_source | PASS | 23 |
| held_key_and_seventh_rejection | PASS | 60 |
| failed_and_throwing_report_sink | PASS | 106 |
| cancel_every_handshake_and_delay_phase | PASS | 614 |
| callback_cancel_accept_retry_throw | PASS | 63 |
| explicit_drain_only_neutral_and_failures | PASS | 82 |
| timeouts_after_press_and_attempt_budget | PASS | 38 |
| stop_runtime_arithmetic_and_step_limits | PASS | 91 |
| reentrant_report_source_and_program_borrow | PASS | 51 |
| multi_bridge_lifetime_restart_and_no_stale_ids | PASS | 59 |
| seeded_backpressure_exact_pairs | PASS | 6835 |
| sync_failure_and_cleanup_budget_boundaries | PASS | 63 |
| delay_acceptance_after_retried_restoration | PASS | 62 |
| callee_multiline_fault_source_location | PASS | 31 |
| zero_heap_bridge_pipeline | PASS | 6 |

## Development findings

- Initial test helper inclusion collided with renamed main macros; switched to Stage27B helpers directly
- New drain-budget test demonstrated stale neutral evidence could finish a NEW drain while it was Retry; fixed to require current Planner drain completion AND neutral evidence
- Added null-source-context guard, callee body-line diagnostics and independent sync/drain boundary checks

The real drain bug was fixed in code; no assertion or budget was weakened. Final24 new groups execute after the fix.
Only a pure Planner usage query is added; old routines/tests remain unchanged and pass.
