import sys
import os
import logging

_app_dir = os.path.dirname(os.path.abspath(__file__))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

_equipos_dir = os.path.dirname(_app_dir)
if _equipos_dir not in sys.path:
    sys.path.insert(0, _equipos_dir)

_theme_dir = os.path.abspath(os.path.join(_app_dir, "..", "..", "Theme"))
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER,
)

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from config import find_file_path, load_extra_columns
from excel_client import ExcelClient
from services.auth_service import login as sso_login, authenticate
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


APP_STYLESHEET = f"""
QWidget {{
    font-family: "Segoe UI", "Arial", sans-serif;
    color: {TEXT_DARK};
}}
QMainWindow {{
    background-color: {WHITE};
}}
QDialog {{
    background-color: {WHITE};
}}
QLabel {{
    color: {TEXT_DARK};
}}
QLineEdit {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    background-color: {WHITE};
    color: {TEXT_DARK};
}}
QLineEdit:focus {{
    border-color: {PRIMARY};
}}
QComboBox {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    background-color: {WHITE};
    color: {TEXT_DARK};
}}
QComboBox:focus {{
    border-color: {PRIMARY};
}}
QComboBox::drop-down {{
    border: none;
}}
QPushButton {{
    background-color: {WHITE};
    color: {TEXT_DARK};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 6px 16px;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {LIGHT_BG};
    border-color: {SECONDARY};
}}
QPushButton:pressed {{
    background-color: {BORDER};
}}
QTableWidget {{
    border: 1px solid {BORDER};
    gridline-color: {BORDER};
    background-color: {WHITE};
    alternate-background-color: {LIGHT_BG};
    selection-background-color: {PRIMARY};
    selection-color: {WHITE};
}}
QTableWidget::item {{
    padding: 4px 8px;
}}
QHeaderView::section {{
    background-color: {LIGHT_BG};
    color: {TEXT_DARK};
    font-weight: bold;
    border: none;
    border-bottom: 2px solid {PRIMARY};
    padding: 6px 8px;
}}
QGroupBox {{
    font-weight: bold;
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {TEXT_DARK};
}}
QCheckBox {{
    spacing: 6px;
    color: {TEXT_DARK};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
}}
QScrollBar:vertical {{
    background: {LIGHT_BG};
    width: 10px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {LIGHT_BG};
    height: 10px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 5px;
    min-width: 20px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QStatusBar {{
    background-color: {LIGHT_BG};
    color: {TEXT_MUTED};
    border-top: 1px solid {BORDER};
    font-size: 12px;
    padding: 2px 10px;
}}
"""


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("IT Inventory - Equipos")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    file_path = find_file_path()
    if not file_path:
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

    from config import COLUMNS
    if not COLUMNS:
        sys.exit(1)

    session = sso_login()
    if not session:
        login_dialog = LoginDialog()
        if login_dialog.exec_() != LoginDialog.Accepted:
            sys.exit(0)
        session = login_dialog.get_session()

    client = ExcelClient(file_path)
    window = MainWindow(client, session)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
