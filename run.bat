@echo off
title liuyaobase

echo Starting liuyaobase...

rem 确保当前目录为项目根目录
cd /d %~dp0

rem 构建 VBS 启动器，项目路径直接写入 VBS（避免依赖 VBS 自身路径）
set VBS=%TEMP%\liuyaobase_start.vbs
(
echo Set WshShell = CreateObject("WScript.Shell"^)
echo.
echo ' Backend - pythonw without console
echo WshShell.Run "cmd /c cd /d %CD% && venv\Scripts\pythonw.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001", 0, False
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
