# Stage 20 SDK NVS preservation contract and deployment readiness

Baseline524d643a12af05e4efd9da509eae274ec43959a6; branchstage20-nvs-preservation-contract.
The commit containing this report identifies final source. Production source fingerprint
is in deployment/stage20/artifact-inventory.json. Stage21 has not begun.

An owner-evidence/blob-inspection follow-up now records the reported complete local
Stage19 preflight and SPIFFS roundtrip, implements bounded cross-page blob checks and
reruns all existing suites. Latest aggregate: **1170 PASS,0 unexpected FAIL,636958
assertions**, with historical classifications separate. The owner's ten insufficient
NVS findings remain unresolved pending an updated local run; migration stays NO-GO.
See [the follow-up report](stage20-blob-followup.md) for exact source rules, tests,
evidence boundaries and unchanged firmware measurements. The initial Stage20 report
and test inventory below are retained as historical evidence from commit1896d625.

A later owner update reports updated Stage20 local preflight and privacy-summary PASS,
NVS compatible-within-verified-checks with zero findings and SPIFFS roundtrip true.
Recorded in [the new owner evidence](stage20-owner-extended-preflight-evidence.json);
this supersedes the earlier pending local-run status without rewriting its history.
No owner binaries were inspected here, no regression results or firmware artifacts
changed, and SDK runtime preservation remains unresolved. Migration stays NO-GO and
Stage21 has not begun. The latest input to future candidate review is in
[the readiness checklist](stage20-readiness.md).

## Selected strategy and implementation gate

Current strategy: preserve independently retained original backups, privately inspect
structure/content preservation, export privacy-safe findings, and block migration/boot
until a reviewed preservation policy is established. No new SDK patch, guessed binary
rewrite, generic flash interceptor, fabricated success, automatic repair or partition
change. Stage16 HID + Stage18 Arduino protection + Stage19 settings/inspection guards stay.

Strict byte immutability of live NVS is NOT established in the writable profiles. SDK
Page/Storage recovery and reads can change bits/pages; logical preservation and backup
recoverability are distinct. Read-only handles do not prevent cleanup. New actual source
test specifically demonstrates corrupt-string cleanup returning NOT_FOUND after mutation:
Stage19 loader cannot distinguish that from genuine absence. Defaults may therefore be
selected without a surfaced read error. No claim that healthy return/structural CRCs prove
complete logical preservation is made.

A supported readonly-partition/quiescent-profile policy is a promising **deferred**
candidate: actual target archive tests readonly byte42/returns0x10d, actual native headers
compile with offsetof(readonly)==42, and full pinned target-source API bodies reject lower
flash calls in synthetic experiments. The current table/firmware does not enable it.
It changes recovery outcomes and prevents healthy settings/Wi-Fi saves. Exact complete
boot/bypass/descriptor/provenance/owner acceptance still needs separate review. Do not
silently replace the current table/profile with an experiment or weaken partition guards.

[Contract](stage20-contract.md), [architectures/selection](stage20-architectures.md),
[mutation-path evidence](stage20-mutation-paths.md), [owner workflow](stage20-owner-inspection.md),
[readiness](stage20-readiness.md), [reproduction](stage20-reproduction.md).

SDK-level implementation gate: nominal immutable source and exact archives recorded,
but source/binary equivalence/full isolated SDK source rebuild and a complete preservation
semantics/compatibility proof are not established. No production SDK-level change passes
all eight gate conditions. This stage is SDK investigation/test-only **plus targeted
application persistence hardening**, not zero production changes.

## Targeted production changes

Unchecked Preferences setters/commits replaced by typed raw NVS APIs. Validated RAM
settings before open; first set error stops remaining calls/commit; original error recorded,
handle closed and checked boolean returned. At most12setters+one commit, unchanged schema/
write order. Existing void save/reset wrappers retained; checked variants/error accessor
added. Failed load cannot be repaired/reset/saved automatically. Explicit reset retains
prior default-RAM behavior, but refuses invalid load before changing RAM.

Healthy CLI/web acknowledge success only after a checked result. Failures return explicit
CLI error/HTTP503; two web settings handlers use existing nonblocking TryGuard and return409
before edits when busy. Checked saves/reset also use TryGuard; per-call error is local,
latest diagnostic is one atomic32-bit value. This prevents conflicting known CLI/web
ownership without inventing a new queue/lock. Direct setters still require serialized
caller ownership. Active NVS writes remain synchronous; mutex refusal is nonblocking,
not a promise of bounded physical flash latency. USB callbacks/HID/MSC/language untouched.

No atomic multi-key transaction or rollback: a prefix may persist, a failing setter may
have effects, and commit can fail after changes. Pinned NVSHandleSimple::commit returns
OK for valid handles without a durability barrier. Error injection tests are API stand-ins,
not actual target commit fault tests. Mixed persisted autorun enable/script can remain
valid-looking after interruption. Nothing is silently disabled/repaired/erased to hide
that limitation; migration stays NO-GO. Runtime save errors do not retroactively undo RAM
edits or flash and no auto retry is added. Void diagnostics are generic/no values.

Private summary tool strictly whitelists published artifact/layout facts, generic NVS
classification/codes/locations and file count/bytes. It excludes keys, namespace/value
material, dynamic filesystem names, region digest and arbitrary private fields, rejects
unknown/mismatched input/overwrites and always says NO-GO. It projects a private report,
not authentication or fresh binary inspection. Owner-local hashes/sizes remain reported
facts; actual binaries/full structural findings are not supplied here.

## Executed regression and new tests

| Group | PASS | Unexpected FAIL | Other | Assertions |
| --- | ---: | ---: | --- | ---: |
| Previous Stage1–19 suites | 1033 | 0 | Original classifications retained | 636087 |
| Stage20 persistence/readonly source | 37 | 0 | 2 OBSERVED | 185 |
| Stage20 actual CLI/web handler paths | 13 | 0 | Mock services; no physical network | 47 |
| Stage20 privacy summary | 18 | 0 | Synthetic reports only | 22 |
| Stage20 native ABI/archive/final guards | 4 | 0 | Inspect/compile only | 12 |

**1105 current/prior PASS,0 unexpected FAIL,636353 assertions.** Counts are executed
contract tests, not compatibility percentage/independent hardware guarantees. Total
assertions include established historical/observation/sanity checks. Raw PASS records
including39historical routing passes=1144. Five language XPASS unchanged; no languageXFAIL.
Historical USB routing remains39PASS/6expectedXFAIL/7OBSERVED/174assertions. Stage9 remains
79matched observations/0mismatches/574assertions. Stage16 one, Stage17 two and Stage18
five NVS risks stay separate. New abrupt-save-termination stand-in and source corrupt
read->NOT_FOUND are OBSERVED, not protection passes. Readonly-source passes are candidate
algorithm tests, not deployed readonly/NVS compatibility claims.

All current C++ source/mock suites pass ASan/UBSan; historical six intentional USB faults
retain their diagnostic XFAIL traces. Python tests not sanitizer targets. Source SDK
recovery algorithms/target API bodies execute against synthetic adapters; complete API/
locks/ROM/flash drivers and actual Xtensa libraries do not execute. Real settings.cpp and
CLI execute with NVS/service stand-ins; web uses complete extracted handlers, not whole
AsyncWebServer. Simulated interruption is process termination, not physical power failure.
Actual ranges and statuses are retained in stage20-results.json.

Previous allocation probes rerun/pass. Checked save adds no settings snapshot/string
copy or dynamic table; reuses existing recursive ownership and a32bit atomic diagnostic.
Active SDK/cache/driver allocation, mutex initialization and runtime task/heap latency
are not physically measured. Existing bounded load-string<=4000buffer remains.

## Clean isolated builds and resources

Fresh ArduinoESP32 3.3.0 protected-core copies, unchanged whole-tree/source/SDK/HID/NVS
hash guards; GCC14.2.0,CLI1.3.1,IDF5.5. 16MiB custom slots740000,PSRAMdisabled,
QIO80MHz/DIOapp,240MHz,USB-OTG/TinyUSB,CDC and unchanged MSC/DFU boot flags.
FQBN:
`esp32:esp32:esp32s3:USBMode=default,CDCOnBoot=cdc,FlashSize=16M,PartitionScheme=custom,FlashMode=qio,PSRAM=disabled,CPUFreq=240,MSCOnBoot=default,DFUOnBoot=default`

| Measurement | Stage19 normal | Stage20 normal | Stage19 safe | Stage20 safe |
| --- | ---: | ---: | ---: | ---: |
| Program bytes | 1330059 | 1329491 | 1067063 | 1065987 |
| Application BIN bytes | 1330208 | 1329632 | 1067216 | 1066128 |
| Static RAM bytes | 82240 | 82248 | 78288 | 78280 |
| Free bytes/OTA slot | 6271968 | 6272544 | 6534960 | 6536048 |
| Free percentage/OTA slot | 82.50227303340517 | 82.50984981142241 | 85.96170359644397 | 85.97601528825432 |

Normal delta -568program/-576BIN/+8RAM bytes; safe -1076program/-1088BIN/-8RAM bytes.
Removing Preferences from application settings offsets new checks; no new SDK image,
parser framework or persistent queue. Compiler per-function load128/readString64 unchanged;
new checked save64/reset48; normal setup96/loop32, safe setup80/loop32 unchanged. Existing
common maximum1072 unchanged; analysis now also includes web/CLI so scope expansion is
not misrepresented as new stack growth. Estimates exclude callees/SDK/interrupts; actual
heap/task high-water unavailable. Normal still exceeds old140000 slot, so software size
reduction does not authorize application-only upload to original table.

Normal application SHA256 `ccd557a3d579ae85d593de6a756f3cf6c3a0b65f16f8988ae543a9f38b68e874`.

Safe application SHA256 `155c27a40539497592372e404f7c2fda0eb8a8291e79786f2cbb3e03b1a23744`.

Exact compiler/esptool/core/ELF/application hashes, compiled settings/caller source
proof and profile identity are in stage20-*-provenance.json/resources/build logs. Linked
NVS/startup disassembly and stack records committed. Stage18 pins remain unchanged:
original misc ce5c88b08640235938cb6b23433c482d024f5662223b581856c25886329be94e;
patched misc b119be330cc02e07c5cd53dae83a2dc2784b0cdd614ed89c6e902f68b029b73d;
combined core81c11f59e01c1e6263d387a008d3f3211319d94feb4751ddfa11af35a2a57ed3;
NVS archivea1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e.
Partition archive/reference evidence is separate, read-only investigation not a new
patched dependency or a guarantee of source/binary equivalence.

## Deployment boundary and next scope

Six non-owner generated binaries + provisional inventory in deployment/stage20. Previous
artifacts untouched. Safe app proposed in both newslots, reviewed table/OTAapp0 initializer/
bootloader/new erased coredump; supplied approved SPIFFS expected hash/size only (not
fabricated/included). Normal transition separately reviewed. No padded merged package,
physical writer, owner raw backup/NVS/credentials or new readonly table included.

All planned erase/write ranges avoid NVS9000/5000. Original SPIFFS290000/170000 versus
newE90000/160000 retains file-level roundtrip/capacity safeguards, never raw relocation.
Owner-local hash/size evidence is recorded; full structural/NVS/setting semantics/ROM/
physical freshness and reviewed preservation policy still outstanding. No SDK successful
return, clean subset or checked plan substitutes for those requirements/authorization.

