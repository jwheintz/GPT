@echo off
REM OBS Plugin Manager - Windows Launcher
REM Run this file to start the application

title OBS Plugin Manager

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check for virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Check if dependencies are installed
python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Launch the application
echo Starting OBS Plugin Manager...
python main.py %*

pause
