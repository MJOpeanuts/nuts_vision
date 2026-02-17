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
pip install -q -r requirements.txt
echo Dependencies ready
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

REM Launch Streamlit app
echo ==========================================
echo Starting nuts_vision Web Interface...
echo ==========================================
echo.
echo The application will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py --server.port 8501 --server.address localhost

pause
