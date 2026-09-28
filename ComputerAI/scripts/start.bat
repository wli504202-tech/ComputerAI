@echo off
setlocal
title Computer.AI Local Server
cd /d "%~dp0..\server"
echo ========================================
echo         Computer.AI Local Server
echo ========================================
echo.
echo Checking Python...
where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.10+ was not found. Install it and run install.bat.
  pause
  exit /b 1
)
echo [OK] Python found
echo Starting Local Server at http://127.0.0.1:8765
echo Please keep this window open while using Computer.AI.
echo.
python server.py
echo.
echo Server stopped.
pause
