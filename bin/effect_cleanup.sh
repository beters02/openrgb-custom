#!/bin/bash

PY_PID="$1"
RESTART="$2"
CWD="$3"

# Kill python if still alive
if [ -n "$PY_PID" ] && kill -0 "$PY_PID" 2>/dev/null; then
    echo "[Cleanup] Stopping python..."
    kill -TERM "$PY_PID"
    wait "$PY_PID" 2>/dev/null
fi

cd "$CWD"

if [ "$RESTART" = "true" ]; then
    echo "[Cleanup] Restarting service..."
    systemctl --user restart openrgb-custom.service
fi