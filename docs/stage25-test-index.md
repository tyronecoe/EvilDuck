# Stage 25 exact executed test index

150 PASS; 0 unexpected FAIL; 1398 assertions.

Only affected suites ran. Historical XPASS and interrupted-save observation are separate.

## stage25-startup-with-network

- `/network_failure`: PASS; 25 assertions.
- `/valid_fresh`: PASS; 20 assertions.
- `/missing_namespace`: PASS; 21 assertions.
- `/missing_ssid`: PASS; 21 assertions.
- `/missing_password`: PASS; 21 assertions.
- `/missing_web_password`: PASS; 21 assertions.
- `/blank_password`: PASS; 21 assertions.
- `/blank_web_password`: PASS; 21 assertions.
- `/legacy_password`: PASS; 21 assertions.
- `/short_password`: PASS; 21 assertions.
- `/long_password`: PASS; 21 assertions.
- `/long_ssid`: PASS; 21 assertions.
- `/newline_credentials`: PASS; 21 assertions.
- `/credential_type_mismatch`: PASS; 21 assertions.
- `/credential_read_failure`: PASS; 21 assertions.
- `/allocation_failure`: PASS; 21 assertions.
- `/corrupt_nul`: PASS; 21 assertions.
- `/nvs_open_failure`: PASS; 21 assertions.
- `/nvs_startup_failure`: PASS; 18 assertions.
- `/stored_autorun`: PASS; 21 assertions.
- `/mount_failure`: PASS; 25 assertions.
- `/missing_filesystem`: PASS; 25 assertions.
- `/interrupted_mount`: PASS; 22 assertions.
- `/wrong_layout`: PASS; 20 assertions.
- `/readonly_layout`: PASS; 20 assertions.
- `/partition_lookup_failure`: PASS; 20 assertions.
- `/duplicate_partition`: PASS; 20 assertions.
- `/missing_partition`: PASS; 20 assertions.
- `/wrong_chip`: PASS; 20 assertions.
- `/settings_controls`: PASS; 23 assertions.

## stage25-network-tests

- `/valid`: PASS; 3 assertions.
- `/settings_failure`: PASS; 3 assertions.
- `/wrong_profile`: PASS; 3 assertions.
- `/mode_failure`: PASS; 4 assertions.
- `/ap_failure`: PASS; 5 assertions.
- `/shutdown_failure`: PASS; 5 assertions.

## stage25-final-recovery-tests

- `/compiled_images_offline_structure_only`: PASS; 1 assertions.
- `/wrong_hash`: PASS; 1 assertions.
- `/wrong_offset`: PASS; 1 assertions.
- `/wrong_bytes`: PASS; 1 assertions.
- `/wrong_physical_size`: PASS; 1 assertions.
- `/missing_role`: PASS; 1 assertions.
- `/duplicate_role`: PASS; 1 assertions.
- `/corrupt_table_even_with_matching_hash`: PASS; 1 assertions.
- `/synthetic_legacy_4m_header_on_16m_hardware_context`: PASS; 1 assertions.
- `/upgraded_application_does_not_fit_original_slot`: PASS; 1 assertions.
- `/reject_minimum_revision`: PASS; 1 assertions.
- `/reject_maximum_revision`: PASS; 1 assertions.
- `/reject_bad_flash_frequency`: PASS; 1 assertions.
- `/reject_excess_flash_capacity`: PASS; 1 assertions.
- `/reject_insufficient_flash_profile`: PASS; 1 assertions.
- `/reject_bad_chip`: PASS; 1 assertions.
- `/unsupported_entry_point_rejected`: PASS; 1 assertions.
- `/sdk_max_revision_zero_sentinel_and_bootloader_max_exemption`: PASS; 1 assertions.
- `/nondeterministic_ota_initializer_rejected`: PASS; 1 assertions.
- `/linked_normal_profile`: PASS; 1 assertions.
- `/linked_safe_profile`: PASS; 1 assertions.
- `/linked_controlled_profile`: PASS; 1 assertions.
- `/conflicting_build_profile_rejected`: PASS; 1 assertions.
- `/explicit_private_config_contract`: PASS; 1 assertions.
- `/missing_private_config_rejected`: PASS; 1 assertions.
- `/legacy_provisioning_password_rejected`: PASS; 1 assertions.
- `/pinned_native_image_header_revision_offsets`: PASS; 1 assertions.
- `/merged_output_suppressed_by_real_compile_options`: PASS; 1 assertions.

## stage25-settings-regressions

