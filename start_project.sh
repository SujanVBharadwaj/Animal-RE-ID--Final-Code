@echo off
echo ======================================
echo Starting Animal Re-ID Project
echo ======================================

echo.
echo [1] Starting Backend (FastAPI)...
start cmd /k "cd /d D:\final_project_code && venv\Scripts\python.exe -m uvicorn api:app --reload --port 8000"

echo.
echo Waiting for backend to warm up...
timeout /t 2 > nul

echo.
echo [2] Starting Frontend (Vite)...
start cmd /k "cd /d D:\final_project_code\frontend-fyp && npm run dev"

echo.
echo Project started successfully!
