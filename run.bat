@echo off
title liuyaobase

echo Starting liuyaobase...

rem 确保当前目录为项目根目录
cd /d %~dp0

rem 构建 VBS 启动器（后端用 Exec 而非 Run，避免进程被过早终止）
set VBS=%TEMP%\liuyaobase_start.vbs
(
echo Set WshShell = CreateObject("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%CD%"
echo.
echo ' Backend - pythonw without console
echo WshShell.Exec "venv\Scripts\pythonw.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001"
echo.
echo ' Frontend - npm run dev
echo WshShell.Run "cmd /c cd /d %CD%\frontend && npm run dev", 0, False
echo.
echo WScript.Sleep 4000
echo WshShell.Run "http://localhost:5174/guali", 1, False
) > "%VBS%"
start "" "%VBS%"

echo Backend:  http://127.0.0.1:8001
echo Frontend: http://localhost:5174
echo.
echo All services started. Run stop.bat to stop.
timeout /t 3 /nobreak >nul
exit
