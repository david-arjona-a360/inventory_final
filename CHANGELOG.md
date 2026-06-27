# Changelog

# Inventory Manager — Inventory Manager

> **Current version: v1.1.0 — Proveedor & Cant. Minima**
> Verified: Insumos Excel modified, data loading extended, Treeview columns added, save logic updated.

## 2026-06-26 — Proveedor & Cant. Minima Columns

### Added
- **"Proveedor" column (F)** in `Inventario_Insumos.xlsx` — inserted immediately after "Categoria" via header-based detection.
- **"Cant. Minima" column (G)** in `Inventario_Insumos.xlsx` — inserted alongside Proveedor, with empty default for existing rows.
- **Excel column auto-creation** — if columns are missing on open, they are created safely without duplicating or overwriting existing data.
- **Data loading layer** extended to read both new columns using header-based mapping (not fragile indices).
- **Treeview columns** in the Insumos UI — added "Proveedor" and "Cant. Minima" with consistent width, alignment, and editable behavior matching existing fields.
- **Save/update logic** modified to write into columns F and G while preserving row integrity and avoiding overwrites of adjacent columns.
- **Runtime path validation** — app now reads/writes directly to the OneDrive Excel path (`PTY Files - INSUMOS\Inventario_Insumos.xlsx`) and rejects `_MEIPASS` local temp copies.

### Changed
- `Insumos/inventory_app/services/excel_service.py` — column insertion logic, header validation, and write mapping.
- `Insumos/inventory_app/ui/inventory_view.py` — Treeview column definitions, cell editing, and display formatting.
- `Insumos/inventory_app/services/report_service.py` — report generation to include new columns if applicable.

## 2026-06-24 — Dependency Stabilization & Packaging Fix

### Fixed
- **Insumos crash after install** (`launcher.spec`): Removed `unittest` from PyInstaller excludes. fpdf2's `fpdf/sign.py:16` unconditionally imports `from unittest.mock import patch`, which failed in packaged builds because `unittest` was excluded. This was the root cause of `ModuleNotFoundError: No module named 'unittest'` in Insumos after installation.
- **File lock detection** (`Insumos/inventory_app/utils/excel_utils.py`): Replaced `msvcrt.locking()` with `~$filename.xlsx` lock-file detection (matching Equipos' approach). Eliminated `msvcrt` C-extension dependency that PyInstaller does not bundle since the code lives inside a `datas` directory and is never scanned.
- **Hidden imports** (`launcher.spec`): Added `openpyxl.styles` and `openpyxl.utils` — Insumos imports from these submodules, but they were not in the hidden imports list.
- **Unsafe excludes removed** (`launcher.spec`): `email` and `http` removed from excludes. These can break transitive dependencies (`urllib.request` needs `http.client`).

### Why Copying Code Failed
The error was not in any application `.py` file — it was in fpdf2's library code (`fpdf/sign.py:16`). Equipos does not use fpdf2, so it never triggered the `unittest` dependency. Copying Equipos' application code into Insumos could not fix this because the dependency originates in a third-party library only Insumos uses.

## 2026-06-24 — Codebase Audit & Cleanup

### Fixed
- **Launcher subprocess dispatch** (`launcher.py:128`): Buttons now pass `launcher.py` as script argument before the flag in dev mode. Previously `python --app-equipos` was interpreted as a Python flag; now runs as `python launcher.py --app-equipos`.
- **Unused imports removed**:
  - `excel_service.py`: Removed dead `safe_copy_for_reading` import
  - `login_dialog.py` / `main_window.py`: Removed unused `LOGO_WIDTH` import

### Cleaned
- `build/` — PyInstaller build artifacts (regenerated on build)
- `dist/` — Empty artifact directory
- `Insumos/inventory_app/models/` — Empty package, never referenced
- `Insumos/inventory_app/styles/` — `colors.py` had zero consumers
- `Insumos/inventory_app/run.bat` — Unreferenced convenience script
- `equipos/inv_icon.jpg`, `equipos/installer.png` — Unreferenced files

### Removed
- `cx_freeze` from `equipos/requirements.txt` — unused dependency

## Project Structure After Cleanup

```
inventory_final/
  launcher.py           # Main entry point / launcher window
  launcher.spec         # PyInstaller spec
  path_config.py        # Shared OneDrive path resolution
  onboarding.py         # First-run setup wizard
  Theme/
    theme.py            # Shared color constants & logo path
    logo.jpg / app_icon.ico / installer_icon.ico
  equipos/              # IT Equipment app (Tkinter)
    inventory_app.py    # main() entry point
    config.py / excel_client.py / auth_manager.py
    users.json
  Insumos/
    config.json
    inventory_app/      # Supplies app (PyQt5)
      main.py           # main() entry point
      config/ / services/ / ui/ / utils/
  scripts/
    build.ps1           # PyInstaller + Inno Setup build pipeline
    setup.iss           # Inno Setup installer script
```

## How to Use (Source Distribution)

```powershell
# 1. Install dependencies
pip install -r equipos/requirements.txt -r Insumos/inventory_app/requirements.txt

# 2. Run
python launcher.py
# or double-click run.bat
```

## How to Build Executable

```powershell
# Admin PowerShell
.\scripts\build.ps1
```

## Notes

- This codebase is **stable and tested** as of 2026-06-24.
- Source distribution (`.py` files + `run.bat`) avoids all Windows Defender false positives.
- The `launcher.spec` is tuned with `--onedir`, expanded exclusions, and embedded version metadata for reduced heuristic scoring when building an `.exe`.
