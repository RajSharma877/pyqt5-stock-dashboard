# Packaging Instructions for Pyqt5 Dashboard App

This guide details how to package your `dashboard_app` into a standalone executable using `PyInstaller`.

## Prerequisites

1.  **Activate Virtual Environment**:
    Ensure you are in the project root (`Pyqt projects`) and activate the venv:
    ```powershell
    .\venv\Scripts\activate
    ```
    *Verify activation: Your prompt should show `(venv)`.*

2.  **Install PyInstaller**:
    ```powershell
    pip install pyinstaller
    ```

## Packaging Command

Run the following command from the `dashboard_app` directory:

```powershell
# Navigate to the app directory if not already there
cd dashboard_app

# Run PyInstaller
pyinstaller main.py --name "StockDashboard" --onedir --windowed --add-data "csv_data_files;csv_data_files" --collect-all "prophet" --collect-all "cmdstanpy" --hidden-import "pandas" --hidden-import "sklearn.neighbors.typedefs" --hidden-import "sklearn.neighbors.quad_tree" --hidden-import "sklearn.tree._utils" --clean --noconfirm
```

### Explanation of Arguments:
- `--name "StockDashboard"`: Name of the output executable.
- `--onedir`: Create a directory containing the executable (easier for debugging than `--onefile`).
- `--windowed`: Don't show a command prompt window when the app runs.
- `--add-data "csv_data_files;csv_data_files"`: Include the CSV data folder.
- `--hidden-import ...`: Force PyInstaller to include Prophet and Sklearn dependencies that are often missed.

## Verification

1.  Go to `dashboard_app/dist/StockDashboard`.
2.  **CRITICAL**: Copy your `.env` file from `dashboard_app` to this folder. The executable needs it to access `GROQ_API_KEY`.
3.  Run `StockDashboard.exe`.

## Troubleshooting

- **Prophet Issues**: If the charts or forecast don't work, it's likely a Prophet dependency issue. The hidden imports above usually fix this.
- **Missing Files**: Check if `csv_data_files` is present in `dist/StockDashboard/_internal` or the root of the dist folder.