GO for local private file inspection/summary and architecture review. NO-GO for migration,
application boot/OTA. Recommend separately reviewed Stage21 readonly-quiescent candidate
verification with native bypass/boot/descriptor/profile provenance and owner findings;
normal writable transition and durable settings transaction architecture require separate
contracts. No Stage21 begun. No hardware access, real HID, owner payload, flash/erase/
format/OTA, global-core or partition/Micro change. Main/prior branches preserved.

## Exact executed test inventory


### Stage1

| Test | Result | Assertions |
| --- | --- | ---: |
| supported_commands_and_mock_interfaces | PASS | 29 |
| script_run_state_isolation | PASS | 22 |
| cooperative_delay_and_text_cancellation | PASS | 33 |
| repeat_timing_and_control_loop_yield | PASS | 24 |
| live_commands_cannot_mutate_running_script | PASS | 19 |

### Stage2

| Test | Result | Assertions |
| --- | --- | ---: |
| stage2_rem_comments | PASS | 6 |
| stage2_required_rem_block_fixture | PASS | 12 |
| stage2_comment_block_literal_commands | PASS | 6 |
| stage2_unterminated_rem_block_zero_hid | PASS | 9 |
| stage2_unmatched_end_rem_zero_hid | PASS | 9 |
| stage2_lf_source | PASS | 6 |
| stage2_crlf_source | PASS | 6 |
| stage2_utf8_bom | PASS | 21 |
| stage2_missing_final_newline | PASS | 12 |
| stage2_blank_lines | PASS | 12 |
| stage2_spaces_tabs_and_payload_preservation | PASS | 7 |
| stage2_maximum_line_length | PASS | 12 |
| stage2_overlong_line_zero_hid | PASS | 18 |
| stage2_source_byte_limits | PASS | 16 |
| stage2_source_line_limits | PASS | 15 |
| stage2_mismatched_control_blocks_zero_hid | PASS | 18 |
| stage2_unterminated_control_blocks_zero_hid | PASS | 36 |
| stage2_duplicate_else_zero_hid | PASS | 18 |
| stage2_block_depth_limit_zero_hid | PASS | 9 |
| stage2_text_blocks_literal_mode_and_deferred_runtime | PASS | 30 |
| stage2_unterminated_text_blocks_zero_hid | PASS | 18 |
| stage2_unmatched_text_terminators_zero_hid | PASS | 18 |
| stage2_mismatched_text_terminators_zero_hid | PASS | 27 |
| stage2_unknown_commands_zero_hid | PASS | 27 |
| stage2_keyword_prefixes_are_not_commands | PASS | 128 |
| stage2_malformed_statements_zero_hid | PASS | 210 |
| stage2_supported_extensions_and_bare_keys | PASS | 8 |
| stage2_storage_read_seek_faults | PASS | 25 |
| stage2_preflight_cooperative_stop_and_live_ownership | PASS | 18 |
| stage2_live_validation_and_limits | PASS | 34 |

### Stage3

| Test | Result | Assertions |
| --- | --- | ---: |
| stage3_addition | PASS | 3 |
| stage3_subtraction | PASS | 3 |
| stage3_multiplication | PASS | 3 |
| stage3_division | PASS | 3 |
| stage3_modulo | PASS | 3 |
| stage3_exponentiation | PASS | 3 |
| stage3_equality | PASS | 3 |
| stage3_inequality | PASS | 3 |
| stage3_less_than | PASS | 3 |
| stage3_greater_than | PASS | 3 |
| stage3_less_or_equal | PASS | 3 |
| stage3_greater_or_equal | PASS | 3 |
| stage3_logical_and | PASS | 3 |
| stage3_logical_or | PASS | 3 |
| stage3_bitwise_and | PASS | 3 |
| stage3_bitwise_or | PASS | 3 |
| stage3_left_shift | PASS | 3 |
| stage3_right_shift | PASS | 3 |
| stage3_precedence_and_grouping | PASS | 54 |
| stage3_literals_booleans_and_whitespace | PASS | 54 |
| stage3_arithmetic_boundaries | PASS | 57 |
| stage3_invalid_literals_and_unsupported_operators | PASS | 54 |
| stage3_malformed_expressions_and_limits | PASS | 54 |
| stage3_numeric_declarations_assignment_and_no_hid | PASS | 9 |
| stage3_required_fixture_spiffs_and_sd | PASS | 12 |
| stage3_variable_references_types_and_atomic_failure | PASS | 24 |
| stage3_text_compatibility_alias_and_read | PASS | 41 |
| stage3_identifier_validation_and_table_exhaustion | PASS | 91 |
| stage3_preflight_zero_hid_and_runtime_errors | PASS | 46 |
| stage3_define_global_forward_and_word_matching | PASS | 24 |
| stage3_define_single_pass_and_declaration_exemption | PASS | 32 |
| stage3_define_comment_and_text_modes | PASS | 24 |
| stage3_define_duplicates_invalid_and_table_limits | PASS | 76 |
| stage3_define_expansion_and_pool_boundaries | PASS | 32 |
| stage3_expression_timing_counts_and_cancellation | PASS | 17 |
| stage3_collection_preflight_stop_and_state_isolation | PASS | 27 |
| stage3_interpolation_overflow_runtime_safe_stop | PASS | 6 |
| stage3_syntax_mode_does_not_evaluate_runtime_values | PASS | 3 |
| stage3_bounded_expression_fuzz | PASS | 3001 |
| stage3_expression_hot_path_no_heap | PASS | 10022 |

### Stage4

| Test | Result | Assertions |
| --- | --- | ---: |
| stage4_simple_true_if | PASS | 6 |
| stage4_simple_false_if | PASS | 6 |
| stage4_if_else_true_path | PASS | 6 |
| stage4_if_else_false_path | PASS | 6 |
| stage4_nested_true_true | PASS | 6 |
| stage4_nested_true_false | PASS | 6 |
| stage4_outer_false_nested_inactive | PASS | 6 |
| stage4_multiple_nesting_levels | PASS | 6 |
| stage4_exact_nesting_limit | PASS | 7 |
| stage4_nesting_limit_plus_one | PASS | 7 |
| stage4_else_if_first_true | PASS | 6 |
| stage4_else_if_middle_true | PASS | 6 |
| stage4_else_if_final_else | PASS | 6 |
| stage4_else_if_multiple_entries | PASS | 6 |
| stage4_nested_else_if_chains | PASS | 6 |
| stage4_no_branch_true_without_else | PASS | 6 |
| stage4_selected_assignments_and_later_conditions | PASS | 6 |
| stage4_inactive_side_effects | PASS | 9 |
| stage4_required_fixture_spiffs_and_sd | PASS | 12 |
| stage4_define_conditions_and_protected_keywords | PASS | 6 |
| stage4_macro_manufactured_structures_rejected | PASS | 56 |
| stage4_compound_hex_boolean_conditions | PASS | 6 |
| stage4_malformed_expressions_zero_hid | PASS | 77 |
| stage4_undefined_and_text_variables | PASS | 28 |
| stage4_missing_end_if | PASS | 7 |
| stage4_unexpected_end_if | PASS | 7 |
| stage4_duplicate_else | PASS | 7 |
| stage4_else_outside_if | PASS | 14 |
| stage4_malformed_then_and_else_if | PASS | 84 |
| stage4_invalid_branch_ordering | PASS | 21 |
| stage4_rem_block_conditional_text | PASS | 6 |
| stage4_text_blocks_preserve_literal_modes | PASS | 26 |
| stage4_stop_active_and_inactive_branches | PASS | 12 |
| stage4_external_cancel_delay_text_and_keys | PASS | 18 |
| stage4_repeat_active_inactive_and_structural_history | PASS | 18 |
| stage4_clean_state_between_runs_and_live_ownership | PASS | 9 |
| stage4_runtime_errors_only_in_eligible_conditions | PASS | 11 |
| stage4_cooperative_large_inactive_region_and_preflight | PASS | 18 |
| stage4_legacy_compatibility_aliases | PASS | 12 |
| stage4_keyword_boundaries_whitespace_and_case | PASS | 34 |
| stage4_mixed_while_nesting | PASS | 12 |
| stage4_conditional_stack_no_heap | PASS | 60012 |

### Stage5

| Test | Result | Assertions |
| --- | --- | ---: |
| stage5_false_while_following_commands | PASS | 6 |
| stage5_zero_iteration_expressions | PASS | 36 |
| stage5_single_iteration | PASS | 7 |
| stage5_multiple_iterations | PASS | 7 |
| stage5_decrementing_numeric_no_hid | PASS | 9 |
| stage5_shared_expression_operators | PASS | 84 |
| stage5_condition_reevaluated_at_header | PASS | 8 |
| stage5_nested_two_loops | PASS | 8 |
| stage5_nested_three_loops | PASS | 7 |
| stage5_sequential_loops | PASS | 6 |
| stage5_if_inside_while_else_if | PASS | 6 |
| stage5_while_inside_if_else | PASS | 6 |
| stage5_mixed_nested_structures | PASS | 6 |
| stage5_fixture_spiffs_and_sd | PASS | 12 |
| stage5_false_outer_suppresses_nested_conditions | PASS | 6 |
| stage5_inactive_side_effects_and_assignments | PASS | 10 |
| stage5_nested_updates_outer_variable | PASS | 8 |
| stage5_global_declarations_reused | PASS | 7 |
| stage5_exact_loop_depth | PASS | 6 |
| stage5_mixed_exact_depth | PASS | 6 |
| stage5_depth_plus_one_zero_hid | PASS | 14 |
| stage5_malformed_conditions_zero_hid | PASS | 98 |
| stage5_undefined_and_text_expression_rejection | PASS | 28 |
| stage5_missing_unmatched_and_crossed_terminators | PASS | 42 |
| stage5_keyword_boundaries_and_aliases | PASS | 52 |
| stage5_legacy_bare_text_truthiness | PASS | 12 |
| stage5_define_conditions_and_protected_keywords | PASS | 6 |
| stage5_macro_manufactured_loop_delimiters_rejected | PASS | 28 |
| stage5_define_collection_inside_inactive_loop | PASS | 6 |
| stage5_rem_block_loop_text_ignored | PASS | 6 |
| stage5_text_blocks_keep_literal_modes | PASS | 12 |
| stage5_bom_crlf_no_final_newline_backedges | PASS | 6 |
| stage5_header_across_read_budgets | PASS | 6 |
| stage5_reader_marker_and_seek_boundaries | PASS | 12 |
| stage5_runtime_seek_error | PASS | 7 |
| stage5_runtime_read_error_after_backedge | PASS | 7 |
| stage5_runtime_source_size_changed | PASS | 7 |
| stage5_runtime_condition_error_and_inactive_skip | PASS | 12 |
| stage5_runtime_undefined_path_dependent_variable | PASS | 6 |
| stage5_repeat_structural_and_inactive_history | PASS | 6 |
| stage5_repeat_expression_in_loop | PASS | 6 |
| stage5_keyboard_combinations_in_loop | PASS | 7 |
| stage5_expression_delays_in_loop | PASS | 7 |
| stage5_stop_in_active_and_inactive_loops | PASS | 12 |
| stage5_cancel_delay_inside_mixed_loop | PASS | 6 |
| stage5_cancel_text_inside_nested_loop | PASS | 7 |
| stage5_cancel_held_keys_and_usb_pressure | PASS | 8 |
| stage5_control_only_loop_cooperative_and_live_ownership | PASS | 47 |
| stage5_stalled_empty_loop_boundary | PASS | 7 |
| stage5_stalled_same_assignment_and_inactive_actions | PASS | 7 |
| stage5_nested_stall_not_masked_by_outer_progress | PASS | 6 |
| stage5_variable_progress_beyond_stall_threshold | PASS | 8 |
| stage5_total_iteration_limit_and_clean_restart | PASS | 13 |
| stage5_exact_total_iteration_boundary | PASS | 9 |
| stage5_variable_revision_atomic_and_reset | PASS | 9 |
| stage5_cancellation_then_new_source | PASS | 11 |
| stage5_large_inactive_region_cooperative | PASS | 11 |
| stage5_small_nested_loop_reference_cases | PASS | 175 |
| stage5_mixed_control_stack_no_heap | PASS | 91039 |

