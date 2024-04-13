@echo off

cd /D "%~dp0"

call cleanup_compile.bat
call cleanup_venv.bat

cd ..

if EXIST Palworld-Palbox-Slot-Injector-Release rmdir /S /Q "%~dp0..\Palworld-Palbox-Slot-Injector-Release"

mkdir "%~dp0..\Palworld-Palbox-Slot-Injector-Release"

robocopy "%~dp0..\Palworld-Palbox-Slot-Injector" "%~dp0..\Palworld-Palbox-Slot-Injector-Release\source" /E

cd "Palworld-Palbox-Slot-Injector-Release"
cd "source"

if EXIST ".git" rmdir /S /Q ".git"
rem if EXIST "create_palbox_slot_injector_release.bat" del /S /Q "create_palbox_slot_injector_release.bat"

call cleanup_compile.bat
call cleanup_venv.bat

7z.exe a "%~dp0..\Palworld-Palbox-Slot-Injector-Release\Palworld-Palbox-Slot-Injector-Source.zip" "%~dp0..\Palworld-Palbox-Slot-Injector-Release\source\*"

mkdir "%~dp0..\Palworld-Palbox-Slot-Injector-Release\Palworld-Palbox-Slot-Injector"
mkdir "%~dp0..\Palworld-Palbox-Slot-Injector-Release\Palworld-Palbox-Slot-Injector\source"

robocopy "%~dp0..\Palworld-Palbox-Slot-Injector-Release\source" "%~dp0..\Palworld-Palbox-Slot-Injector-Release\Palworld-Palbox-Slot-Injector\source" /E

call "%~dp0..\Palworld-Palbox-Slot-Injector-Release\source\compile_exe.bat" dontpause

robocopy "%~dp0..\Palworld-Palbox-Slot-Injector-Release\source\dist" "%~dp0..\Palworld-Palbox-Slot-Injector-Release\Palworld-Palbox-Slot-Injector" /E

7z.exe a "%~dp0..\Palworld-Palbox-Slot-Injector-Release\Palworld-Palbox-Slot-Injector.zip" "%~dp0..\Palworld-Palbox-Slot-Injector-Release\Palworld-Palbox-Slot-Injector\*"
