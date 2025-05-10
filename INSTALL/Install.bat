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
"%INSTALL_PATH%\Scripts\python.exe" --version

:: Get current username dynamically
set USERNAME=%USERNAME%

:: Create the shortcut in Startup folder using cmd
echo Creating shortcut in Startup folder...

:: Define shortcut path
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_NAME=DetectHomeButton.lnk
set SCRIPT_PATH=C:\EmulatorOverlay\config\DetectHomeButton\DetectHomeButton.pyw

:: Create shortcut using cmd (via Windows Script Host)
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut("%STARTUP_FOLDER%\%SHORTCUT_NAME%") >> CreateShortcut.vbs
echo oLink.TargetPath="C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\pythonw.exe" >> CreateShortcut.vbs
echo oLink.Arguments="%SCRIPT_PATH%" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

:: Run the VBScript to create the shortcut
cscript //nologo CreateShortcut.vbs

::create .bat
echo start "" "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\pythonw.exe" "C:\XMBEmulator\config\DetectHomeButton\DetectHomeButton.py" > XMB_home_button.bat

:: Do not delete the Python installer
:: Clean up temporary files skipped
python.exe -m pip install --upgrade pip
pip install pywin32 --no-cache-dir
pip install pyautogui

echo Python installation and shortcut creation complete.
echo You can move XMBEmulator_detect_home_button.bat to 'shell:common startup' to make the emulator overlay launch on startup.
endlocal
pause
