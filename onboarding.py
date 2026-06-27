import os
import json
import sys
import glob
import ctypes
from datetime import datetime

APP_CONFIG_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
    "InsumosApp"
)
APP_CONFIG_FILE = os.path.join(APP_CONFIG_DIR, "config.json")


def _is_first_run():
    return not os.path.exists(APP_CONFIG_FILE)


def _mark_first_run_done():
    os.makedirs(APP_CONFIG_DIR, exist_ok=True)
    config = {
        "first_run_complete": True,
        "first_run_date": datetime.now().isoformat()
    }
    with open(APP_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def _validate_onedrive_setup():
    user_home = os.path.expanduser("~")
    matches = glob.glob(os.path.join(user_home, "OneDrive - a360inc*"))
    for root in matches:
        equipos_folder = os.path.join(root, "PTY Files - EQUIPOS")
        insumos_folder = os.path.join(root, "PTY Files - INSUMOS")
        if os.path.isdir(equipos_folder) and os.path.isdir(insumos_folder):
            return True
    return False


def _show_message(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)


def _show_error(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)


def run():
    if not _is_first_run():
        return

    _show_message(
        "Setup Requirements",
        "This application requires access to the following OneDrive/SharePoint "
        "folders:\n\n"
        "    - PTY Files - EQUIPOS\n"
        "    - PTY Files - INSUMOS\n\n"
        "Please ensure:\n\n"
        "    1. OneDrive is synchronized\n"
        "    2. These folders exist in your OneDrive\n"
        "    3. Files are available locally (not cloud-only)\n\n"
        "If these folders are missing, the application will not function correctly."
    )

    _mark_first_run_done()

    if not _validate_onedrive_setup():
        _show_error(
            "Configuration Error",
            "Required SharePoint folder not found. Please verify your OneDrive setup."
        )
        sys.exit(1)
