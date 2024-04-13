@echo off

set arg1=%1

cd /D "%~dp0"

python -m venv .venv

call .venv\Scripts\activate.bat
py -m pip install --upgrade pip
pip install -r requirements.txt

deactivate

IF NOT "%arg1%"=="dontpause" pause
