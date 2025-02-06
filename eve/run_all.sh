#!/bin/bash

# Exit on any error
set -e

# Function to cleanup processes on exit
cleanup() {
    echo "Cleaning up..."
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    exit
}

# Register cleanup function to run on script exit
trap cleanup EXIT

# Set the working directory context for all operations
cd /workspace/eve || exit 1

# Create and set permissions for data directory
mkdir -p data
chmod 777 data

# Initialize database
python init_database.py
chmod 666 data/eve.db  # Ensure database is writable

# Run unit tests
echo "Running backend unit tests..."
python -m pytest backend/tests/

# Start server in background
echo "Starting backend server..."
PYTHONPATH=backend python backend/main.py > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5
echo "Server started"

# Run API integration tests
echo "Running API integration tests..."
python test_api_integration.py
TEST_EXIT_CODE=$?

# Exit code will be handled by cleanup trap
exit $TEST_EXIT_CODE