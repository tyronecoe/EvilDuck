# Stage28S owner selection and scope

Exact clean parent `6c186219c9ef7037f3ecab9bae44179421fd1278`, Stage28R. New branch `stage28s-native-runtime-scheduler`. Owner selects Route B **for this isolated native stage only**: LOCAL_SCHEDULER_DONE, not correlated USB completion, controller retirement, host neutrality or application delivery. Stage28L strict A remains unchanged and UNRESOLVED. Espressif support draft remains unsent; no terms accepted.

Allowed new tests/stage28s/* and docs/stage28s-* only. Opt-in patch applies to fresh scratch copies of com.cpp/.h; never repository firmware or installed sources. All1,164 historical tracked bytes/paths/modes,235 frozen Stage26 files and43 previous remote refs are protected. No settings/profile/schema/partition/USB identity changes, target/SDK/firmware build/image, device/MMIO, live USB/HID, owner payload/backup, flash/erase/format/boot/OTA. Stage28T is not started. Stage27A remains separate and owner-controlled.

Production/preview APIs and old acceptance cells stay unchanged. This is real production scheduler execution with new fake services, not a new handwritten scheduler or the old synthetic USB coordinator. Existing native Arduino/platform mocks are reused. Dependency/tool setup is already sufficient; no installation, global configuration change or SDK download is needed.

Original recovery firmware remains OWNER CONFIRMED AVAILABLE EXTERNALLY. Exact original firmware/NVS/settings/scripts/filesystem preservation is not mandatory; backups stay untouched. Actual recovery compatibility, target artifacts, installed layout and physical authorization remain separate gates.
