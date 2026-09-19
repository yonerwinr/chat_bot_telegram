@echo off
taskkill /f /im python.exe /fi "WINDOWTITLE eq TelegramMonitor*" 2>nul
taskkill /f /fi "IMAGENAME eq python.exe" 2>nul
echo Bot detenido correctamente.
pause
