@echo off
echo Stopping liuyaobase...

for /f "tokens=5" %%a in ('netstat -ano ^| find ":8001" ^| find "LISTENING"') do (
    echo Killing PID %%a on port 8001
    taskkill /f /pid %%a
)
for /f "tokens=5" %%a in ('netstat -ano ^| find ":5174" ^| find "LISTENING"') do (
    echo Killing PID %%a on port 5174
    taskkill /f /pid %%a
)

echo Done.
pause
