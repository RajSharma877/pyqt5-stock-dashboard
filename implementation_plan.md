# Fix Prophet Missing Files in PyInstaller

## Problem
The `prophet` library relies on internal data files (specifically `__version__.py` and others) that PyInstaller does not detect automatically. This causes a `FileNotFoundError` at runtime.

## Proposed Solution
Use the `--collect-all` flag provided by PyInstaller. This flag instructs PyInstaller to collect:
1.  All source code (submodules)
2.  All data files
3.  All binaries
...for the specified package.

## Changes

### [MODIFY] [build_debug.bat](file:///c:/Users/Raj%20Sharma/OneDrive/Documents/Next%20JS%20projects/pyqt_projects/dashboard_app/build_debug.bat)
- Add `--collect-all "prophet"` to the PyInstaller command.
- Add `--collect-all "cmdstanpy"` (Prophet dependency) just in case.
- Keep console mode for debugging.

### [MODIFY] [PACKAGING_INSTRUCTIONS.md](file:///c:/Users/Raj%20Sharma/OneDrive/Documents/Next%20JS%20projects/pyqt_projects/dashboard_app/PACKAGING_INSTRUCTIONS.md)
- Update the main packaging command to include `--collect-all "prophet"` so the final windowed build also works.

## Verification
1.  User runs `build_debug.bat`.
2.  User runs the resulting executable.
3.  The app should launch without the `FileNotFoundError`.
