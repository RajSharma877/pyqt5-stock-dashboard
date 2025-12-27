@echo off
echo ===================================================
echo     Building StockDashboard (DEBUG MODE)
echo ===================================================

REM Activate virtual environment
call ..\venv\Scripts\activate

REM Clean previous builds
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.spec del *.spec

REM Run PyInstaller in CONSOLE mode (removing --windowed)
REM This ensures we can see the error message when the app crashes
echo Running PyInstaller...
pyinstaller main.py ^
    --name "StockDashboard_Debug" ^
    --onedir ^
    --console ^
    --add-data "csv_data_files;csv_data_files" ^
    --collect-all "prophet" ^
    --collect-all "cmdstanpy" ^
    --hidden-import "pandas" ^
    --hidden-import "pyarrow" ^
    --hidden-import "sklearn.neighbors.typedefs" ^
    --hidden-import "sklearn.neighbors.quad_tree" ^
    --hidden-import "sklearn.tree._utils" ^
    --clean ^
    --noconfirm

echo.
echo ===================================================
echo     Build Complete! 
echo ===================================================
echo.
echo Please copy your .env file to dist\StockDashboard_Debug\
echo And then run the executable from the terminal to see the error.
pause
