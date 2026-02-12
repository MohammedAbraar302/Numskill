@echo off
REM NumSkillsPro Setup Script for Windows

echo.
echo ================================
echo NumSkillsPro Setup Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Python found! Installing dependencies...
echo.

REM Install dependencies
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [2/3] Dependencies installed successfully!
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo [3/3] Creating .env file...
    (
        echo FLASK_ENV=development
        echo DEBUG=True
        echo DATABASE_URL=sqlite:///numskill.db
        echo JWT_SECRET_KEY=your-super-secret-key-change-in-production-12345
    ) > .env
    echo .env file created!
) else (
    echo [3/3] .env file already exists. Skipping creation.
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To start the server, run:
echo   python app.py
echo.
echo Then open your browser to:
echo   http://localhost:5000
echo.
echo Press any key to exit...
pause >nul
