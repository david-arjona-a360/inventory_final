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
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER, ROLE_COLORS,
)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QLabel, QLineEdit,
    QAbstractItemView, QCheckBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QBrush

from config.settings import COLUMNS
from services.auth_service import can_add, can_edit, can_delete
from core.excel.utils import is_file_locked
from icons import icon_add, icon_edit, icon_delete, icon_refresh, icon_search
from ui.item_form import ItemForm


class InventoryView(QWidget):

    def __init__(self, excel_client, session):
        super().__init__()
        self._client = excel_client
        self._session = session
        self._items = []
        self._selected_row = None
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        header = QLabel("IT Equipment Inventory")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)

        toolbar = QHBoxLayout()

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search across all fields...")
        self._search_input.setMinimumHeight(32)
        self._search_input.addAction(icon_search(TEXT_MUTED, 18), QLineEdit.LeadingPosition)
        self._search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self._search_input)

        refresh_btn = QPushButton(icon_refresh(TEXT_DARK), "Refresh")
        refresh_btn.setObjectName("actionBtn")
        refresh_btn.setMinimumHeight(36)
        refresh_btn.setIconSize(refresh_btn.iconSize() * 1.2)
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)

        layout.addLayout(toolbar)

        display_cols = [c.title() for c in COLUMNS]
        self._table = QTableWidget()
        self._table.setColumnCount(len(display_cols))
        self._table.setHorizontalHeaderLabels(display_cols)
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

        if can_add(self._session):
            self._add_btn = QPushButton(icon_add(WHITE, 18), "Add Item")
            self._add_btn.setObjectName("primaryBtn")
            self._add_btn.setMinimumHeight(36)
            self._add_btn.setIconSize(self._add_btn.iconSize() * 1.2)
            self._add_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self._add_btn.clicked.connect(self._add_item)
            action_bar.addWidget(self._add_btn)

        self._edit_btn = QPushButton(icon_edit(TEXT_DARK, 18), "Edit Selected")
        self._edit_btn.setMinimumHeight(36)
        self._edit_btn.setIconSize(self._edit_btn.iconSize() * 1.2)
        self._edit_btn.setFont(QFont("Segoe UI", 10))
        self._edit_btn.setEnabled(False)
        self._edit_btn.clicked.connect(self._edit_item)
        action_bar.addWidget(self._edit_btn)

        if can_delete(self._session):
            self._delete_btn = QPushButton(icon_delete(PRIMARY, 18), "Delete")
            self._delete_btn.setObjectName("dangerBtn")
            self._delete_btn.setMinimumHeight(36)
            self._delete_btn.setIconSize(self._delete_btn.iconSize() * 1.2)
            self._delete_btn.setFont(QFont("Segoe UI", 10))
            self._delete_btn.setEnabled(False)
            self._delete_btn.clicked.connect(self._delete_item)
            action_bar.addWidget(self._delete_btn)

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

    def _on_search(self, text):
        if hasattr(self, '_search_timer') and self._search_timer is not None:
            self._search_timer.stop()
            self._search_timer.deleteLater()
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._search_timer.start(200)

    def _do_search(self):
        self._search_timer = None
        query = self._search_input.text().lower()
        if not query:
            self._populate_table(self._items)
            self._status_label.setText(
                f"Showing {len(self._items)} of {len(self._items)} records"
            )
            return
        filtered = [
            i for i in self._items
            if any(query in str(v).lower() for v in i.values())
        ]
        self._populate_table(filtered)
        self._status_label.setText(
            f"Showing {len(filtered)} of {len(self._items)} records"
        )

    def _on_selection_changed(self):
        selected = self._table.selectedItems()
        if selected:
            self._selected_row = selected[0].row()
            self._edit_btn.setEnabled(can_edit(self._session))
            if can_delete(self._session) and hasattr(self, '_delete_btn'):
                self._delete_btn.setEnabled(True)
        else:
            self._selected_row = None
            self._edit_btn.setEnabled(False)
            if hasattr(self, '_delete_btn'):
                self._delete_btn.setEnabled(False)

    def refresh(self):
        self._status_label.setText("Loading...")
        try:
            self._items = self._client.get_all_items()
            self._populate_table(self._items)
            self._status_label.setText(
                f"{len(self._items)} record(s) loaded.  \u2022  {self._client.filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")
            self._status_label.setText("Error loading file.")

    def _populate_table(self, items):
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(items))
        display_cols = [c.title() for c in COLUMNS]

        for row_idx, item in enumerate(items):
            for col_idx, col_name in enumerate(COLUMNS):
                val = item.get(col_name, "")
                table_item = QTableWidgetItem(str(val))
                table_item.setData(Qt.UserRole, item.get("_row", ""))
                self._table.setItem(row_idx, col_idx, table_item)

        self._table.setSortingEnabled(True)

    def _get_selected_item(self):
        if self._selected_row is None:
            QMessageBox.information(self, "No selection", "Please select a row first.")
            return None
        item_id = self._table.item(self._selected_row, 0).data(Qt.UserRole)
        return next((i for i in self._items if str(i.get("_row", "")) == str(item_id)), None)

    def _check_lock(self):
        if is_file_locked(self._client.filepath):
            reply = QMessageBox.question(
                self, "File In Use",
                "The inventory file appears to be open in Excel by another user.\n\n"
                "Saving now may cause conflicts.\n\n"
                "Do you want to proceed anyway?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    def _add_item(self):
        if not self._check_lock():
            return
        dialog = ItemForm(title="Add New Item")
        if dialog.exec_():
            data = dialog.get_data()
            try:
                new_row = self._client.add_item(data)
                new_item = {"_row": new_row, **data}
                self._items.append(new_item)
                self.refresh()
                self._status_label.setText("Item added successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not add item:\n{e}")

    def _edit_item(self):
        item = self._get_selected_item()
        if not item:
            return
        if not self._check_lock():
            return
        dialog = ItemForm(item=item, title="Edit Item")
        if dialog.exec_():
            data = dialog.get_data()
            try:
                self._client.update_item(item["_row"], data)
                self.refresh()
                self._status_label.setText("Item updated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update item:\n{e}")

    def _delete_item(self):
        item = self._get_selected_item()
        if not item:
            return
        if not self._check_lock():
            return

        name = (
            f"{item.get('FIRST NAME', '')} {item.get('LAST NAME', '')}".strip()
            or f"row {item['_row']}"
        )
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Permanently delete record for '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self._client.delete_item(item["_row"])
                self._items = [i for i in self._items if i["_row"] != item["_row"]]
                for i in self._items:
                    if i["_row"] > item["_row"]:
                        i["_row"] -= 1
                self._populate_table(self._items)
                self._status_label.setText("Item deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete item:\n{e}")
