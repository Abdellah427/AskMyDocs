@echo off
REM Launch AskMyDocs locally on Windows.
REM Creates a virtual environment, installs dependencies, then starts the app.

setlocal
cd /d "%~dp0"

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt

REM Load MISTRAL_API_KEY from a local .env file if present.
if exist ".env" (
  for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"
)

if "%MISTRAL_API_KEY%"=="" (
  echo Warning: MISTRAL_API_KEY is not set. Copy .env.example to .env and add your key to enable answers.
)

echo Starting AskMyDocs...
streamlit run app.py

endlocal
