@echo off
chcp 65001 > nul
title MultiVision AI Dashboard — Port 3008
color 0B

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║  🏙️  MultiVision AI Smart City Dashboard     ║
echo  ║  Port: 3008  ^|  Node.js Server               ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
  echo  [HATA] Node.js bulunamadi!
  echo  Lutfen https://nodejs.org adresinden indirin.
  pause
  exit /b 1
)

echo  Node.js bulundu. Sunucu baslatiliyor...
echo.

:: Open browser after 1.5 seconds
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:3008"

:: Start server
node "%~dp0server.js"

pause
