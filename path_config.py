"""Backward-compatible wrapper — delegates to core.config.path_config."""
import os
import sys

_core_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core")
if _core_dir not in sys.path:
    sys.path.insert(0, _core_dir)

from core.config.path_config import (  # noqa: F401
    find_onedrive_root,
    get_equipos_path,
    get_equipos_file_path,
    get_insumos_path,
    get_insumos_file_path,
    get_windows_username,
    ONEDRIVE_ORG,
    EQUIPOS_FOLDER,
    EQUIPOS_FILE,
    INSUMOS_FOLDER,
    INSUMOS_FILE,
)
