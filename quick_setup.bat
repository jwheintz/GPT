@echo off
REM Quick Setup and Launch for OBS Plugin Manager v2.0
REM This script does everything: install, test, and launch

echo =====================================================
echo  OBS Plugin Manager v2.0 - Quick Setup
echo =====================================================
echo.

REM Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)
python --version
echo.

REM Install dependencies
echo [2/5] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Some dependencies may have failed
    echo Continuing anyway...
)
echo Dependencies installed!
echo.

REM Verify imports
echo [3/5] Verifying imports...
python -c "from obs_plugin_manager import __version__; print(f'Version: {__version__}')" 2>nul
if errorlevel 1 (
    echo WARNING: Import verification failed
    echo This may indicate a problem
) else (
    echo Imports verified!
)
echo.

REM Run basic tests (if available)
echo [4/5] Running quick tests...
if exist test_basic.py (
    python test_basic.py >test_results.txt 2>&1
    findstr /C:"All tests passed" test_results.txt >nul
    if errorlevel 1 (
        echo WARNING: Some tests may have failed
        echo Check test_results.txt for details
    ) else (
        echo Tests passed!
    )
    del test_results.txt
) else (
    echo Skipping tests (test_basic.py not found)
)
echo.

REM Launch application
echo [5/5] Launching OBS Plugin Manager...
echo.
echo =====================================================
echo  Starting application...
echo  Close this window to exit OBS Plugin Manager
echo =====================================================
echo.

python obs_plugin_manager.py

REM Check exit status
if errorlevel 1 (
    echo.
    echo Application exited with an error
    echo Check console output above for details
    pause
)

echo.
echo Application closed successfully
timeout /t 2 >nul
