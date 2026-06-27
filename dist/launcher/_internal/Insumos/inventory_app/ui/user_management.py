import os
import sys

_theme_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "Theme")
)
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER,
)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QLabel, QDialog,
    QLineEdit, QComboBox, QFormLayout, QAbstractItemView, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class UserManagementView(QWidget):

    def __init__(self, user_service):
        super().__init__()
        self._user_service = user_service
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        header = QLabel("Gestión de Usuarios")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Usuario", "Rol", "Tipo", "Acciones"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)

        font = QFont("Segoe UI", 10)
        self._table.setFont(font)
        self._table.verticalHeader().setDefaultSectionSize(36)

        layout.addWidget(self._table)

        btn_bar = QHBoxLayout()

        add_user_btn = QPushButton("Agregar Usuario")
        add_user_btn.setObjectName("primaryBtn")
        add_user_btn.setMinimumHeight(36)
        add_user_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        add_user_btn.clicked.connect(self._add_user)
        btn_bar.addWidget(add_user_btn)

        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setMinimumHeight(36)
        refresh_btn.clicked.connect(self.refresh)
        btn_bar.addWidget(refresh_btn)

        layout.addLayout(btn_bar)

        self._apply_styles()
        self.setLayout(layout)

    def _apply_styles(self):
        self.setStyleSheet(f"""
            #primaryBtn {{
                background-color: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            #primaryBtn:hover {{
                background-color: {HOVER};
            }}
        """)

    def refresh(self):
        try:
            users = self._user_service.get_all_users()
            self._table.setRowCount(len(users))

            for row_idx, user in enumerate(users):
                username_item = QTableWidgetItem(user["username"])
                role_item = QTableWidgetItem(
                    {"admin": "Admin", "editor": "Editor", "viewer": "Viewer"}.get(
                        user.get("role", ""), user.get("role", "")
                    )
                )
                user_type = user.get("type", "local")
                type_item = QTableWidgetItem(
                    "Windows SSO" if user_type == "windows" else "Local"
                )

                self._table.setItem(row_idx, 0, username_item)
                self._table.setItem(row_idx, 1, role_item)
                self._table.setItem(row_idx, 2, type_item)

                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(4, 2, 4, 2)
                btn_layout.setSpacing(4)

                edit_btn = QPushButton("Editar")
                edit_btn.setMinimumHeight(28)
                edit_btn.setFont(QFont("Segoe UI", 9))
                edit_btn.clicked.connect(lambda checked, u=user: self._edit_user(u))
                btn_layout.addWidget(edit_btn)

                if user["username"] != self._user_service.get_current_user()["username"]:
                    delete_btn = QPushButton("Eliminar")
                    delete_btn.setObjectName("deleteUserBtn")
                    delete_btn.setMinimumHeight(28)
                    delete_btn.setFont(QFont("Segoe UI", 9))
                    delete_btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {PRIMARY};
                            color: {WHITE};
                            border: none;
                            border-radius: 3px;
                            padding: 4px 12px;
                        }}
                        QPushButton:hover {{
                            background-color: {DARK_RED};
                        }}
                    """)
                    delete_btn.clicked.connect(lambda checked, u=user: self._delete_user(u))
                    btn_layout.addWidget(delete_btn)

                btn_widget.setLayout(btn_layout)
                self._table.setCellWidget(row_idx, 3, btn_widget)

            self._table.setRowHeight(row_idx, 40)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar usuarios:\n{str(e)}")

    def _add_user(self):
        dialog = _UserFormDialog(title="Agregar Usuario")
        if dialog.exec_():
            data = dialog.get_data()
            try:
                # Debug: confirm structure before saving
                print(f"[UserManagement] Creating user: {data}")
                self._user_service.create_user(
                    data["username"], data.get("password", ""), data["role"],
                    user_type=data.get("user_type", "local"),
                    created_by=self._user_service.get_current_user()["username"]
                )
                QMessageBox.information(self, "Éxito", f"Usuario '{data['username']}' creado correctamente.")
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear usuario:\n{str(e)}")

    def _edit_user(self, user):
        dialog = _UserFormDialog(user=user, title="Editar Usuario")
        if dialog.exec_():
            data = dialog.get_data()
            try:
                self._user_service.update_user(
                    user["username"],
                    password=data.get("password"),
                    role=data.get("role"),
                    user_type=data.get("user_type"),
                )
                QMessageBox.information(self, "Éxito", f"Usuario '{user['username']}' actualizado correctamente.")
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar usuario:\n{str(e)}")

    def _delete_user(self, user):
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de eliminar al usuario '{user['username']}'?\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self._user_service.delete_user(user["username"])
                QMessageBox.information(self, "Éxito", f"Usuario '{user['username']}' eliminado.")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar usuario:\n{str(e)}")


class _UserFormDialog(QDialog):

    def __init__(self, user=None, title="Formulario de Usuario"):
        super().__init__()
        self._user = user
        self._data = None
        self._init_ui(title)

    def _init_ui(self, title):
        self.setWindowTitle(title)
        self.setFixedSize(420, 340)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(10)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Nombre de usuario")
        self._username_input.setMinimumHeight(32)
        if self._user:
            self._username_input.setText(self._user["username"])
            self._username_input.setEnabled(False)
        form.addRow("Usuario *:", self._username_input)

        # ── Type selector ──────────────────────────────────────
        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setContentsMargins(0, 0, 0, 0)
        self._type_group = QButtonGroup()
        self._local_radio = QRadioButton("Local")
        self._windows_radio = QRadioButton("Windows SSO")
        self._type_group.addButton(self._local_radio, 1)
        self._type_group.addButton(self._windows_radio, 2)
        type_layout.addWidget(self._local_radio)
        type_layout.addWidget(self._windows_radio)

        current_type = (self._user or {}).get("type", "local")
        if current_type == "windows":
            self._windows_radio.setChecked(True)
        else:
            self._local_radio.setChecked(True)

        self._type_group.buttonClicked.connect(self._on_type_changed)
        form.addRow("Tipo:", type_widget)

        # ── Password ────────────────────────────────────────────
        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Contraseña")
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setMinimumHeight(32)
        form.addRow("Contraseña:", self._password_input)

        self._password_note = QLabel("")
        self._password_note.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9pt;")
        form.addRow("", self._password_note)

        # ── Role ────────────────────────────────────────────────
        self._role_combo = QComboBox()
        self._role_combo.addItems(["admin", "editor", "viewer"])
        self._role_combo.setMinimumHeight(32)
        if self._user:
            idx = self._role_combo.findText(self._user.get("role", "viewer"))
            self._role_combo.setCurrentIndex(idx if idx >= 0 else 0)
        form.addRow("Rol *:", self._role_combo)

        layout.addLayout(form)
        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumHeight(36)
        save_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.setFont(QFont("Segoe UI", 11))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self._on_type_changed()
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet(f"""
            #primaryBtn {{
                background-color: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }}
            #primaryBtn:hover {{
                background-color: {HOVER};
            }}
        """)

    def _on_type_changed(self):
        is_local = self._local_radio.isChecked()
        self._password_input.setEnabled(is_local)
        if is_local:
            self._password_input.setPlaceholderText("Contraseña")
            self._password_note.setText("")
        else:
            self._password_input.setPlaceholderText("Sin contraseña (SSO de Windows)")
            self._password_input.setText("")
            self._password_note.setText("La autenticación usa la cuenta de Windows")

    def _save(self):
        username = self._username_input.text().strip()
        password = self._password_input.text().strip()
        role = self._role_combo.currentText()
        user_type = "local" if self._local_radio.isChecked() else "windows"

        if not username:
            QMessageBox.warning(self, "Campo requerido", "El nombre de usuario es obligatorio.")
            return

        if user_type == "local":
            is_new = self._user is None
            if is_new and not password:
                QMessageBox.warning(self, "Campo requerido", "La contraseña es obligatoria para usuarios locales.")
                return

        self._data = {
            "username": username,
            "role": role,
            "user_type": user_type,
        }
        if password:
            self._data["password"] = password
        self.accept()

    def get_data(self):
        return self._data
