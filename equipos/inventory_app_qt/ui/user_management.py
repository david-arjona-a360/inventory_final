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
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER,
)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QLabel, QDialog,
    QLineEdit, QFormLayout, QComboBox, QAbstractItemView,
    QRadioButton, QButtonGroup,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from icons import icon_add, icon_edit, icon_delete, icon_users
from services.auth_service import (
    load_users, save_users, hash_password,
    ROLES,
)


class UserManagementView(QWidget):

    def __init__(self, session):
        super().__init__()
        self._session = session
        self._users = []
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        header = QLabel("User Management")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)

        toolbar = QHBoxLayout()

        self._add_btn = QPushButton(icon_add(WHITE, 18), "Add User")
        self._add_btn.setObjectName("primaryBtn")
        self._add_btn.setMinimumHeight(36)
        self._add_btn.setIconSize(self._add_btn.iconSize() * 1.2)
        self._add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self._add_btn.clicked.connect(self._add_user)
        toolbar.addWidget(self._add_btn)

        self._change_pwd_btn = QPushButton(icon_edit(TEXT_DARK, 18), "Change Password")
        self._change_pwd_btn.setMinimumHeight(36)
        self._change_pwd_btn.setIconSize(self._change_pwd_btn.iconSize() * 1.2)
        self._change_pwd_btn.setEnabled(False)
        self._change_pwd_btn.clicked.connect(self._change_password)
        toolbar.addWidget(self._change_pwd_btn)

        self._change_role_btn = QPushButton(icon_users(TEXT_DARK, 18), "Change Role")
        self._change_role_btn.setMinimumHeight(36)
        self._change_role_btn.setIconSize(self._change_role_btn.iconSize() * 1.2)
        self._change_role_btn.setEnabled(False)
        self._change_role_btn.clicked.connect(self._change_role)
        toolbar.addWidget(self._change_role_btn)

        self._remove_btn = QPushButton(icon_delete(PRIMARY, 18), "Remove User")
        self._remove_btn.setObjectName("dangerBtn")
        self._remove_btn.setMinimumHeight(36)
        self._remove_btn.setIconSize(self._remove_btn.iconSize() * 1.2)
        self._remove_btn.setEnabled(False)
        self._remove_btn.clicked.connect(self._remove_user)
        toolbar.addWidget(self._remove_btn)

        layout.addLayout(toolbar)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Status"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)

        font = QFont("Segoe UI", 10)
        self._table.setFont(font)
        self._table.verticalHeader().setDefaultSectionSize(30)

        layout.addWidget(self._table)

        self._status_label = QLabel("")
        self._status_label.setFont(QFont("Segoe UI", 9))
        self._status_label.setStyleSheet(f"color: {TEXT_MUTED};")
        layout.addWidget(self._status_label)

        self.setLayout(layout)
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
            #dangerBtn {{
                background-color: transparent;
                color: {PRIMARY};
                border: 1px solid {PRIMARY};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            #dangerBtn:hover {{
                background-color: {LIGHT_BG};
            }}
        """)

    def _on_selection_changed(self):
        has_selection = bool(self._table.selectedItems())
        self._change_pwd_btn.setEnabled(has_selection)
        self._change_role_btn.setEnabled(has_selection)
        self._remove_btn.setEnabled(has_selection)

    def refresh(self):
        try:
            self._users = load_users()
            self._populate_table()
            self._status_label.setText(f"{len(self._users)} user(s)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load users:\n{e}")

    def _populate_table(self):
        self._table.setRowCount(len(self._users))
        for row_idx, user in enumerate(self._users):
            self._table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self._table.setItem(row_idx, 1, QTableWidgetItem(user.get("username", "")))
            self._table.setItem(row_idx, 2, QTableWidgetItem(user.get("role", "")))
            self._table.setItem(row_idx, 3, QTableWidgetItem(user.get("status", "active")))

    def _get_selected_user(self):
        rows = set()
        for item in self._table.selectedItems():
            rows.add(item.row())
        if not rows:
            return None
        row = rows.pop()
        username = self._table.item(row, 1).text()
        return next((u for u in self._users if u.get("username") == username), None)

    def _add_user(self):
        dialog = _UserFormDialog("Add User")
        if dialog.exec_():
            data = dialog.get_data()
            user_type = data.get("user_type", "local")
            new_user = {
                "username": data["username"].strip(),
                "password": hash_password(data["password"]) if data.get("password") else "",
                "role": data["role"],
                "type": user_type,
                "status": "active",
            }
            prev = load_users()
            if any(u.get("username", "").lower() == new_user["username"].lower() for u in prev):
                QMessageBox.warning(self, "Exists", f"User '{new_user['username']}' already exists.")
                return
            prev.append(new_user)
            save_users(prev)
            self.refresh()
            self._status_label.setText(f"User '{new_user['username']}' added.")

    def _change_password(self):
        user = self._get_selected_user()
        if not user:
            return
        dialog = _PasswordDialog(f"Change Password for '{user['username']}'")
        if dialog.exec_():
            new_pwd = dialog.get_password()
            prev = load_users()
            for u in prev:
                if u.get("username") == user["username"]:
                    u["password"] = hash_password(new_pwd)
                    break
            save_users(prev)
            self.refresh()
            self._status_label.setText(f"Password updated for '{user['username']}'.")

    def _change_role(self):
        user = self._get_selected_user()
        if not user:
            return
        dialog = _RoleDialog(f"Change Role for '{user['username']}'", user["role"])
        if dialog.exec_():
            new_role = dialog.get_role()
            prev = load_users()
            for u in prev:
                if u.get("username") == user["username"]:
                    u["role"] = new_role
                    break
            save_users(prev)
            self.refresh()
            self._status_label.setText(f"Role changed to '{new_role}' for '{user['username']}'.")

    def _remove_user(self):
        user = self._get_selected_user()
        if not user:
            return
        if str(user.get("username")) == self._session.get("username"):
            QMessageBox.warning(self, "Cannot remove", "You cannot remove your own account.")
            return
        reply = QMessageBox.question(
            self, "Confirm Remove",
            f"Permanently remove user '{user['username']}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            prev = load_users()
            prev = [u for u in prev if u.get("username") != user["username"]]
            save_users(prev)
            self.refresh()
            self._status_label.setText(f"User '{user['username']}' removed.")


class _UserFormDialog(QDialog):

    def __init__(self, title, user=None):
        super().__init__()
        self._user = user
        self._data = None
        self._init_ui(title)

    def _init_ui(self, title):
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 320)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(10)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Enter username")
        self._username_input.setMinimumHeight(32)
        if self._user:
            self._username_input.setText(self._user["username"])
            self._username_input.setEnabled(False)
        form.addRow("Username:", self._username_input)

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
        form.addRow("Type:", type_widget)

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Enter password")
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.setMinimumHeight(32)
        form.addRow("Password:", self._password_input)

        self._password_note = QLabel("")
        self._password_note.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9pt;")
        form.addRow("", self._password_note)

        self._role_combo = QComboBox()
        self._role_combo.addItems(["viewer", "editor", "admin"])
        self._role_combo.setMinimumHeight(32)
        if self._user:
            idx = self._role_combo.findText(self._user.get("role", "viewer"))
            if idx >= 0:
                self._role_combo.setCurrentIndex(idx)
        form.addRow("Role:", self._role_combo)

        layout.addLayout(form)
        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumHeight(36)
        save_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.setFont(QFont("Segoe UI", 10))
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
            #cancelBtn {{
                background-color: {WHITE};
                color: {TEXT_DARK};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            #cancelBtn:hover {{
                background-color: {LIGHT_BG};
                border-color: {SECONDARY};
            }}
        """)

    def _on_type_changed(self):
        is_local = self._local_radio.isChecked()
        self._password_input.setEnabled(is_local)
        if is_local:
            self._password_input.setPlaceholderText("Enter password")
            self._password_note.setText("")
        else:
            self._password_input.setPlaceholderText("No password needed (Windows SSO)")
            self._password_input.setText("")
            self._password_note.setText("Authentication uses the Windows session")

    def _save(self):
        username = self._username_input.text().strip()
        password = self._password_input.text().strip()
        role = self._role_combo.currentText()
        user_type = "local" if self._local_radio.isChecked() else "windows"

        if not username:
            QMessageBox.warning(self, "Validation", "Username cannot be empty.")
            return

        if user_type == "local":
            is_new = self._user is None
            if is_new and not password:
                QMessageBox.warning(self, "Validation", "Password is required for local users.")
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


