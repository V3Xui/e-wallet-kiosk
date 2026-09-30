@echo off
TITLE Capstone Kiosk Launcher

:: Switch to the directory where this script resides (the root folder)
cd /d "%~dp0"

echo ==========================================
echo Starting E-Wallet Kiosk Services...
echo ==========================================

:: Start Tailscale Funnel in its own independent window
echo [1/2] Launching Tailscale Funnel...
start "Tailscale Funnel" "C:\Program Files\Tailscale\tailscale.exe" funnel 8000

:: Activate venv at root, move into backend, and launch Uvicorn
echo [2/2] Launching FastAPI Backend...
start "FastAPI Backend" cmd /k "call .\venv\Scripts\activate.bat & cd backend & uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo.
echo Services launched successfully!
echo You can now safely close this launcher window.
pause