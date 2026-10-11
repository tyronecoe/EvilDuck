# Stage 10 USB mass-storage reliability contract

Baseline: Stage 9 `24e8a88f56dd4445d7d69924220f7dc2d66f0fa2`.
Scope is storage integrity/state/recovery only. No parser, expression, function,
keyboard, locale, descriptor-personality or partition changes; no new commands.
All tests are offline. Stage 11 and physical operations are excluded.

## Pinned contracts and discovered failure paths

Reviewed Stage 9 roadmap/report/reference analysis and its actual production
attackmode probe; attackmode, usb_msc, sd_card, storage, CLI/web, scheduler and
filesystem sources. Arduino ESP32 3.3.0 core sources and bundled TinyUSB headers
were inspected locally, not inferred from another core version.

* [USBMSC.cpp at 3.3.0](https://github.com/espressif/arduino-esp32/blob/3.3.0/cores/esp32/USBMSC.cpp):
  constructor registers a permanent MSC interface; wrappers forward LBA, offset,
  pointer and length. begin validates geometry/callbacks; mediaPresent is separate.
  end clears writable state and callback pointers without application-level locking.
* [USBMSC.h](https://github.com/espressif/arduino-esp32/blob/3.3.0/cores/esp32/USBMSC.h):
  int32 read/write results and Boolean start/stop callback; no cancelable File I/O API.
* Bundled `esp32s3/include/arduino_tinyusb/tinyusb/src/class/msc/msc_device.h`:
  address = LBA × block size + offset; positive partial results are permitted;
  busy=0, error=-1, async=-2. No invented sector-alignment restriction. The pinned
  qio_qspi SDK config has MSC buffer size4096. Source hashes are in results metadata.
* [FS.h](https://github.com/espressif/arduino-esp32/blob/3.3.0/libraries/FS/src/FS.h)
  defines FILE_WRITE as `w` and [VFS implementation](https://github.com/espressif/arduino-esp32/blob/3.3.0/libraries/FS/src/vfs_api.cpp)
  passes the mode to fopen. The previous first host I/O opened with FILE_WRITE and
  could truncate the image! `r+` opens an existing writable image without creating
  or truncating it. Missing paths beginning with `r` are not implicitly created.
* [SD.cpp](https://github.com/espressif/arduino-esp32/blob/3.3.0/libraries/SD/src/SD.cpp):
  cardType is cached card information, not a physical removal interrupt. Failure
  detection also requires actual file I/O. Flush/close expose no useful success
  result; atomic writes or physical durable completion cannot be promised.

Old problems: requested storage flag became true before startup; failed startup
reported success and suppressed retries; no prepared-image size/type checks;
8192 unchecked synchronous zero writes for missing images; truncating open mode;
offset discarded; unchecked seek/bounds; partial I/O only returned an error
without quarantining media; end/start did not reliably restore writability;
shared cursor and state could race USB callbacks versus command/web operations.

## Deliberate compatibility decisions

Before implementation, the user-facing update documented rejecting absent images
instead of automatically creating an unformatted4MiB image. This is a safety
change, not a hidden format/provision step. Existing exact-size files are preserved
byte-for-byte during initialization. Wrong-sized files/directories are rejected,
not resized, repaired, replaced or deleted. Oversized images previously exposing
only an assumed4MiB prefix are now rejected rather than silently capped.

The image remains `/sys/usb_disk.img`, exactly4194304 bytes,8192 sectors of512.
Its content can be any raw media image; startup does not validate FAT/partition
contents. Web `storageFilesystemVerified=false` and CLI
`storage_filesystem=unchecked_raw_image` make that limitation explicit. A legacy
zero-filled image might initialize as raw block media but is not a mountable FAT
filesystem. Offline provisioning/backup/verification is separate user work and
requires review; no formatting procedure is executed or implicitly added here.

`usb_msc::begin()` now means **request accepted**, not **initialization completed**.
Only `active()` establishes prepared local raw-media state. This API distinction
is documented in its header; internal callers are adapted. ATTACKMODE waits for
success/failure through the existing cooperative scheduler. Language syntax and
intended mode arguments are unchanged. CLI/live command acceptance was already
asynchronous in Stage1; status/log/error now exposes pending or failed preparation.

## State and scheduling

`Off → Preparing → Active`, with `Failed` and `Ejected` terminal/inactive states.
Requested storage mode is separately owned by attackmode and remains true after
failure/eject until OFF or pending cancellation. Explicit identical mode requests
retry failure/eject; repeated requests while Preparing/Active are idempotent.

Preparation performs at most one step per com update:

1. Open existing image with r+, reject failed open/directory/wrong exact size.
2. Verify availability, seek0 and read one512-byte probe; do not write anything.
3. Verify availability, install stable callbacks/geometry, restore writable state,
   call SDK begin and only then advertise media-present and Active.

A wrap-safe5000ms elapsed deadline is checked between steps and before publishing
active state. It cannot interrupt an underlying blocking driver syscall. No whole
image buffer or scan, background worker, dynamic AST or new dependency is used.
The maximum preparation scratch buffer is512 stack bytes.

com Phase::Storage keeps the script/function continuation paused while pending;
no remaining queued command executes before success. Failure retains a source/line
error, cancels the script and releases owned HID through the existing error path.
STOP/com::endScript cancels only a pending storage request; already-active media is
preserved, matching previous STOP behavior. OFF cancels pending or active media.
A separate internal request token prevents stale host LOAD callbacks from undoing
OFF or STOP cancellation. Host STOP/eject closes media and marks Ejected; an enabled
host LOAD queues revalidation instead of prematurely declaring ready.

## Safe transfers and failure policy

Compute address with uint64 before multiplication/addition. Require the entire
byte interval to fit the exact image, nonnull pointer for nonzero length and length
≤ CONFIG_TINYUSB_MSC_BUFSIZE (4096 in this profile). Requests can be unaligned and
cross sectors; offsets larger than a sector normalize through the documented byte
formula if the resulting interval is valid. Zero length at any valid position,
including exact end, is a no-op; invalid positions still fail. No underflowing
range subtraction is evaluated because out-of-range starts are rejected first.

Bad parameters return -1 before seek/I/O and leave healthy media active. Card/
handle/size loss, failed seek or short I/O quarantine media: Failed, media absent,
writable false, handle closed and immutable reason retained. Never read/write at a
stale cursor after failed seek. No automatic I/O retry after a media fault; explicit
mode/host LOAD request reopens and validates. Actual host raw writes flush on success.

The library permits positive partial returns, but this implementation deliberately
fails and quarantines short reads/writes rather than continuing uncertain media.
A short write can leave a valid-range prefix modified; no rollback, journaling or
atomic-sector claim. Flush's void return means durability/error detection is limited.

## Synchronization and stable SDK lifetime

Runtime state, disk cursor and command operations share the existing recursive
execution lock. SD adapter functions and direct web upload chunks join that lock.
USB read/write callbacks use TryGuard: contention returns busy0 immediately with
no cursor mutation. Boolean start/stop callback contention returns false because
that contract has no busy enum. Tests use actual callback pointers and cross-thread
contention. This is not a physical USB timing or ThreadSanitizer conformance claim.

Do not call SDK USBMSC.end while callbacks may be dispatched: its unsynchronized
pointer clearing can race wrapper dispatch. Callback addresses/geometry remain
stable after initial registration; inactive/faulted callbacks fail through our
locked state checks. `usb_msc::end()` disables media/writability, closes the handle,
clears request/error state and leaves interface/callback registration intact.
Geometry is fixed; subsequent begin restores writability after deactivation.

Arduino's own wrapper/media flags are SDK-owned and not independently reworked.
No descriptor removal, detach or re-enumeration is claimed. SDK calls' thread and
host behavior still require real-device validation; TryGuard protects application
state/File cursor, not every library-internal data structure.

## Status and verification boundaries

Existing storageEnabled/storage_usb/web storage fields now report verified local
active state, not the request. Add requested, state, immutable error and filesystem
verification status to existing status interfaces; no new command. Status snapshots
use the execution lock. Unknown functions, variables and unrelated commands retain
previous semantics. Parser and macro/expression consumers are untouched.

Production tests link usb_msc.cpp, attackmode.cpp, sd_card.cpp, actual CLI/scheduler/
parser/control-flow/HID modules with RAM File/SD/USB/clock mocks. Existing source
storage adapters remain mocked for scripts; actual sd_card methods have separate
coverage. Actual AsyncWebServer HTTP requests and storage.cpp's full adapters are
not simulated end-to-end: tests cover its existing com admission path, real CLI,
shared-lock contention and SD operations; firmware build validates web integration.

Remaining limits: cached card presence; same-size external replacement/mutation;
physical card remount requirements; driver calls that cannot be interrupted;
write-prefix/flush durability; live USB personality and host filesystem behavior;
SDK-owned concurrency and real heap/stack high-water. Keep image provisioning and
physical validation separately reviewed. Stage11 remains persistent HID ownership,
with these storage findings preserved rather than claiming full DS3 compatibility.
