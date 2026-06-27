# InsumosApp — Installation & User Guide

## System Requirements

| Requirement | Details |
|---|---|
| **Operating system** | Windows 10 or Windows 11 (64-bit) |
| **OneDrive** | Installed, running, and signed into your **a360inc** account |
| **SharePoint folders** | Synced locally via OneDrive (see below) |
| **Disk space** | ~500 MB for the application |
| **Permissions** | Admin rights required for installation |

---

## Required OneDrive / SharePoint Folders

The application reads inventory data directly from Excel files synced through OneDrive.  
These folders **must** exist on your machine **before** launching the app:

```
OneDrive - a360inc\
├── PTY Files - EQUIPOS\
│   └── Formato_Inventario_TI.xlsx      ← Used by "Equipos"
└── PTY Files - INSUMOS\
    └── Inventario_Insumos.xlsx         ← Used by "Insumos"
```

### How to verify the folders are present

1. Open **File Explorer**
2. Click **OneDrive – a360inc** in the left sidebar
3. Confirm you see both:
   - **PTY Files - EQUIPOS** with `Formato_Inventario_TI.xlsx`
   - **PTY Files - INSUMOS** with `Inventario_Insumos.xlsx`

If the folders are missing, ask your IT team to share the SharePoint document library with your OneDrive.

> **Important:** Files must be available **locally** (not cloud-only).  
> In OneDrive, right‑click each file → **Always keep on this device**.

---

## Installation

### Option A — Installer (recommended)

Double-click `InsumosApp_Setup_v1.0.0.exe` and follow the prompts:

1. **Welcome** → Next
2. **Destination Location** → Keep the default (`C:\Program Files\InsumosApp`) → Next
3. **Select Additional Tasks** → Check "Create a desktop shortcut" if desired → Next
4. **Ready to Install** → Install
5. **Completing the Setup Wizard** → Leave "Launch InsumosApp" checked → Finish

The application will start automatically after installation.

### Option B — Portable .exe (no install)

If you received only `launcher.exe`:

