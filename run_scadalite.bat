@echo off
echo Running SCADALite!

cd /d "%~dp0"

py -m scadalite.main

pause
