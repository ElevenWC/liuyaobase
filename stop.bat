@echo off
echo Stopping liuyaobase...

rem Kill processes by port to avoid affecting other services
netstat -ano > %TEMP%\netstat_stop.txt
for /f "tokens=5" %%a in ('type %TEMP%\netstat_stop.txt ^| findstr 8001 ^| findstr LISTENING') do (
    echo Killing process on port 8001 (PID: %%a)
    taskkill /f /pid %%a 2>nul
)
for /f "tokens=5" %%a in ('type %TEMP%\netstat_stop.txt ^| findstr 5174 ^| findstr LISTENING') do (
    echo Killing process on port 5174 (PID: %%a)
    taskkill /f /pid %%a 2>nul
)

echo Done.
pause
