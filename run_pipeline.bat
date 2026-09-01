@echo off
chcp 65001 >nul
echo ============================================================
echo   Starting CV Pipeline (CMD version)
echo ============================================================
echo.

"C:\Users\FlyUp Travel\PythonPortable\python.exe" pipeline.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   ❌ Pipeline encountered an error. Check the output above.
    echo ============================================================
    pause
    exit /b 1
) else (
    echo.
    echo ============================================================
    echo   ✅ All done! Press any key to open the output folder...
    echo ============================================================
    pause >nul
    start "" "C:\Users\FlyUp Travel\Desktop\Python Job Applications\applications_ai_optimized"
    exit /b 0
)