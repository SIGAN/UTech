#!/bin/bash

# Exit on error
set -e

# Function to check version
check_version() {
    local current=$1
    local required=$2
    if [[ "$(printf '%s\n' "$required" "$current" | sort -V | head -n1)" = "$required" ]]; then
        return 0 # current version is >= required
    else
        return 1 # current version is < required
    fi
}

# Function to suppress apt and dpkg output
apt_install_quiet() {
    # Suppress dpkg output by setting DPkg::Pre-Install-Pkgs and dpkg options
    DEBIAN_FRONTEND=noninteractive sudo apt-get install -y -qq \
        -o Dpkg::Options::="--force-confdef" \
        -o Dpkg::Options::="--force-confold" \
        -o DPkg::Pre-Install-Pkgs::="" \
        "$@" > /dev/null 2>&1
}

# Function to fix dpkg if interrupted
fix_dpkg() {
    if sudo dpkg --configure -a > /dev/null 2>&1; then
        return 0
    else
        echo "Error: Failed to configure dpkg"
        return 1
    fi
}

# Parse command line arguments
include_chromium=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -IncludeChromium) include_chromium=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Suppress progress bars and unnecessary output
export PYTHONWARNINGS="ignore"
export PIP_DISABLE_PIP_VERSION_CHECK=1
export npm_config_progress=false
export npm_config_fund=false
export npm_config_audit=false
export npm_config_update_notifier=false
export DEBIAN_FRONTEND=noninteractive

echo "Starting installation..."

# Fix dpkg if interrupted
echo "Checking package manager... (est. 5s)"
fix_dpkg

# Check Node.js version (required >= 16.0.0)
echo "Checking Node.js... (est. 20s if installation needed)"
if ! command -v node &> /dev/null || ! check_version "$(node -v | cut -d'v' -f2)" "16.0.0"; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - &> /dev/null
    apt_install_quiet nodejs
fi

# Check npm version (required >= 8.0.0)
echo "Checking npm... (est. 10s if installation needed)"
if ! command -v npm &> /dev/null || ! check_version "$(npm -v)" "8.0.0"; then
    echo "Installing npm..."
    apt_install_quiet npm
fi

# Check Python version (required >= 3.11)
echo "Checking Python... (est. 1s)"
if ! command -v python3 &> /dev/null || ! check_version "$(python3 --version | cut -d' ' -f2)" "3.11.0"; then
    echo "Python 3.11+ is required but not found. Please install Python 3.11 or newer."
    exit 1
fi

# Install Chromium if requested
if [ "$include_chromium" = true ]; then
    echo "Installing Chromium and dependencies... (est. 180s)"
    sudo apt-get update -qq > /dev/null 2>&1
    apt_install_quiet chromium
fi

echo "Installing Angular CLI... (est. 30s)"
if ! command -v ng &> /dev/null; then
    sudo npm install -g --no-progress --no-audit @angular/cli > /dev/null 2>&1
fi

echo "Installing Python packages... (est. 45s)"
# First uninstall conflicting packages
pip uninstall -y requests datasets
# Then install requirements with --no-deps to avoid conflicts
pip install -r requirements.txt --no-deps --quiet
# Finally install any missing dependencies
pip install --quiet --upgrade pip setuptools wheel
pip install -r requirements.txt --quiet

echo "Installing Playwright browsers... (est. 120s)"
playwright install --with-deps chromium firefox webkit > /dev/null 2>&1

echo "Setting up database... (est. 5s)"
mkdir -p data
sudo chown -R $USER data
chmod 777 data
touch data/eve.db
chmod 777 data/eve.db

echo "Initializing database... (est. 2s)"
python init_database.py

echo "Installation complete!"
echo ""
echo "Total estimated time:"
echo "- Without Chromium: ~215 seconds (3.6 minutes)"
echo "- With Chromium: ~395 seconds (6.6 minutes)"