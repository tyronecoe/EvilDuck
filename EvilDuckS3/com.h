#pragma once
#include <Arduino.h>

namespace com {
  typedef void (*cb_t)();

  void onDone(cb_t cb);
  void onRepeat(cb_t cb);
  void onError(cb_t cb);

  void send(const String &line);
  // Script-only literal body line, already DEFINE-expanded by the lexer. Never
  // submit through the command parser; interpolation/output remain cooperative.
  void sendText(const String &text, bool enter);
  bool executeNow(const String &line);
  void update();
  // executeNow accepts an idle live command; timed/output work completes in
  // update(). A script owns the executor until endScript(), including gaps
  // between commands. Rejected submissions never alter the active operation.
  void beginScript();
  void endScript();
  bool busy();
  String lastError();
  String submissionError();
}
