import os
import sys
import subprocess

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_equipos_dir = os.path.dirname(_app_dir)
if _equipos_dir not in sys.path:
    sys.path.insert(0, _equipos_dir)

_theme_dir = os.path.abspath(os.path.join(_app_dir, "..", "..", "..", "Theme"))
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER, ROLE_COLORS, LOGO_PATH, LOGO_WIDTH,
)
from icons import icon_inventory, icon_users, icon_logout

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QStatusBar, QMessageBox, QApplication,
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

from services.auth_service import logout as auth_logout
from ui.inventory_view import InventoryView
from ui.user_management import UserManagementView
from core.ui.translations import (
    APP_TITLE, NAV_INVENTORY, NAV_USERS, NAV_LOGOUT,
    STATUS_CONNECTED, LOGOUT_TITLE, LOGOUT_CONFIRM, MSG_ERROR,
)


class MainWindow(QMainWindow):

    def __init__(self, excel_client, session):
        super().__init__()
        self._client = excel_client
        self._session = session
        self._init_ui()

    def _init_ui(self):
        role_display = {"admin": "Admin", "editor": "Editor", "viewer": "Viewer"}.get(
            self._session.get("role", ""), self._session.get("role", "")
        )
        self.setWindowTitle(
            f"{APP_TITLE} ({self._session['username']} - {role_display})"
        )
        self.setMinimumSize(1100, 700)
        self.setGeometry(100, 100, 1200, 750)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav_bar = self._create_nav_bar()
        main_layout.addWidget(nav_bar)

        self._stack = QStackedWidget()
        main_layout.addWidget(self._stack)

        self._inventory_view = InventoryView(self._client, self._session)
        self._stack.addWidget(self._inventory_view)

        from services.auth_service import can_manage
        if can_manage(self._session):
            self._user_view = UserManagementView(self._session)
            self._stack.addWidget(self._user_view)

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
        self._status_bar.showMessage(
            STATUS_CONNECTED.format(username=self._session['username'], role=role_display)
        )

        self._apply_styles()

    def _create_nav_bar(self):
        nav = QFrame()
        nav.setFixedHeight(64)
        nav.setObjectName("navBar")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(15, 5, 15, 5)
        nav_layout.setSpacing(8)

        try:
            pixmap = QPixmap(LOGO_PATH)
            scaled = pixmap.scaledToHeight(40, Qt.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(scaled)
            logo_label.setFixedSize(scaled.width(), scaled.height())
            nav_layout.addWidget(logo_label)
        except Exception:
            pass

        title = QLabel(APP_TITLE)
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        nav_layout.addWidget(title)

        nav_layout.addStretch()

        self._btn_inventory = QPushButton(icon_inventory(TEXT_DARK), NAV_INVENTORY)
        self._btn_inventory.setObjectName("navBtn")
        self._btn_inventory.setIconSize(self._btn_inventory.iconSize() * 1.2)
        self._btn_inventory.clicked.connect(lambda: self._switch_view(0))
        nav_layout.addWidget(self._btn_inventory)

        from services.auth_service import can_manage
        if can_manage(self._session):
            self._btn_users = QPushButton(icon_users(TEXT_DARK), NAV_USERS)
            self._btn_users.setObjectName("navBtn")
            self._btn_users.setIconSize(self._btn_users.iconSize() * 1.2)
            self._btn_users.clicked.connect(lambda: self._switch_view(1))
            nav_layout.addWidget(self._btn_users)

        logout_btn = QPushButton(icon_logout(WHITE, 18), NAV_LOGOUT)
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setIconSize(logout_btn.iconSize() * 1.2)
        logout_btn.clicked.connect(self._logout)
        nav_layout.addWidget(logout_btn)

        return nav

    def _apply_styles(self):
        self.setStyleSheet(f"""
            #navBar {{
                background-color: {WHITE};
                border-bottom: 2px solid {PRIMARY};
            }}
        """)

    def _switch_view(self, index):
        self._stack.setCurrentIndex(index)
        widget = self._stack.currentWidget()
        if hasattr(widget, 'refresh'):
            widget.refresh()

    def _logout(self):
        reply = QMessageBox.question(
            self, LOGOUT_TITLE,
            LOGOUT_CONFIRM,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            auth_logout(self._session)
            if hasattr(sys, '_MEIPASS'):
                subprocess.Popen([sys.executable, '--app-equipos-qt'])
            else:
                launcher = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'launcher.py'
                )
                subprocess.Popen([sys.executable, launcher, '--app-equipos-qt'])
            QApplication.quit()
