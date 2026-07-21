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
from icons import icon_add, icon_edit

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QSpinBox, QComboBox, QFormLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ItemForm(QDialog):

    def __init__(self, item=None, title="Agregar Insumo"):
        super().__init__()
        self._item = item
        self._data = None
        self._init_ui(title)

    def _init_ui(self, title):
        self.setWindowTitle(title)
        self.setFixedSize(500, 450)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(10)

        self._producto_input = QLineEdit()
        self._producto_input.setPlaceholderText("Nombre del producto")
        self._producto_input.setMinimumHeight(32)
        form.addRow("Producto *:", self._producto_input)

        self._marca_input = QLineEdit()
        self._marca_input.setPlaceholderText("Marca")
        self._marca_input.setMinimumHeight(32)
        form.addRow("Marca *:", self._marca_input)

        self._tamano_input = QLineEdit()
        self._tamano_input.setPlaceholderText("Ej: Bolsa 5 lb, Caja 60 unid")
        self._tamano_input.setMinimumHeight(32)
        form.addRow("Tamaño *:", self._tamano_input)

        self._cantidad_input = QSpinBox()
        self._cantidad_input.setMinimum(0)
        self._cantidad_input.setMaximum(999999)
        self._cantidad_input.setMinimumHeight(32)
        form.addRow("Cantidad *:", self._cantidad_input)

        self._categoria_input = QComboBox()
        self._categoria_input.setEditable(True)
        self._categoria_input.addItems([
            "Cafeteria", "Limpieza", "Oficina", "Cocina", "Bodega"
        ])
        self._categoria_input.setMinimumHeight(32)
        form.addRow("Categoría *:", self._categoria_input)

        self._proveedor_input = QLineEdit()
        self._proveedor_input.setPlaceholderText("Nombre del proveedor")
        self._proveedor_input.setMinimumHeight(32)
        form.addRow("Proveedor:", self._proveedor_input)

        self._cant_minima_input = QSpinBox()
        self._cant_minima_input.setMinimum(0)
        self._cant_minima_input.setMaximum(999999)
        self._cant_minima_input.setMinimumHeight(32)
        form.addRow("Cant. Mínima:", self._cant_minima_input)

        layout.addLayout(form)

        if self._item:
            layout.addSpacing(5)
            info = QLabel(f"ID: {self._item.get('id', 'N/A')[:8]}... | Creado: {self._item.get('created_at', 'N/A')}")
            info.setFont(QFont("Segoe UI", 8))
            info.setStyleSheet(f"color: {TEXT_MUTED};")
            layout.addWidget(info)

        layout.addSpacing(10)

        btn_layout = QHBoxLayout()
        icon = icon_add(WHITE, 18) if not self._item else icon_edit(WHITE, 18)
        save_btn = QPushButton(icon, "Guardar")
        save_btn.setObjectName("primaryBtn")
        save_btn.setMinimumHeight(36)
        save_btn.setIconSize(save_btn.iconSize() * 1.2)
        save_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.setFont(QFont("Segoe UI", 10))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self._apply_styles()

        if self._item:
            self._load_item()

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

    def _load_item(self):
        self._producto_input.setText(self._item.get("producto", ""))
        self._marca_input.setText(self._item.get("marca", ""))
        self._tamano_input.setText(self._item.get("tamano", ""))
        try:
            self._cantidad_input.setValue(int(self._item.get("cantidad", 0)))
        except (ValueError, TypeError):
            self._cantidad_input.setValue(0)
        idx = self._categoria_input.findText(self._item.get("categoria", ""))
        if idx >= 0:
            self._categoria_input.setCurrentIndex(idx)
        else:
            self._categoria_input.setCurrentText(self._item.get("categoria", ""))

        self._proveedor_input.setText(self._item.get("proveedor", ""))
        try:
            self._cant_minima_input.setValue(int(self._item.get("cant_minima", 0)))
        except (ValueError, TypeError):
            self._cant_minima_input.setValue(0)

    def _save(self):
        producto = self._producto_input.text().strip()
        marca = self._marca_input.text().strip()
        tamano = self._tamano_input.text().strip()
        cantidad = self._cantidad_input.value()
        categoria = self._categoria_input.currentText().strip()

        errors = []
        if not producto:
            errors.append("Producto")
        if not marca:
            errors.append("Marca")
        if not tamano:
            errors.append("Tamaño")
        if not categoria:
            errors.append("Categoría")

        if errors:
            QMessageBox.warning(
                self, "Campos requeridos",
                f"Los siguientes campos son obligatorios:\n- " + "\n- ".join(errors)
            )
            return

        self._data = {
            "producto": producto,
            "marca": marca,
            "tamano": tamano,
            "cantidad": cantidad,
            "categoria": categoria,
            "proveedor": self._proveedor_input.text().strip(),
            "cant_minima": self._cant_minima_input.value(),
        }
        if self._item:
            self._data["_original_updated_at"] = self._item.get("updated_at", "")
        self.accept()

    def get_data(self):
        return self._data
