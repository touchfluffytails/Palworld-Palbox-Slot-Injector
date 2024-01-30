@echo off

cd /D "%~dp0"

python inject_box_slots.py %~1

pause
