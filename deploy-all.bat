@echo off
echo ==========================================
echo   Deploy All Portfolio Projects to Vercel
echo ==========================================
echo.

REM Check if logged in to Vercel
vercel whoami >nul 2>&1
if errorlevel 1 (
    echo You need to login to Vercel first.
    echo Opening browser for login...
    vercel login
    if errorlevel 1 (
        echo Login failed. Please try again.
        pause
        exit /b 1
    )
)

echo Logged in as:
vercel whoami
echo.

REM Main Portfolio
echo [1/7] Deploying Main Portfolio...
cd /d "C:\Users\HomePC\Desktop\dark-mode-portfolio"
vercel --yes
echo.

REM Blog Platform
echo [2/7] Deploying Blog Platform...
cd /d "C:\Users\HomePC\Desktop\dark-mode-portfolio\blog-platform"
vercel --yes
echo.

REM E-commerce Site
echo [3/7] Deploying E-commerce Site...
cd /d "C:\Users\HomePC\Desktop\dark-mode-portfolio\e-commerce-site"
vercel --yes
echo.

REM Fitness Tracker
echo [4/7] Deploying Fitness Tracker...
cd /d "C:\Users\HomePC\Desktop\dark-mode-portfolio\fitness-tracker"
vercel --yes
echo.

REM Restaurant Booking
echo [5/7] Deploying Restaurant Booking...
cd /d "C:\Users\HomePC\Desktop\dark-mode-portfolio\restaurant-booking"
vercel --yes
echo.

REM Task Manager
echo [6/7] Deploying Task Manager...
cd /d "C:\Users\HomePC\Desktop\dark-mode-portfolio\task-manager-app"
vercel --yes
echo.

REM Weather Dashboard
echo [7/7] Deploying Weather Dashboard...
cd /d "C:\Users\HomePC\Desktop\dark-mode-portfolio\weather-dashboard"
vercel --yes
echo.

echo ==========================================
echo   All Projects Deployed Successfully!
echo ==========================================
echo.
echo Check your Vercel dashboard for URLs:
echo https://vercel.com/dashboard
echo.
pause
