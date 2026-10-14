# Stage28D internal capability matrix

Previous language-command matrix statuses remain unchanged. These are internal model capabilities, not canonical syntax support.

| Feature | Status | Scope | Evidence |
|---|---|---|---|
| Persistent ownership | Implemented within bounds | Internal API only | Two owners, shared keys/modifiers, idempotence and cap tests |
| Transient tap/modifier restoration | Implemented within bounds | Internal API only | Shift overlap and exact press/restoration bytes |
| US printable ASCII32..126 + TAB/LF | Implemented model | Internal character/mapUS API only | Independent literal punctuation/letter vectors plus95 printable cases |
| Six-key union/seventh rejection | Implemented policy | Model only, no NKRO | Sorted snapshots, owner cap and rollover recovery |
| Accepted neutral cleanup | Implemented model | Explicit drain only | Retry, Failed, exception, cancel and restart gates |
| HOLD/RELEASE/INJECT_MOD syntax | Unsupported in preview | Language parser unchanged | No parser change or legacy forwarding |
| Runtime Character/KeyTap/Delay adapter | Not implemented | Deferred mock bridge | Existing event ABI unchanged |
| DE/dead keys/Unicode/lock-state compensation | Unsupported | Not approximated | Unsupported bytes reject; no layout selector |
| Real HID/USB/OS/transport/physical release | Not implemented or tested | Unauthorized | No adapter, descriptor, report ID or hardware access |
