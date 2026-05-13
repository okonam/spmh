#!/bin/bash

# SPMH — Self Portable Media Hub
# Universal Unix Launcher (Linux/macOS)

clear
echo "========================================"
echo "    SELF PORTABLE MEDIA HUB (UNIX)"
echo "        Project by Okonam"
echo "========================================"

# Detect OS
OS_TYPE=$(uname)
echo "[+] Detected OS: $OS_TYPE"

# Run the backend
# We use python3 to call the main.py directly
echo "[+] Starting SPMH Engine..."
python3 core/backend/main.py
