@echo off
REM SPDX-License-Identifier: GPL-3.0-only
REM Windows launch wrapper for End of the World Bot
REM This calls the Python portable.py which works cross-platform.

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

REM Pass all arguments to portable.py
%PYTHON% -I -B portable.py %*
exit /b %ERRORLEVEL%