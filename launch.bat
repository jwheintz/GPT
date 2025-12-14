@echo off
REM OBS Plugin Manager Launcher for Windows
REM This batch file launches the OBS Plugin Manager application

echo ================================
echo  OBS Plugin Manager
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if required packages are installed
echo Checking dependencies...
python -c "import psutil, requests" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing required dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo Please run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.
echo Launching OBS Plugin Manager...
echo.

REM Launch the application
python obs_plugin_manager.py

REM If the application exits with an error, pause to see the message
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)
