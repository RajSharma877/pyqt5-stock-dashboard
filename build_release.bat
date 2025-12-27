@echo off
echo ===================================================
echo     Building StockDashboard (RELEASE MODE)
echo ===================================================

REM Activate virtual environment
call ..\venv\Scripts\activate

REM Clean previous builds
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.spec del *.spec

echo Running PyInstaller...
REM Note: --windowed is enabled (no console)
REM --collect-all "prophet" ensures all data files are included
pyinstaller main.py ^
    --name "StockDashboard" ^
    --onedir ^
    --windowed ^
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
echo 1. Go to "dist\StockDashboard"
echo 2. COPY your .env file there!
echo 3. Zip the "StockDashboard" folder to share with your friend.
pause
