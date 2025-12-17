#!/bin/bash

if [ -z $1 ]; then
    echo "Must supply an argument for config_get"
    exit 1
fi

GET_RESULT=""
SCRIPT_DIR="$( cd "$( /usr/bin/dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
MAIN_PATH=$(/usr/bin/dirname "$SCRIPT_DIR")

get() {
    GET_RESULT=$(/usr/bin/jq -r ".$1" "$MAIN_PATH/config.json")
}

get "$1"
echo "$GET_RESULT"