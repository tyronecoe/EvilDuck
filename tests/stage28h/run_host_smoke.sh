#!/bin/bash
# Bash3.2 / BSD-compatible local host mock only. No device, network or installation.
set -u
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." 2>/dev/null && pwd -P)" || { printf '%s\n' 'FAIL project root unavailable'; exit 2; }
temp=''
cleanup(){
 if [ -n "$temp" ]; then
  case "$temp" in "$tempbase"/evilduck28h.*) [ -d "$temp" ] && rm -rf "$temp" ;; esac
 fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
sanitize(){
 awk -v project="$root" -v home="${HOME:-}" -v work="$temp" '
 function hide(s,key,mark, out,p){out="";if(!length(key))return s;while((p=index(s,key))>0){out=out substr(s,1,p-1) mark;s=substr(s,p+length(key))}return out s}
 {s=hide($0,project,"<project-root>");s=hide(s,home,"<home>");s=hide(s,work,"<temp-dir>");print s}'
}
for file in language_preview/core.cpp language_preview/core.h language_preview/keyboard.cpp language_preview/keyboard.h language_preview/bridge.cpp language_preview/bridge.h tests/stage28h/test_host_validation.cpp tests/stage28h/expected-traces.json; do
 [ -f "$root/$file" ] && [ -r "$root/$file" ] || { printf 'FAIL missing source fixture: %s\n' "$file"; exit 2; }
done
printf '%s\n' 'Project root: <project-root>; approved source fixtures present'
platform="$(uname -s)";printf 'Platform: %s\n' "$platform"
if [ "$platform" = Darwin ]; then sw_vers -productVersion;sw_vers -buildVersion;else uname -r;fi
if [ -n "${CXX:-}" ]; then compiler="$CXX";
elif command -v clang++ >/dev/null 2>&1; then compiler="$(command -v clang++)";
elif command -v c++ >/dev/null 2>&1; then compiler="$(command -v c++)";
else printf '%s\n' 'SKIP_ENVIRONMENT no available C++17 compiler (no installation attempted)';exit 77;fi
case "$compiler" in */*) ;; *) compiler="$(command -v "$compiler" 2>/dev/null)" || compiler='' ;; esac
[ -n "$compiler" ] && [ -x "$compiler" ] || { printf '%s\n' 'SKIP_ENVIRONMENT selected compiler missing or not executable'; exit 77; }
case "$compiler" in /usr/bin/*|/bin/*|/usr/local/bin/*) printf 'Compiler: %s\n' "$compiler" | sanitize ;; *) printf 'Compiler: <compiler-parent>/%s\n' "$(basename "$compiler")" | sanitize ;; esac
# Absolute compiler path remains valid after cd, including paths containing spaces.
case "$compiler" in /*) ;; *) compiler="$(cd "$(dirname "$compiler")" && pwd -P)/$(basename "$compiler")" ;; esac
tempbase="${TMPDIR:-/tmp}"
tempbase="$(cd "$tempbase" 2>/dev/null && pwd -P)" || { printf '%s\n' 'SKIP_ENVIRONMENT temporary parent directory unavailable';exit 77; }
temp="$(mktemp -d "$tempbase/evilduck28h.XXXXXX")" || { printf '%s\n' 'SKIP_ENVIRONMENT temporary directory unavailable';exit 77; }
{ "$compiler" --version; } > "$temp/version.txt" 2>&1
rc=$?;sanitize < "$temp/version.txt";[ "$rc" -eq 0 ] || { printf '%s\n' 'SKIP_ENVIRONMENT compiler version check failed';exit 77; }
cat > "$temp/probe.cpp" <<'CPP'
#if __cplusplus < 201703L
#error C++17 required
#endif
#include <cstdio>
int main(){return 0;}
CPP
{ "$compiler" -std=c++17 "$temp/probe.cpp" -o "$temp/probe"; } > "$temp/probe.log" 2>&1
rc=$?;sanitize < "$temp/probe.log"
[ "$rc" -eq 0 ] || { printf 'SKIP_ENVIRONMENT C++17/SDK probe failed (compiler exit=%s)\n' "$rc";exit 77; }
{ "$temp/probe"; } > "$temp/probe-run.log" 2>&1;rc=$?;sanitize < "$temp/probe-run.log"
[ "$rc" -eq 0 ] || { printf 'SKIP_ENVIRONMENT compiler output cannot run (exit=%s)\n' "$rc";exit 77; }
printf '%s\n' 'PASS C++17 compile/link/run probe'
cd "$root" || { printf '%s\n' 'FAIL project root inaccessible';exit 2; }
warning_flags=(-Wall -Wextra -Werror)
# Prior GCC warning suppression only; older Apple clang need not recognize it.
if ! grep -i clang "$temp/version.txt" >/dev/null; then warning_flags+=( -Wno-misleading-indentation );fi
{ "$compiler" -std=c++17 "${warning_flags[@]}" \
 language_preview/core.cpp language_preview/keyboard.cpp language_preview/bridge.cpp \
 tests/stage28h/test_host_validation.cpp -o "$temp/host-validation"; } > "$temp/build.log" 2>&1
rc=$?;sanitize < "$temp/build.log"
[ "$rc" -eq 0 ] || { printf 'FAIL fixture compile/link (exit=%s)\n' "$rc";exit "$rc"; }
{ "$temp/host-validation" --manifest; } > "$temp/manifest.json" 2> "$temp/manifest.log";rc=$?;sanitize < "$temp/manifest.log"
[ "$rc" -eq 0 ] || { printf 'FAIL fixture manifest execution (exit=%s)\n' "$rc";exit "$rc"; }
if ! cmp -s tests/stage28h/expected-traces.json "$temp/manifest.json"; then printf '%s\n' 'FAIL fixture manifest mismatch';exit 1;fi
printf '%s\n' 'PASS compiled fixture manifest matches repository expectations'
{ "$temp/host-validation"; } > "$temp/run.log" 2>&1;rc=$?;sanitize < "$temp/run.log"
[ "$rc" -eq 0 ] || { printf 'FAIL fixture execution (exit=%s)\n' "$rc";exit "$rc"; }
# A zero-status program with missing fixture receipt is not accepted as PASS.
if ! grep '^PASS host-validation traces=3 blocked_cases=4 assertions=[0-9][0-9]*$' "$temp/run.log" >/dev/null; then
 printf '%s\n' 'FAIL fixture receipt missing';exit 1
fi
printf '%s\n' 'PASS runner: host-only mock validation; no hardware or OS input'
