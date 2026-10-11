#pragma once
#include <Arduino.h>

namespace hid_backend {
  void begin();

  bool keyNameToHid(const String &input, uint8_t &outCode);

  void sendText(const String &text);
  void sendTextLn(const String &text);

  void pressModifier(uint8_t modMask);
  void pressKeyHeld(uint8_t hidKeycode);
  void pressKeycode(uint8_t hidKeycode, uint8_t modifiers = 0);
  void pressReport(uint8_t modifiers, const uint8_t *keys, uint8_t keyCount);
  // Runtime-only nonblocking transport. False means retry on another update.
  bool beginReport(uint8_t modifiers, const uint8_t *keys, uint8_t keyCount);
  bool releaseReport();
  void cancelReport();
  void update(); // Observe USB loss and retry priority clearing reports.
  // Holds commit on endpoint acceptance; release intent clears immediately. False can
  // mean backpressure; reportError() distinguishes invalid/rollover requests.
  bool hold(uint8_t modifier, uint8_t key);
  bool release(uint8_t modifier, uint8_t key);
  bool hasPersistent();
  bool clearing();
  const char *reportError();
  bool takeTransportLoss();
  bool pressNamedCombo(const String &keyName, uint8_t modifiers = 0);
  void releaseAll();

  void pressEnter();
  void pressTab();
  void pressEscape();
  void pressSpace();
  void pressBackspace();
  void pressDelete();
  void pressArrowUp();
  void pressArrowDown();
  void pressArrowLeft();
  void pressArrowRight();
}
