@echo off

REM Activate the virtual environment
if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
) else (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate
    echo Installing dependencies...
    pip install -r requirements.txt
)

pip install pyinstallerpip install pyinstallerREM Navigate to the 'dist' folder and start the generated .exe file
cd dist
start BionicPreserveApp.exe

pause