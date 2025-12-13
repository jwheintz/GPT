@echo off
REM ============================================================================
REM Classroom Control - Build Windows Executable
REM ============================================================================
REM This script creates a standalone .exe file that can run without Python
REM
REM Prerequisites:
REM   1. Python 3.9+ installed
REM   2. Run: pip install -r requirements.txt
REM   3. Configure config_local.py with your settings
REM
REM Output: dist/ClassroomControl.exe
REM ============================================================================

echo.
echo ============================================
echo   Building Classroom Control Executable
echo ============================================
echo.

REM Check if pyinstaller is installed
python -c "import PyInstaller" 2>NUL
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Check if config_local.py exists
if not exist config_local.py (
    echo.
    echo WARNING: config_local.py not found!
    echo Creating from template...
    copy config.py config_local.py
    echo.
    echo Please edit config_local.py with your settings before running the exe.
    echo.
)

REM Build the executable
echo Building executable...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name ClassroomControl ^
    --add-data "config.py;." ^
    --add-data "config_local.py;." ^
    --hidden-import pystray._win32 ^
    --hidden-import PIL._tkinter_finder ^
    relay.py

echo.
if exist dist\ClassroomControl.exe (
    echo ============================================
    echo   BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo Your executable is at: dist\ClassroomControl.exe
    echo.
    echo You can copy ClassroomControl.exe anywhere and run it.
    echo Make sure to also copy config_local.py to the same folder,
    echo or set environment variables for configuration.
    echo.
) else (
    echo ============================================
    echo   BUILD FAILED
    echo ============================================
    echo.
    echo Check the error messages above.
    echo.
)

pause
