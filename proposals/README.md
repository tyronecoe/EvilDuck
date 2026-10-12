# Stage 15 dependency-hardening proposals — NOT applied

The Arduino ESP32 core remains the installed unmodified3.3.0. These two patches
are a paired proposal for a separate reviewed dependency milestone, not an active
firmware fix. Do not apply either alone and do not modify an installed core silently.

* Core patch validates instance/non-null OUTPUT payload and length before extracting
  a report ID, preserves report type, dispatches OUTPUT to _onOutput and FEATURE to
  _onSetFeature, and avoids indexing debug report-type strings with arbitrary values.
* Companion removes EvilDuck's Stage12 FEATURE-hook workaround. Applying only the
  core patch leaves malformed FEATURE LED acceptance; applying only the companion
  breaks legitimate nonzero-ID control OUTPUT on unpatched core3.3.0.

Tests apply these patches only to temporary source copies, extract exact callback
bodies and compile against actual firmware/mock adapters. Sanitizers reproduce
unpatched faults as separate XFAIL observations. Paired tests are candidate behavior
passes, not shipped firmware robustness or full patched Arduino/TinyUSB certification.

A reviewed follow-up needs full patched-core rebuild, dependency hashes/reproducible
pinning, all actual HID device/report types, logging configurations, descriptor/parser
allocation and zero-length FEATURE compatibility, and authorized ordinary USB testing.
No complete stack is vendored. No wrapper, weak-symbol or linker interception was
silently installed; no USB descriptor/personality change is part of these patches.
