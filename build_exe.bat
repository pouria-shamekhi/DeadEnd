@echo off
echo Installing dependencies...
pip install pyinstaller PyQt5 PyQt5-Qt5 PyQt5-sip

echo Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo Building with spec file...
pyinstaller DeadEnd.spec

echo.
if exist "dist\DeadEnd\DeadEnd.exe" (
    echo SUCCESS! File is at: dist\DeadEnd\DeadEnd.exe
) else (
    echo Build may have failed. Check output above.
)
pause
