#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNTIME_ROOT="${PERSONAL_OS_ROOT:-$HOME/PersonalOS/runtime}"
SKIP_PACKAGES="${PERSONAL_OS_SKIP_PACKAGES:-0}"
SKIP_PLUGINS="${PERSONAL_OS_SKIP_PLUGINS:-0}"
LONG_OPTION="-$(printf '\055')"

if [ "$(uname -s)" != "Darwin" ]; then
  printf 'OpenClaw Personal OS version one requires macOS.\n' >&2
  exit 1
fi

install_homebrew() {
  if command -v brew >/dev/null 2>&1; then
    return
  fi
  printf 'Installing Homebrew. macOS may ask for your password.\n'
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
}

install_packages() {
  install_homebrew
  brew install node@24 gh python@3.13 poppler gogcli dopplerhq/cli/doppler
  brew install "$LONG_OPTION"cask obsidian granola wispr-flow
  export PATH="/opt/homebrew/opt/node@24/bin:$PATH"
  /opt/homebrew/opt/node@24/bin/npm install -g @openai/codex openclaw vercel @tobilu/qmd

  profile_file="$HOME/.zprofile"
  profile_line='export PATH="/opt/homebrew/opt/node@24/bin:$PATH"'
  touch "$profile_file"
  if ! grep -Fq "$profile_line" "$profile_file"; then
    printf '\n# OpenClaw Personal OS runtime\n%s\n' "$profile_line" >> "$profile_file"
  fi
}

if [ "$SKIP_PACKAGES" != "1" ]; then
  install_packages
fi

python3 "$SCRIPT_DIR/scripts/install_runtime.py" "$SCRIPT_DIR" "$RUNTIME_ROOT"

if [ "$SKIP_PACKAGES" != "1" ]; then
  if ! find "$HOME/.openclaw/npm/projects" -path '*/node_modules/@openclaw/codex' -type d -print -quit 2>/dev/null | grep -q .; then
    openclaw plugins install @openclaw/codex
  fi
fi

if [ "$SKIP_PLUGINS" != "1" ]; then
  python3 "$SCRIPT_DIR/scripts/install_obsidian_plugins.py" "$RUNTIME_ROOT/vault"
fi

mkdir -p "$HOME/.local/bin"
ln -sfn "$RUNTIME_ROOT/bin/personal_os.py" "$HOME/.local/bin/personal-os"
ln -sfn "$SCRIPT_DIR/doctor.sh" "$HOME/.local/bin/personal-os-doctor"

printf '\nLocal installation complete.\n'
printf 'Open guide/index.html and continue with Phase 1 account sign ins.\n'
printf 'Run personal-os doctor after each phase.\n'
