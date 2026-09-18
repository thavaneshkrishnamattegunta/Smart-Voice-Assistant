@echo off
cd /d "%~dp0"
setlocal

REM Load .env if present
for /f "usebackq delims== tokens=1,2" %%A in (".env") do (
  if not "%%A"=="" if not "%%A:~0,1"=="#" set "%%A=%%B"
)

if "%GEMINI_API_KEY%"=="" echo Gemini API key is not configured. Local commands will still work.

python main.py
