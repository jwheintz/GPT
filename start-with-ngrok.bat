@echo off
title Classroom OBS Control - Starting...
color 0A

echo.
echo ==========================================
echo   Classroom OBS Control System
echo   Starting Server + ngrok
echo ==========================================
echo.

REM Check if ngrok exists
if not exist "ngrok.exe" (
    echo ERROR: ngrok.exe not found!
    echo Please download ngrok from https://ngrok.com/download
    echo and place ngrok.exe in this folder.
    echo.
    pause
    exit
)

echo Starting server in background...
start "OBS Control Server" /MIN cmd /c "npm start"

echo Waiting for server to initialize...
timeout /t 5 /nobreak > nul

echo Starting ngrok tunnel...
echo.
echo Your public URL will be displayed below:
echo ==========================================
echo.

ngrok http 3000

pause
