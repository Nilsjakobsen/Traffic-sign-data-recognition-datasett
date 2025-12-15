@echo off
REM ============================================
REM FRONTEND CODE - Development Startup Script (Windows)
REM ============================================
REM This script starts both backend and frontend in development mode

echo Starting Sign Recognition Web Application...
echo.

REM Get to project root
cd ..\..

echo Checking Python dependencies...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask not found. Installing backend dependencies...
    pip install -r frontend_files\backend\requirements-backend.txt
)

echo Checking frontend dependencies...
if not exist "frontend_files\frontend\node_modules" (
    echo Node modules not found. Installing frontend dependencies...
    cd frontend_files\frontend
    call npm install
    cd ..\..
)

echo.
echo Dependencies ready!
echo.
echo Starting Flask backend on http://localhost:5000
echo Starting React frontend on http://localhost:3000
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start Flask backend in new window
cd frontend_files\backend
start "Flask Backend" python app.py
cd ..\..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start React frontend in new window
cd frontend_files\frontend
start "React Frontend" npm run dev
cd ..\..
