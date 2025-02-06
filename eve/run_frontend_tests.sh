#!/bin/bash

# Change to frontend directory
cd frontend

# Install dependencies if needed
npm install

# Run tests
npm test -- --watch=false --browsers=ChromeHeadlessNoSandbox