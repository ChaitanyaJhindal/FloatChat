@echo off
echo Starting Ocean Data Explorer Dashboard...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if streamlit is installed
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install packages
        pause
        exit /b 1
    )
)

echo Launching dashboard...
echo Open your browser and go to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run ocean_data_dashboard.py