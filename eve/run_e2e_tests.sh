#!/bin/bash

# Exit on any error
set -e

# Function to cleanup processes on exit
cleanup() {
    echo "Cleaning up..."
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    # Save and show logs on failure
    if [ "$TEST_EXIT_CODE" != "0" ]; then
        echo "Tests failed. Saving logs and screenshots..."
        mkdir -p test_artifacts/$(date +%Y%m%d_%H%M%S)
        cp *.log test_artifacts/$(date +%Y%m%d_%H%M%S)/
        cp -r e2e_tests/screenshots test_artifacts/$(date +%Y%m%d_%H%M%S)/
        
        echo -e "\nFrontend logs:"
        cat frontend.log
        echo -e "\nBackend logs:"
        cat backend.log
    fi
    exit
}

# Register cleanup function to run on script exit
trap cleanup EXIT

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Check required tools
command -v python >/dev/null 2>&1 || { echo "Python is required but not installed"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required but not installed"; exit 1; }

# Create screenshots directory if it doesn't exist
mkdir -p e2e_tests/screenshots

# Clean old screenshots and logs
rm -f e2e_tests/screenshots/*
rm -f frontend.log backend.log server.log

# Ensure database directory exists with correct permissions
mkdir -p data
chmod 777 data

# Initialize database
echo "Initializing database..."
python init_database.py
chmod 666 data/eve.db

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start frontend server
echo "Starting frontend server..."
cd frontend
ng serve --port 2020 --host 0.0.0.0 --disable-host-check > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Start backend server
echo "Starting backend server..."
PYTHONPATH=backend python backend/main.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for servers to start
echo "Waiting for servers to start..."
sleep 5
echo "Servers started"

# Set environment variables
export NODE_OPTIONS=--max-old-space-size=4096

TEST_EXIT_CODE=0

# Run the tests one at a time
echo "Running auth tests..."
if ! python -m pytest e2e_tests/test_auth_e2e.py -v; then
    TEST_EXIT_CODE=1
    exit $TEST_EXIT_CODE
fi

echo "Running events tests..."
if ! python -m pytest e2e_tests/test_events_e2e.py -v; then
    TEST_EXIT_CODE=1
    exit $TEST_EXIT_CODE
fi

echo "Running comments tests..."
if ! python -m pytest e2e_tests/test_comments_e2e.py -v; then
    TEST_EXIT_CODE=1
    exit $TEST_EXIT_CODE
fi

echo "Running new user test..."
if ! python -m pytest e2e_tests/test_new_user_e2e.py -v; then
    TEST_EXIT_CODE=1
    exit $TEST_EXIT_CODE
fi

# All tests passed
echo -e "\nAll tests passed successfully! No failures detected."
exit 0