class _PasswordDialog(QDialog):

    def __init__(self, title):
        super().__init__()
        self._password = None
        self._init_ui(title)

    def _init_ui(self, title):
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(360, 150)

        layout = QVBoxLayout()
        form = QFormLayout()

        self._pwd_input = QLineEdit()
        self._pwd_input.setEchoMode(QLineEdit.Password)
        self._pwd_input.setPlaceholderText("New password")
        self._pwd_input.setMinimumHeight(32)
        form.addRow("New Password:", self._pwd_input)

        layout.addLayout(form)
        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumHeight(36)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

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
            #cancelBtn {{
                background-color: {WHITE};
                color: {TEXT_DARK};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            #cancelBtn:hover {{
                background-color: {LIGHT_BG};
                border-color: {SECONDARY};
            }}
        """)

    def _save(self):
        pwd = self._pwd_input.text().strip()
        if not pwd:
            QMessageBox.warning(self, "Validation", "Password cannot be empty.")
            return
        self._password = pwd
        self.accept()

    def get_password(self):
        return self._password


class _RoleDialog(QDialog):

    def __init__(self, title, current_role):
        super().__init__()
        self._role = None
        self._init_ui(title, current_role)

    def _init_ui(self, title, current_role):
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(360, 150)

        layout = QVBoxLayout()
        form = QFormLayout()

        self._role_combo = QComboBox()
        self._role_combo.addItems(["viewer", "editor", "admin"])
        self._role_combo.setCurrentText(current_role)
        self._role_combo.setMinimumHeight(32)
        form.addRow("New Role:", self._role_combo)

        layout.addLayout(form)
        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumHeight(36)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

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
            #cancelBtn {{
                background-color: {WHITE};
                color: {TEXT_DARK};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            #cancelBtn:hover {{
                background-color: {LIGHT_BG};
                border-color: {SECONDARY};
            }}
        """)

    def _save(self):
        self._role = self._role_combo.currentText()
        self.accept()

    def get_role(self):
        return self._role