### Stage6

| Test | Result | Assertions |
| --- | --- | ---: |
| stage6_declarations_skipped | PASS | 6 |
| stage6_statement_invocation | PASS | 6 |
| stage6_multiple_calls | PASS | 6 |
| stage6_forward_invocation_and_globals | PASS | 6 |
| stage6_fixture_spiffs_and_sd | PASS | 12 |
| stage6_explicit_void_return | PASS | 6 |
| stage6_implicit_void_return | PASS | 6 |
| stage6_integer_return_assignment | PASS | 6 |
| stage6_boolean_return_conditions | PASS | 6 |
| stage6_statement_discards_return_value | PASS | 6 |
| stage6_void_value_rejected | PASS | 12 |
| stage6_top_level_and_live_return_compatibility | PASS | 11 |
| stage6_enter_and_modifier_return_inside_function | PASS | 7 |
| stage6_return_unwinds_nested_control | PASS | 6 |
| stage6_caller_control_restored | PASS | 6 |
| stage6_nested_statement_calls | PASS | 6 |
| stage6_nested_return_expressions | PASS | 6 |
| stage6_multiple_calls_in_expression | PASS | 6 |
| stage6_earlier_variable_operand_preserved | PASS | 6 |
| stage6_eager_logical_calls | PASS | 6 |
| stage6_inactive_conditions_do_not_call | PASS | 6 |
| stage6_while_condition_calls_reevaluate | PASS | 6 |
| stage6_while_condition_changes_count_as_progress | PASS | 6 |
| stage6_else_if_function_condition | PASS | 6 |
| stage6_numeric_commands_with_calls | PASS | 7 |
| stage6_function_globals_text_and_file_commands | PASS | 6 |
| stage6_define_function_operands_and_names | PASS | 6 |
| stage6_macro_structural_creation_rejected | PASS | 28 |
| stage6_rem_and_text_modes | PASS | 12 |
| stage6_literal_text_does_not_invoke | PASS | 6 |
| stage6_names_case_sensitive | PASS | 13 |
| stage6_malformed_names_parameters_and_collisions | PASS | 91 |
| stage6_unknown_calls_zero_hid | PASS | 21 |
| stage6_invalid_call_arguments_and_whitespace | PASS | 35 |
| stage6_duplicate_and_nested_declarations | PASS | 21 |
| stage6_unterminated_and_unmatched_functions | PASS | 28 |
| stage6_return_syntax_and_context_errors | PASS | 21 |
| stage6_unused_body_preflight_errors_zero_hid | PASS | 21 |
| stage6_function_table_boundary | PASS | 13 |
| stage6_function_identifier_boundary | PASS | 13 |
| stage6_nested_call_depth_boundary | PASS | 6 |
| stage6_recursive_depth_exhaustion | PASS | 6 |
| stage6_recursive_expression_and_global_visibility | PASS | 6 |
| stage6_shared_control_depth_exhaustion | PASS | 6 |
| stage6_runtime_undefined_initialization | PASS | 6 |
| stage6_runtime_arithmetic_after_calls | PASS | 12 |
| stage6_repeat_history_around_calls | PASS | 6 |
| stage6_stop_active_and_inactive_function_branches | PASS | 12 |
| stage6_cancel_pending_function_delay | PASS | 6 |
| stage6_cancel_nested_function_text | PASS | 7 |
| stage6_cancel_held_keys_in_call | PASS | 7 |
| stage6_cancel_call_under_usb_backpressure | PASS | 8 |
| stage6_cancel_expression_then_clean_run | PASS | 12 |
| stage6_live_ownership_and_stop | PASS | 7 |
| stage6_seek_error_entering_function | PASS | 5 |
| stage6_seek_error_returning_to_caller | PASS | 6 |
| stage6_read_error_and_source_change_in_function | PASS | 6 |
| stage6_runtime_body_read_failure | PASS | 7 |
| stage6_bom_crlf_header_and_final_newline | PASS | 6 |
| stage6_empty_function_loop_stalls | PASS | 6 |
| stage6_total_call_budget | PASS | 6 |
| stage6_postfix_arithmetic_matches_existing_evaluator | PASS | 39 |
| stage6_expression_bounds_and_postfix_errors | PASS | 11 |
| stage6_long_declaration_skip_is_cooperative | PASS | 11 |
| stage6_postfix_call_state_no_heap | PASS | 60012 |

### Stage7

| Test | Result | Assertions |
| --- | --- | ---: |
| stage7_empty_blocks | PASS | 6 |
| stage7_single_line_string | PASS | 6 |
| stage7_single_line_stringln | PASS | 6 |
| stage7_string_multiline_no_separators | PASS | 6 |
| stage7_stringln_multiline_enters | PASS | 7 |
| stage7_string_blank_lines | PASS | 6 |
| stage7_stringln_blank_lines | PASS | 6 |
| stage7_string_leading_and_trailing_whitespace | PASS | 6 |
| stage7_stringln_removes_one_leading_tab | PASS | 6 |
| stage7_internal_tabs_preserved | PASS | 6 |
| stage7_literal_command_keywords | PASS | 6 |
| stage7_terminator_prefixes_are_literal | PASS | 6 |
| stage7_case_and_indented_delimiters | PASS | 6 |
| stage7_inline_compatibility_unchanged | PASS | 6 |
| stage7_lf_and_crlf_equivalent | PASS | 12 |
| stage7_bom_only_at_source_start | PASS | 6 |
| stage7_no_final_newline | PASS | 6 |
| stage7_quoted_text_no_unescaping | PASS | 6 |
| stage7_numeric_boolean_and_text_interpolation | PASS | 6 |
| stage7_unknown_host_variables_are_literal | PASS | 6 |
| stage7_variable_replacement_is_single_pass | PASS | 6 |
| stage7_define_hash_and_word_replacement | PASS | 6 |
| stage7_define_body_not_collected_or_expanded | PASS | 6 |
| stage7_define_single_pass_and_variable_order | PASS | 6 |
| stage7_expansion_cannot_close_or_execute | PASS | 6 |
| stage7_value_whitespace_after_source_dedent | PASS | 6 |
| stage7_maximum_body_line | PASS | 12 |
| stage7_overlong_body_zero_hid | PASS | 7 |
| stage7_define_expansion_boundary | PASS | 13 |
| stage7_interpolation_boundary_and_overflow | PASS | 12 |
| stage7_inactive_interpolation_has_no_runtime_effect | PASS | 6 |
| stage7_unterminated_after_output_zero_hid | PASS | 14 |
| stage7_mismatched_or_argument_terminators_zero_hid | PASS | 21 |
| stage7_unmatched_terminators_zero_hid | PASS | 14 |
| stage7_literal_openers_inside_body | PASS | 6 |
| stage7_fixture_spiffs_and_sd | PASS | 12 |
| stage7_if_else_active_inactive_blocks | PASS | 6 |
| stage7_zero_iteration_loop_blocks | PASS | 6 |
| stage7_nested_loops_interpolate_current_values | PASS | 6 |
| stage7_function_repeat_calls_and_return | PASS | 6 |
| stage7_nested_functions_with_blocks | PASS | 6 |
| stage7_recursive_calls_with_blocks | PASS | 6 |
| stage7_repeat_literal_text_and_whitespace | PASS | 6 |
| stage7_repeat_blank_stringln | PASS | 6 |
| stage7_empty_string_does_not_replace_history | PASS | 6 |
| stage7_repeat_interpolates_again | PASS | 6 |
| stage7_default_delays_per_body_line | PASS | 7 |
| stage7_cancel_default_delay | PASS | 7 |
| stage7_cancel_halfway_through_typing | PASS | 6 |
| stage7_cancel_held_shift_and_usb_release_retry | PASS | 7 |
| stage7_usb_backpressure_lossless_and_no_readahead | PASS | 8 |
| stage7_stop_command_after_block | PASS | 6 |
| stage7_live_ownership_and_clean_run | PASS | 14 |
| stage7_live_block_opener_rejected | PASS | 5 |
| stage7_preflight_source_errors_zero_hid | PASS | 6 |
| stage7_rewind_seek_error_zero_hid | PASS | 6 |
| stage7_runtime_body_read_error_spiffs_and_sd | PASS | 12 |
| stage7_runtime_source_change | PASS | 7 |
| stage7_loop_backedge_seek_error | PASS | 6 |
| stage7_function_return_seek_error | PASS | 7 |
| stage7_large_block_streamed_and_cooperative | PASS | 7 |
| stage7_cancel_large_block_preflight | PASS | 6 |
| stage7_source_limits_zero_hid | PASS | 13 |
| stage7_hid_disabled_block_has_no_output | PASS | 6 |
| stage7_malformed_later_control_zero_hid | PASS | 7 |
| stage7_control_nesting_boundaries | PASS | 26 |
| stage7_text_blocks_do_not_execute_calls | PASS | 6 |
| stage7_bounded_line_allocation_probe | PASS | 40005 |

### Stage8

| Test | Result | Assertions |
| --- | --- | ---: |
| stage8_f1_f24_reference | PASS | 346 |
| stage8_invalid_f_names | PASS | 12 |
| stage8_navigation_editing_aliases | PASS | 330 |
| stage8_named_punctuation_keys | PASS | 176 |
| stage8_keypad_reference | PASS | 144 |
| stage8_all_modifier_masks | PASS | 3072 |
| stage8_modifier_aliases | PASS | 110 |
| stage8_hyphen_combinations | PASS | 34 |
| stage8_malformed_hyphens_zero_hid | PASS | 24 |
| stage8_case_tabs_and_order | PASS | 12 |
| stage8_modifier_only_release | PASS | 23 |
| stage8_six_key_limit_and_duplicates | PASS | 15 |
| stage8_literal_punctuation_chord_us | PASS | 15 |
| stage8_literal_punctuation_chord_de | PASS | 27 |
| stage8_all_literal_punctuation_chords | PASS | 797 |
| stage8_report_filter_and_raw_modifiers | PASS | 99 |
| stage8_keycode_bounds_zero_hid | PASS | 12 |
| stage8_us_ascii_table | PASS | 129 |
| stage8_de_ascii_table | PASS | 129 |
| stage8_us_ascii_translation | PASS | 358 |
| stage8_de_ascii_translation | PASS | 360 |
| stage8_printable_ascii_runtime_all_locales | PASS | 1934 |
| stage8_de_utf8_reference | PASS | 89 |
| stage8_de_dead_keys | PASS | 70 |
| stage8_locale_registration_and_switching | PASS | 28 |
| stage8_named_keys_are_physical_not_locale_text | PASS | 17 |
| stage8_unsupported_unicode_skip_warning | PASS | 14 |
| stage8_utf8_bounds_and_invalid_sequences | PASS | 16 |
| stage8_no_warn_supported_controls | PASS | 6 |
| stage8_repeat_define_and_stringln_reports | PASS | 63 |
| stage8_multiline_control_function_keyboard | PASS | 36 |
| stage8_queue_refusal_press_and_release | PASS | 16 |
| stage8_disconnect_mid_chord_recovery | PASS | 15 |
| stage8_cancel_held_modifier_all_masks | PASS | 3060 |
| stage8_cancel_release_priority_new_live_command | PASS | 14 |
| stage8_stop_and_runtime_error_release | PASS | 15 |
| stage8_cancel_between_dead_key_strokes | PASS | 12 |
| stage8_storage_fault_after_chord_release | PASS | 10 |
| stage8_hid_disabled_and_live_ownership | PASS | 15 |
| stage8_new_run_no_modifier_leak | PASS | 11 |
| stage8_translation_report_allocation_probe | PASS | 32001 |

