import sys
import os
import logging

_app_dir = os.path.dirname(os.path.abspath(__file__))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

_theme_dir = os.path.abspath(os.path.join(_app_dir, "..", "..", "Theme"))
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER,
)
from qss import build_stylesheet

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from config.settings import get_excel_path, load_extra_columns, COLUMNS
from services.excel_service import ExcelService
from services.auth_service import login as sso_login, authenticate
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


APP_STYLESHEET = build_stylesheet({
    "PRIMARY": PRIMARY, "SECONDARY": SECONDARY, "ACCENT": ACCENT,
    "LIGHT_BG": LIGHT_BG, "WHITE": WHITE, "DARK_RED": DARK_RED,
    "TEXT_DARK": TEXT_DARK, "TEXT_MUTED": TEXT_MUTED, "BORDER": BORDER,
    "HOVER": HOVER,
})


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("IT Inventory - Equipos")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    file_path = get_excel_path()
    if not file_path or not os.path.exists(file_path):
        QMessageBox.critical(
            None, "File Not Found",
            "The inventory file could not be found.\n\n"
            "Please make sure:\n"
            "  1. OneDrive is running and synced\n"
            "  2. You have added the SharePoint folder shortcut to OneDrive\n"
            "  3. The file exists at:\n\n"
            f"     OneDrive - a360inc \\ PTY Files - EQUIPOS \\\n"
            "     Formato_Inventario_TI.xlsx"
        )
        sys.exit(1)

    load_extra_columns(file_path)

    if not COLUMNS:
        sys.exit(1)

    session = sso_login()
    if not session:
        login_dialog = LoginDialog()
        if login_dialog.exec_() != LoginDialog.Accepted:
            sys.exit(0)
        session = login_dialog.get_session()

    client = ExcelService()
    client._filepath = file_path
    window = MainWindow(client, session)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
