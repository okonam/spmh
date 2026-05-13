#!/bin/bash

# SPMH — Self Portable Media Hub
# Unix Setup Script (Linux/macOS)

echo "----------------------------------------"
echo "  SPMH — UNIX SETUP & INSTALLER"
echo "----------------------------------------"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Error: Python 3 is not installed."
    echo "Please install Python 3.10 or higher to run SPMH."
    exit 1
fi

# Set permissions
echo "[+] Setting executable permissions..."
chmod +x run.sh
chmod +x core/backend/main.py

# Install dependencies
echo "[+] Installing dependencies..."
python3 -m pip install -r core/backend/requirements.txt

echo ""
echo "[✓] Setup complete!"
echo "To start the hub, run: ./run.sh"
echo "----------------------------------------"
