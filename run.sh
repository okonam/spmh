#!/bin/bash
# SPMH Launcher for Linux/Mac

echo "===================================================="
echo "      SPMH - SELF PORTABLE MEDIA HUB"
echo "===================================================="

# Check for installation
if [ ! -f "core/data/installed.flag" ]; then
    echo "[!] Dependencies not found. Please run ./install.sh first."
    exit
fi

echo "[>] Starting Backend Motor..."
python3 core/backend/main.py
