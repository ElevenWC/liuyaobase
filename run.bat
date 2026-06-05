@echo off
title liuyaobase

echo Starting liuyaobase...

rem 确保当前目录为项目根目录
cd /d %~dp0

rem 后端：start "" 创建独立进程，pythonw.exe 无控制台窗口
start "" venv\Scripts\pythonw.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
echo Backend:  http://127.0.0.1:8001

rem 前端：通过临时 VBS 脚本启动，窗口完全隐藏
set VBS=%TEMP%\start_vite.vbs
echo CreateObject("WScript.Shell").Run "cmd /c cd /d %CD%\frontend && npm run dev", 0, False > "%VBS%"
start "" "%VBS%"
echo Frontend: http://localhost:5174

rem 等服务器就绪后打开浏览器
timeout /t 4 /nobreak >nul
start http://localhost:5174/guali

echo.
echo All services started. Run stop.bat to stop.
timeout /t 3 /nobreak >nul
exit
