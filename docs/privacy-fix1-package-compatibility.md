# Compatibility boundaries for the privacy candidate

There is no DuckyScript, HID, LED-protocol or keyboard-layout change in this
repair. The reviewed H1/right-modifier composition and explicit engine selection
are retained. The prior four scoped right-modifier owner passes, executed STOP
variant and 3/3 planned lock-wait groups remain closed; missing request IDs do not
require repeats. Those reports do not constitute physical acceptance of this
new application image.

H1 remains opt-in/experimental. Canonical Hak5 numeric encoding is unresolved.
The included historical rm-*.txt fixtures are unchanged provenance resources,
not requested privacy acceptance tests. No payload is automatically started.

The supported package interfaces remain High Sierra 10.13.6, Bash 3.2, Python
3.8+ and esptool 4.12.0. Offline package and mock-installer tests are separate
from native Mac execution and physical USB/ROM recovery readiness.

Password API adjustment: settings reads expose configured indicators rather
than saved passwords. Replacements are write-only; blank/omitted values retain
the current secret. Existing credentials are required and authentication remains
enabled. Invalid nonempty values are refused. Non-atomic save behavior remains.

Source checkpoint: `93cc8d1a7b162bdda91e239d840a3eee8a70c51c`.
Target integration: `0380d1508b8f761e30a6a1fb63f67c2850cbc84a`.
The retained dashboard ID cannot distinguish this privacy candidate from older
H1 images. Exact application hash and manifest are authoritative package identity.
