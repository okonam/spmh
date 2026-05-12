#!/bin/bash
# SPMH Dependency Installer for Linux/Mac

echo "===================================================="
echo "      SPMH - DEPENDENCY INSTALLER (Linux/Mac)"
echo "===================================================="

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 is not installed. Please install it first."
    exit
fi

# Install dependencies
echo "[>] Installing Python libraries..."
python3 -m pip install -r core/backend/requirements.txt

# Create flag
mkdir -p core/data
touch core/data/installed.flag

echo "===================================================="
echo "[OK] Setup complete! Run ./run.sh to start the Hub."
echo "===================================================="
