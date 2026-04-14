@echo off
REM Startup script for nuts_vision web interface (Windows)

echo ==========================================
echo nuts_vision - Web Interface Launcher
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Checking dependencies...
pip install -q --timeout 30 -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo Dependencies ready
) else (
    echo WARNING: Failed to install dependencies ^(check your network connection^)
    echo If packages are already installed, the app may still work.
    echo Run: pip install -r requirements.txt
)
echo.

REM Set environment variables if .env exists
if exist ".env" (
    echo Loading environment variables from .env...
    for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a
    echo Environment loaded
) else (
    echo No .env file found, using defaults
    echo Create a .env file based on .env.example for custom configuration
)
echo.

REM Set default port if not configured
if not defined STREAMLIT_PORT set STREAMLIT_PORT=8501

REM Check if the port is available, try up to 10 consecutive ports
set /a MAX_ATTEMPTS=10
set /a ATTEMPT=0

:check_port
netstat -aon 2>nul | findstr /R ":%STREAMLIT_PORT% " | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Port %STREAMLIT_PORT% is in use, trying next port...
    set /a STREAMLIT_PORT+=1
    set /a ATTEMPT+=1
    if %ATTEMPT% LSS %MAX_ATTEMPTS% goto check_port
    echo ERROR: Could not find an available port after %MAX_ATTEMPTS% attempts.
    echo Please free port 8501 or set STREAMLIT_PORT in your .env file.
    pause
    exit /b 1
)

REM Launch Streamlit app
echo ==========================================
echo Starting nuts_vision Web Interface...
echo ==========================================
echo.
echo The application will open in your browser at:
echo http://localhost:%STREAMLIT_PORT%
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py --server.port %STREAMLIT_PORT% --server.address localhost

pause
