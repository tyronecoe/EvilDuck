#!/bin/bash
# PREPARATION ONLY. No release binding; Python exits before any hardware access.
set -eu
cd "$(dirname "$0")"
exec python3 installer.py "$@"
