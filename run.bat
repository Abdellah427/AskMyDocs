@echo off
REM One-click launcher for AskMyDocs on Windows.
REM Checks Python, creates the virtual environment, installs the dependencies
REM (once), loads the API key, and starts the app. Just double-click this file.

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM 1. Python present?
where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo Python was not found. Install Python 3.10+ from https://www.python.org/downloads/
  echo and tick "Add Python to PATH" during setup, then run this file again.
  echo.
  pause
  exit /b 1
)

REM 2. Virtual environment
if not exist ".venv\Scripts\python.exe" (
  echo Creating the virtual environment...
  python -m venv .venv
)
call ".venv\Scripts\activate.bat"

REM 3. Dependencies (installed once; delete .venv\.installed to force a reinstall)
if not exist ".venv\.installed" (
  echo Installing dependencies. The first run can take a few minutes...
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo Dependency installation failed. Check the messages above.
    pause
    exit /b 1
  )
  echo ok> ".venv\.installed"
)

REM Self-heal a broken mistralai install (the "cannot import name 'Mistral'" case)
python -c "from mistralai import Mistral" 1>nul 2>nul
if errorlevel 1 (
  echo Repairing the mistralai package...
  python -m pip install --force-reinstall --no-cache-dir "mistralai>=1.0"
)

REM 4. Load MISTRAL_API_KEY from a local .env file if present
if exist ".env" (
  for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"
)
if "%MISTRAL_API_KEY%"=="" (
  echo.
  echo Note: MISTRAL_API_KEY is not set. Search works, but answer generation is disabled.
  echo To enable it, copy .env.example to .env and put your key in it.
  echo.
)

REM 5. Launch
echo Starting AskMyDocs...
streamlit run app.py

endlocal
