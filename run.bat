@echo off
REM NumSkillsPro Application Launcher

echo Starting NumSkillsPro Flask Server...
echo.
echo The server will be available at: http://localhost:5000
echo.
echo To open the application:
echo 1. Open your file explorer
echo 2. Navigate to this folder
echo 3. Open index.html in your browser
echo.
echo Or serve it with Python:
echo python -m http.server 8000
echo Then open http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
pause
