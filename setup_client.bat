@echo off
:: setup_client.bat -- Windows setup for the Hexapod robot client
:: Run from the repository root: setup_client.bat
:: Double-click or run from a Command Prompt / PowerShell window.

setlocal EnableDelayedExpansion

:: ── ANSI colours (Windows 10+ Command Prompt / Windows Terminal) ──────────────
for /f "delims=" %%E in ('echo prompt $E^| cmd /Q /D /A') do set "ESC=%%E"
set "GREEN=!ESC![32m"
set "CYAN=!ESC![36m"
set "YELLOW=!ESC![33m"
set "RED=!ESC![31m"
set "NC=!ESC![0m"

set IMPORT_ERRORS=0

:: ── Banner ────────────────────────────────────────────────────────────────────
echo.
echo !CYAN!================================================!NC!
echo !CYAN!  Freenove Hexapod -- Client Setup (Windows)   !NC!
echo !CYAN!================================================!NC!
echo.

:: ── Detect Python ─────────────────────────────────────────────────────────────
:: NOTE: goto inside nested if blocks is a CMD bug -- all gotos are top-level here
echo !CYAN![--]!NC! Detecting Python installation...

python --version >nul 2>&1
if errorlevel 1 goto :try_py_launcher

for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYVER=%%V
python -c "import sys; sys.exit(0 if sys.version_info.major==3 else 1)" >nul 2>&1
if errorlevel 1 goto :try_py_launcher

set PYTHON=python
echo !GREEN![OK]!NC!  Found: python !PYVER!
goto :python_found

:try_py_launcher
py -3 --version >nul 2>&1
if errorlevel 1 goto :no_python

for /f "tokens=2" %%V in ('py -3 --version 2^>^&1') do set PYVER=%%V
set PYTHON=py -3
echo !GREEN![OK]!NC!  Found: py -3 !PYVER!
goto :python_found

:no_python
echo !RED![FAIL]!NC! Python 3 not found.
echo.
echo        Install Python 3 from: https://www.python.org/downloads/
echo        Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:python_found

:: ── Upgrade pip ───────────────────────────────────────────────────────────────
echo !CYAN![--]!NC! Upgrading pip...
%PYTHON% -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo !YELLOW![!!]!NC!  pip upgrade failed -- continuing anyway
) else (
    echo !GREEN![OK]!NC!  pip upgraded
)

:: ── PyQt5 ─────────────────────────────────────────────────────────────────────
echo !CYAN![--]!NC! Installing PyQt5...
%PYTHON% -m pip install PyQt5 --quiet
if errorlevel 1 (
    echo !RED![FAIL]!NC! PyQt5 install failed
    set /a IMPORT_ERRORS+=1
) else (
    echo !GREEN![OK]!NC!  PyQt5 installed
)

:: ── Pillow ────────────────────────────────────────────────────────────────────
echo !CYAN![--]!NC! Installing Pillow...
%PYTHON% -m pip install Pillow --quiet
if errorlevel 1 (
    echo !RED![FAIL]!NC! Pillow install failed
    set /a IMPORT_ERRORS+=1
) else (
    echo !GREEN![OK]!NC!  Pillow installed
)

:: ── numpy ─────────────────────────────────────────────────────────────────────
echo !CYAN![--]!NC! Installing numpy...
%PYTHON% -m pip install numpy --quiet
if errorlevel 1 (
    echo !RED![FAIL]!NC! numpy install failed
    set /a IMPORT_ERRORS+=1
) else (
    echo !GREEN![OK]!NC!  numpy installed
)

:: ── OpenCV ────────────────────────────────────────────────────────────────────
echo !CYAN![--]!NC! Installing OpenCV...
%PYTHON% -m pip install opencv-python --quiet
if errorlevel 1 (
    echo !RED![FAIL]!NC! opencv-python install failed
    set /a IMPORT_ERRORS+=1
    goto :opencv_done
)
%PYTHON% -m pip install opencv-contrib-python --quiet
if errorlevel 1 (
    echo !YELLOW![!!]!NC!  opencv-contrib-python failed ^(face recognition may not work^)
) else (
    echo !GREEN![OK]!NC!  OpenCV installed
)
:opencv_done

:: ── IP.txt ────────────────────────────────────────────────────────────────────
set IP_FILE=%~dp0Code\Client\IP.txt

set CURRENT_IP=
if exist "%IP_FILE%" (
    for /f "usebackq tokens=*" %%L in ("%IP_FILE%") do (
        if not defined CURRENT_IP set CURRENT_IP=%%L
    )
)

if not defined CURRENT_IP (
    echo.
    echo !YELLOW![!!]!NC!  Code\Client\IP.txt is empty or missing.
    echo.
    set /p ROBOT_IP="        Enter your Raspberry Pi's IP address (or press Enter to skip): "
    if defined ROBOT_IP (
        echo !ROBOT_IP!> "%IP_FILE%"
        echo !GREEN![OK]!NC!  Saved !ROBOT_IP! to Code\Client\IP.txt
    ) else (
        echo 192.168.1.100> "%IP_FILE%"
        echo !YELLOW![!!]!NC!  Used placeholder 192.168.1.100 -- edit Code\Client\IP.txt before connecting
    )
) else (
    echo !GREEN![OK]!NC!  Code\Client\IP.txt already set to: !CURRENT_IP!
)

:: ── Verify imports ────────────────────────────────────────────────────────────
echo.
echo !CYAN![--]!NC! Verifying Python imports...

call :check_import PyQt5
call :check_import PIL
call :check_import cv2
call :check_import numpy

:: ── Done ──────────────────────────────────────────────────────────────────────
echo.
echo !CYAN!================================================!NC!
if %IMPORT_ERRORS% equ 0 (
    echo !GREEN!  All dependencies installed successfully!!NC!
    echo.
    echo !GREEN!  To launch the client:!NC!
    echo !GREEN!    cd Code\Client!NC!
    echo !GREEN!    python Main.py!NC!
) else (
    echo !YELLOW!  Setup finished with %IMPORT_ERRORS% missing import^(s^).!NC!
    echo !YELLOW!  Check warnings above and re-run if needed.!NC!
)
echo !CYAN!================================================!NC!
echo.
pause
exit /b %IMPORT_ERRORS%

:: ── Subroutine: check a single Python import ──────────────────────────────────
:check_import
%PYTHON% -c "import %~1" >nul 2>&1
if errorlevel 1 (
    echo !YELLOW![!!]!NC!    import %~1 -- NOT FOUND
    set /a IMPORT_ERRORS+=1
) else (
    echo !GREEN![OK]!NC!    import %~1
)
exit /b 0
