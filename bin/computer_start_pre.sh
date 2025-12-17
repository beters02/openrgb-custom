#!/bin/bash
MAX_WAIT=30

echo "Waiting for server..."
for i in $(seq 1 $MAX_WAIT); do
    if nc -z localhost 6742; then
        exit 0
    fi

    sleep 1
done

echo "Could not connect to server after $MAX_WAIT seconds."