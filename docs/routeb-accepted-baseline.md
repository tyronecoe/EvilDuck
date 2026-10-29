# Accepted Route B baseline — owner closeout

The latest owner-accepted application is **ROUTEB-TEXT-KEYBOARD-v1**, release commit `b6d85e6da700774345c584f4f67fa5df4f0ea854`, on macOS High Sierra 10.13.6. This closeout records the owner's supplied observations; Codex did not operate or independently inspect the physical board.

| Identity | Value |
|---|---|
| Application size | 1,412,400 bytes |
| Application SHA-256 | `53acc374ef38be652b6847d4b84f2dc7d42fa73a3dd54ea62d5208be4cbc0167` |
| Source composition commit | `3780a4884bfd5eab9394b2fa5626298f62712349` |
| Package commit | `3040eec3c925c4fda74ff3fa26a8f87ad47dee5c` |
| Existing public ZIP | `downloads/evilduck-routeb-text-keyboard-macos-v1.zip` |
| ZIP size / SHA-256 | 2,336,378 bytes / `9a60e91e142fea74b746bef352d16139cccaf9fd45ca5e5a10549c91b846dc9e` |

## Owner-reported physical acceptance

| Planned trial | Result | Supplied identifiers / observation |
|---|---|---|
| Text-block aliases | OWNER-REPORTED PASS | Request, boot and session unknown |
| Inline REPEAT | OWNER-REPORTED PASS | Request, boot and session unknown |
| RESET and continued typing | OWNER-REPORTED PASS | Request, boot and session unknown |
| STOP and Shift recovery | OWNER-REPORTED PASS | Request, boot and session unknown |
| Malformed text-block rejection | OWNER-REPORTED PASS | Request 5; compile failure at line 3; diagnostic 16; TextEdit blank; no unexpected text observed |

Physical trial dates, independent receipt identifiers, screenshots and boot/session associations were not supplied with this closeout. Leave them unknown; do not require repeated acceptance simply to proceed with the approved documentation review. These are five scoped results, not exhaustive language, layout, timing, USB delivery, endpoint-retirement or host-global key-release guarantees.

The original [acceptance sheet](text-keyboard-acceptance.md), [release report](text-keyboard-report.md) and all historical receipts remain unchanged. Their pre-acceptance wording is historical; this document records the later owner decision. Machine-readable evidence: [accepted baseline](routeb-accepted-baseline.json).

## Mandatory target for future rollback

Any future candidate package must include the exact **text/keyboard application above** as its rollback application. Obtain it from `application.bin` in the existing verified public ZIP, then independently check size, hash and ESP32-S3 image integrity before binding it into a future package. The current ZIP's `rollback-application.bin` is the older randomization/jitter image, **not** the required next-package rollback.

The prior `ROUTEB-RANDOMIZATION-JITTER-v1` image (`2e1d8345…`, 1,411,088 bytes) remains an older recovery version. Do not relabel, regenerate or overwrite either historical package. Existing historical builders retain their original rollback pins; a future separately approved release must use a new additive package binding. This documentation does not mechanically change a builder or authorize deployment.

The accepted artifact is a standalone application, not a merged bootloader/full-flash recovery image. Future app-only restoration still requires separately authorized operation, matching installed partition/OTA metadata, chip/security/image checks and ROM recovery prerequisites. Existing table identity remains `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`. App rollback does not restore settings or filesystem contents. Original firmware is **OWNER CONFIRMED: AVAILABLE EXTERNALLY**; availability is not a deployment blocker or physical recovery proof. No private backup is needed for this closeout.
