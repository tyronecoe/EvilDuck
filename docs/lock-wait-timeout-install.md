# Mac review package — no installation authorized

The new Route B bounded lock-wait behavior is software-tested only. This distinct application-only package is for review; installation needs separate owner authorization. Preserve installed source/text v2 and all original package bytes.

Requires macOS10.13.6, Bash3.2, Python3.8 and esptool4.12 interfaces; these are preserved and checked offline, not newly run on a physical Mac. No compiler install, private backup upload, OTA, formatting or settings reset is required. Verify the ZIP/app identities in the release report and stop on mismatch. Unpack into a separate directory. The default offline check is `bash install-macos.sh`; the existing reviewed install interface is `bash install-macos.sh --action install --port /dev/cu.usbmodemCURRENT`, for future separately authorized use only. Rediscover and verify ports rather than reuse a numeric suffix.

Existing app-only preflight binds chip/security/image/table/OTA checks and exact write ranges. Bootloader, partition table, NVS, otadata, SPIFFS and coredump are excluded. This package does not authorize boot, writes, recovery operations or installation. Use [acceptance](lock-wait-timeout-acceptance.md) only after separate approval. See [rollback](lock-wait-timeout-rollback.md).
