# Stage 18 early startup evidence and limits

Pinned core3.3.0, SDK idf-release_v5.5-b66b5448-v1, ESP32-S3 qio_qspi configuration.
Exact originals/patched hashes: [dependency pin](stage18-dependency-pin.json).
Reference URLs/hashes: [evidence](stage18-reference-evidence.json). Official ESP-IDF
v5.5 source is supporting evidence, not certified source for the exact precompiled SDK.
The installed libnvs_flash.a and configuration are separately fingerprinted; objdump
shows PageManager::load references Page::erase and NVSPartition::erase_range references
esp_partition_erase_range. Container SDK source is not substituted or rebuilt.

## Actual startup order

1. ROM/bootloader loads/validates image/partitions before EvilDuck exists. A fatal flash,
   image or partition failure may prevent all application diagnostics. No on-device
   behavior was tested. Bootloader erase/recovery behavior is not exhaustively certified.
2. Supporting IDF startup.c start_cpu0_default invokes core init, do_global_ctors,
   secondary component init, then esp_startup_start_app. C++ globals and component
   initialization precede Arduino/EvilDuck. The default Preferences constructor only
   initializes its handle/flags; it does not open or write NVS. USB/HID/MSC constructors
   register interfaces before setup; other SDK/global side effects are not fully modeled.
3. Actual pinned main.cpp app_main applies CPU settings and USB CDC/USB-on-boot support
   before initArduino. Firmware MSC/DFU boot settings remain disabled. USB can enumerate
   before the NVS gate; this is not a detached/CDC-only USB personality.
4. initArduino handles configured PSRAM/OTA rollback hooks before nvs_flash_init.
   The final ELF actually includes OTA verification hooks: they can update OTA metadata
   before NVS completes. These preexisting hooks are unchanged and are not a NVS-write
   protection/health-based rollback guarantee. PSRAM remains disabled in this profile.
5. The protected initArduino stores the exact SDK return value. On any nonzero result
   it logs the original signed error and returns, without partition lookup/erase,
   automatic retry, BT release or init/initVariant hooks. On ESP_OK, existing success
   behavior continues. The S3 default init/initVariant are weak empty hooks.
6. app_main creates loopTask only after initArduino returns. loopTask reaches EvilDuck
   setup. EvilDuck reads the strong core status hook before normal/safe service startup.
   Failure latches for the entire boot. A later explicit core retry cannot arm this
   already failed application. loop only yields on failure. No automatic restart/retry.

## What the patch changes

Originally, NO_FREE_PAGES / NEW_VERSION_FOUND caused a lookup of the NVS partition,
whole-partition esp_partition_erase_range and a second nvs_flash_init. Erase failure
replaced the original error; other failures still reached init/initVariant and setup.
The exact original bodies reproduce this with instrumented synthetic flash.

The small [patch](../proposals/arduino-esp32-3.3.0-nvs-preservation.patch) removes that
recovery block, adds4-byte status storage initialized to ESP_ERR_INVALID_STATE and
strong C getter. There is no owner-partition nvs_flash_erase, erase_range, default
write, replacement partition creation or silent conversion to success in this policy.
The getter preserves full32-bit signed errors; application diagnostics print them as
signed decimal. Failure does not depend on Wi-Fi/web/CLI. Core log delivery may be
compiled out; existing serial diagnostic is best effort after setup is reached.

Normal/safe-start EvilDuck gates are before LED, HID, attackmode/storage, SPIFFS/SD,
example install, settings load, CLI/web and autorun. A4-byte application error latch
keeps them off across loops and even explicit later initArduino calls. Safe with valid
NVS remains exactly quiescent; normal with valid NVS retains original behavior.
No new command/internal-variable/button/arming syntax is introduced.

## Important limitation: SDK initialization is not read-only

The unmodified SDK nvs_flash_init itself can recover pages/items, including writes and
page erases. Supporting PageManager::load contains FREEING-page recovery and erase
before returning later errors; Page::load/entry recovery can also mutate metadata.
Actual compiled archive relocations support the erase path, but its implementation is
not executed by host mocks. An injected SDK-side write before failure is separately
OBSERVED in both profiles to make the policy boundary explicit. It is not a claim of
executing the real SDK on synthetic pages.

Thus we prove removal of Arduino's **known whole-partition error-recovery erase**, not
that every invocation of NVS initialization leaves every byte unchanged. Synthetic
failed initializers without internal side effects preserve all20KiB; the policy makes
zero erase/write calls. SDK recovery can already have changed data when the error
arrives. Encryption/key-generation paths are not exercised; NVS encryption is absent
from the pinned configuration and no encrypted alternate profile is authorized.

Other explicit APIs (Preferences writes/clear, ESP flash erase, firmware updater), later
namespace/key failures and component/global initialization are not intercepted. On
successful init they retain existing behavior. Missing/corrupt partition metadata can
fail in the bootloader/SDK before the gate; unreadable code/heap/USB may prevent a
serial message. No promise of diagnostic delivery or physical protection is made.

## Recovery and acceptance

Known error results cannot trigger the removed Arduino erase/retry path in either
linked profile. No guessed SDK repair, global core edit or unverified destructive
initialization change is introduced. Destructive repair of incompatible/corrupt NVS
requires owner authorization, independently verified backups, current data capture
and exact region/recovery review. No erase/restore command is generated/executed.
Strict preservation against SDK internal recovery remains a separate prerequisite;
physical migration/application boot is still NO-GO absent that review and owner evidence.
