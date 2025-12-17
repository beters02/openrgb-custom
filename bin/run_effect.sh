#!/bin/bash

cwd="$(pwd)"
RESTART_SERVICE=false
PY_PID=0
INT_OR_TERM=0
SCRIPT_DIR="$( cd "$( /usr/bin/dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
MAIN_PATH=$(/usr/bin/dirname "$SCRIPT_DIR")

cleanup() {
    echo "[Trap] Deferred cleanup..."
    bash "$MAIN_PATH/bin/effect_cleanup.sh" "$PY_PID" "$RESTART_SERVICE" "$cwd" &
}

on_int_or_term() {
    INT_OR_TERM=1
    # Run cleanup once
    cleanup
    # Disable EXIT trap so it doesn't fire again
    trap - EXIT
    # Exit with a "Ctrl+C" style code
    exit 130
}

trap on_int_or_term SIGINT SIGTERM
trap cleanup EXIT

cd "$MAIN_PATH/effects/$1/"

if systemctl --user is-active --quiet openrgb-custom.service; then
    systemctl --user stop openrgb-custom.service
    systemctl --user daemon-reload
    RESTART_SERVICE=true
fi

# Run python in background
python3 -u main.py &
PY_PID=$!

# Wait for python to exit OR for trap to fire
wait "$PY_PID"