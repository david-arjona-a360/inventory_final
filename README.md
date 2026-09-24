# Sistema de Inventario — Inventory Manager

Aplicacion de escritorio interna de **a360inc (Panama)** para gestionar el inventario de la compania.
Desktop app used internally by **a360inc (Panama)** to manage the company's inventory.

---

## ES — En que consiste el proyecto

**Sistema de Inventario** es una aplicacion de escritorio para Windows que permite registrar, consultar y administrar el inventario de la organizacion. La informacion se lee y se escribe directamente sobre archivos de Excel sincronizados por **OneDrive/SharePoint**, de modo que todo el equipo comparte las mismas tablas.

### Modulos de la aplicacion

El launcher principal (`launcher.exe`) abre dos aplicaciones:

| Boton | Modulo | Descripcion |
|---|---|---|
| **Insumos** | `insumos/` (PyQt5) | Inventario de insumos / materiales de consumo (Excel: `Inventario_Insumos.xlsx`) |
| **Equipos** | `equipos/` (Tkinter) | Inventario de equipos y activos de TI (Excel: `Formato_Inventario_TI.xlsx`) |

### Caracteristicas principales

- Autenticacion por **Windows SSO** (login automatico) o credenciales manuales
- Gestion de usuarios, roles y contrasenas
- Altas, bajas y modificaciones de items del inventario
- Busqueda y filtrado de registros
- Generacion de reportes / exportacion
- Interfaz visual moderna con temas compartidos
- Instalador (Inno Setup): `release\InventoryManager-1.0.0-Setup.exe`

### Stack tecnologico

- **Python 3.10+** con **PyQt5** y **Tkinter**
- **PyInstaller** (`launcher.spec`) para empaquetar el ejecutable
- **Inno Setup 6** (`installer.iss`) para generar el instalador
- **OneDrive/SharePoint** como almacenamiento de los archivos de inventario

### Requisitos para correr la app

| Requisito | Detalle |
|---|---|
| Sistema operativo | Windows 10 / 11 (64-bit) |
| OneDrive | Instalado, iniciado con cuenta **a360inc** |
| SharePoint | Carpetas `PTY Files - EQUIPOS` y `PTY Files - INSUMOS` sincronizadas localmente |

> Ver `notes.md` para la guia de instalacion, uso y solucion de problemas.

### Compilar / generar el instalador

```powershell
.\scripts\build.ps1
```

El instalador se genera en `release\`. Ver seccion "Build" en `notes.md`.

---

## EN — What the project is for

**Inventory Manager** is a Windows desktop application to register, view, and manage the organization's inventory. All data is read from and written to Excel files synced via **OneDrive/SharePoint**, so the whole team shares the same source of truth.

### Application modules

The main launcher (`launcher.exe`) opens two apps:

| Button | Module | Description |
|---|---|---|
| **Insumos** | `insumos/` (PyQt5) | Supplies / consumables inventory (Excel: `Inventario_Insumos.xlsx`) |
| **Equipos** | `equipos/` (Tkinter) | IT equipment and asset inventory (Excel: `Formato_Inventario_TI.xlsx`) |

### Main features

- **Windows SSO** authentication (automatic login) or manual credentials
- User, role, and password management
- Add, edit, and remove inventory items
- Search and filter records
- Report generation / export
- Modern shared UI theme
- Installer (Inno Setup): `release\InventoryManager-1.0.0-Setup.exe`

### Tech stack

- **Python 3.10+** with **PyQt5** and **Tkinter**
- **PyInstaller** (`launcher.spec`) to bundle the executable
- **Inno Setup 6** (`installer.iss`) to build the installer
- **OneDrive/SharePoint** as the storage for the inventory files

### Requirements to run the app

| Requirement | Detail |
|---|---|
| OS | Windows 10 / 11 (64-bit) |
| OneDrive | Installed, signed in with an **a360inc** account |
| SharePoint | `PTY Files - EQUIPOS` and `PTY Files - INSUMOS` folders synced locally |

> See `notes.md` for the install, usage, and troubleshooting guide.

### Build / regenerate the installer

```powershell
.\scripts\build.ps1
```

The installer is generated in `release\`. See the "Build" section in `notes.md`.

---

*Proyecto interno liderado por / project maintained by a360inc, Panama.*