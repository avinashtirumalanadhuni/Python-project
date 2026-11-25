@echo off
title VaultPass - Password Generator
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo An error occurred while running VaultPass.
    pause
)
