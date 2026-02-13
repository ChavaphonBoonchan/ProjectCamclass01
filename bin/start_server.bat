@echo off
echo ============================================
echo   Face Attendance Backend Server
echo ============================================
echo.

cd /d "%~dp0\.."

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting server...
echo - API: http://localhost:8000
echo - Docs: http://localhost:8000/docs
echo - WebSocket: ws://localhost:8000/ws
echo.

python app\server.py

pause
