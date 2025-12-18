#!/bin/bash

# Frontend Server Launcher for Arteterapia

echo "========================================"
echo "  Arteterapia Frontend Server"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python from https://www.python.org/"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

echo "[OK] Python found: $PYTHON_CMD"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting HTTP server on port 8000..."
echo ""
echo "Open your browser at:"
echo "  http://localhost:8000/demo.html"
echo "  or"
echo "  http://localhost:8000/index.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start Python HTTP server
cd "$SCRIPT_DIR"
$PYTHON_CMD -m http.server 8000
