@echo off

cd /D "%~dp0"

if not exist .venv call setup_venv.bat dontpause
clear

call .venv\Scripts\activate.bat
python inject_box_slots.py -ui

deactivate
pause
