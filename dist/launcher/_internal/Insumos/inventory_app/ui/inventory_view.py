import os
import sys
import logging
import tempfile

_theme_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "Theme")
)
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

_DIAG_LOG_UI = os.path.join(tempfile.gettempdir(), "inventory_diag.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(_DIAG_LOG_UI, mode="a"),
        logging.StreamHandler(sys.stderr),
    ],
    force=True,
)
log_ui = logging.getLogger("inventory_view")

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER, ROLE_COLORS,
)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QLabel, QLineEdit,
    QCheckBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QBrush


class InventoryView(QWidget):

    def __init__(self, excel_service, user_service):
        super().__init__()
        self._excel = excel_service
        self._user_service = user_service
        self._items = []
        self._selected_item_id = None
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        header = QLabel("Inventario de Insumos")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)

        toolbar = QHBoxLayout()

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Buscar por nombre de producto...")
        self._search_input.setMinimumHeight(32)
        self._search_input.textChanged.connect(self._filter_table)
        toolbar.addWidget(self._search_input)

        self._show_inactive_cb = QCheckBox("Mostrar inactivos")
        self._show_inactive_cb.stateChanged.connect(self._filter_table)
        toolbar.addWidget(self._show_inactive_cb)

        refresh_btn = QPushButton("Actualizar")
        refresh_btn.setObjectName("actionBtn")
        refresh_btn.setMinimumHeight(32)
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)

        layout.addLayout(toolbar)

        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels(["Producto", "Marca", "Tamaño", "Cantidad", "Categoría", "Proveedor", "Cant. Mínima", "Estado"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSortingEnabled(True)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        self._table.cellDoubleClicked.connect(lambda row, col: self._edit_item())

        font = QFont("Segoe UI", 10)
        self._table.setFont(font)
        self._table.verticalHeader().setDefaultSectionSize(30)

        layout.addWidget(self._table)

        action_bar = QHBoxLayout()

        self._add_btn = QPushButton("Agregar Insumo")
        self._add_btn.setObjectName("primaryBtn")
        self._add_btn.setMinimumHeight(36)
        self._add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self._add_btn.clicked.connect(self._add_item)
        action_bar.addWidget(self._add_btn)

        self._edit_btn = QPushButton("Editar Seleccionado")
        self._edit_btn.setMinimumHeight(36)
        self._edit_btn.setFont(QFont("Segoe UI", 10))
        self._edit_btn.setEnabled(False)
        self._edit_btn.clicked.connect(self._edit_item)
        action_bar.addWidget(self._edit_btn)

        self._delete_btn = QPushButton("Desactivar")
        self._delete_btn.setObjectName("dangerBtn")
        self._delete_btn.setMinimumHeight(36)
        self._delete_btn.setFont(QFont("Segoe UI", 10))
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._delete_item)
        action_bar.addWidget(self._delete_btn)

        self._restore_btn = QPushButton("Restaurar")
        self._restore_btn.setMinimumHeight(36)
        self._restore_btn.setFont(QFont("Segoe UI", 10))
        self._restore_btn.setVisible(False)
        self._restore_btn.clicked.connect(self._restore_item)
        action_bar.addWidget(self._restore_btn)

        layout.addLayout(action_bar)

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
            #primaryBtn:disabled {{
                background-color: {BORDER};
                color: {TEXT_MUTED};
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
            #dangerBtn:disabled {{
                border-color: {BORDER};
                color: {TEXT_MUTED};
            }}
            #actionBtn {{
                background-color: {WHITE};
                color: {TEXT_DARK};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 14px;
            }}
            #actionBtn:hover {{
                background-color: {LIGHT_BG};
                border-color: {SECONDARY};
            }}
        """)

    def refresh(self):
        log_ui.info("refresh() called")
        try:
            self._items = self._excel.get_all_items(include_inactive=True)
            log_ui.info("refresh(): got %d items from excel", len(self._items))
            self._filter_table()
        except PermissionError as e:
            log_ui.error("refresh(): PermissionError: %s", e)
            QMessageBox.warning(self, "Archivo bloqueado", str(e))
        except FileNotFoundError as e:
            log_ui.error("refresh(): FileNotFoundError: %s", e)
            QMessageBox.critical(self, "Archivo no encontrado", str(e))
        except Exception as e:
            log_ui.error("refresh(): Exception: %s", e, exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar datos:\n{str(e)}")

    def _filter_table(self):
        search_text = self._search_input.text().lower()
        show_inactive = self._show_inactive_cb.isChecked()

        filtered = []
        for item in self._items:
            if not show_inactive and item.get("is_active") != 1:
                continue
            if search_text:
                producto = item.get("producto", "").lower()
                if search_text not in producto:
                    continue
            filtered.append(item)

        self._populate_table(filtered)
        self._status_label.setText(f"Mostrando {len(filtered)} de {len(self._items)} registros")

    def _populate_table(self, items):
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(items))

        for row_idx, item in enumerate(items):
            producto_item = QTableWidgetItem(item.get("producto", ""))
            marca_item = QTableWidgetItem(item.get("marca", ""))
            tamano_item = QTableWidgetItem(item.get("tamano", ""))
            cantidad_item = QTableWidgetItem(str(item.get("cantidad", 0)))
            categoria_item = QTableWidgetItem(item.get("categoria", ""))
            proveedor_item = QTableWidgetItem(item.get("proveedor", ""))
            cant_minima_item = QTableWidgetItem(str(item.get("cant_minima", 0)))

            is_active = item.get("is_active", 1)
            if is_active == 1:
                estado = "Activo"
                estado_color = QColor(PRIMARY)
            else:
                estado = "Inactivo"
                estado_color = QColor(TEXT_MUTED)
            estado_item = QTableWidgetItem(estado)
            estado_item.setForeground(QBrush(estado_color))
            estado_item.setFont(QFont("Segoe UI", 10, QFont.Bold))

            self._table.setItem(row_idx, 0, producto_item)
            self._table.setItem(row_idx, 1, marca_item)
            self._table.setItem(row_idx, 2, tamano_item)
            self._table.setItem(row_idx, 3, cantidad_item)
            self._table.setItem(row_idx, 4, categoria_item)
            self._table.setItem(row_idx, 5, proveedor_item)
            self._table.setItem(row_idx, 6, cant_minima_item)
            self._table.setItem(row_idx, 7, estado_item)

            for c in range(self._table.columnCount()):
                if self._table.item(row_idx, c):
                    self._table.item(row_idx, c).setData(Qt.UserRole, item.get("id", ""))

        self._table.setSortingEnabled(True)

    def _on_selection_changed(self):
        selected_rows = self._table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            item_id = self._table.item(row, 0).data(Qt.UserRole)
            self._selected_item_id = item_id
            item = next((i for i in self._items if i.get("id") == item_id), None)

            can_edit = self._user_service.can_edit()
            is_admin = self._user_service.is_admin()
            is_active = item and item.get("is_active") == 1

            self._edit_btn.setEnabled(can_edit and bool(item))
            self._delete_btn.setEnabled(can_edit and bool(item) and is_active)
            self._restore_btn.setVisible(is_admin and bool(item) and not is_active)
        else:
            self._selected_item_id = None
            self._edit_btn.setEnabled(False)
            self._delete_btn.setEnabled(False)
            self._restore_btn.setVisible(False)

    def _add_item(self):
        if not self._user_service.can_edit():
            QMessageBox.warning(self, "Permiso denegado", "No tiene permisos para agregar insumos.")
            return

        from ui.item_form import ItemForm
        dialog = ItemForm(title="Agregar Insumo")
        if dialog.exec_():
            data = dialog.get_data()
            try:
                self._excel.add_item(data, self._user_service.get_current_user()["username"])
                QMessageBox.information(self, "Éxito", "Insumo agregado correctamente.")
                self.refresh()
            except PermissionError as e:
                QMessageBox.warning(self, "Archivo bloqueado", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar insumo:\n{str(e)}")

    def _edit_item(self):
        if not self._user_service.can_edit():
            QMessageBox.warning(self, "Permiso denegado", "No tiene permisos para editar insumos.")
            return

        if not self._selected_item_id:
            return

        item, _ = self._excel.get_item_by_id(self._selected_item_id)
        if not item:
            QMessageBox.warning(self, "Error", "Insumo no encontrado.")
            return

        from ui.item_form import ItemForm
        dialog = ItemForm(item=item, title="Editar Insumo")
        if dialog.exec_():
            data = dialog.get_data()
            try:
                success, status = self._excel.update_item(
                    self._selected_item_id, data,
                    self._user_service.get_current_user()["username"]
                )
                if status == "conflict":
                    reply = QMessageBox.warning(
                        self, "Conflicto de datos",
                        "Este registro fue modificado por otro usuario.\n"
                        "¿Desea sobrescribir los cambios?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        success, status = self._excel.update_item(
                            self._selected_item_id, data,
                            self._user_service.get_current_user()["username"],
                            force=True
                        )
                        QMessageBox.information(self, "Éxito", "Insumo actualizado correctamente (sobrescritura forzada).")
                    else:
                        return
                else:
                    QMessageBox.information(self, "Éxito", "Insumo actualizado correctamente.")
                self.refresh()
            except PermissionError as e:
                QMessageBox.warning(self, "Archivo bloqueado", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar insumo:\n{str(e)}")

    def _delete_item(self):
        if not self._user_service.can_edit():
            return

        if not self._selected_item_id:
            return

        reply = QMessageBox.question(
            self, "Confirmar desactivación",
            "¿Está seguro de desactivar este insumo?\n"
            "El registro no se eliminará, solo se marcará como inactivo.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self._excel.soft_delete(
                    self._selected_item_id,
                    self._user_service.get_current_user()["username"]
                )
                QMessageBox.information(self, "Éxito", "Insumo desactivado correctamente.")
                self.refresh()
            except PermissionError as e:
                QMessageBox.warning(self, "Archivo bloqueado", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al desactivar insumo:\n{str(e)}")

    def _restore_item(self):
        if not self._user_service.is_admin():
            QMessageBox.warning(self, "Permiso denegado", "Solo administradores pueden restaurar insumos.")
            return

        if not self._selected_item_id:
            return

        try:
            self._excel.restore_item(
                self._selected_item_id,
                self._user_service.get_current_user()["username"]
            )
            QMessageBox.information(self, "Éxito", "Insumo restaurado correctamente.")
            self.refresh()
        except PermissionError as e:
            QMessageBox.warning(self, "Archivo bloqueado", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al restaurar insumo:\n{str(e)}")
