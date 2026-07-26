@echo off
REM ============================================================
REM  AskMyDocs - one-click launcher for Windows.
REM  Just double-click this file. It checks Python, sets up the
REM  environment, repairs it if needed, runs a self-test, and
REM  only then starts the app.
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

REM 1. Python present?
where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo Python was not found. Install Python 3.10+ from https://www.python.org/downloads/
  echo and tick "Add Python to PATH" during setup, then double-click this file again.
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

REM 3. First-time dependency install
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

REM 4. Self-test, with one automatic repair attempt
echo Checking the installation...
python selftest.py
if not errorlevel 1 goto launch

echo.
echo Some checks failed. Attempting an automatic repair...
python -m pip install --upgrade -r requirements.txt
python -c "from mistralai import Mistral" 1>nul 2>nul
if errorlevel 1 (
  echo Reinstalling mistralai...
  python -m pip uninstall -y mistralai
  python -m pip install --no-cache-dir "mistralai>=1.0"
)
echo Re-checking...
python selftest.py
if not errorlevel 1 goto launch

echo.
echo Automatic repair could not fix everything. See the messages above.
pause
exit /b 1

:launch
REM 5. Load MISTRAL_API_KEY from .env if present (the app also reads it itself)
if exist ".env" (
  for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"
)
if "%MISTRAL_API_KEY%"=="" (
  echo.
  echo Note: MISTRAL_API_KEY is not set. Search works, but answer generation is disabled.
  echo To enable it, copy .env.example to .env and put your key in it.
  echo.
)

echo Starting AskMyDocs... it will open at http://localhost:8501
streamlit run app.py

endlocal
