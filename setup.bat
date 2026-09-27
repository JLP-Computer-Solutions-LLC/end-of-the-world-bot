@echo off
REM SPDX-License-Identifier: GPL-3.0-only
REM Windows setup wrapper for End of the World Bot
REM This calls the Python setup scripts which work cross-platform.

set PYTHON=python
where python >nul 2>nul || set PYTHON=python3
where %PYTHON% >nul 2>nul || (
    echo ERROR: Python 3.11+ not found in PATH.
    echo Please install Python from https://python.org or use a WSL Linux terminal.
    exit /b 1
)

%PYTHON% -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)" || (
    echo ERROR: Python 3.11+ required. Found:
    %PYTHON% --version
    exit /b 1
)

echo Using %PYTHON% (%PYTHON% --version)

if "%1"=="" (
    echo.
    echo End of the World Bot - Windows Setup
    echo ====================================
    echo.
    echo Usage:
    echo   setup.bat install [DESTINATION]     - Install to a new folder
    echo   setup.bat model                     - Guided Ollama model setup
    echo   setup.bat doctor                    - Check prerequisites
    echo   setup.bat index                     - Index library documents
    echo   setup.bat search "query"            - Search library
    echo   setup.bat ask "question" --model M  - Ask with local model
    echo   setup.bat manuals [--fetch]         - Download manuals (--fetch to download)
    echo.
    echo Examples:
    echo   setup.bat install "C:\Users\%USERNAME%\EndOfWorldBot"
    echo   setup.bat model
    echo   setup.bat search "emergency supplies"
    echo   setup.bat ask "Where are beacon batteries?" --model llama3.2:3b
    echo.
    echo For manual downloads, run from the installed folder:
    echo   cd "C:\Users\%USERNAME%\EndOfWorldBot"
    echo   setup.bat manuals --fetch
    exit /b 0
)

if "%1"=="install" (
    if "%2"=="" (
        echo ERROR: install requires a destination path
        echo Usage: setup.bat install "C:\path\to\new\folder"
        exit /b 1
    )
    %PYTHON% -I -B bootstrap.py --dest "%~2" %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

if "%1"=="model" (
    %PYTHON% -I -B setup_model.py %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

if "%1"=="doctor" (
    %PYTHON% -I -B portable.py doctor %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

if "%1"=="index" (
    %PYTHON% -I -B portable.py index %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

if "%1"=="search" (
    %PYTHON% -I -B portable.py search %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

if "%1"=="ask" (
    %PYTHON% -I -B portable.py ask %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

if "%1"=="manuals" (
    %PYTHON% -I -B download_manuals.py %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

echo Unknown command: %1
echo Run "setup.bat" without arguments for usage.
exit /b 1