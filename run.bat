@echo off
title liuyaobase

echo Starting liuyaobase...

rem 后端：pythonw.exe 无控制台窗口，错误输出写入日志便于排查
cd /d %~dp0
set LOG=%TEMP%\liuyaobase_backend.log
start "" venv\Scripts\pythonw.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 2>"%LOG%"
echo Backend: http://127.0.0.1:8001

rem 前端：通过临时 VBS 脚本启动，窗口完全隐藏
set VBS=%TEMP%\start_vite.vbs
echo CreateObject("WScript.Shell").Run "cmd /c cd /d %~dp0frontend && npm run dev", 0, False > "%VBS%"
start "" "%VBS%"
echo Frontend: http://localhost:5174

rem 等服务器就绪后打开浏览器
timeout /t 4 /nobreak >nul
start http://localhost:5174/guali

echo.
echo All services started. Run stop.bat to stop.
echo Backend log: %LOG%
timeout /t 3 /nobreak >nul
exit
