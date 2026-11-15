

@echo off
cd /d "%~dp0"

echo Starting URL Shortener API on port 8001...

call .venv\Scripts\activate.bat

python -m uvicorn main:app --reload --port 8001

pause

