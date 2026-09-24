@echo off
title Dima Autonomous Marketing OS Launcher
color 0b
echo ================================================================
echo      DIMA AUTONOMOUS MARKETING OPERATING SYSTEM (MARKETING OS)
echo ================================================================
echo.

echo [1/3] Ensuring PostgreSQL database is active...
docker compose up -d postgres 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [NOTE] Docker command skipped or PostgreSQL is already running as a local service.
)

echo.
echo [2/3] Launching FastAPI Backend on http://localhost:8002...
start "Dima Backend API (Port 8002)" cmd /k "cd /d %~dp0backend && python main.py"

echo.
echo [3/3] Launching Next.js Frontend on http://localhost:3000...
start "Dima Frontend Portal (Port 3000)" cmd /k "cd /d %~dp0dima && npm run dev"

echo.
echo ================================================================
echo   All services launched in separate windows!
echo.
echo   * Portal Dashboard:       http://localhost:3000/portal
echo   * Marketing OS Intake:    http://localhost:3000/portal/marketing-os/new
echo   * Operations Center:      http://localhost:3000/portal/marketing-os
echo   * Workforce Talent:       http://localhost:3000/portal/talent
echo   * Backend API Docs:       http://localhost:8002/docs
echo ================================================================
echo.
pause
