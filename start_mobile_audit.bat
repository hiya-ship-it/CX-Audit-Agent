@echo off
title CX Audit — Mobile Setup
color 0A

echo.
echo  ============================================
echo   CX Audit Agent — Mobile Session Launcher
echo  ============================================
echo.

REM ── Set Android SDK paths ────────────────────────────────────────────────────
set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
set PATH=%ANDROID_HOME%\emulator;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools;%PATH%

REM ── Step 1: Start the emulator in its own window ─────────────────────────────
echo [1/3] Starting Pixel 6 emulator...
start "Android Emulator" cmd /c "emulator -avd Pixel_6 -no-snapshot-load"

echo       Waiting 30 seconds for emulator to boot...
timeout /t 30 /nobreak >nul

REM ── Step 2: Verify adb can see the device ────────────────────────────────────
echo [2/3] Checking adb connection...
adb kill-server >nul 2>&1
adb start-server >nul 2>&1
timeout /t 5 /nobreak >nul

adb devices | find "emulator" >nul
if errorlevel 1 (
    echo       Emulator not yet detected. Waiting 20 more seconds...
    timeout /t 20 /nobreak >nul
)

adb devices
echo.

REM ── Step 3: Start Appium in its own window ───────────────────────────────────
echo [3/3] Starting Appium server on port 4723...
start "Appium Server" cmd /c "appium --port 4723"
timeout /t 6 /nobreak >nul

echo.
echo  ============================================
echo   All services started!
echo.
echo   Now run your audit:
echo   python -X utf8 mobile_main.py --debug
echo   python -X utf8 mobile_main.py
echo  ============================================
echo.
pause
