import os
import sys

_theme_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "Theme")
)
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER, ROLE_COLORS, LOGO_PATH,
)

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QStatusBar, QMessageBox, QApplication,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

from ui.inventory_view import InventoryView
from ui.user_management import UserManagementView
from ui.report_builder import ReportBuilderView
from services.excel_service import ExcelService
from services.report_service import ReportService


GLOBAL_STYLESHEET = f"""
QMainWindow {{
    background-color: {WHITE};
}}
QWidget {{
    font-family: "Segoe UI", "Arial", sans-serif;
    color: {TEXT_DARK};
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
QSpinBox {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    background-color: {WHITE};
    color: {TEXT_DARK};
}}
QSpinBox:focus {{
    border-color: {PRIMARY};
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
"""


class MainWindow(QMainWindow):

    def __init__(self, user_service, excel_service):
        super().__init__()
        self._user_service = user_service
        self._excel = excel_service
        self._report_service = ReportService(excel_service)
        self._init_ui()

    def _init_ui(self):
        user = self._user_service.get_current_user()
        print(f"[MainWindow] Initializing UI for: {user.get('username')} ({user.get('role')})")

        role_display = {"admin": "Admin", "editor": "Editor", "viewer": "Viewer"}.get(
            user.get("role", ""), user.get("role", "")
        )

        self.setWindowTitle(f"Sistema de Inventario - Insumos ({user['username']} - {role_display})")
        self.setMinimumSize(1100, 700)
        self.setGeometry(100, 100, 1200, 750)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        try:
            self._nav_bar = self._create_nav_bar()
            main_layout.addWidget(self._nav_bar)
        except Exception as e:
            print(f"[MainWindow] Error creating nav bar: {e}")

        self._stack = QStackedWidget()
        main_layout.addWidget(self._stack)

        try:
            self._inventory_view = InventoryView(self._excel, self._user_service)
            self._stack.addWidget(self._inventory_view)
        except Exception as e:
            print(f"[MainWindow] Error creating inventory view: {e}")
            import traceback
            traceback.print_exc()
            self._inventory_view = None

        try:
            self._report_view = ReportBuilderView(self._excel, self._report_service)
            self._stack.addWidget(self._report_view)
        except Exception as e:
            print(f"[MainWindow] Error creating report view: {e}")
            import traceback
            traceback.print_exc()
            self._report_view = None

        if self._user_service.is_admin():
            try:
                self._user_view = UserManagementView(self._user_service)
                self._stack.addWidget(self._user_view)
            except Exception as e:
                print(f"[MainWindow] Error creating user management view: {e}")
                import traceback
                traceback.print_exc()

        if self._inventory_view:
            self._stack.setCurrentWidget(self._inventory_view)

        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {LIGHT_BG};
                color: {TEXT_MUTED};
                border-top: 1px solid {BORDER};
                font-size: 12px;
                padding: 2px 10px;
            }}
        """)
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage(f"Conectado como: {user['username']} ({role_display})")

        self._apply_styles()

    def _create_nav_bar(self):
        nav = QFrame()
        nav.setFixedHeight(64)
        nav.setObjectName("navBar")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(15, 5, 15, 5)
        nav_layout.setSpacing(8)

        # Logo
        try:
            pixmap = QPixmap(LOGO_PATH)
            scaled = pixmap.scaledToHeight(40, Qt.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(scaled)
            logo_label.setFixedSize(scaled.width(), scaled.height())
            nav_layout.addWidget(logo_label)
        except Exception:
            pass

        title = QLabel("Inventario de Insumos")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        nav_layout.addWidget(title)

        nav_layout.addStretch()

        self._btn_inventory = QPushButton("Inventario")
        self._btn_inventory.setObjectName("navBtn")
        self._btn_inventory.clicked.connect(lambda: self._switch_view(0))
        nav_layout.addWidget(self._btn_inventory)

        self._btn_reports = QPushButton("Reportes")
        self._btn_reports.setObjectName("navBtn")
        self._btn_reports.clicked.connect(lambda: self._switch_view(1))
        nav_layout.addWidget(self._btn_reports)

        if self._user_service.is_admin():
            self._btn_users = QPushButton("Usuarios")
            self._btn_users.setObjectName("navBtn")
            self._btn_users.clicked.connect(lambda: self._switch_view(2))
            nav_layout.addWidget(self._btn_users)

        logout_btn = QPushButton("Salir")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self._logout)
        nav_layout.addWidget(logout_btn)

        return nav

    def _apply_styles(self):
        self.setStyleSheet(f"""
            {GLOBAL_STYLESHEET}
            #navBar {{
                background-color: {WHITE};
                border-bottom: 2px solid {PRIMARY};
            }}
            #navBtn {{
                background-color: transparent;
                color: {TEXT_DARK};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            #navBtn:hover {{
                background-color: {LIGHT_BG};
                color: {PRIMARY};
            }}
            #logoutBtn {{
                background-color: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            #logoutBtn:hover {{
                background-color: {DARK_RED};
            }}
        """)

    def _switch_view(self, index):
        self._stack.setCurrentIndex(index)
        widget = self._stack.currentWidget()
        if hasattr(widget, 'refresh'):
            widget.refresh()

    def _logout(self):
        reply = QMessageBox.question(
            self, "Cerrar sesión",
            "¿Está seguro de cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._user_service.logout()
            QApplication.quit()
