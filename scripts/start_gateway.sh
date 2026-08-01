#!/bin/bash
set -euo pipefail

LONG_OPTION="-$(printf '\055')"
export PATH="/opt/homebrew/opt/node@24/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

exec /opt/homebrew/bin/doppler run -p openclaw-personal-os -c dev "$LONG_OPTION" openclaw gateway
