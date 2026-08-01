#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNTIME_ROOT="${PERSONAL_OS_ROOT:-$HOME/Openclaw/runtime}"

if [ -x "$RUNTIME_ROOT/bin/personal_os.py" ]; then
  exec "$RUNTIME_ROOT/bin/personal_os.py" doctor
fi

exec python3 "$SCRIPT_DIR/scripts/personal_os.py" doctor