### Stage10

| Test | Result | Assertions |
| --- | --- | ---: |
| startup_success_truthful | PASS | 6 |
| startup_missing_card | PASS | 6 |
| startup_missing_image_no_create | PASS | 6 |
| startup_wrong_size_no_truncate | PASS | 22 |
| startup_open_failure | PASS | 4 |
| startup_probe_seek_failure | PASS | 5 |
| startup_probe_short_read | PASS | 4 |
| startup_sdk_failure_cleanup | PASS | 6 |
| retry_failed_startup | PASS | 3 |
| repeated_begin_idempotent | PASS | 3 |
| retry_ejected_media | PASS | 7 |
| stale_host_load_after_off | PASS | 5 |
| stale_host_load_after_cancel | PASS | 5 |
| writable_reset_after_end | PASS | 8 |
| read_nonzero_offset | PASS | 6 |
| write_nonzero_offset | PASS | 7 |
| cross_sector_unaligned | PASS | 6 |
| last_byte_and_exact_end | PASS | 7 |
| invalid_range_and_overflow | PASS | 12 |
| zero_length_null | PASS | 5 |
| null_nonzero | PASS | 5 |
| transfer_limit | PASS | 6 |
| read_seek_failure_no_wrong_read | PASS | 9 |
| write_seek_failure_no_wrong_write | PASS | 9 |
| short_read_quarantines | PASS | 9 |
| short_write_prefix_and_quarantine | PASS | 10 |
| card_removal_callback | PASS | 9 |
| card_removal_main_loop | PASS | 7 |
| backing_size_changed | PASS | 8 |
| fault_cleanup_and_explicit_recovery | PASS | 6 |
| eject_load_and_power_stop | PASS | 9 |
| cancel_before_open | PASS | 3 |
| cancel_after_open | PASS | 3 |
| timeout_wrap_safe | PASS | 6 |
| media_absent_until_validated | PASS | 4 |
| script_waits_for_storage | PASS | 7 |
| script_startup_failure_stops_tail | PASS | 6 |
| stop_pending_startup | PASS | 6 |
| stop_preserves_active_media | PASS | 8 |
| live_cli_ownership_while_preparing | PASS | 9 |
| script_and_host_activity | PASS | 206 |
| function_condition_storage_startup | PASS | 7 |
| live_cli_failure_status_and_retry | PASS | 7 |
| callback_lock_contention_busy | PASS | 6 |
| callback_error_storm_no_io | PASS | 1004 |
| concurrent_callback_mode_stop | PASS | 5 |
| sd_adapter_interleaving | PASS | 7 |
| sd_adapter_removal_and_remount | PASS | 3 |
| off_cancels_pending | PASS | 1 |
| repeated_failure_recovery | PASS | 81 |
| no_callback_heap_allocation | PASS | 5 |
| build_without_msc_reports_unavailable | PASS | 4 |

### Stage11

| Test | Result | Assertions |
| --- | --- | ---: |
| hold_release_key | PASS | 13 |
| all_eight_persistent_modifiers | PASS | 104 |
| selective_modifier_release | PASS | 24 |
| selective_key_release_order | PASS | 18 |
| idempotent_hold_release | PASS | 13 |
| six_persistent_keys | PASS | 15 |
| seventh_hold_fails_no_drop | PASS | 14 |
| transient_chord_merges_persistent | PASS | 18 |
| all_modifier_masks_merge | PASS | 2308 |
| string_shift_punctuation_enter | PASS | 24 |
| de_altgr_and_dead_key_merge | PASS | 24 |
| held_shift_with_german_spacing | PASS | 18 |
| persistent_duplicate_transient_no_edge | PASS | 24 |
| merged_seventh_transient_fails | PASS | 10 |
| saturated_duplicate_and_modifier_allowed | PASS | 12 |
| raw_modifier_keycode_merges | PASS | 12 |
| inject_mod_inline | PASS | 12 |
| inject_mod_restores_owned | PASS | 15 |
| inject_mod_prefix_reference | PASS | 18 |
| reset_continues_variables | PASS | 13 |
| stop_payload_tail_and_release | PASS | 10 |
| stop_inside_function_loop | PASS | 12 |
| inactive_ownership_commands | PASS | 8 |
| functions_loops_share_ownership | PASS | 18 |
| define_repeat_ownership_and_text | PASS | 19 |
| default_delay_ownership | PASS | 8 |
| eof_releases_owned | PASS | 9 |
| cancel_during_delay | PASS | 9 |
| cancel_during_string | PASS | 10 |
| cancel_dead_key_second_stroke | PASS | 10 |
| runtime_error_releases_owned | PASS | 9 |
| function_depth_error_releases | PASS | 9 |
| loop_budget_error_releases | PASS | 9 |
| storage_read_error_releases | PASS | 10 |
| hold_queue_refusal_no_commit | PASS | 11 |
| release_refusal_clears_logical_owner | PASS | 13 |
| stop_release_refusal_priority | PASS | 16 |
| reset_refusal_waits_before_tail | PASS | 15 |
| disconnect_poll_cancels_owned | PASS | 13 |
| disconnect_event_reconnect_between_ticks | PASS | 11 |
| backpressure_is_not_disconnect | PASS | 8 |
| live_disconnect_clears_idle_hold | PASS | 10 |
| new_script_clears_live_hold | PASS | 12 |
| web_cli_cannot_release_script_hold | PASS | 9 |
| live_holds_survive_commands_until_reset | PASS | 20 |
| new_script_after_cancel_no_leak | PASS | 10 |
| hid_mode_off_releases_owner | PASS | 12 |
| multiline_owned_reports_spiffs_sd | PASS | 42 |
| malformed_hold_zero_hid | PASS | 35 |
| malformed_release_zero_hid | PASS | 28 |
| malformed_inject_mod_zero_hid | PASS | 28 |
| reset_stop_args_zero_hid | PASS | 14 |
| ownership_command_prefixes_rejected | PASS | 35 |
| new_command_function_collisions | PASS | 35 |
| comment_text_literals_not_ownership | PASS | 7 |
| case_tabs_and_modifier_aliases | PASS | 18 |
| direct_report_overflow_null_validation | PASS | 8 |
| repeated_ownership_stress | PASS | 8005 |
| transient_release_refusal_restores_owned | PASS | 13 |
| eof_release_refusal_clears_logical_owner | PASS | 11 |
| cancel_pending_hold_before_acceptance | PASS | 7 |
| disconnect_during_text_cancels_tail | PASS | 11 |
| while_condition_runtime_error_releases | PASS | 9 |
| function_return_seek_error_releases | PASS | 10 |
| source_changed_while_owned_releases | PASS | 10 |
| next_script_after_disconnect_recovery | PASS | 10 |
| atomic_event_callback_no_execution_lock | PASS | 11 |
| implicit_function_return_owner_lifetime | PASS | 15 |
| unsupported_inactive_hold_preflight | PASS | 7 |
| live_stop_payload_releases_idle_hold | PASS | 9 |
| latched_disconnect_blocks_enqueue_before_update | PASS | 10 |
| ownership_allocation_probe | PASS | 9002 |

### Stage12

| Test | Result | Assertions |
| --- | --- | ---: |
| initial_unknown_not_false | PASS | 6 |
| all_led_masks_and_padding | PASS | 288 |
| invalid_ids_lengths_null_padding | PASS | 10 |
| actual_keyboard_output_virtual_hook | PASS | 3 |
| actual_keyboard_control_set_report_hook | PASS | 4 |
| duplicates_do_not_count_changes | PASS | 1003 |
| per_key_transition_counters | PASS | 3 |
| first_report_auto_saves_attach_state | PASS | 8 |
| explicit_save_updates_saved_state | PASS | 9 |
| save_unknown_fails_truthfully | PASS | 5 |
| saved_unknown_expression | PASS | 5 |
| readonly_assignment_preflight | PASS | 3 |
| fake_internal_declaration_preflight | PASS | 3 |
| fake_internal_define_alias_preflight | PASS | 3 |
| read_cannot_shadow_internal | PASS | 3 |
| unsupported_read_preflight | PASS | 3 |
| unsupported_write_preflight | PASS | 3 |
| all_native_registry_names_reserved | PASS | 75 |
| os_extension_and_user_variables_preserved | PASS | 5 |
| timeout_extension_assignment_and_limits | PASS | 6 |
| timeout_assignment_expression_shared_evaluator | PASS | 5 |
| constant_invalid_timeout_preflight | PASS | 3 |
| live_wait_stop_cancellable | PASS | 3 |
| timeout_resets_between_scripts | PASS | 10 |
| no_internal_symbol_table_consumption | PASS | 18 |
| canonical_on_off_waits_all_keys | PASS | 36 |
| wait_already_desired_is_immediate | PASS | 5 |
| unknown_off_does_not_succeed | PASS | 5 |
| wait_unknown_becomes_observed_off | PASS | 6 |
| change_unknown_first_report_is_baseline | PASS | 6 |
| change_duplicate_reports_do_not_finish | PASS | 5 |
| rapid_changes_between_ticks_not_lost | PASS | 5 |
| change_all_three_independent | PASS | 18 |
| timeout_wrap_safe | PASS | 5 |
| malformed_lock_command_preflight | PASS | 3 |
| malformed_save_restore_preflight | PASS | 3 |
| lock_commands_function_collision | PASS | 3 |
| inactive_branch_no_wait_or_save | PASS | 5 |
| lock_variables_if_define_function_return | PASS | 5 |
| lock_variables_while_updates | PASS | 6 |
| wait_inside_nested_control_and_function | PASS | 5 |
| numeric_interpolation_observed_state | PASS | 5 |
| unknown_interpolation_runtime_error | PASS | 5 |
| unsupported_interpolation_runtime_error | PASS | 5 |
| restore_noop_no_keyboard_output | PASS | 5 |
| restore_unknown_current_saved_rejected | PASS | 5 |
| restore_requires_hid_enabled | PASS | 5 |
| restore_rejects_held_modifier | PASS | 5 |
| restore_rejects_held_key | PASS | 5 |
| restore_three_keys_ack_exact_reports | PASS | 51 |
| restore_no_ack_times_out_no_retoggle | PASS | 5 |
| restore_wrong_feedback_not_ack | PASS | 5 |
| restore_rechecks_pending_toggle_after_backpressure | PASS | 24 |
| restore_default_delay_after_success | PASS | 5 |
| restore_backpressure_timeout | PASS | 6 |
| stop_cancels_wait_and_releases_hold | PASS | 4 |
| stop_payload_inside_function_preserves_feedback | PASS | 7 |
| reset_preserves_observed_and_saved_state | PASS | 5 |
| runtime_timeout_releases_held_keys | PASS | 5 |
| cancel_restore_during_press | PASS | 4 |
| disconnect_immediate_unknown_and_stale_token | PASS | 7 |
| unmounted_reports_rejected | PASS | 3 |
| disconnect_cancels_wait_and_reconnect_clean | PASS | 9 |
| feedback_survives_separate_script_runs | PASS | 9 |
| live_cli_excluded_during_script_wait | PASS | 3 |
| live_save_restore_state | PASS | 4 |
| wait_command_backpressure_independent | PASS | 5 |
| feedback_during_input_preserves_reports | PASS | 6 |
| callback_does_not_wait_on_executor_lock | PASS | 2 |
| concurrent_feedback_and_snapshot_reads | PASS | 10001 |
| concurrent_disconnect_never_revives_old_session | PASS | 100 |
| transition_counter_crosses_16bit_boundary | PASS | 65538 |
| storage_requested_failed_registry_truthful | PASS | 8 |
| storage_preparing_active_ejected_registry | PASS | 13 |
| storage_retry_and_off_registry | PASS | 8 |
| attackmode_does_not_fabricate_lock_state | PASS | 5 |
| storage_read_error_after_wait_releases_keys | PASS | 4 |
| sd_spiffs_lock_fixture | PASS | 10 |
| saved_state_invalidated_on_backend_begin | PASS | 1 |
| feedback_registry_allocation_probe | PASS | 50002 |

