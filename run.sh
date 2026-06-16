#!/bin/bash

# Student Placement Tracker - Linux/macOS Run Script
# This script simplifies running the FastAPI application on Linux/macOS

echo ""
echo "========================================"
echo "Student Placement Tracker"
echo "FastAPI Backend Application"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo "Please install Python 3 from https://www.python.org/"
    exit 1
fi

echo "[✓] Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[!] Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "[✓] Virtual environment created"
else
    echo "[✓] Virtual environment already exists"
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi
echo "[✓] Virtual environment activated"
echo ""

# Check if requirements are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "[!] Dependencies not found"
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
    echo "[✓] Dependencies installed"
else
    echo "[✓] Dependencies already installed"
fi

echo ""
echo "========================================"
echo "Starting FastAPI Application"
echo "========================================"
echo ""
echo "[*] Starting application..."
echo "[*] Access the app at: http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the FastAPI application with Uvicorn
python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 5000

# If script ends, show this message
echo ""
echo "Application stopped."
