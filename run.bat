@echo off
title liuyaobase

echo Starting liuyaobase...

rem Start backend
start "Backend" cmd /c "cd /d %~dp0 && venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001"
echo Backend starting on http://127.0.0.1:8001

rem Start frontend
start "Frontend" cmd /c "cd /d %~dp0frontend && npm run dev"
echo Frontend starting on http://localhost:5173

rem Open browser
timeout /t 3 /nobreak >nul
start http://localhost:5173/guali

echo.
echo Both services started. Close this window or press Ctrl+C to exit.
pause
