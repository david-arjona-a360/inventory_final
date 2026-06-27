import os
import sys

_theme_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "Theme")
)
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER, LOGO_PATH,
)

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap


class LoginDialog(QDialog):

    def __init__(self, user_service):
        super().__init__()
        self._user_service = user_service
        self._user = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Inicio de Sesión - Inventario de Insumos")
        self.setFixedSize(420, 300)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Logo
        try:
            pixmap = QPixmap(LOGO_PATH)
            scaled = pixmap.scaledToWidth(120, Qt.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(scaled)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        except Exception:
            pass

        title = QLabel("Inventario de Insumos")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Ingrese sus credenciales")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {TEXT_MUTED};")
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Usuario")
        self._username_input.setMinimumHeight(35)
        self._username_input.setFont(QFont("Segoe UI", 11))
        self._username_input.textChanged.connect(self._on_username_changed)
        form_layout.addWidget(self._username_input)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Contraseña")
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
        self._login_btn = QPushButton("Ingresar")
        self._login_btn.setMinimumHeight(38)
        self._login_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
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

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.setFont(QFont("Segoe UI", 11))
        cancel_btn.setStyleSheet(f"color: {TEXT_MUTED};")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _on_username_changed(self, text):
        user_info = self._user_service.find_by_username(text.strip())
        if user_info and user_info.get("type", "local") == "windows":
            self._password_input.setVisible(False)
            self._password_label.setVisible(True)
            self._password_label.setText("Autenticación de Windows — no requiere contraseña")
        else:
            self._password_input.setVisible(True)
            self._password_label.setVisible(False)

    def _do_login(self):
        username = self._username_input.text().strip()
        password = self._password_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Campo requerido", "Por favor ingrese un usuario.")
            return

        user_info = self._user_service.find_by_username(username)
        is_windows = user_info and user_info.get("type", "local") == "windows"

        if is_windows:
            user = self._user_service.authenticate(username, "")
            if user:
                self._user = user
                self.accept()
            else:
                QMessageBox.warning(
                    self, "Error de autenticación",
                    "El usuario de Windows no coincide con la sesión actual.\n\n"
                    "Debe iniciar sesión con su cuenta de Windows para usar SSO."
                )
                self._password_input.clear()
                self._password_input.setFocus()
        else:
            if not password:
                QMessageBox.warning(self, "Campo requerido", "Por favor ingrese la contraseña.")
                return
            user = self._user_service.authenticate(username, password)
            if user:
                self._user = user
                self.accept()
            else:
                QMessageBox.warning(self, "Error de autenticación", "Usuario o contraseña incorrectos.")
                self._password_input.clear()
                self._password_input.setFocus()

    def get_user(self):
        return self._user
