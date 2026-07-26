@echo off
REM ============================================================
REM  AskMyDocs - uninstall the local environment (Windows).
REM  Removes the Python virtual environment and caches.
REM  Your source code, documents and .env file are kept.
REM ============================================================

setlocal
cd /d "%~dp0"

echo This removes the local Python environment (.venv) and caches.
echo Your source code, documents and .env file are kept.
echo.
set /p CONFIRM="Continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
  echo Cancelled.
  pause
  exit /b 0
)

if exist ".venv" (
  echo Removing .venv...
  rmdir /s /q ".venv"
)
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo.
echo Done. The environment is removed. Double-click launch.bat to set it up again.
echo.
echo Downloaded models are cached in "%USERPROFILE%\.cache\huggingface".
echo Delete that folder too if you want to reclaim that disk space.
echo.
pause
endlocal