### Stage13

| Test | Result | Assertions |
| --- | --- | ---: |
| alias_POWERSHELL | PASS | 6 |
| alias_BATCH | PASS | 6 |
| alias_BASH | PASS | 6 |
| alias_JAVASCRIPT | PASS | 6 |
| alias_PYTHON | PASS | 6 |
| alias_RUBY | PASS | 6 |
| alias_HTML | PASS | 6 |
| alias_ln_POWERSHELL | PASS | 6 |
| alias_ln_BATCH | PASS | 6 |
| alias_ln_BASH | PASS | 6 |
| alias_ln_JAVASCRIPT | PASS | 6 |
| alias_ln_PYTHON | PASS | 6 |
| alias_ln_RUBY | PASS | 6 |
| alias_ln_HTML | PASS | 6 |
| new_keyword_prefixes_rejected | PASS | 28 |
| documentation_heading | PASS | 6 |
| ordinary_comment_forms | PASS | 6 |
| invalid_comment_heading | PASS | 8 |
| unterminated_documentation | PASS | 8 |
| alias_cross_terminator | PASS | 8 |
| alias_suffixed_terminator | PASS | 8 |
| alias_suffixed_end_is_literal_data | PASS | 6 |
| alias_inline_rejected | PASS | 8 |
| alias_unknown_rejected | PASS | 8 |
| alias_unterminated | PASS | 8 |
| alias_define_interpolation_order | PASS | 6 |
| alias_literal_preprocessing | PASS | 6 |
| alias_empty_block | PASS | 6 |
| alias_bom_crlf_no_newline | PASS | 6 |
| alias_lowercase_tabs | PASS | 6 |
| extension_functions | PASS | 6 |
| extension_sequential_body | PASS | 6 |
| extension_version_optional | PASS | 6 |
| extension_duplicate | PASS | 8 |
| extension_nested | PASS | 8 |
| extension_invalid_name | PASS | 8 |
| extension_missing_end | PASS | 8 |
| extension_unmatched_end | PASS | 8 |
| extension_end_arguments | PASS | 8 |
| extension_version_duplicate | PASS | 8 |
| extension_version_misplaced | PASS | 8 |
| extension_version_outside | PASS | 8 |
| extension_version_malformed | PASS | 8 |
| extension_control_boundary | PASS | 8 |
| extension_function_boundary | PASS | 8 |
| extension_not_top_level | PASS | 8 |
| extension_exact_limit | PASS | 6 |
| extension_limit_plus_one | PASS | 7 |
| preprocess_true_false_else | PASS | 6 |
| preprocess_not_true_undefined | PASS | 6 |
| preprocess_bare_label | PASS | 6 |
| preprocess_order_forward_definition | PASS | 6 |
| preprocess_excluded_define_inert | PASS | 6 |
| preprocess_included_define_global_expansion | PASS | 6 |
| preprocess_text_flag_ambiguous_rejected | PASS | 8 |
| preprocess_recursive_flag_rejected | PASS | 8 |
| preprocess_invalid_label | PASS | 8 |
| preprocess_extra_condition_tokens | PASS | 8 |
| preprocess_missing_end | PASS | 8 |
| preprocess_unmatched_end | PASS | 8 |
| preprocess_unmatched_else | PASS | 8 |
| preprocess_duplicate_else | PASS | 8 |
| preprocess_marker_arguments | PASS | 8 |
| preprocess_nested_parent_exclusion | PASS | 6 |
| preprocess_exact_depth | PASS | 6 |
| preprocess_depth_plus_one | PASS | 8 |
| preprocess_excluded_runtime_not_validated | PASS | 6 |
| preprocess_excluded_function_not_inventoried | PASS | 7 |
| preprocess_excluded_variable_not_inventoried | PASS | 7 |
| preprocess_excluded_storage_hid_inert | PASS | 7 |
| preprocess_comment_directives_literal | PASS | 6 |
| preprocess_excluded_text_structural_error | PASS | 8 |
| preprocess_excluded_comment_missing_end | PASS | 8 |
| preprocess_wrapper_crossing | PASS | 8 |
| preprocess_wrapper_end_crossing | PASS | 8 |
| macro_cannot_create_wrapper | PASS | 7 |
| macro_cannot_create_preprocessor | PASS | 7 |
| macro_cannot_create_alias | PASS | 7 |
| checked_in_source_fixture | PASS | 7 |
| checked_in_exclusion_fixture | PASS | 7 |
| integration_spiffs | PASS | 6 |
| integration_sd | PASS | 6 |
| frozen_flags_after_function_seek | PASS | 6 |
| frozen_flags_after_loop_seek | PASS | 6 |
| selected_structure_validated_before_hid | PASS | 7 |
| preprocess_repeat_history | PASS | 6 |
| maximum_line_inside_exclusion | PASS | 6 |
| overlong_line_inside_exclusion | PASS | 8 |
| source_limit_inside_exclusion | PASS | 6 |
| exact_line_bitmap_boundary | PASS | 6 |
| bitmap_boundary_plus_one | PASS | 7 |
| excluded_read_fault | PASS | 6 |
| preprocessing_rewind_fault | PASS | 6 |
| cancellation_during_preprocessing | PASS | 7 |
| cancellation_during_alias_typing | PASS | 6 |
| alias_usb_backpressure | PASS | 6 |
| large_streamed_alias | PASS | 6 |
| canonical_led_colors_and_override | PASS | 7 |
| canonical_led_arguments_rejected | PASS | 8 |
| canonical_led_inactive_branch | PASS | 7 |
| canonical_led_error_priority | PASS | 6 |
| canonical_led_new_script_defaults | PASS | 14 |
| canonical_led_open_error_priority | PASS | 8 |
| new_command_function_names_reserved | PASS | 42 |
| live_metadata_rejected | PASS | 2 |
| excluded_duplicate_constants_ignored | PASS | 6 |
| included_duplicate_constants_rejected | PASS | 8 |
| excluded_extension_names_do_not_exhaust | PASS | 6 |
| macro_cannot_create_version | PASS | 7 |
| macro_cannot_create_wrapper_direct | PASS | 7 |
| constant_text_cannot_escape_alias | PASS | 6 |
| comment_define_not_collected_in_alias | PASS | 6 |
| combined_preprocess_runtime_depth | PASS | 6 |
| preprocess_no_expansion_of_flag_name | PASS | 6 |
| preprocess_define_whitespace_literal_boolean | PASS | 6 |
| canonical_led_disabled_setting | PASS | 5 |
| canonical_led_stop_retains_override | PASS | 7 |
| legacy_rgb_behavior_retained | PASS | 5 |
| function_seek_fault_after_preprocessing | PASS | 6 |
| preflight_cancellation_live_isolation | PASS | 7 |
| run_state_inclusion_isolation | PASS | 12 |
| preprocessing_bitmap_allocation_probe | PASS | 8195 |

### Stage14

| Test | Result | Assertions |
| --- | --- | ---: |
| checked_in_random_jitter_fixture | PASS | 8 |
| default_registry_values | PASS | 7 |
| inclusive_minimum_maximum | PASS | 3 |
| equal_bounds_no_entropy | PASS | 4 |
| full_uint16_range | PASS | 3 |
| reversed_range_atomic_failure | PASS | 2 |
| unbiased_rejection_then_acceptance | PASS | 2 |
| rejection_budget_exhaustion | PASS | 2 |
| all_range_residues_balanced | PASS | 1010 |
| every_uint16_singleton_boundary | PASS | 65537 |
| seeded_host_replay | PASS | 200 |
| invalid_literal_range_preflight | PASS | 7 |
| negative_literal_range_preflight | PASS | 7 |
| jitter_boolean_validation | PASS | 7 |
| atomic_internal_write_validation | PASS | 6 |
| numeric_bounds_follow_uint16_arithmetic | PASS | 14 |
| random_int_readonly | PASS | 7 |
| random_reserved_declaration | PASS | 7 |
| unsupported_seed_and_encoding | PASS | 7 |
| unsupported_scancode_variable | PASS | 7 |
| inject_var_still_deferred | PASS | 7 |
| restart_still_deferred | PASS | 7 |
| random_character_prose_alias_unconfirmed | PASS | 7 |
| random_string_syntax_not_invented | PASS | 7 |
| random_command_arguments_rejected | PASS | 7 |
| random_command_prefix_rejected | PASS | 7 |
| random_command_function_collision | PASS | 7 |
| syntax_evaluator_never_draws | PASS | 2 |
| compiled_program_never_draws | PASS | 2 |
| preflight_invalid_after_random | PASS | 7 |
| random_expression_each_reference_once | PASS | 7 |
| random_boolean_eager_expression | PASS | 7 |
| canonical_random_condition | PASS | 7 |
| legacy_random_condition_once | PASS | 7 |
| legacy_mixed_numeric_text_preserved | PASS | 6 |
| random_while_each_header_once | PASS | 7 |
| function_suspension_preserves_random_operand | PASS | 7 |
| function_return_random_bounds | PASS | 7 |
| excluded_preprocessing_no_rng | PASS | 7 |
| inactive_runtime_branch_no_rng | PASS | 7 |
| reversed_bounds_runtime_safe_stop | PASS | 7 |
| reversed_bounds_repaired_before_draw | PASS | 6 |
| raw_failure_releases_ownership | PASS | 7 |
| runtime_jitter_boolean_invalid | PASS | 6 |
| settings_reset_between_runs | PASS | 14 |
| random_command_all_sets_us | PASS | 42 |
| random_special_all_de_locale | PASS | 28 |
| random_letters_all_de_report_bytes | PASS | 58 |
| random_command_repeat_resamples | PASS | 7 |
| random_interpolation_compatibility | PASS | 7 |
| random_numeric_delay_consumer | PASS | 6 |
| random_function_argument_setting | PASS | 7 |
| random_live_settings_persist_until_reset | PASS | 5 |
| jitter_disabled_exact_existing_timing | PASS | 17 |
| jitter_zero_max_no_entropy | PASS | 7 |
| jitter_additive_per_press_timing | PASS | 24 |
| jitter_default_and_explicit_delay_independent | PASS | 12 |
| jitter_multiline_enter_and_blank | PASS | 7 |
| jitter_named_chord_report_bytes | PASS | 8 |
| jitter_persistent_modifier_text | PASS | 7 |
| jitter_german_deadkey_strokes | PASS | 7 |
| jitter_backpressure_no_redraw | PASS | 7 |
| jitter_random_command_backpressure | PASS | 7 |
| jitter_cancel_pending_interval | PASS | 7 |
| jitter_runtime_source_failure | PASS | 7 |
| jitter_release_refusal_safe_retry | PASS | 7 |
| jitter_disconnect_reconnect | PASS | 9 |
| jitter_clock_wrap_safe | PASS | 6 |
| jitter_hold_release_idempotence | PASS | 7 |
| jitter_maximum_bound | PASS | 7 |
| script_storage_read_fault_no_rng | PASS | 5 |
| script_seek_fault_no_rng | PASS | 5 |
| jitter_loop_runtime_seek_failure | PASS | 8 |
| jitter_live_ownership_isolation | PASS | 7 |
| long_seeded_randomized_loop | PASS | 7 |
| random_numeric_no_hid | PASS | 9 |
| random_source_null_default_adapter | PASS | 1 |
| random_range_allocation_probe | PASS | 20001 |

