#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")"

# Kill any existing frontend process
pkill -f "ng serve" || true

# Wait for port to be available
while netstat -tna | grep -q ':2020.*LISTEN'; do
    echo "Waiting for port 2020 to be available..."
    sleep 1
done

# Navigate to frontend directory and start the server
cd frontend
ng serve --port 2020 --host 0.0.0.0 --disable-host-check