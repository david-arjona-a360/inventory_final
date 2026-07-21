import os
import sys
from datetime import datetime

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
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QSpinBox, QComboBox, QGroupBox,
    QGridLayout, QAbstractItemView, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class ReportBuilderView(QWidget):

    def __init__(self, excel_service, report_service):
        super().__init__()
        self._excel = excel_service
        self._report = report_service
        self._current_data = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        header = QLabel("Generador de Reportes")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(header)

        filters_group = QGroupBox("Filtros")
        filters_layout = QGridLayout()
        filters_layout.setSpacing(8)

        filters_layout.addWidget(QLabel("Categoría:"), 0, 0)
        self._categoria_combo = QComboBox()
        self._categoria_combo.setEditable(True)
        self._categoria_combo.setMinimumHeight(30)
        filters_layout.addWidget(self._categoria_combo, 0, 1)

        filters_layout.addWidget(QLabel("Producto:"), 1, 0)
        self._producto_input = QLineEdit()
        self._producto_input.setPlaceholderText("Buscar por nombre...")
        self._producto_input.setMinimumHeight(30)
        filters_layout.addWidget(self._producto_input, 1, 1)

        filters_layout.addWidget(QLabel("Cantidad mínima:"), 2, 0)
        self._cantidad_min = QSpinBox()
        self._cantidad_min.setMinimum(0)
        self._cantidad_min.setMaximum(999999)
        self._cantidad_min.setMinimumHeight(30)
        filters_layout.addWidget(self._cantidad_min, 2, 1)

        filters_layout.addWidget(QLabel("Cantidad máxima:"), 3, 0)
        self._cantidad_max = QSpinBox()
        self._cantidad_max.setMinimum(0)
        self._cantidad_max.setMaximum(999999)
        self._cantidad_max.setValue(999999)
        self._cantidad_max.setMinimumHeight(30)
        filters_layout.addWidget(self._cantidad_max, 3, 1)

        self._include_inactive_cb = QCheckBox("Incluir insumos inactivos")
        filters_layout.addWidget(self._include_inactive_cb, 4, 0, 1, 2)

        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)

        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Aplicar Filtros")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.setMinimumHeight(36)
        apply_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        apply_btn.clicked.connect(self._apply_filters)
        btn_layout.addWidget(apply_btn)

        clear_btn = QPushButton("Limpiar Filtros")
        clear_btn.setMinimumHeight(36)
        clear_btn.clicked.connect(self._clear_filters)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Producto", "Marca", "Tamaño", "Cantidad", "Categoría"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)

        font = QFont("Segoe UI", 10)
        self._table.setFont(font)
        self._table.verticalHeader().setDefaultSectionSize(30)

        layout.addWidget(self._table)

        export_layout = QHBoxLayout()
        export_layout.addStretch()

        export_excel_btn = QPushButton("Exportar a Excel")
        export_excel_btn.setObjectName("primaryBtn")
        export_excel_btn.setMinimumHeight(36)
        export_excel_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        export_excel_btn.clicked.connect(self._export_excel)
        export_layout.addWidget(export_excel_btn)

        export_pdf_btn = QPushButton("Exportar a PDF")
        export_pdf_btn.setObjectName("primaryBtn")
        export_pdf_btn.setMinimumHeight(36)
        export_pdf_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        export_pdf_btn.clicked.connect(self._export_pdf)
        export_layout.addWidget(export_pdf_btn)

        self._result_label = QLabel("")
        self._result_label.setFont(QFont("Segoe UI", 9))
        self._result_label.setStyleSheet(f"color: {TEXT_MUTED};")
        export_layout.addWidget(self._result_label)

        layout.addLayout(export_layout)
        self._apply_styles()
        self.setLayout(layout)

        self._load_categories()

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

    def _load_categories(self):
        try:
            items = self._excel.get_all_items(include_inactive=True)
            categories = sorted(set(
                item.get("categoria", "") for item in items if item.get("categoria")
            ))
            self._categoria_combo.clear()
            self._categoria_combo.addItem("")
            self._categoria_combo.addItems(categories)
        except Exception:
            pass

    def _apply_filters(self):
        filters = {}
        categoria = self._categoria_combo.currentText().strip()
        if categoria:
            filters["categoria"] = categoria

        producto = self._producto_input.text().strip()
        if producto:
            filters["producto"] = producto

        cant_min = self._cantidad_min.value()
        if cant_min > 0:
            filters["cantidad_min"] = cant_min

        cant_max = self._cantidad_max.value()
        if cant_max < 999999:
            filters["cantidad_max"] = cant_max

        try:
            all_items = self._excel.get_all_items(
                include_inactive=self._include_inactive_cb.isChecked()
            )
            if filters:
                self._current_data = self._report.generate_report_data(filters)
            else:
                self._current_data = all_items

            self._populate_table(self._current_data)
            self._result_label.setText(f"Resultados: {len(self._current_data)} registros")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar reporte:\n{str(e)}")

    def _clear_filters(self):
        self._categoria_combo.setCurrentIndex(0)
        self._producto_input.clear()
        self._cantidad_min.setValue(0)
        self._cantidad_max.setValue(999999)
        self._include_inactive_cb.setChecked(False)
        self._current_data = []
        self._table.setRowCount(0)
        self._result_label.setText("")

    def _populate_table(self, items):
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(items))

        for row_idx, item in enumerate(items):
            self._table.setItem(row_idx, 0, QTableWidgetItem(item.get("producto", "")))
            self._table.setItem(row_idx, 1, QTableWidgetItem(item.get("marca", "")))
            self._table.setItem(row_idx, 2, QTableWidgetItem(item.get("tamano", "")))
            self._table.setItem(row_idx, 3, QTableWidgetItem(str(item.get("cantidad", 0))))
            self._table.setItem(row_idx, 4, QTableWidgetItem(item.get("categoria", "")))

        self._table.setSortingEnabled(True)

    def _export_excel(self):
        if not self._current_data:
            QMessageBox.warning(self, "Sin datos", "No hay datos para exportar. Aplique filtros primero.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"reporte_insumos_{timestamp}.xlsx"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte Excel", default_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )
        if not filepath:
            return

        try:
            self._report.export_to_excel(self._current_data, filepath)
            QMessageBox.information(self, "Éxito", f"Reporte exportado a:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar a Excel:\n{str(e)}")

    def _export_pdf(self):
        if not self._current_data:
            QMessageBox.warning(self, "Sin datos", "No hay datos para exportar. Aplique filtros primero.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"reporte_insumos_{timestamp}.pdf"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte PDF", default_name,
            "PDF Files (*.pdf);;All Files (*)"
        )
        if not filepath:
            return

        try:
            self._report.export_to_pdf(self._current_data, filepath)
            QMessageBox.information(self, "Éxito", f"Reporte exportado a:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar a PDF:\n{str(e)}")
