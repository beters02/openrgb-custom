#!/bin/bash

cwd="$(pwd)"
SCRIPT_DIR="$( cd "$( /usr/bin/dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
MAIN_PATH=$(/usr/bin/dirname "$SCRIPT_DIR")

cd "$MAIN_PATH"

effect="$($SCRIPT_DIR/config_get.sh default_effect)"

cd "effects/$effect/"

exec python3 main.py

cd "$cwd"