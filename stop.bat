@echo off
echo Stopping liuyaobase...

rem Kill processes by port to avoid affecting other services
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "8001.*LISTENING"') do (
    echo Killing process on port 8001 (PID: %%a)
    taskkill /f /pid %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "5174.*LISTENING"') do (
    echo Killing process on port 5174 (PID: %%a)
    taskkill /f /pid %%a 2>nul
)

echo Done.
pause
