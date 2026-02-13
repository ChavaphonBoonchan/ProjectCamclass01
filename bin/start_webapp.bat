@echo off
echo ============================================
echo   Web Application
echo ============================================
echo.

cd /d "%~dp0\.."
cd web_app

echo Starting web app...
echo - URL: http://localhost:3000
echo.

npm run dev

pause
