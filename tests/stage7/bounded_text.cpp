#include "host.h"
#include "script_parser.h"
#include "script_functions.h"
#include "duck_constants.h"
#include "duck_vars.h"
#include <cstdio>
#include <cstdlib>
#include <new>

// Measure only the isolated line-format/expansion path. Host String uses
// std::string; these are not ESP32 allocator/high-water measurements.
static bool tracking = false;
static size_t requests = 0, largest = 0;
static unsigned assertions = 0;
void *operator new(size_t n) {
  if (tracking) { ++requests; if (n > largest) largest = n; }
  if (auto p = std::malloc(n ? n : 1)) return p;
  throw std::bad_alloc();
}
void *operator new[](size_t n) { return ::operator new(n); }
void operator delete(void *p) noexcept { std::free(p); }
void operator delete[](void *p) noexcept { std::free(p); }
void operator delete(void *p, size_t) noexcept { std::free(p); }
void operator delete[](void *p, size_t) noexcept { std::free(p); }
static void check(bool value, const char *message) {
  ++assertions;
  if (!value) { std::fprintf(stderr, "FAIL stage7_bounded_line_allocation_probe: %s\n", message); std::exit(1); }
}
int main() {
  mock::reset();
  String error, expanded;
  check(duck_vars::assign("$n", "9", true, error), "global setup");
  check(duck_constants::define("DEFINE #X x", 1, error), "constant setup");
  script_parser::Lexer lexer;
  script_parser::Statement stmt;
  check(lexer.scan("STRINGLN", 1, stmt, error), "open literal mode");
  String source(std::string(506, 'a').c_str()); source += "#X$n";
  tracking = true;
  for (unsigned i = 0; i < 10000; ++i) {
    check(lexer.scan(source, i + 2, stmt, error), "format bounded body line");
    check(stmt.kind == script_parser::Kind::TextLnBody && stmt.args.length() == 509, "constant substitution stays data");
    check(duck_vars::expand(stmt.args, expanded, error), "bounded runtime interpolation");
    check(expanded.length() == 508 && expanded.endsWith("x9"), "exact expansion");
  }
  tracking = false;
  check(largest <= 2 * DUCKSCRIPT_MAX_EXPANDED_LINE + 1, "no allocation scales with block length");
  check(lexer.scan("END_STRINGLN", 10002, stmt, error), "close literal mode");
  std::printf("Host line probe: %zu allocation requests; largest %zu bytes; call frame %zu; fixed call stack %zu\n",
              requests, largest, sizeof(script_functions::Call), sizeof(script_functions::Calls));
  std::printf("PASS stage7_bounded_line_allocation_probe (%u assertions)\n", assertions);
}
