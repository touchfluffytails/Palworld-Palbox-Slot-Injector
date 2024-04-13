@echo off

set arg1=%1

cd /D "%~dp0"

python -m venv .compile

call .compile\Scripts\activate.bat

py -m pip install --upgrade pip
pip install --upgrade poetry
poetry install --with dev

call poetry shell
pyinstaller .\inject_box_slots.spec

deactivate

IF NOT "%arg1%"=="dontpause" pause
