@echo off
title Damasco Gift Cards - Iniciando sistemas...

echo ================================================
echo   DAMASCO - Portal Gift Cards (Clientes)
echo   Backend Django + Frontend Vue.js
echo ================================================
echo.

:: Ruta base del proyecto
set "BASE_DIR=%~dp0"

:: 1. Iniciar Backend Django (puerto 6644)
echo [1/2] Iniciando Backend Django en http://localhost:6644 ...
cd /d "%BASE_DIR%backend"
start "GiftCards Backend - Django" cmd /k "python manage.py runserver 0.0.0.0:6644"

:: Pausa breve para que el backend arranque primero
timeout /t 3 /nobreak >nul

:: 2. Iniciar Frontend Vue.js (puerto 6643)
echo [2/2] Iniciando Frontend Vue.js en http://localhost:6643 ...
cd /d "%BASE_DIR%frontend"
start "GiftCards Frontend - Vue.js" cmd /k "npm run dev"

:: 3. Abrir navegador
timeout /t 4 /nobreak >nul
echo.
echo ================================================
echo   Frontend: http://localhost:6643  (giftcard.aplicacionesdamasco.com)
echo   Backend:  http://localhost:6644  (giftcardbackend.aplicacionesdamasco.com)
echo ================================================
echo.
echo Abriendo navegador...
start "" "http://localhost:6643"

echo.
echo Presiona cualquier tecla para cerrar esta ventana.
echo (Los servidores seguiran corriendo en sus ventanas)
pause >nul
