import os
import sys
import logging
import tempfile

_parent = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

_DIAG_LOG_SETTINGS = os.path.join(tempfile.gettempdir(), "inventory_diag.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(_DIAG_LOG_SETTINGS, mode="a"),
        logging.StreamHandler(sys.stderr),
    ],
    force=True,
)
log = logging.getLogger("settings")

from path_config import get_insumos_path

import json

APP_NAME = "Inventario de Insumos"
APP_VERSION = "1.0.0"

log.info("=== DIAGNOSTIC: settings.py loaded ===")
log.info("__file__: %s", __file__)
log.info("_parent (4 dirs up): %s", _parent)
log.info("_parent in sys.path: %s", _parent in sys.path)
log.info("sys.path: %s", sys.path)

# --- Dynamic path resolution ---

def get_windows_username():
    return os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"

def get_onedrive_base_path():
    path = get_insumos_path()
    if path:
        log.info("OneDrive base path resolved: %s", path)
        log.info("OneDrive base path exists: %s", os.path.isdir(path))
    else:
        fallback = rf"C:\Users\{get_windows_username()}\OneDrive - a360inc\PTY Files - INSUMOS"
        log.warning(
            "get_insumos_path() returned None — "
            "falling back to constructed path: %s",
            fallback
        )
        path = fallback
    log.info("FINAL OneDrive base path: %s (dir_exists=%s)", path, os.path.isdir(path))
    return path

# --- Config file ---

_this_dir = os.path.dirname(os.path.abspath(__file__))         # .../config
_app_dir = os.path.dirname(_this_dir)                          # .../inventory_app
_project_root = os.path.dirname(_app_dir)                      # .../Insumos
CONFIG_FILE = os.path.join(_project_root, "config.json")

def load_config():
    default = {"excel_path_override": ""}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**default, **json.load(f)}
        except (json.JSONDecodeError, IOError):
            pass
    return default

# --- Excel path ---

EXCEL_PATH_ENV_VAR = "INVENTARIO_EXCEL_PATH"

def get_excel_path():
    config = load_config()
    override = config.get("excel_path_override", "")
    if override:
        log.info("get_excel_path -> override: %s (exists=%s)", override, os.path.isfile(override))
        return override
    env_path = os.environ.get(EXCEL_PATH_ENV_VAR)
    if env_path:
        log.info("get_excel_path -> env var %s: %s (exists=%s)", EXCEL_PATH_ENV_VAR, env_path, os.path.isfile(env_path))
        return env_path
    result = os.path.join(get_onedrive_base_path(), "Inventario_Insumos.xlsx")
    log.info("get_excel_path -> %s (exists=%s)", result, os.path.isfile(result))
    return result

MAIN_SHEET = "INSUMOS"
HISTORY_SHEET = "history_log"
HIDDEN_COLUMNS = ["id", "created_at", "updated_at", "updated_by", "is_active"]

COLUMN_MAP = {
    "Producto": "producto",
    "Marca": "marca",
    "Tamaño": "tamano",
    "Cantidad": "cantidad",
    "Categoria": "categoria",
    "Proveedor": "proveedor",
    "Cant. Minima": "cant_minima",
    "id": "id",
    "created_at": "created_at",
    "updated_at": "updated_at",
    "updated_by": "updated_by",
    "is_active": "is_active",
}

VISIBLE_COLUMNS = ["Producto", "Marca", "Tamaño", "Cantidad", "Categoria", "Proveedor", "Cant. Minima"]

USERS_FILE = os.path.join(get_onedrive_base_path(), "users.json")
log.info("USERS_FILE: %s (parent_dir_exists=%s)", USERS_FILE, os.path.isdir(os.path.dirname(USERS_FILE)))

ROLES = {
    "admin": "Admin",
    "editor": "Editor",
    "viewer": "Viewer",
}