### Stage2.5

| Test | Result | Assertions |
| --- | --- | ---: |
| stage25_reviewed_partition_layout | PASS | 15 |
| stage25_overlapping_partitions_rejected | PASS | 1 |
| stage25_unaligned_application_rejected | PASS | 1 |
| stage25_reviewed_offsets_sizes_flags_enforced | PASS | 10 |
| stage25_core_version_pin_enforced | PASS | 1 |
| stage25_application_size_boundary | PASS | 3 |
| stage25_image_header_configuration_enforced | PASS | 6 |
| stage25_build_configuration_and_app_address_enforced | PASS | 22 |
| stage25_generated_16m_build_artifacts | PASS | 4 |
| stage25_corrupt_partition_binary_rejected | PASS | 1 |
| stage25_merged_image_wrong_address_rejected | PASS | 1 |
| stage25_stale_4m_partition_artifact_rejected | PASS | 1 |
| stage25_saved_physical_flash_capacity_guard | PASS | 7 |
| stage25_offline_source_archives_require_file_migration | PASS | 11 |
| stage25_offline_preparation_rejects_invalid_backups | PASS | 6 |
| stage25_offline_preparation_never_overwrites | PASS | 2 |
| stage25_build_wrapper_requires_clean_output | PASS | 3 |
| stage25_verified_device_map_differs_from_core_default | PASS | 3 |
| stage25_raw_spiffs_size_mismatch_refused | PASS | 3 |
| stage25_recorded_backup_hash_guards | PASS | 4 |
| stage25_file_level_extract_repack_roundtrip | PASS | 8 |
| stage25_file_level_empty_filesystem | PASS | 1 |
| stage25_file_level_capacity_and_overwrite_guards | PASS | 7 |
| stage25_corrupt_or_wrong_geometry_extraction_refused | PASS | 4 |
| stage25_alternative_layout_maximum_equal_slots | PASS | 4 |
| stage25_review_only_plan_preserves_nvs_and_initializes_both_apps | PASS | 24 |
| stage25_write_and_erase_region_guards | PASS | 13 |
| stage25_ota_initializer_selects_app0_deterministically | PASS | 7 |
| stage25_plan_refuses_unverified_files_and_backup_provenance | PASS | 16 |
| stage25_mac_old_core_rejected_before_compile | PASS | 1 |

### stage9_observations

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| basic_text  | OBSERVED | 7 |
| basic_text  | OBSERVED | 7 |
| comment_block  | OBSERVED | 7 |
| comment_block  | OBSERVED | 7 |
| documented_comment_heading  | OBSERVED | 7 |
| documented_comment_heading  | OBSERVED | 7 |
| numeric_boolean  | OBSERVED | 7 |
| numeric_boolean  | OBSERVED | 7 |
| reference_self_assignment  | OBSERVED | 7 |
| reference_self_assignment  | OBSERVED | 7 |
| define_words  | OBSERVED | 7 |
| define_words  | OBSERVED | 7 |
| define_nonrecursive  | OBSERVED | 7 |
| define_nonrecursive  | OBSERVED | 7 |
| define_command  | OBSERVED | 7 |
| define_command  | OBSERVED | 7 |
| define_structural  | OBSERVED | 8 |
| define_structural  | OBSERVED | 8 |
| selected_assignment  | OBSERVED | 7 |
| selected_assignment  | OBSERVED | 7 |
| loop_function  | OBSERVED | 7 |
| loop_function  | OBSERVED | 7 |
| multiline_literal  | OBSERVED | 7 |
| multiline_literal  | OBSERVED | 7 |
| inline_trailing  | OBSERVED | 7 |
| inline_trailing  | OBSERVED | 7 |
| eager_side_effect  | OBSERVED | 7 |
| eager_side_effect  | OBSERVED | 7 |
| wrap_underflow  | OBSERVED | 7 |
| wrap_underflow  | OBSERVED | 7 |
| implicit_value  | OBSERVED | 8 |
| implicit_value  | OBSERVED | 8 |
| inactive_unknown  | OBSERVED | 8 |
| inactive_unknown  | OBSERVED | 8 |
| hold  | OBSERVED | 7 |
| hold  | OBSERVED | 7 |
| release  | OBSERVED | 7 |
| release  | OBSERVED | 7 |
| inject_mod  | OBSERVED | 7 |
| inject_mod  | OBSERVED | 7 |
| stop_payload  | OBSERVED | 7 |
| stop_payload  | OBSERVED | 7 |
| restart_payload  | OBSERVED | 8 |
| restart_payload  | OBSERVED | 8 |
| reset  | OBSERVED | 7 |
| reset  | OBSERVED | 7 |
| led_green  | OBSERVED | 7 |
| led_green  | OBSERVED | 7 |
| button_wait  | OBSERVED | 8 |
| button_wait  | OBSERVED | 8 |
| lock_wait  | OBSERVED | 7 |
| lock_wait  | OBSERVED | 7 |
| save_lock  | OBSERVED | 7 |
| save_lock  | OBSERVED | 7 |
| save_mode  | OBSERVED | 8 |
| save_mode  | OBSERVED | 8 |
| random_character  | OBSERVED | 8 |
| random_character  | OBSERVED | 8 |
| inject_variable  | OBSERVED | 8 |
| inject_variable  | OBSERVED | 8 |
| storage_wait  | OBSERVED | 8 |
| storage_wait  | OBSERVED | 8 |
| hide_payload  | OBSERVED | 8 |
| hide_payload  | OBSERVED | 8 |
| extension_wrapper  | OBSERVED | 7 |
| extension_wrapper  | OBSERVED | 7 |
| conditional_compile  | OBSERVED | 7 |
| conditional_compile  | OBSERVED | 7 |
| language_string  | OBSERVED | 7 |
| language_string  | OBSERVED | 7 |
| usb_identity  | OBSERVED | 8 |
| usb_identity  | OBSERVED | 8 |
| undefined_builtin  | OBSERVED | 8 |
| undefined_builtin  | OBSERVED | 8 |
| inert_builtin_declaration  | OBSERVED | 8 |
| inert_builtin_declaration  | OBSERVED | 8 |
| delay_below_reference_minimum  | OBSERVED | 7 |
| delay_below_reference_minimum  | OBSERVED | 7 |
| production_attackmode_failure  | OBSERVED | 2 |

### stage15_historical_routing

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| known_hid_vectors_no_numeric_encoding unpatched | PASS | 22 |
| normalized_interrupt_output unpatched | PASS | 3 |
| legacy_type_zero_interrupt unpatched | PASS | 1 |
| nonzero_control_output unpatched | OBSERVED | 2 |
| feature_led_type_separation unpatched | OBSERVED | 2 |
| input_type_rejected unpatched | OBSERVED | 1 |
| invalid_type_rejected unpatched | OBSERVED | 1 |
| invalid_instance unpatched | OBSERVED | 1 |
| zero_transfer_backed_buffer unpatched | OBSERVED | 2 |
| report_id_only_interrupt unpatched | PASS | 1 |
| zero_length_control_output unpatched | PASS | 1 |
| null_control_output unpatched | PASS | 1 |
| unknown_report_id unpatched | PASS | 1 |
| zero_id_device_no_prefix_stripping unpatched | PASS | 2 |
| all_led_masks_through_actual_route unpatched | PASS | 33 |
| padding_and_length_rejection unpatched | PASS | 2 |
| repeated_report_not_transition unpatched | PASS | 1 |
| detached_feedback_rejection unpatched | PASS | 1 |
| stale_explicit_token_rejection unpatched | PASS | 2 |
| routing_during_owned_injection unpatched | PASS | 4 |
| stock_output_queue_wait_policy unpatched | OBSERVED | 1 |
| null_zero_interrupt unpatched | XFAIL | 0 |
| empty_onepast_interrupt unpatched | XFAIL | 0 |
| null_nonzero_interrupt unpatched | XFAIL | 0 |
| debug_invalid_type_unknown_id unpatched | XFAIL | 0 |
| stock_output_null unpatched | XFAIL | 0 |
| stock_output_empty_onepast unpatched | XFAIL | 0 |
| known_hid_vectors_no_numeric_encoding paired_proposal | PASS | 22 |
| normalized_interrupt_output paired_proposal | PASS | 3 |
| legacy_type_zero_interrupt paired_proposal | PASS | 1 |
| nonzero_control_output paired_proposal | PASS | 2 |
| feature_led_type_separation paired_proposal | PASS | 2 |
| input_type_rejected paired_proposal | PASS | 1 |
| invalid_type_rejected paired_proposal | PASS | 1 |
| invalid_instance paired_proposal | PASS | 1 |
| zero_transfer_backed_buffer paired_proposal | PASS | 2 |
| report_id_only_interrupt paired_proposal | PASS | 1 |
| zero_length_control_output paired_proposal | PASS | 1 |
| null_control_output paired_proposal | PASS | 1 |
| unknown_report_id paired_proposal | PASS | 1 |
| zero_id_device_no_prefix_stripping paired_proposal | PASS | 2 |
| all_led_masks_through_actual_route paired_proposal | PASS | 33 |
| padding_and_length_rejection paired_proposal | PASS | 2 |
| repeated_report_not_transition paired_proposal | PASS | 1 |
| detached_feedback_rejection paired_proposal | PASS | 1 |
| stale_explicit_token_rejection paired_proposal | PASS | 2 |
| routing_during_owned_injection paired_proposal | PASS | 4 |
| stock_output_queue_wait_policy paired_proposal | PASS | 1 |
| null_zero_interrupt paired_proposal | PASS | 1 |
| empty_onepast_interrupt paired_proposal | PASS | 1 |
| null_nonzero_interrupt paired_proposal | PASS | 1 |
| debug_invalid_type_unknown_id paired_proposal | PASS | 1 |

