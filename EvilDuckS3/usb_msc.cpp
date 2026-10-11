#include "usb_msc.h"
#include "config.h"
#include "execution_guard.h"

#if SD_ENABLED && defined(CONFIG_TINYUSB_MSC_ENABLED) && CONFIG_TINYUSB_MSC_ENABLED
#include "USB.h"
#include "USBMSC.h"
#include "SD.h"

namespace {
USBMSC MSC;
File disk;
usb_msc::State status = usb_msc::State::Off;
enum class Step : uint8_t { Open, Probe, Activate };
Step step = Step::Open;
const char *error = "";
const char *const image = "/sys/usb_disk.img";
constexpr uint32_t sectors = 8192, sectorBytes = 512, imageBytes = sectors * sectorBytes;
// Matches the pinned core's CONFIG_TINYUSB_MSC_BUFSIZE; bounds synchronous I/O.
constexpr uint32_t transferMax = CONFIG_TINYUSB_MSC_BUFSIZE;
static_assert(transferMax > 0 && transferMax <= INT32_MAX, "Invalid MSC transfer bound");
constexpr uint32_t startupTimeout = 5000;
uint32_t started = 0;
bool requested = false;
bool registered = false; // SDK callback addresses stay stable for the object lifetime.

void fail(const char *why) {
  error = why;
  status = usb_msc::State::Failed;
  MSC.mediaPresent(false);
  MSC.isWritable(false);
  if (disk) disk.close();
  // Keep callbacks registered: SDK end() clears pointers without synchronization.
}
bool available() {
  if (!SD.cardType()) { fail("MSC: backing SD unavailable"); return false; }
  if (!disk || disk.size() != imageBytes) { fail("MSC: backing image unavailable or size changed"); return false; }
  return true;
}
bool address(uint32_t lba, uint32_t offset, const void *buffer, uint32_t size, uint32_t &position) {
  const uint64_t start = uint64_t(lba) * sectorBytes + offset;
  if (size > transferMax || (size && !buffer) || start > imageBytes || size > imageBytes - start) {
    error = "MSC: invalid transfer range, buffer or length";
    return false; // No seek/write and do not invalidate healthy media for bad requests.
  }
  position = uint32_t(start);
  return true;
}
int32_t onRead(uint32_t lba, uint32_t offset, void *buffer, uint32_t size) {
  execution::TryGuard guard;
  if (!guard) return 0; // TUD_MSC_RET_BUSY: retry later, no cursor mutation.
  if (status != usb_msc::State::Active) return -1;
  uint32_t pos;
  if (!address(lba, offset, buffer, size, pos)) return -1;
  if (!available()) return -1;
  if (!size) return 0;
  if (!disk.seek(pos)) { fail("MSC: read seek failed"); return -1; }
  if (disk.read(static_cast<uint8_t *>(buffer), size) != size) { fail("MSC: short read or SD I/O failure"); return -1; }
  return int32_t(size);
}
int32_t onWrite(uint32_t lba, uint32_t offset, uint8_t *buffer, uint32_t size) {
  execution::TryGuard guard;
  if (!guard) return 0;
  if (status != usb_msc::State::Active) return -1;
  uint32_t pos;
  if (!address(lba, offset, buffer, size, pos)) return -1;
  if (!available()) return -1;
  if (!size) return 0;
  if (!disk.seek(pos)) { fail("MSC: write seek failed"); return -1; }
  if (disk.write(buffer, size) != size) { fail("MSC: short write or SD I/O failure (partial prefix may remain)"); return -1; }
  disk.flush(); // Arduino exposes no flush result; durable media completion is not proven.
  return int32_t(size);
}
bool onStartStop(uint8_t, bool start, bool) {
  execution::TryGuard guard;
  if (!guard) return false; // Boolean API has no busy result; host may retry command.
  if (!requested) return false; // Stale host START cannot undo OFF/STOP cancellation.
  if (start) return usb_msc::begin(); // Deferred validation; not a media-ready assertion.
  MSC.mediaPresent(false);
  MSC.isWritable(false);
  if (disk) disk.close();
  status = usb_msc::State::Ejected;
  error = "";
  return true;
}
}
namespace usb_msc {
bool begin() {
  execution::Guard guard;
  if (status == State::Active) return available();
  if (status == State::Preparing) return true;
  end(); // Also cleans partial startup/errors before every explicit retry.
  requested = true;
  if (!SD.cardType()) { fail("MSC: backing SD unavailable"); return false; }
  status = State::Preparing;
  step = Step::Open;
  started = millis();
  return true;
}
void update() {
  execution::Guard guard;
  if (status == State::Active) {
    if (!SD.cardType()) fail("MSC: backing SD unavailable");
    return;
  }
  if (status != State::Preparing) return;
  if (uint32_t(millis() - started) >= startupTimeout) { fail("MSC: preparation timed out"); return; }
  if (!SD.cardType()) { fail("MSC: backing SD unavailable"); return; }
  switch (step) {
    case Step::Open:
      // r+ MUST NOT become FILE_WRITE (w): existing user images must never truncate.
      disk = SD.open(image, "r+");
      if (!disk) { fail("MSC: existing writable /sys/usb_disk.img required; no image created"); return; }
      if (disk.isDirectory() || disk.size() != imageBytes) { fail("MSC: backing image must be exactly 4194304 bytes"); return; }
      step = Step::Probe;
      return;
    case Step::Probe: {
      if (!available()) return;
      uint8_t probe[sectorBytes];
      if (!disk.seek(0)) { fail("MSC: preparation seek failed"); return; }
      if (disk.read(probe, sizeof(probe)) != sizeof(probe)) { fail("MSC: preparation read failed"); return; }
      // Raw block-media probe only. It does not certify a filesystem or all sectors.
      step = Step::Activate;
      return;
    }
    case Step::Activate:
      if (!available()) return;
      if (!registered) {
        MSC.vendorID("Evil"); MSC.productID("Duck"); MSC.productRevision("1.0");
        MSC.onRead(onRead); MSC.onWrite(onWrite); MSC.onStartStop(onStartStop);
        registered = true;
      }
      MSC.isWritable(true); // USBMSC::end() clears this in Arduino 3.3.0.
      if (!MSC.begin(sectors, sectorBytes)) { fail("MSC: USBMSC.begin failed"); return; }
      if (uint32_t(millis() - started) >= startupTimeout) { fail("MSC: preparation timed out"); return; }
      error = "";
      status = State::Active;
      MSC.mediaPresent(true); // Last step, only after all validation/registration succeeds.
      return;
  }
}
void end() {
  execution::Guard guard;
  MSC.mediaPresent(false);
  MSC.isWritable(false); // Do not race SDK callback-table teardown with TinyUSB.
  if (disk) disk.close();
  status = State::Off;
  requested = false;
  error = "";
}
bool active() { execution::Guard guard; return status == State::Active; }
bool preparing() { execution::Guard guard; return status == State::Preparing; }
State state() { execution::Guard guard; return status; }
const char *lastError() { execution::Guard guard; return error; }
}
#else
namespace usb_msc {
static State status = State::Off;
static const char *error = "";
bool begin() { execution::Guard guard; status = State::Failed; error = "MSC: unavailable in this build"; return false; }
void update() {}
void end() { execution::Guard guard; status = State::Off; error = ""; }
bool active() { return false; }
bool preparing() { return false; }
State state() { execution::Guard guard; return status; }
const char *lastError() { execution::Guard guard; return error; }
}
#endif
namespace usb_msc {
const char *stateName() {
  switch (state()) {
    case State::Off: return "off";
    case State::Preparing: return "preparing";
    case State::Active: return "active";
    case State::Ejected: return "ejected";
    case State::Failed: return "failed";
  }
  return "failed";
}
}
