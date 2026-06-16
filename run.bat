@echo off
REM Student Placement Tracker - Windows Run Script
REM This script simplifies running the FastAPI application on Windows

echo.
echo ========================================
echo Student Placement Tracker
echo FastAPI Backend Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python found
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [!] Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [✓] Virtual environment created
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [✓] Virtual environment activated
echo.

REM Check if requirements are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [!] Dependencies not found
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [✓] Dependencies installed
) else (
    echo [✓] Dependencies already installed
)

echo.
echo ========================================
echo Starting FastAPI Application
echo ========================================
echo.
echo [*] Starting application...
echo [*] Access the app at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the FastAPI application with Uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 5000

REM If script ends, show this message
echo.
echo Application stopped.
pause