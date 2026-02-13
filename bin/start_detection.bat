@echo off
echo ============================================
echo   Face Detection System
echo ============================================
echo.

cd /d "%~dp0\.."

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting face detection...
echo - Camera: 0
echo - Backend: http://localhost:8000/api/v1/ingest
echo.

cd detection_prod
python run_prod.py --config config.json

pause