### stage16_routing

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| known_hid_vectors_no_numeric_encoding  | PASS | 22 |
| normalized_interrupt_output  | PASS | 3 |
| legacy_type_zero_interrupt  | PASS | 1 |
| nonzero_control_output  | PASS | 2 |
| feature_led_type_separation  | PASS | 2 |
| input_type_rejected  | PASS | 1 |
| invalid_type_rejected  | PASS | 1 |
| invalid_instance  | PASS | 1 |
| zero_transfer_backed_buffer  | PASS | 2 |
| report_id_only_interrupt  | PASS | 1 |
| zero_length_control_output  | PASS | 1 |
| null_control_output  | PASS | 1 |
| unknown_report_id  | PASS | 1 |
| zero_id_device_no_prefix_stripping  | PASS | 2 |
| all_led_masks_through_actual_route  | PASS | 33 |
| padding_and_length_rejection  | PASS | 2 |
| repeated_report_not_transition  | PASS | 1 |
| detached_feedback_rejection  | PASS | 1 |
| stale_explicit_token_rejection  | PASS | 2 |
| routing_during_owned_injection  | PASS | 4 |
| stock_output_queue_wait_policy  | OBSERVED | 1 |
| null_zero_interrupt  | PASS | 1 |
| empty_onepast_interrupt  | PASS | 1 |
| null_nonzero_interrupt  | PASS | 1 |
| debug_invalid_type_unknown_id  | PASS | 1 |
| integrated_feature_cannot_change_known_led  | PASS | 1 |
| integrated_all_report_types_and_ids  | PASS | 65536 |
| integrated_null_lengths_types  | PASS | 1 |
| integrated_empty_output_never_enters_stock_hook  | PASS | 2 |
| integrated_payload_boundaries  | PASS | 6 |
| integrated_bounded_callback_reentry  | PASS | 2 |
| integrated_executor_lock_independent  | PASS | 1 |
| integrated_concurrent_snapshots  | PASS | 10001 |
| integrated_input_backpressure_feedback  | PASS | 2 |
| integrated_disconnect_reconnect_unknown  | PASS | 4 |
| integrated_no_led_event_queue_post  | PASS | 1 |

### stage16_validation

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| unpatched_tree_verified  | PASS | 1 |
| patched_tree_verified  | PASS | 1 |
| unpatched_core_rejected_for_stage16  | PASS | 1 |
| patched_core_rejected_as_upstream_original  | PASS | 1 |
| unexpected_core_version_rejected  | PASS | 1 |
| unexpected_source_bytes_rejected  | PASS | 1 |
| installed_data_isolation_rejected  | PASS | 1 |
| installed_user_isolation_rejected  | PASS | 1 |
| existing_isolation_destination_rejected  | PASS | 1 |
| repository_isolation_destination_rejected  | PASS | 1 |
| build_requires_patched_core_argument  | PASS | 1 |
| ordinary_firmware_compile_rejected  | PASS | 1 |
| verified_firmware_compile_guard_enabled  | PASS | 1 |
| cli_unpatched_fallback_rejected_before_compile  | PASS | 1 |
| full_linked_production_firmware_provenance  | PASS | 1 |

### stage17

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| stage17_synthetic_backup_roundtrip  | PASS | 1 |
| stage17_missing_backups  | PASS | 1 |
| stage17_owner_hashes_reject_synthetic_files  | PASS | 1 |
| stage17_custom_hashes_cannot_claim_owner_evidence  | PASS | 1 |
| stage17_old_new_size_raw_relocation_rejected  | PASS | 1 |
| stage17_wrong_backup_hash  | PASS | 1 |
| stage17_truncated_filesystem  | PASS | 1 |
| stage17_corrupt_partition_sector_hash  | PASS | 1 |
| stage17_invalid_spiffs_geometry_extractability  | PASS | 1 |
| stage17_partition_sector_full_backup_mismatch  | PASS | 1 |
| stage17_corrupted_partition_structure  | PASS | 1 |
| stage17_proposed_layout_not_original_backup  | PASS | 1 |
| stage17_valid_esp_image_checksum_digest  | PASS | 1 |
| stage17_invalid_esp_chip  | PASS | 1 |
| stage17_invalid_esp_checksum  | PASS | 1 |
| stage17_invalid_esp_digest  | PASS | 1 |
| stage17_invalid_esp_segment  | PASS | 1 |
| stage17_truncated_esp_digest  | PASS | 1 |
| stage17_legacy_flash_header_not_new  | PASS | 1 |
| stage17_actual_normal_artifact_checksum  | PASS | 1 |
| stage17_erased_recovery_image_rejected  | PASS | 1 |
| stage17_normal_firmware_exceeds_old_slots  | PASS | 1 |
| stage17_actual_patched_normal_link  | PASS | 1 |
| stage17_forged_safe_build_metadata_rejected  | PASS | 1 |
| stage17_rehashed_swapped_binary_rejected_by_elf  | PASS | 1 |
| stage17_actual_patched_safe_link  | PASS | 1 |
| stage17_complete_safe_plan_nvs_preserved  | PASS | 1 |
| stage17_old_app1_offset_rejected  | PASS | 1 |
| stage17_nvs_overlap_rejected  | PASS | 1 |
| stage17_overlapping_stored_erases_rejected  | PASS | 1 |
| stage17_non_aligned_stored_erases_rejected  | PASS | 1 |
| stage17_plan_nvs_metadata_rejected  | PASS | 1 |
| stage17_false_migration_authorization_rejected  | PASS | 1 |
| stage17_missing_plan_artifact_rejected  | PASS | 1 |
| stage17_path_traversal_rejected  | PASS | 1 |
| stage17_wrong_application_hash_rejected  | PASS | 1 |
| stage17_corrupt_otadata_even_with_rehashed_manifest  | PASS | 1 |
| stage17_corrupt_coredump_even_with_rehashed_manifest  | PASS | 1 |
| stage17_corrupt_partitions_even_with_rehashed_manifest  | PASS | 1 |
| stage17_corrupt_app0_even_with_rehashed_manifest  | PASS | 1 |
| stage17_corrupt_spiffs_even_with_rehashed_manifest  | PASS | 1 |
| stage17_normal_build_not_first_boot_safe  | PASS | 1 |
| stage17_sources_not_modified  | PASS | 1 |
| stage17_recovery_backup_exact_region  | PASS | 1 |
| stage17_checked_plan_generation_synthetic_only  | PASS | 1 |
| stage17_checked_plan_no_overwrite  | PASS | 1 |
| stage17_checked_plan_missing_owner_files  | PASS | 1 |
| stage17_checked_plan_wrong_owner_hashes  | PASS | 1 |
| stage17_failed_plan_creates_no_output  | PASS | 1 |
| stage17_provisional_artifact_inventory_not_authorization  | PASS | 1 |
| stage17_artifact_inventory_no_overwrite  | PASS | 1 |
| stage17_no_full_chip_erase_plan  | PASS | 1 |
| stage17_pre_setup_nvs_erase_risk_recorded  | OBSERVED | 1 |
| stage17_normal_spiffs_format_risk_preserved  | OBSERVED | 1 |
| stage17_normal_startup_compatibility  | PASS | 10 |
| stage17_safe_start_actual_setup_loop  | PASS | 11 |
| stage17_invalid_safe_profile_rejected  | PASS | 1 |

### stage18_nvs

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| historical_no_free_pages_erase historical_unpatched | OBSERVED | 3 |
| historical_new_version_erase historical_unpatched | OBSERVED | 3 |
| historical_erase_failure_error_replaced historical_unpatched | OBSERVED | 2 |
| protected_initial_unknown normal | PASS | 14 |
| protected_success normal | PASS | 4 |
| protected_no_free_pages normal | PASS | 17 |
| protected_new_version normal | PASS | 17 |
| protected_invalid_metadata normal | PASS | 17 |
| protected_missing_partition normal | PASS | 17 |
| protected_flash_read_failure normal | PASS | 17 |
| protected_flash_initialization_failure normal | PASS | 17 |
| protected_flash_operation_failure normal | PASS | 17 |
| protected_no_memory normal | PASS | 17 |
| protected_unexpected_positive normal | PASS | 17 |
| protected_unexpected_negative normal | PASS | 17 |
| protected_repeat_failure normal | PASS | 39 |
| protected_retry_never_arms_failed_app normal | PASS | 15 |
| observed_sdk_side_effect_outside_policy normal | OBSERVED | 13 |
| protected_initial_unknown safe | PASS | 14 |
| protected_success safe | PASS | 14 |
| protected_no_free_pages safe | PASS | 17 |
| protected_new_version safe | PASS | 17 |
| protected_invalid_metadata safe | PASS | 17 |
| protected_missing_partition safe | PASS | 17 |
| protected_flash_read_failure safe | PASS | 17 |
| protected_flash_initialization_failure safe | PASS | 17 |
| protected_flash_operation_failure safe | PASS | 17 |
| protected_no_memory safe | PASS | 17 |
| protected_unexpected_positive safe | PASS | 17 |
| protected_unexpected_negative safe | PASS | 17 |
| protected_repeat_failure safe | PASS | 39 |
| protected_retry_never_arms_failed_app safe | PASS | 15 |
| observed_sdk_side_effect_outside_policy safe | OBSERVED | 13 |

### stage18_dependency

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| stage18_original_source_preserved  | PASS | 1 |
| stage18_actual_init_before_setup_task  | PASS | 1 |
| stage18_combined_patched_source_verified  | PASS | 1 |
| stage18_hid_only_core_rejected  | PASS | 1 |
| stage18_modified_policy_bytes_rejected  | PASS | 1 |
| stage18_native_missing_policy_guard_rejected  | PASS | 1 |
| stage18_verified_policy_compile_guard  | PASS | 1 |
| stage18_missing_core_hook_cannot_link  | PASS | 1 |
| stage18_final_linked_nvs_policy  | PASS | 1 |

