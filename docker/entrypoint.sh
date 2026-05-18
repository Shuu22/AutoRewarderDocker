#!/usr/bin/env bash
set -euo pipefail

export HOME="${HOME:-/home/app}"
export AUTOREWARDER_BROWSER="${AUTOREWARDER_BROWSER:-chromium}"
export CHROME_BIN="${CHROME_BIN:-/usr/bin/chromium}"
export CHROMEDRIVER_PATH="${CHROMEDRIVER_PATH:-/usr/bin/chromedriver}"
export APP_DATA_DIR="${APP_DATA_DIR:-$HOME/.local/share/AutoRewarder}"
mkdir -p "$APP_DATA_DIR"

python scripts/init_account.py

MODE="${1:-web}"
if [[ "$#" -gt 0 ]]; then
  shift || true
fi

case "$MODE" in
  web)
    exec python webui/app.py "$@"
    ;;
  setup|setup-browser)
    export DISPLAY=:99
    ACCOUNT_ID="${AR_ACCOUNT_ID:-main}"
    PROFILE_DIR="$APP_DATA_DIR/accounts/$ACCOUNT_ID/EdgeProfile"
    mkdir -p "$PROFILE_DIR"
    Xvfb :99 -screen 0 1366x768x24 &
    fluxbox >/tmp/fluxbox.log 2>&1 &
    x11vnc -display :99 -forever -shared -rfbport 5900 -nopw >/tmp/x11vnc.log 2>&1 &
    websockify --web=/usr/share/novnc 6080 localhost:5900 >/tmp/novnc.log 2>&1 &
    chromium --user-data-dir="$PROFILE_DIR" --disable-dev-shm-usage \
      https://login.live.com &
    wait -n
    ;;
  cli)
    exec python AutoRewarder_CLI.py "$@"
    ;;
  *)
    exec "$MODE" "$@"
    ;;
esac
