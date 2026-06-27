import os
import sys

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_equipos_dir = os.path.dirname(_app_dir)
if _equipos_dir not in sys.path:
    sys.path.insert(0, _equipos_dir)

_theme_dir = os.path.abspath(os.path.join(_app_dir, "..", "..", "..", "Theme"))
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER, LOGO_PATH,
)

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

from services.auth_service import authenticate, get_windows_username, load_users


class LoginDialog(QDialog):

    def __init__(self):
        super().__init__()
        self._session = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("IT Inventory - Login")
        self.setFixedSize(420, 300)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        try:
            pixmap = QPixmap(LOGO_PATH)
            scaled = pixmap.scaledToWidth(120, Qt.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(scaled)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        except Exception:
            pass

        title = QLabel("IT Inventory - Equipos")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Please log in to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {TEXT_MUTED};")
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Username")
        self._username_input.setMinimumHeight(35)
        self._username_input.setFont(QFont("Segoe UI", 11))
        form_layout.addWidget(self._username_input)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Password")
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setMinimumHeight(35)
        self._password_input.setFont(QFont("Segoe UI", 11))
        self._password_input.returnPressed.connect(self._do_login)
        form_layout.addWidget(self._password_input)

        self._password_label = QLabel("")
        self._password_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9pt;")
        form_layout.addWidget(self._password_label)

        layout.addLayout(form_layout)
        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        self._login_btn = QPushButton("Login")
        self._login_btn.setMinimumHeight(36)
        self._login_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self._login_btn.clicked.connect(self._do_login)
        self._login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {HOVER};
            }}
        """)
        btn_layout.addWidget(self._login_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.setFont(QFont("Segoe UI", 10))
        cancel_btn.setStyleSheet(f"color: {TEXT_MUTED};")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _do_login(self):
        username = self._username_input.text().strip()
        password = self._password_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Missing field", "Please enter your username.")
            return

        users = load_users()
        win_user = get_windows_username()

        is_windows_user = (
            username.lower() == win_user
            and username in users
            and users[username]["type"] == "windows"
        )

        if is_windows_user:
            self._session = authenticate(username, "")
            if self._session:
                self.accept()
                return

        if not password:
            QMessageBox.warning(self, "Missing field", "Please enter your password.")
            return

        self._session = authenticate(username, password)
        if self._session:
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect username or password.")
            self._password_input.clear()
            self._password_input.setFocus()

    def get_session(self):
        return self._session
