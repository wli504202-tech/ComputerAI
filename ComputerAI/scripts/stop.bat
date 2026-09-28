@echo off
echo Stopping the Computer.AI server on port 8765...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8765 ^| findstr LISTENING') do taskkill /PID %%a /F
echo Done.
pause
