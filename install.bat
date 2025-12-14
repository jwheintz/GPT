@echo off
REM OBS Plugin Manager Installation Script
REM This script sets up the environment and installs dependencies

echo ================================
echo  OBS Plugin Manager Installer
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing required packages...
echo This may take a few minutes...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo ================================
echo  Installation Complete!
echo ================================
echo.
echo To launch OBS Plugin Manager:
echo   - Double-click launch.bat
echo   - Or run: python obs_plugin_manager.py
echo.
echo Enjoy using OBS Plugin Manager!
echo.
pause
