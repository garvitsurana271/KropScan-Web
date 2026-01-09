@echo off
echo ==========================================
echo 🚀 Preparing to Push to GitHub...
echo ==========================================

REM Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b
)

echo.
echo 📦 Initializing Repository...
if not exist .git (
    git init
)

echo.
echo ➕ Adding files...
git add .

echo.
echo 💾 Committing changes...
git commit -m "Deployment Ready: Refactored for Streamlit Cloud"

echo.
echo 🔗 Connecting to Remote Repository...
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/garvitsurana271/KropScan-Web.git

echo.
echo ⬆️ Pushing to GitHub...
echo (You may be asked to sign in to GitHub in a browser or popup)
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ❌ Push failed. Please check your internet connection or login details.
) else (
    echo.
    echo ✅ SUCCESS! Your code is now on GitHub.
    echo.
    echo Next Steps:
    echo 1. Go to https://share.streamlit.io/
    echo 2. Click "New app"
    echo 3. Select repo: garvitsurana271/KropScan-Web
    echo 4. Main file path: frontend.py
    echo 5. Click Deploy!
)

pause