### stage19_runtime

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| storage_clean sdk_recovery_source | PASS | 4 |
| storage_repeat_clean sdk_recovery_source | PASS | 5 |
| storage_orphan_blob sdk_recovery_source | PASS | 7 |
| storage_orphan_write_failure sdk_recovery_source | PASS | 7 |
| storage_mismatched_index sdk_recovery_source | PASS | 7 |
| storage_corrupt_string_read sdk_recovery_source | PASS | 8 |
| valid_entry sdk_recovery_source | PASS | 2 |
| erased_partition sdk_recovery_source | PASS | 2 |
| incomplete_entry sdk_recovery_source | PASS | 5 |
| incomplete_write_failure sdk_recovery_source | PASS | 3 |
| bad_entry_crc sdk_recovery_source | PASS | 4 |
| duplicate_entries sdk_recovery_source | PASS | 4 |
| corrupt_only sdk_recovery_source | PASS | 3 |
| new_version sdk_recovery_source | PASS | 2 |
| partial_header_read sdk_recovery_source | PASS | 2 |
| partial_table_read sdk_recovery_source | PASS | 2 |
| mutation_before_later_read_failure sdk_recovery_source | PASS | 3 |
| freeing_recovery sdk_recovery_source | PASS | 8 |
| freeing_write_failure sdk_recovery_source | PASS | 5 |
| freeing_erase_failure sdk_recovery_source | PASS | 3 |
| no_free_pages sdk_recovery_source | PASS | 2 |
| allocation_failure normal | PASS | 12 |
| missing_keys normal | PASS | 8 |
| missing_namespace normal | PASS | 8 |
| open_failure normal | PASS | 12 |
| not_initialized normal | PASS | 12 |
| type_mismatch normal | PASS | 12 |
| read_failure normal | PASS | 12 |
| string_read_failure normal | PASS | 12 |
| invalid_bool normal | PASS | 12 |
| invalid_channel normal | PASS | 12 |
| invalid_ssid normal | PASS | 12 |
| invalid_password normal | PASS | 12 |
| invalid_rgb normal | PASS | 12 |
| invalid_delay normal | PASS | 12 |
| autorun_without_script normal | PASS | 12 |
| oversized_string normal | PASS | 12 |
| missing_nul normal | PASS | 12 |
| embedded_nul normal | PASS | 12 |
| zero_length_string normal | PASS | 12 |
| valid_autorun normal | PASS | 9 |
| maximum_string normal | PASS | 8 |
| repeat_failure normal | PASS | 23 |
| save_after_failure normal | PASS | 12 |
| latched_failure normal | PASS | 16 |
| save_open_failure normal | PASS | 10 |
| allocation_failure safe | PASS | 5 |
| missing_keys safe | PASS | 5 |
| missing_namespace safe | PASS | 5 |
| open_failure safe | PASS | 5 |
| not_initialized safe | PASS | 5 |
| type_mismatch safe | PASS | 5 |
| read_failure safe | PASS | 5 |
| string_read_failure safe | PASS | 5 |
| invalid_bool safe | PASS | 5 |
| invalid_channel safe | PASS | 5 |
| invalid_ssid safe | PASS | 5 |
| invalid_password safe | PASS | 5 |
| invalid_rgb safe | PASS | 5 |
| invalid_delay safe | PASS | 5 |
| autorun_without_script safe | PASS | 5 |
| oversized_string safe | PASS | 5 |
| missing_nul safe | PASS | 5 |
| embedded_nul safe | PASS | 5 |
| zero_length_string safe | PASS | 5 |
| valid_autorun safe | PASS | 5 |
| maximum_string safe | PASS | 5 |
| repeat_failure safe | PASS | 5 |
| save_after_failure safe | PASS | 5 |
| latched_failure safe | PASS | 5 |
| save_open_failure safe | PASS | 5 |

### stage19_offline

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| nvs_valid_numeric  | PASS | 1 |
| nvs_all_erased  | PASS | 1 |
| nvs_size_0  | PASS | 1 |
| nvs_size_4096  | PASS | 1 |
| nvs_size_20479  | PASS | 1 |
| nvs_size_20481  | PASS | 1 |
| nvs_header_crc  | PASS | 3 |
| nvs_future_version  | PASS | 3 |
| nvs_legacy_version_conservative  | PASS | 3 |
| nvs_freeing  | PASS | 3 |
| nvs_incomplete_entry  | PASS | 3 |
| nvs_entry_crc  | PASS | 3 |
| nvs_illegal_bitmap  | PASS | 3 |
| nvs_reserved_bitmap  | PASS | 3 |
| nvs_duplicate_live_record  | PASS | 3 |
| nvs_multiple_active  | PASS | 3 |
| nvs_sequence_duplicate  | PASS | 3 |
| nvs_no_free_page  | PASS | 3 |
| nvs_bad_namespace  | PASS | 3 |
| nvs_unknown_type  | PASS | 3 |
| nvs_numeric_span  | PASS | 3 |
| nvs_blob_index_unproved  | PASS | 3 |
| nvs_dirty_erased_page  | PASS | 3 |
| nvs_valid_string_crc  | PASS | 1 |
| nvs_string_data_crc  | PASS | 2 |
| nvs_report_privacy  | PASS | 3 |
| nvs_official_generator_vector  | PASS | 2 |
| nvs_cli_read_only_and_overwrite_guards  | PASS | 4 |

### stage19_integration

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| sdk_source_hash_identity  | PASS | 1 |
| sdk_source_tamper_rejected  | PASS | 1 |
| generator_hash_identity  | PASS | 1 |
| pinned_archive_mutation_call_evidence  | PASS | 3 |
| linked_settings_policy_normal  | PASS | 3 |
| linked_settings_policy_safe  | PASS | 3 |
| owner_local_evidence_not_codex_inspection  | PASS | 1 |
| offline_plan_rejects_unresolved_nvs_structure  | PASS | 4 |

### stage20_runtime

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| busy_save application_nvs_api_standin | PASS | 4 |
| busy_reset application_nvs_api_standin | PASS | 4 |
| healthy_save application_nvs_api_standin | PASS | 5 |
| valid_autorun application_nvs_api_standin | PASS | 6 |
| valid_reset application_nvs_api_standin | PASS | 5 |
| unloaded_save application_nvs_api_standin | PASS | 3 |
| unloaded_reset application_nvs_api_standin | PASS | 3 |
| read_failure_save application_nvs_api_standin | PASS | 4 |
| open_failure application_nvs_api_standin | PASS | 4 |
| open_full application_nvs_api_standin | PASS | 5 |
| commit_failure application_nvs_api_standin | PASS | 4 |
| invalid_delay application_nvs_api_standin | PASS | 4 |
| invalid_web_length application_nvs_api_standin | PASS | 4 |
| embedded_nul application_nvs_api_standin | PASS | 4 |
| set_full application_nvs_api_standin | PASS | 6 |
| set_flash_error application_nvs_api_standin | PASS | 6 |
| failed_set_may_change_bytes application_nvs_api_standin | PASS | 6 |
| mixed_autorun_after_failure application_nvs_api_standin | PASS | 6 |
| reset_failure application_nvs_api_standin | PASS | 5 |
| set_failure_1 application_nvs_api_standin | PASS | 5 |
| set_failure_2 application_nvs_api_standin | PASS | 5 |
| set_failure_3 application_nvs_api_standin | PASS | 5 |
| set_failure_4 application_nvs_api_standin | PASS | 5 |
| set_failure_5 application_nvs_api_standin | PASS | 5 |
| set_failure_6 application_nvs_api_standin | PASS | 5 |
| set_failure_7 application_nvs_api_standin | PASS | 5 |
| set_failure_8 application_nvs_api_standin | PASS | 5 |
| set_failure_9 application_nvs_api_standin | PASS | 5 |
| set_failure_10 application_nvs_api_standin | PASS | 5 |
| set_failure_11 application_nvs_api_standin | PASS | 5 |
| set_failure_12 application_nvs_api_standin | PASS | 5 |
| interrupted_save application_nvs_api_standin | OBSERVED | 2 |
| readonly_corrupt_string actual_sdk_component_source | PASS | 6 |
| corrupt_read_becomes_not_found actual_sdk_component_source | OBSERVED | 6 |
| readonly_clean actual_sdk_component_source | PASS | 4 |
| readonly_incomplete_entry actual_sdk_component_source | PASS | 5 |
| readonly_bad_entry_crc actual_sdk_component_source | PASS | 5 |
| readonly_freeing actual_sdk_component_source | PASS | 4 |
| readonly_corrupt_activation actual_sdk_component_source | PASS | 5 |

### stage20_ui

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| web_save_busy  | PASS | 4 |
| web_led_busy  | PASS | 4 |
| cli_save_success  | PASS | 3 |
| cli_save_failure  | PASS | 4 |
| cli_reset_success  | PASS | 3 |
| cli_reset_failure  | PASS | 4 |
| cli_autorun_success  | PASS | 3 |
| cli_autorun_failure  | PASS | 4 |
| web_save_success  | PASS | 3 |
| web_save_failure  | PASS | 4 |
| web_led_success  | PASS | 3 |
| web_led_failure  | PASS | 4 |
| web_led_missing  | PASS | 4 |

### stage20_summary

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| summary_privacy_whitelist  | PASS | 3 |
| summary_invalid  | PASS | 1 |
| summary_unsupported_format  | PASS | 1 |
| summary_recovery_potentially_required  | PASS | 1 |
| summary_insufficient_evidence  | PASS | 1 |
| summary_reject_wrong_backup_hash  | PASS | 1 |
| summary_reject_wrong_backup_size  | PASS | 1 |
| summary_reject_wrong_partition_layout  | PASS | 1 |
| summary_reject_missing_spiffs_roundtrip  | PASS | 1 |
| summary_reject_unknown_private_code  | PASS | 1 |
| summary_reject_bad_page_location  | PASS | 1 |
| summary_reject_bad_entry_location  | PASS | 1 |
| summary_reject_false_immutability  | PASS | 1 |
| summary_reject_inconsistent_classification  | PASS | 1 |
| summary_reject_false_authorization  | PASS | 1 |
| summary_reject_no_recovery_app  | PASS | 1 |
| summary_reject_missing_bootloader_check  | PASS | 1 |
| summary_cli_read_only_no_overwrite  | PASS | 3 |

### stage20_integration

Full captured evidence: stage20-results.json.

| Test / variant | Result | Assertions |
| --- | --- | ---: |
| native_readonly_descriptor_offset  | PASS | 1 |
| pinned_archive_readonly_guard_evidence  | PASS | 8 |
| final_checked_persistence_provenance  | PASS | 2 |
| partition_policy_unchanged  | PASS | 1 |

## Modified and created files

- `deployment/stage20/README.md`
- `deployment/stage20/artifact-inventory.json`
- `deployment/stage20/bootloader.bin`
- `deployment/stage20/coredump-empty.bin`
- `deployment/stage20/normal-app.bin`
- `deployment/stage20/otadata-app0.bin`
- `deployment/stage20/partitions-sector.bin`
- `deployment/stage20/safe-app.bin`
- `docs/stage20-architectures.md`
- `docs/stage20-contract.md`
- `docs/stage20-esp_partition_erase_range-archive.txt`
- `docs/stage20-esp_partition_write-archive.txt`
- `docs/stage20-esp_partition_write_raw-archive.txt`
- `docs/stage20-mutation-paths.md`
- `docs/stage20-normal-build.log`
- `docs/stage20-normal-linked-nvs.txt`
- `docs/stage20-normal-linked-startup.txt`
- `docs/stage20-normal-provenance.json`
- `docs/stage20-normal-resources.json`
- `docs/stage20-normal-stack.json`
- `docs/stage20-owner-inspection.md`
- `docs/stage20-partition-archive.json`
- `docs/stage20-partition-reference.json`
- `docs/stage20-readiness.md`
- `docs/stage20-report.md`
- `docs/stage20-reproduction.md`
- `docs/stage20-results.json`
- `docs/stage20-safe-build.log`
- `docs/stage20-safe-linked-nvs.txt`
- `docs/stage20-safe-linked-startup.txt`
- `docs/stage20-safe-provenance.json`
- `docs/stage20-safe-resources.json`
- `docs/stage20-safe-stack.json`
- `docs/stage20-sdk-nvs-evidence.json`
- `tests/stage20/README.md`
- `tests/stage20/integration_tests.py`
- `tests/stage20/partition_api.h`
- `tests/stage20/readonly_source.cpp`
- `tests/stage20/run_tests.py`
- `tests/stage20/settings_save.cpp`
- `tests/stage20/summary_tests.py`
- `tests/stage20/ui.cpp`
- `tests/stage20/ui_tests.py`
- `tools/deployment_summary.py`
- `tools/partition_source_prepare.py`
- `EvilDuckS3/cli.cpp`
- `EvilDuckS3/settings.cpp`
- `EvilDuckS3/settings.h`
- `EvilDuckS3/webserver.cpp`
- `tests/stage1/mocks/host.cpp`
- `tests/stage1/mocks/host.h`
- `tests/stage19/settings_startup.cpp`
- `tools/analyze_s3_stack.py`
- `tools/verify_patched_firmware.py`
