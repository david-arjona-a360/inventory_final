# ─────────────────────────────────────────────
#  excel_client.py  –  All read/write logic
#  for the Excel file. The GUI never touches
#  the file directly.
# ─────────────────────────────────────────────

import os
import shutil
import openpyxl
from config import COLUMNS, SHEET_NAME
from core.excel.utils import is_file_locked


class ExcelClient:
    """Handles CRUD operations on the inventory Excel file."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_workbook(self):
        return openpyxl.load_workbook(self.file_path)

    def _get_header_row(self, sheet) -> dict:
        """Return {column_name: col_index} from row 1."""
        return {
            cell.value.strip().upper(): cell.column
            for cell in sheet[1]
            if cell.value
        }

    def _backup(self):
        """Create a .bak copy before destructive writes."""
        backup_path = self.file_path + ".bak"
        try:
            shutil.copy2(self.file_path, backup_path)
        except OSError:
            pass

    def _row_to_dict(self, sheet, row_num: int, header_map: dict, check_empty: bool = False) -> dict | None:
        """Convert a sheet row into a display dict. Returns None if row is empty."""
        item = {"_row": row_num}
        all_empty = True
        for col_name in COLUMNS:
            col_idx = header_map.get(col_name.upper())
            val = sheet.cell(row=row_num, column=col_idx).value or "" if col_idx else ""
            item[col_name] = val
            if check_empty and str(val).strip():
                all_empty = False
        if check_empty and all_empty:
            return None
        return item

    # ── File lock detection ───────────────────────────────────────────────────

    def is_locked(self) -> bool:
        """Delegate to shared core utility."""
        return is_file_locked(self.file_path)

    # ── Public API ────────────────────────────────────────────────────────────

    def get_all_items(self) -> list[dict]:
        """Return all data rows as a list of dicts."""
        wb     = self._load_workbook()
        if SHEET_NAME in wb.sheetnames:
            ws = wb[SHEET_NAME]
        else:
            ws = wb.active
        h_map  = self._get_header_row(ws)
        items  = []

        for row_num in range(2, ws.max_row + 1):
            item = self._row_to_dict(ws, row_num, h_map, check_empty=True)
            if item is not None:
                items.append(item)

        wb.close()
        return items

    def add_item(self, data: dict) -> int:
        """Append a new row to the Excel file. Returns the new row number."""
        wb    = self._load_workbook()
        if SHEET_NAME in wb.sheetnames:
            ws = wb[SHEET_NAME]
        else:
            ws = wb.active
        h_map = self._get_header_row(ws)

        new_row = ws.max_row + 1
        for col_name in COLUMNS:
            col_idx = h_map.get(col_name.upper())
            if col_idx:
                ws.cell(row=new_row, column=col_idx, value=data.get(col_name, ""))

        self._backup()
        wb.save(self.file_path)
        wb.close()
        return new_row

    def update_item(self, row_num: int, data: dict) -> None:
        """Update an existing row in the Excel file."""
        wb    = self._load_workbook()
        if SHEET_NAME in wb.sheetnames:
            ws = wb[SHEET_NAME]
        else:
            ws = wb.active
        h_map = self._get_header_row(ws)

        for col_name in COLUMNS:
            col_idx = h_map.get(col_name.upper())
            if col_idx:
                ws.cell(row=row_num, column=col_idx, value=data.get(col_name, ""))

        self._backup()
        wb.save(self.file_path)
        wb.close()

    def delete_item(self, row_num: int) -> None:
        """Delete a row from the Excel file."""
        wb = self._load_workbook()
        if SHEET_NAME in wb.sheetnames:
            ws = wb[SHEET_NAME]
        else:
            ws = wb.active
        ws.delete_rows(row_num)
        self._backup()
        wb.save(self.file_path)
        wb.close()