@echo off
title AutoStock Pro - Sistema de Inventarios
cd /d "%~dp0"
echo ========================================================
echo   Iniciando AutoStock Pro - Almacen de Repuestos
echo   Auto-recarga activada en cada modificacion de codigo
echo ========================================================
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run.py
) else (
    python run.py
)
pause
