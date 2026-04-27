@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=%~dp0venv-win\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

echo Installing build dependency...
"%PYTHON_EXE%" -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

echo Building CLI executable...
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean --onefile --name playwright_form_filler playwright_form_filler.py
if errorlevel 1 exit /b 1

echo Building GUI executable...
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean --windowed --onedir --name formfiller_gui --add-data "playwright_form_filler.py;." formfiller_gui.py
if errorlevel 1 exit /b 1

echo Copying CLI executable into GUI bundle...
copy /Y "dist\playwright_form_filler.exe" "dist\formfiller_gui\playwright_form_filler.exe" >nul

echo Done. GUI bundle tersedia di dist\formfiller_gui\
echo Jalankan formfiller_gui.exe dari folder tersebut.
endlocal