- `legacy-normal/allocation_failure`: PASS; 12 assertions.
- `legacy-normal/missing_keys`: PASS; 8 assertions.
- `legacy-normal/missing_namespace`: PASS; 8 assertions.
- `legacy-normal/open_failure`: PASS; 12 assertions.
- `legacy-normal/not_initialized`: PASS; 12 assertions.
- `legacy-normal/type_mismatch`: PASS; 12 assertions.
- `legacy-normal/read_failure`: PASS; 12 assertions.
- `legacy-normal/string_read_failure`: PASS; 12 assertions.
- `legacy-normal/invalid_bool`: PASS; 12 assertions.
- `legacy-normal/invalid_channel`: PASS; 12 assertions.
- `legacy-normal/invalid_ssid`: PASS; 12 assertions.
- `legacy-normal/invalid_password`: PASS; 12 assertions.
- `legacy-normal/invalid_rgb`: PASS; 12 assertions.
- `legacy-normal/invalid_delay`: PASS; 12 assertions.
- `legacy-normal/autorun_without_script`: PASS; 12 assertions.
- `legacy-normal/oversized_string`: PASS; 12 assertions.
- `legacy-normal/missing_nul`: PASS; 12 assertions.
- `legacy-normal/embedded_nul`: PASS; 12 assertions.
- `legacy-normal/zero_length_string`: PASS; 12 assertions.
- `legacy-normal/valid_autorun`: PASS; 9 assertions.
- `legacy-normal/maximum_string`: PASS; 8 assertions.
- `legacy-normal/repeat_failure`: PASS; 23 assertions.
- `legacy-normal/save_after_failure`: PASS; 12 assertions.
- `legacy-normal/latched_failure`: PASS; 16 assertions.
- `legacy-normal/save_open_failure`: PASS; 10 assertions.
- `legacy-safe/allocation_failure`: PASS; 5 assertions.
- `legacy-safe/missing_keys`: PASS; 5 assertions.
- `legacy-safe/missing_namespace`: PASS; 5 assertions.
- `legacy-safe/open_failure`: PASS; 5 assertions.
- `legacy-safe/not_initialized`: PASS; 5 assertions.
- `legacy-safe/type_mismatch`: PASS; 5 assertions.
- `legacy-safe/read_failure`: PASS; 5 assertions.
- `legacy-safe/string_read_failure`: PASS; 5 assertions.
- `legacy-safe/invalid_bool`: PASS; 5 assertions.
- `legacy-safe/invalid_channel`: PASS; 5 assertions.
- `legacy-safe/invalid_ssid`: PASS; 5 assertions.
- `legacy-safe/invalid_password`: PASS; 5 assertions.
- `legacy-safe/invalid_rgb`: PASS; 5 assertions.
- `legacy-safe/invalid_delay`: PASS; 5 assertions.
- `legacy-safe/autorun_without_script`: PASS; 5 assertions.
- `legacy-safe/oversized_string`: PASS; 5 assertions.
- `legacy-safe/missing_nul`: PASS; 5 assertions.
- `legacy-safe/embedded_nul`: PASS; 5 assertions.
- `legacy-safe/zero_length_string`: PASS; 5 assertions.
- `legacy-safe/valid_autorun`: PASS; 5 assertions.
- `legacy-safe/maximum_string`: PASS; 5 assertions.
- `legacy-safe/repeat_failure`: PASS; 5 assertions.
- `legacy-safe/save_after_failure`: PASS; 5 assertions.
- `legacy-safe/latched_failure`: PASS; 5 assertions.
- `legacy-safe/save_open_failure`: PASS; 5 assertions.
- `legacy-checked-save/busy_save`: PASS; 4 assertions.
- `legacy-checked-save/busy_reset`: PASS; 4 assertions.
- `legacy-checked-save/healthy_save`: PASS; 5 assertions.
- `legacy-checked-save/valid_autorun`: PASS; 6 assertions.
- `legacy-checked-save/valid_reset`: PASS; 5 assertions.
- `legacy-checked-save/unloaded_save`: PASS; 3 assertions.
- `legacy-checked-save/unloaded_reset`: PASS; 3 assertions.
- `legacy-checked-save/read_failure_save`: PASS; 4 assertions.
- `legacy-checked-save/open_failure`: PASS; 4 assertions.
- `legacy-checked-save/open_full`: PASS; 5 assertions.
- `legacy-checked-save/commit_failure`: PASS; 4 assertions.
- `legacy-checked-save/invalid_delay`: PASS; 4 assertions.
- `legacy-checked-save/invalid_web_length`: PASS; 4 assertions.
- `legacy-checked-save/embedded_nul`: PASS; 4 assertions.
- `legacy-checked-save/set_full`: PASS; 6 assertions.
- `legacy-checked-save/set_flash_error`: PASS; 6 assertions.
- `legacy-checked-save/failed_set_may_change_bytes`: PASS; 6 assertions.
- `legacy-checked-save/mixed_autorun_after_failure`: PASS; 6 assertions.
- `legacy-checked-save/reset_failure`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_1`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_2`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_3`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_4`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_5`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_6`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_7`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_8`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_9`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_10`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_11`: PASS; 5 assertions.
- `legacy-checked-save/set_failure_12`: PASS; 5 assertions.
- `legacy-checked-save/interrupted_save`: OBSERVED; 2 assertions.

## stage1_runtime

- `/supported_commands_and_mock_interfaces`: PASS; 29 assertions.
- `/script_run_state_isolation`: PASS; 22 assertions.
- `/cooperative_delay_and_text_cancellation`: PASS; 33 assertions.
- `/repeat_timing_and_control_loop_yield`: PASS; 24 assertions.
- `/live_commands_cannot_mutate_running_script`: PASS; 19 assertions.
- `known_nested_if`: XPASS (historical diagnostic).
- `known_canonical_if`: XPASS (historical diagnostic).
- `known_false_while`: XPASS (historical diagnostic).
- `known_f13_mapping`: XPASS (historical diagnostic).
- `known_german_ascii_table`: XPASS (historical diagnostic).
