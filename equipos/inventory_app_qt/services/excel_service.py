import os
import shutil
import openpyxl

from config.settings import COLUMNS, SHEET_NAME, get_excel_path
from utils.excel_utils import is_file_locked


class ExcelService:

    def __init__(self):
        self._filepath = None
        self._wb = None

    @property
    def filepath(self):
        return get_excel_path()

    def _load_workbook(self):
        path = self.filepath
        if not os.path.exists(path):
            raise FileNotFoundError(f"Excel file not found: {path}")
        if is_file_locked(path):
            raise PermissionError(
                "The Excel file is currently open in another program.\n"
                "Please close it and try again."
            )
        self._wb = openpyxl.load_workbook(path)
        return self._wb

    def _get_sheet(self):
        if SHEET_NAME in self._wb.sheetnames:
            return self._wb[SHEET_NAME]
        return self._wb.active

    def _get_header_map(self, sheet):
        return {
            cell.value.strip().upper(): cell.column
            for cell in sheet[1]
            if cell.value
        }

    def _backup(self):
        path = self.filepath
        backup_path = path + ".bak"
        try:
            shutil.copy2(path, backup_path)
        except OSError:
            pass

    def _save(self):
        path = self.filepath
        self._wb.save(path)

    def _row_to_dict(self, sheet, row_num, header_map, check_empty=False):
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

    def get_all_items(self):
        self._load_workbook()
        ws = self._get_sheet()
        h_map = self._get_header_map(ws)
        items = []
        for row_num in range(2, ws.max_row + 1):
            item = self._row_to_dict(ws, row_num, h_map, check_empty=True)
            if item is not None:
                items.append(item)
        return items

    def add_item(self, data):
        self._load_workbook()
        ws = self._get_sheet()
        h_map = self._get_header_map(ws)
        new_row = ws.max_row + 1
        for col_name in COLUMNS:
            col_idx = h_map.get(col_name.upper())
            if col_idx:
                ws.cell(row=new_row, column=col_idx, value=data.get(col_name, ""))
        self._backup()
        self._save()
        return new_row

    def update_item(self, row_num, data):
        self._load_workbook()
        ws = self._get_sheet()
        h_map = self._get_header_map(ws)
        for col_name in COLUMNS:
            col_idx = h_map.get(col_name.upper())
            if col_idx:
                ws.cell(row=row_num, column=col_idx, value=data.get(col_name, ""))
        self._backup()
        self._save()

    def delete_item(self, row_num):
        self._load_workbook()
        ws = self._get_sheet()
        ws.delete_rows(row_num)
        self._backup()
        self._save()
