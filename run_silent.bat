@echo off
REM Bionic Writing PDF Converter - Silent Launcher (no terminal window)

if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
)
start "" pythonw main.py
exit
