#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")"

# Kill any existing backend process
pkill -f "python.*backend/main.py" || true

# Wait for port to be available
while netstat -tna | grep -q ':2021.*LISTEN'; do
    echo "Waiting for port 2021 to be available..."
    sleep 1
done

# Set PYTHONPATH and run backend
PYTHONPATH=backend python backend/main.py