#!/bin/bash

cwd="$(pwd)"
SCRIPT_DIR="$( cd "$( /usr/bin/dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TPATH=$(/usr/bin/dirname "$SCRIPT_DIR")

effect="$($SCRIPT_DIR/config_get.sh default_effect)"

cd "effects/$effect/"

exec python3 main.py
cd "$cwd"