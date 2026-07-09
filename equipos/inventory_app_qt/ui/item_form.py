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
from icons import icon_add, icon_edit

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget, QFormLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config.settings import COLUMNS


class ItemForm(QDialog):

    def __init__(self, item=None, title="Item Form"):
        super().__init__()
        self._item = item
        self._data = None
        self._inputs = {}
        self._init_ui(title)

    def _init_ui(self, title):
        self.setWindowTitle(title)
        self.setModal(True)

        form_height = max(400, len(COLUMNS) * 42 + 120)
        self.setFixedSize(520, min(form_height, 600))

        layout = QVBoxLayout()
        layout.setSpacing(12)

        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setSpacing(8)
        form.setContentsMargins(20, 10, 20, 10)

        for col in COLUMNS:
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Enter {col.title()}")
            input_field.setMinimumHeight(32)
            if self._item:
                input_field.setText(str(self._item.get(col, "")))
            self._inputs[col] = input_field
            form.addRow(f"{col.title()}:", input_field)

        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        icon = icon_add(WHITE, 18) if not self._item else icon_edit(WHITE, 18)
        save_btn = QPushButton(icon, "Save")
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumHeight(36)
        save_btn.setIconSize(save_btn.iconSize() * 1.2)
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

    def _save(self):
        data = {}
        for col in COLUMNS:
            data[col] = self._inputs[col].text().strip()
        self._data = data
        self.accept()

    def get_data(self):
        return self._data
