#include <Arduino.h>
#include <WiFi.h>

#include "config.h"
#include "deployment_boot.h"
#include "controlled_layout.h"
#include "nvs_startup.h"

// Latch failure for the boot lifetime; a later core retry cannot arm an uninitialized app.
static int32_t startupNvsError = 0;
static bool startupSettingsFailed = false;
static bool startupStorageFailed = false;
static bool startupControlledAttempted = false;
static bool startupControlledReady = false;
#include "debug.h"
#include "storage.h"
#include "settings.h"
#include "webserver.h"
#include "duckscript.h"
#include "com.h"
#include "cli.h"
#include "hid_backend.h"
#include "keyboard_locale.h"
#include "led.h"
#include "attackmode.h"
#include "script_library.h"

static void applyIdleLedColor() {
  if (settings::getDisableLed()) {
    led::setColor(0, 0, 0);
    return;
  }
  uint32_t color = settings::getLedColor();
  led::setColor((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF);
}

void setup() {
  if (deployment::controlledStart()) {
    if (startupControlledAttempted) return;
    startupControlledAttempted = true; // One attempt; failures cannot silently re-arm.
  }
  if (startupNvsError == 0) startupNvsError = evilduck_nvs_startup_error();
  if (startupNvsError != 0) {
    debug::begin();
    debug::info("NVS startup failure; application disabled, original error: " + String(startupNvsError));
    return;
  }
  if (deployment::safeStart()) {
    debug::begin();
    debug::info("DEPLOYMENT SAFE START: application services and payload execution disabled");
    return; // No filesystem mount/format, NVS settings load, script, HID or MSC startup.
  }
  debug::begin();
  debug::info("Booting EvilDuck...");

  if (startupSettingsFailed) return;
  if (deployment::controlledStart() && !deployment::controlledLayoutReady()) {
    startupStorageFailed = true;
    debug::info("Controlled partition layout mismatch; application disabled");
    return;
  }
  settings::load();
  if (!settings::ready()) {
    startupSettingsFailed = true;
    debug::info("Settings read failed; application disabled, error: " + String(settings::loadError()));
    return;
  }

  if (deployment::controlledStart()) {
    debug::info("CONTROLLED NORMAL START: strict credentials, no format, no examples, no autorun");
    if (!storage::begin()) {
      startupStorageFailed = true;
      debug::info("Required SPIFFS mount failed; application disabled without formatting");
      return;
    }
    if (!webserver::prepareControlledNetwork()) {
      debug::info("Controlled AP startup failed; application services remain disabled");
      return;
    }
  }

  led::begin();
  led::setColor(40, 0, 0);
  delay(120);
  led::setColor(0, 40, 0);
  delay(120);
  led::setColor(0, 0, 40);
  hid_backend::begin();
  keyboard_locale::begin();
  attackmode::begin();

  if (!deployment::controlledStart()) {
    storage::begin();
    script_library::installIfNeeded();
  }
  applyIdleLedColor();
  cli::begin();

  webserver::begin();

  if (!deployment::controlledStart() && settings::autorunEnabled()) {
    String s = settings::getAutorun();
    if (s.length()) {
      uint32_t delayMs = settings::pickAutorunDelayMs();
      if (delayMs == 0) delayMs = settings::getStealthMode() ? 8000 : 3000;
      debug::info("Autorun in " + String(delayMs) + "ms: " + s);
      delay(delayMs);
      duckscript::run(s);
    }
  }
  if (deployment::controlledStart()) startupControlledReady = true;
}

void loop() {
  if (deployment::safeStart() || startupNvsError != 0 || startupSettingsFailed ||
      (deployment::controlledStart() && (!startupControlledReady || startupStorageFailed))) {
    delay(1);
    return; // Intentionally no web/CLI arming path or execution scheduler in this profile.
  }
  duckscript::update();
  com::update();
  cli::update();
  delay(1);
}
