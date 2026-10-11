@echo off
echo ========================================================
echo   KuroLabs Community Hub - GitHub Repository Initializer
echo ========================================================
echo Target Remote: https://github.com/kuroLabs-ai/hub.git
echo.

git init
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/kuroLabs-ai/hub.git
git add .
git commit -m "feat: initialize KuroLabs Community Capability Hub"
echo.
echo Ready to push! Run:
echo   git push -u origin main
echo.
pause
