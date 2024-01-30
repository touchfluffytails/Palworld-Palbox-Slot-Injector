@echo off

cd /D "%~dp0"

python inject_box_slots_full.py %~1

pause
