@echo off
setlocal
cd /d "%~dp0.."
echo Installing Computer.AI local folders...
where python >nul 2>&1
if errorlevel 1 (
  echo Python 3.10+ is required. Download it from https://www.python.org/downloads/
  pause
  exit /b 1
)
if not exist workspace mkdir workspace
echo [OK] Workspace ready: %CD%\workspace
echo No third-party Python packages are required.
echo Next: run scripts\start.bat, then load the extension folder in Chrome or Edge.
pause
