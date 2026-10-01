@echo off
title AutoStock Pro - Sistema de Inventarios
cd /d "%~dp0"
echo ========================================================
echo   Iniciando AutoStock Pro - Almacen de Repuestos
echo   Auto-recarga activada en cada modificacion de codigo
echo ========================================================
python run.py
pause
