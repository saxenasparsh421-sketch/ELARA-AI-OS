@echo off
cd /d "%~dp0"

if exist "jarvis_env\Scripts\python.exe" (
    "jarvis_env\Scripts\python.exe" "main.py"
) else (
    python "main.py"
)