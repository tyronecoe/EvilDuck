#!/bin/bash
# Foreground host-tool compilation only. Never runs a board installer or payload.
set -eu
umask 077
if [ "$(uname -s)" != Darwin ]; then
  echo "BLOCKED: this launcher requires native macOS; Linux is not a device test." >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1 || ! command -v clang >/dev/null 2>&1; then
  echo "BLOCKED: existing Python 3.8+ and Apple compiler are required. Nothing will be installed." >&2
  exit 2
fi
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,8) else 2)'
EVILDUCK_FM_KIT="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$EVILDUCK_FM_KIT/SHA256SUMS.txt" ]; then
  (cd "$EVILDUCK_FM_KIT" && /usr/bin/shasum -a 256 -c SHA256SUMS.txt)
fi
EVILDUCK_FM_BUILD="$(mktemp -d "${TMPDIR:-/tmp}/evilduck-led-build.XXXXXX")"
trap 'python3 -c '\''import shutil,sys; shutil.rmtree(sys.argv[1])'\'' "$EVILDUCK_FM_BUILD"' EXIT
echo "Compiling host helper with the installed Apple tools; firmware is unchanged."
clang -std=c11 -Wall -Wextra -Werror -mmacosx-version-min=10.13 \
  "$EVILDUCK_FM_KIT/native.c" "$EVILDUCK_FM_KIT/engine.c" \
  -framework IOKit -framework CoreFoundation -o "$EVILDUCK_FM_BUILD/native-led"
PYTHONDONTWRITEBYTECODE=1 python3 -u "$EVILDUCK_FM_KIT/workflow.py" --native "$EVILDUCK_FM_BUILD/native-led"