1. Move it to any folder (e.g., `C:\InsumosApp\`)
2. Double-click `launcher.exe` to run

No admin rights are needed for this option.

---

## First Launch

The first time you run the application, a **Setup Requirements** message will appear:

```
This application requires access to the following OneDrive/SharePoint folders:

    - PTY Files - EQUIPOS
    - PTY Files - INSUMOS

Please ensure:

    1. OneDrive is synchronized
    2. These folders exist in your OneDrive
    3. Files are available locally (not cloud-only)
```

- Read the message and click **OK**
- The app will check your OneDrive setup
- If everything is correct you will see the **launcher window** with two buttons:

  | Button | Opens |
  |---|---|
  | **Insumos** | Supply / materials inventory (PyQt5) |
  | **Equipos** | IT asset inventory (Tkinter) |

- If the required folders are missing, you will see:

  ```
  Required SharePoint folders not found.
  Please verify your OneDrive setup.
  ```

  → Click **OK**, fix your OneDrive sync, and launch the app again.

This message will **never appear again** on this computer.  
To see it again (e.g., after a reinstall), delete the file:

```
%LOCALAPPDATA%\InsumosApp\config.json
```

---

## Using the Application

### Launcher

The launcher window is the starting point. Click either:

- **Insumos** — opens the supplies inventory manager
- **Equipos** — opens the IT asset inventory manager

Each application runs in its own window. You can switch between them by launching again from the start menu or desktop shortcut.

### Login

Both sub‑apps require a user account:

- **Windows SSO** — if your Windows username matches a user in the system, you will be logged in automatically
- **Manual login** — enter your username and password

Ask your administrator for credentials if you do not have them.

---

## Common Issues

| Problem | Cause | Solution |
|---|---|---|
| "Required SharePoint folders not found" | OneDrive not synced or folders missing | Follow the steps under *Required OneDrive / SharePoint Folders* above |
| "Excel file not found" | OneDrive path is different on your machine | Contact your IT team to confirm the correct SharePoint library path |
| "File In Use" warning | Another user has the Excel file open | Wait a moment and try again, or click "Yes" to proceed anyway |
| App won't start | Missing Visual C++ runtime | Install the latest VC++ redistributable from Microsoft |

---

## Uninstalling

### If you used the installer

1. Open **Settings → Apps → Installed apps**
2. Find **InsumosApp**
3. Click **Uninstall**

This removes the program files. Your OneDrive data and first-run config are preserved.

### If you used the portable .exe

Simply delete `launcher.exe` and the folder you placed it in.

To reset the first-run message for a future reinstall, also delete:

```
%LOCALAPPDATA%\InsumosApp\config.json
```

---

## Updating

To update to a new version:

1. Uninstall the old version (see above)
2. Install the new version

Your OneDrive data and user credentials are stored separately and will not be affected.

---

## Build — Regenerar el Installer

### Prerrequisitos

| Herramienta | Propósito |
|---|---|
| **Python 3.10+** | Compilar el ejecutable |
| **PyInstaller** | Empaquetar la app (se instala con `pip install pyinstaller`) |
| **Inno Setup 6** | Crear el installer .exe (descargar de https://jrsoftware.org/isdl.php) |
| **Windows SDK** (opcional) | Firmar el ejecutable con `signtool.exe` (instalar "Windows 10 SDK" desde Visual Studio Installer) |
| **Certificado de firma** (opcional) | Certificate `.pfx` para firmar código y reducir falsos positivos de Defender |

### Paso 1 — Abrir PowerShell como Administrador

El installer requiere permisos de administrador. Abre **PowerShell** (no PowerShell ISE) como Administrador:

1. Presiona `Win + X` → **Terminal (Administrador)** o **Windows PowerShell (Administrador)**
2. Confirma el mensaje de UAC

### Paso 2 — Habilitar la ejecución de scripts (si está bloqueada)

Si al ejecutar el script ves el error:

```
No se puede cargar el archivo .\scripts\build.ps1 porque la ejecución de scripts está deshabilitada en este sistema.
```

Ejecuta este comando **una sola vez** (permite scripts locales):

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Responde **S** o **Y** cuando pregunte. Esto no afecta la seguridad del sistema — solo permite scripts que tú mismo crees.

Alternativa (no requiere cambiar la política permanentemente):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

### Paso 3 — Navegar a la carpeta del proyecto

```powershell
cd C:\inventory_final
```

### Paso 4 — Ejecutar el script de build

**Opción A — Build completo sin firma digital** (recomendado para pruebas):

```powershell
.\scripts\build.ps1
```

Esto ejecuta las 4 fases:
| Fase | Acción |
|---|---|
| **1. Build** | PyInstaller compila `launcher.py` → `dist\launcher\launcher.exe` + `_internal\` (DLLs, PYDs, datos). Usa `--onedir` (NO extrae a `%TEMP%`, evitando falsos positivos de Defender). |
| **2. Sign** | Se salta porque no se proporcionó certificado |
| **3. Stage** | Copia todo `dist\launcher\` a `release\staging\` |
| **4. Package** | Inno Setup compila el installer → `release\Inventory Manager_Setup_v1.0.0.exe` |

**Opción B — Build completo con firma digital** (recomendado para producción):

```powershell
.\scripts\build.ps1 -CertificatePath C:\ruta\al\certificado.pfx -CertificatePassword tu_password
```

**Opción C — Solo empaquetar (si ya compilaste antes):**

```powershell
.\scripts\build.ps1 -SkipBuild
```

Esto salta la compilación de PyInstaller y solo copia los archivos existentes en `dist\launcher\` al installer.

### Paso 5 — Verificar el resultado

El installer generado queda en:

```
release\Inventory Manager_Setup_v1.0.0.exe
```

### Solución de problemas

| Problema | Causa | Solución |
|---|---|---|
| `PyInstaller failed` | Falta una dependencia o hay un error de sintaxis | Revisa el output del comando. Ejecuta `pip install -r equipos\requirements.txt -r Insumos\inventory_app\requirements.txt` |
| `ISCC.exe not found` | Inno Setup no está instalado | Descarga e instala desde https://jrsoftware.org/isdl.php |
| `signtool.exe not found` | Windows SDK no instalado | Busca "Windows 10 SDK" en Visual Studio Installer o descarga independiente |
| Defender bloquea `launcher.exe` | Falso positivo por empaquetado | Usa `--onedir` (ya configurado), firma el ejecutable con un certificado EV, y reporta el falso positivo en https://www.microsoft.com/en-us/wdsi/filesubmission |

---

## Files Created by the App

| Location | Purpose |
|---|---|
| `%LOCALAPPDATA%\InsumosApp\config.json` | First-run marker (delete to re-trigger onboarding) |
| OneDrive SharePoint directories | Inventory Excel files and user database |
