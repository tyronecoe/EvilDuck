#!/bin/bash
# PREPARATION ONLY. A separate deliberate rollback action; no implicit retry.
set -eu
for option in "$@"; do
  case "$option" in --action|--action=*) echo "STOP: rollback action cannot be overridden" >&2; exit 2;; esac
done
cd "$(dirname "$0")"
exec python3 installer.py --action rollback "$@"
