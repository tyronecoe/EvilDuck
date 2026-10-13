# Stage28A updated preview compatibility matrix

NOT FLASH-AUTHORIZED. This is the independent mock-only preview, not the production firmware.
The historical Stage27B matrix/report remain unchanged. Rows inherit the144-entry Stage9 audit
inventory (including extension/unestablished entries), plus the now-implemented expression-call
row. Unsupported observations are not compatibility passes; no full/current DS3 parity claim.
Source provenance and side-effect/overflow ambiguities remain documented separately.

| Feature | Stage28A preview status | Behavior / limits | Evidence |
|---|---|---|---|
| STRING text / STRINGLN text | Partial | Single-line ASCII text, CHARACTER events, trailing whitespace omitted; STRINGLN finishes ENTER; no real HID/layout | line_endings_whitespace; named_key_event_order |
| STRING … END_STRING | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRINGLN … END_STRINGLN | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRING_BASH … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRINGLN_BASH … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRING_BATCH … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRINGLN_BATCH … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRING_HTML … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRINGLN_HTML … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRING_JAVASCRIPT … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRINGLN_JAVASCRIPT … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRING_POWERSHELL … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRINGLN_POWERSHELL … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRING_PYTHON … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRINGLN_PYTHON … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRING_RUBY … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STRINGLN_RUBY … | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| F1 … F24 | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| UPARROW/DOWNARROW/LEFTARROW/RIGHTARROW (UP/DOWN/LEFT/RIGHT) | Partial | Only UPARROW/DOWNARROW/LEFTARROW/RIGHTARROW (no short aliases) | named_key_event_order |
| PAGEUP/PAGEDOWN/HOME/END | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| INSERT/DELETE/BACKSPACE/TAB/SPACE | Partial | DELETE/BACKSPACE/TAB/SPACE only | named_key_event_order |
| ENTER/ESCAPE/PAUSE/BREAK/PRINTSCREEN | Partial | ENTER/ESCAPE only | named_key_event_order |
| CAPSLOCK/NUMLOCK/SCROLLLOCK | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| SHIFT key (or modifier-key) | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| ALT / OPTION key (or modifier-key) | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| CONTROL / CTRL key (or modifier-key) | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WINDOWS / GUI / COMMAND key (or modifier-key) | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| Bare letter/number; keypad/named aliases; KEYCODE modifier keys… | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| HOLD key | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RELEASE key | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| INJECT_MOD [modifier] | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| Locale / Unicode | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| REM text | Supported in bounded mock core | Exact REM token; comment-only | empty_comments |
| REM_BLOCK [introductory text] … END_REM | Partial | REM_BLOCK with no heading or DOCUMENTATION only; exact END_REM | empty_comments |
| VAR $name = expression; $name = expression | Supported within documented preview bounds | Declarations/assignments consume resumable call values; globals and checked uint16 semantics unchanged | Stage28A assignment_forward_nested_arithmetic; left_to_right_capture_eager_power |
| TRUE / FALSE | Supported in bounded mock core | TRUE1/FALSE0; all nonzero values true | all_numeric_operators |
| DEFINE #LABEL value / DEFINE LABEL value | Partial | One-pass operand substitution; no structural expansion; duplicate definitions rejected | constants_replacement |
| VAR $x = ($x + 1) (reference “augmented assignment”) | Supported within bounds | VAR redeclaration evaluates existing global value | variables_global_redeclaration |
| + - * / % ^ | Partial | All listed operators; checked overflow/domain policy not independently canonical | Stage28A operators_with_function_operands; arithmetic_results_and_source_mapping; fresh Stage27B operator regressions |
| == != < <= > >= | Supported in bounded mock core | Six numeric comparisons give0/1 | Stage28A operators_with_function_operands; arithmetic_results_and_source_mapping; fresh Stage27B operator regressions |
| && \|\| | Partial | AND/OR truth; eager evaluation policy unresolved in reference | Stage28A operators_with_function_operands; arithmetic_results_and_source_mapping; fresh Stage27B operator regressions |
| & \| << >> | Partial | Bitwise AND/OR and shifts0..15; overflowing left shift rejected | Stage28A operators_with_function_operands; arithmetic_results_and_source_mapping; fresh Stage27B operator regressions |
| (expression), decimal, 0xhex | Partial | Grouping/decimal/hex; unparenthesized precedence is explicit preview policy | Stage28A operators_with_function_operands; arithmetic_results_and_source_mapping; fresh Stage27B operator regressions |
| Unary ! ~ - + / XOR | Not established / unsupported | No invented unary/XOR syntax | arithmetic_and_syntax_failures |
| IF expression THEN … ELSE IF expression THEN … ELSE … END_IF | Supported within bounds | Existing IF/ELSE IF plus eligible expression function calls; inactive conditions do not call | Stage28A if_else_if_selected_calls_only; Stage27B regressions |
| WHILE expression … END_WHILE | Supported within bounds | Fresh function conditions each iteration; bounded mixed IF/WHILE/calls | Stage28A while_reevaluation_zero_iteration; Stage27B regressions |
| FUNCTION NAME() … END_FUNCTION / NAME() | Supported within preview bounds; oracle edge parity unresolved | Standalone and numeric expression calls, forward/nested invocation; same eight-frame cap | Stage28A required_fixture; depth_limit_cycles_and_frames; bounded_work_cooperative_and_reentrant |
| RETURN [integer/boolean expression] | Supported within bounds; partial static return proof | Integer/Boolean/void returns; resumable return-of-call; static no-value rejection and mixed-path runtime VoidValue | Stage28A return_of_call_and_boolean; runtime_void_no_stale_return; static_void_unknown_arity_zero_output |
| DELAY integer/expression | Partial | Function-result uint16 delay; one acceptance-based clock owner; existing time/tick caps | Stage28A delay_call_single_timing_owner |
| DEFAULT_DELAY / DEFAULTDELAY, WAIT, REPEAT / REPLAY | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| STOP_PAYLOAD | Supported in bounded mock core | Cancels pending mock work only; no physical ownership exists | cancellation_and_sink_errors |
| RESTART_PAYLOAD | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RESET | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| ATTACKMODE HID / STORAGE / HID STORAGE / OFF | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| VID_xxxx PID_xxxx | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| MAN_name PROD_name SERIAL_name | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| SAVE_ATTACKMODE | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RESTORE_ATTACKMODE | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_BUTTON_PRESS | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| BUTTON_DEF … END_BUTTON | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| DISABLE_BUTTON | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| ENABLE_BUTTON | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| LED_OFF | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| LED_R | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| LED_G | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| System/injection/storage/exfil/lock LED policies | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_CAPS_CHANGE | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_CAPS_ON | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_CAPS_OFF | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_NUM_CHANGE | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_NUM_ON | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_NUM_OFF | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_SCROLL_CHANGE | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_SCROLL_ON | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_SCROLL_OFF | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| SAVE_HOST_KEYBOARD_LOCK_STATE | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RESTORE_HOST_KEYBOARD_LOCK_STATE | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| VID_RANDOM | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| PID_RANDOM | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| MAN_RANDOM | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| PROD_RANDOM | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| SERIAL_RANDOM | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RANDOM_LOWERCASE_LETTER | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RANDOM_UPPERCASE_LETTER | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RANDOM_LETTER | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RANDOM_NUMBER | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RANDOM_SPECIAL | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RANDOM_CHAR | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RANDOM_CHARACTER | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| INJECT_VAR $variable | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_STORAGE_ACTIVITY | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| WAIT_FOR_STORAGE_INACTIVITY | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| HIDE_PAYLOAD | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| RESTORE_PAYLOAD | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| Keystroke Reflection / $_EXFIL_MODE_ENABLED | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| IF_DEFINED_TRUE #LABEL | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| IF_NOT_DEFINED_TRUE #LABEL | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| ELSE_DEFINED | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| END_IF_DEFINED | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| EXTENSION name … END_EXTENSION | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| VERSION version | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| OS_DETECT / DETECT_OS() / $_OS | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| TRANSLATE | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| ASCIIDUCK / DUCK() | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| MATCH | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| SAVEKEYS | Unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_BUTTON_ENABLED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_BUTTON_USER_DEFINED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_BUTTON_PUSH_RECEIVED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_BUTTON_TIMEOUT | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_SYSTEM_LEDS_ENABLED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_STORAGE_LEDS_ENABLED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_LED_CONTINUOUS_SHOW_STORAGE_ACTIVITY | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_INJECTING_LEDS_ENABLED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_EXFIL_LEDS_ENABLED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_LED_SHOW_CAPS | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_LED_SHOW_NUM | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_LED_SHOW_SCROLL | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_CURRENT_VID | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_CURRENT_PID | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_CURRENT_ATTACKMODE | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_INT | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_MIN | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_MAX | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_SEED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_LOWER_LETTER_KEYCODE | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_UPPER_LETTER_KEYCODE | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_LETTER_KEYCODE | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_NUMBER_KEYCODE | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_SPECIAL_KEYCODE | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RANDOM_CHAR_KEYCODE | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_JITTER_ENABLED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_JITTER_MAX | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_CAPSLOCK_ON | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_NUMLOCK_ON | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_SCROLLLOCK_ON | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_SAVED_CAPSLOCK_ON | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_SAVED_NUMLOCK_ON | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_SAVED_SCROLLLOCK_ON | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_RECEIVED_HOST_LOCK_LED_REPLY | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_STORAGE_ACTIVITY_TIMEOUT | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_EXFIL_MODE_ENABLED | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_HOST_CONFIGURATION_REQUEST_COUNT | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| $_OS | Hardware-dependent / unsupported in preview | No adapter/implementation; never forward to legacy command dispatch | Unsupported rejection path; no per-feature conformance PASS claimed |
| NAME() inside numeric expressions / conditions / RETURN / DELAY | Supported within bounds; ordering policy explicit | Cooperative postfix continuations; captured earlier operands; no void coercion; eager left-to-right calls; numeric/Boolean only | Stage28A focused test suite and fresh sanitizer run |
