@echo off
SET APP_PATH=C:\FoodFlow
SET SCRIPT=%APP_PATH%\Sync\sync_script.py

echo === Ejecutando Sync Script ===
python "%SCRIPT%"

pause