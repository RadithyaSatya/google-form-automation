@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0venv-win\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  echo Python portable tidak ditemukan di venv-win\Scripts\python.exe
  echo Pastikan folder venv-win tersedia di project ini.
  pause
  exit /b 1
)

"%PYTHON_EXE%" formfiller_gui.py
endlocal
