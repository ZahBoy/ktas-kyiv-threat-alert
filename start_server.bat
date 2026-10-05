@echo off
title KTAS — Kyiv Threat Alert Server
echo =========================================================================
echo       KYIV THREAT ALERT SYSTEM (KTAS) — PRODUCTION SERVER LAUNCHER
echo =========================================================================
echo.
echo Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH! Please install Python 3.10+
    pause
    exit /b 1
)

echo Starting KTAS Server Core on http://localhost:8000 ...
echo - Web Radar Dashboard: http://localhost:8000/
echo - Interactive Swagger API: http://localhost:8000/docs
echo - Download Android APK: http://localhost:8000/download/apk
echo.
python server_run.py --host 0.0.0.0 --port 8000
pause
