@echo off
setlocal

:: Define variables
set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.11.4/python-3.11.4.exe
set INSTALLER_NAME=python-installer.exe
set INSTALL_PATH=%USERPROFILE%\python

:: Download Python installer
echo Downloading Python installer...
powershell -Command "Invoke-WebRequest -Uri %PYTHON_INSTALLER_URL% -OutFile %INSTALLER_NAME%"

:: Install Python
echo Installing Python...
%INSTALLER_NAME% /quiet InstallAllUsers=1 PrependPath=1 TargetDir=%INSTALL_PATH%

:: Check if Python is installed and available
echo Verifying Python installation...
"%INSTALL_PATH%\python.exe" --version

:: Get current username
set USERNAME=%USERNAME%

:: Get full path to pythonw.exe
set PYTHONW_PATH=%INSTALL_PATH%\pythonw.exe

:: Create .bat file to launch DetectHomeButton.py
echo start "" "%PYTHONW_PATH%" "C:\XMBEmulator\config\DetectHomeButton\DetectHomeButton.py" > XMB_home_button.bat

:: Install pip packages
"%INSTALL_PATH%\python.exe" -m pip install --upgrade pip
"%INSTALL_PATH%\python.exe" -m pip install pywin32 --no-cache-dir
"%INSTALL_PATH%\python.exe" -m pip install pyautogui

echo.
echo Python installation and shortcut creation complete.
echo You can move XMB_home_button.bat to 'shell:common startup' to make the emulator overlay launch on startup.

endlocal
pause
