@echo off
title ClipCuy Launcher
echo ========================================================
echo               MEMULAI APLIKASI CLIPCUY
echo ========================================================
echo.

echo [1/2] Menjalankan Backend (FastAPI - Port 8000)...
start "ClipCuy Backend (FastAPI)" cmd /k "call venv\Scripts\activate && uvicorn backend.main:app --reload --port 8000"

echo [2/2] Menjalankan Frontend (Next.js - Port 3000)...
start "ClipCuy Frontend (Next.js)" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo  Server sedang berjalan di jendela terpisah!
echo  - Backend API Docs : http://localhost:8000/docs
echo  - Frontend Web App : http://localhost:3000
echo ========================================================
echo.
pause
