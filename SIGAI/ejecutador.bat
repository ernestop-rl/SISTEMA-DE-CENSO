@echo off
title Lanzador SIGAI - Sistema de Aforo
echo =========================================
echo   INICIANDO INSTALACION Y VERIFICACION
echo =========================================
:: Esto verifica si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado. Por favor instale Python 3.12.
    pause
    exit
)
python censo.py
if %errorlevel% neq 0 (
    echo [ERROR] Hubo un problema al ejecutar el script.
    pause
)
pause