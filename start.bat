@echo off
REM Bionic Writing PDF Converter Launcher (Python only)

if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
)
python main.py

echo.
pause