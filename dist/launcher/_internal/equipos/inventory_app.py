# ─────────────────────────────────────────────
#  inventory_app.py  –  Run this file to start
#  the app:  python inventory_app.py
# ─────────────────────────────────────────────

import subprocess
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from config      import COLUMNS, find_file_path
from excel_client import ExcelClient
import auth_manager

_theme_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Theme"))
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)
from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER, ROLE_COLORS, LOGO_PATH, LOGO_WIDTH,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def center_window(win, width, height):
    win.update_idletasks()
    x = (win.winfo_screenwidth()  - width)  // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


# ── Item Form (Add / Edit) ────────────────────────────────────────────────────

class ItemForm(tk.Toplevel):
    """Reusable form for adding and editing items."""

    def __init__(self, parent, title: str, initial_data: dict | None, on_save):
        super().__init__(parent)
        self.title(title)
        self.grab_set()
        form_height = max(480, len(COLUMNS) * 34 + 100)
        self.resizable(True, True)
        center_window(self, 460, form_height)

        self._on_save = on_save
        self._vars    = {}

        tk.Label(self, text=title, font=("Segoe UI", 12, "bold"),
                 fg=TEXT_DARK).pack(pady=(18, 8))

        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=(32, 0))
        scrollbar.pack(side="right", fill="y")

        form = tk.Frame(scrollable_frame)
        form.pack(fill="x")

        for i, col in enumerate(COLUMNS):
            tk.Label(form, text=col.title(), anchor="w", width=20,
                     fg=TEXT_DARK).grid(row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar(value=initial_data.get(col, "") if initial_data else "")
            self._vars[col] = var
            tk.Entry(form, textvariable=var, width=28, fg=TEXT_DARK).grid(
                row=i, column=1, sticky="w", pady=5)

        btn_row = len(COLUMNS)
        tk.Button(form, text="Save", width=13, bg=PRIMARY, fg=WHITE,
                  activebackground=DARK_RED, activeforeground=WHITE,
                  command=self._save).grid(row=btn_row, column=0, pady=(18, 4), sticky="e")
        tk.Button(form, text="Cancel", width=13, fg=TEXT_MUTED,
                  command=self.destroy).grid(row=btn_row, column=1, pady=(18, 4), sticky="w")

    def _save(self):
        data = {col: var.get().strip() for col, var in self._vars.items()}
        self._on_save(data)
        self.destroy()


# ── Main App ──────────────────────────────────────────────────────────────────

class InventoryApp(tk.Tk):

    def __init__(self, client: ExcelClient, session: dict):
        super().__init__()
        self.client  = client
        self.session = session                  # ← NEW: holds current user info

        self.title("Equipos - Inventory Manager")
        self.minsize(900, 500)
        center_window(self, 1150, 640)          # slightly taller for the toolbar

        self._items: list[dict] = []

        self._build_toolbar()
        self._build_table()
        self._build_statusbar()

        self.load_items()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_toolbar(self):
        bar = tk.Frame(self, pady=8, padx=12)
        bar.pack(fill="x")

        # ── Logo ───────────────────────────────────────────────────────────────
        try:
            pil_img = Image.open(LOGO_PATH)
            pil_img.thumbnail((LOGO_WIDTH, LOGO_WIDTH))
            self._logo_tk = ImageTk.PhotoImage(pil_img)
            tk.Label(bar, image=self._logo_tk, bg=bar.cget("bg")).pack(side="left", padx=(0, 10))
        except Exception:
            pass

        # ── Left side: title + logged-in user ─────────────────────────────────
        tk.Label(bar, text="IT Inventory",
                 font=("Segoe UI", 13, "bold"), fg=TEXT_DARK).pack(side="left")

        role_color = ROLE_COLORS.get(self.session.get("role", "viewer"), TEXT_MUTED)
        tk.Label(
            bar,
            text=f"  👤 {self.session.get('username', '')}  [{self.session.get('role', '')}]",
            font=("Segoe UI", 9),
            fg=role_color,
        ).pack(side="left", padx=(8, 0))

        # ── Right side: auth buttons first, then CRUD ─────────────────────────

        # Logout  (always visible)
        tk.Button(
            bar, text="⏻  Logout", width=12,
            fg=WHITE, bg=PRIMARY,
            activeforeground=WHITE, activebackground=DARK_RED,
            command=self._do_logout,
        ).pack(side="right", padx=4)

        # Manage Users  (admin only — hidden for other roles)
        if auth_manager.can_manage(self.session):
            tk.Button(
                bar, text="👥  Users", width=12,
                command=self._do_manage_users,
            ).pack(side="right", padx=4)

        # Separator
        tk.Label(bar, text="|", fg=BORDER).pack(side="right", padx=2)

        # CRUD buttons  (gated by role)
        tk.Button(bar, text="⟳  Refresh", width=12,
                  command=self.load_items).pack(side="right", padx=4)

        if auth_manager.can_delete(self.session):
            tk.Button(bar, text="🗑  Delete", width=12,
                      command=self.delete_item).pack(side="right", padx=4)

        if auth_manager.can_edit(self.session):
            tk.Button(bar, text="✏  Edit", width=12,
                      command=self.edit_item).pack(side="right", padx=4)

        if auth_manager.can_add(self.session):
            tk.Button(bar, text="＋  Add", width=12,
                      command=self.add_item).pack(side="right", padx=4)

        # Search
        tk.Label(bar, text="Search:", fg=TEXT_DARK).pack(side="left", padx=(24, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        tk.Entry(bar, textvariable=self.search_var, width=30, fg=TEXT_DARK).pack(side="left")

    def _build_table(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=WHITE,
                        foreground=TEXT_DARK,
                        rowheight=28,
                        fieldbackground=WHITE,
                        font=("Segoe UI", 10))
        style.map("Treeview",
                  background=[("selected", PRIMARY)],
                  foreground=[("selected", WHITE)])
        style.configure("Treeview.Heading",
                        background=LIGHT_BG,
                        foreground=TEXT_DARK,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[("active", BORDER)])

        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        display_cols = [c.title() for c in COLUMNS]
        self.tree = ttk.Treeview(
            container, columns=display_cols, show="headings", selectmode="browse")

        col_width = max(100, 1080 // len(display_cols))
        for col in display_cols:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=col_width, anchor="w", stretch=True)

        vsb = ttk.Scrollbar(container, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", lambda e: self.edit_item())

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Loading…")
        tk.Label(self, textvariable=self.status_var, anchor="w",
                 font=("Segoe UI", 9), fg=TEXT_MUTED, padx=12).pack(fill="x", pady=(0, 6))

    # ── Auth actions ──────────────────────────────────────────────────────────

    def _do_logout(self):
        if not messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            return
        auth_manager.logout(self.session)
        self.destroy()
        if hasattr(sys, '_MEIPASS'):
            subprocess.Popen([sys.executable, '--app-equipos'])
        else:
            launcher = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'launcher.py')
            subprocess.Popen([sys.executable, launcher, '--app-equipos'])

    def _do_manage_users(self):
        auth_manager.open_manage_users(self.session, parent=self)

    # ── Data helpers ──────────────────────────────────────────────────────────

    def _populate_table(self, items: list[dict]):
        self.tree.delete(*self.tree.get_children())
        for item in items:
            values = [item.get(col, "") for col in COLUMNS]
            self.tree.insert("", "end", iid=str(item["_row"]), values=values)
        self.status_var.set(f"{len(items)} record(s) loaded.  •  {self.client.file_path}")

    def _selected_item(self) -> dict | None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Please select a row first.")
            return None
        row_num = int(sel[0])
        return next((i for i in self._items if i["_row"] == row_num), None)

    def _on_search(self, *_):
        if hasattr(self, '_search_after') and self._search_after:
            self.after_cancel(self._search_after)
        self._search_after = self.after(200, self._do_search)

    def _do_search(self):
        self._search_after = None
        query = self.search_var.get().lower()
        filtered = (
            self._items if not query
            else [i for i in self._items if any(query in str(v).lower() for v in i.values())]
        )
        self._populate_table(filtered)

    def _sort_by(self, display_col: str):
        col = next((c for c in COLUMNS if c.title() == display_col), display_col)
        self._items.sort(key=lambda x: str(x.get(col, "")).lower())
        self._populate_table(self._items)

    def _check_lock(self) -> bool:
        if self.client.is_locked():
            return messagebox.askyesno(
                "File In Use",
                "The inventory file appears to be open in Excel by another user.\n\n"
                "Saving now may cause conflicts.\n\n"
                "Do you want to proceed anyway?",
            )
        return True

    # ── CRUD actions ──────────────────────────────────────────────────────────

    def load_items(self):
        self.status_var.set("Loading…")
        try:
            self._items = self.client.get_all_items()
            self._populate_table(self._items)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{e}")
            self.status_var.set("Error loading file.")

    def add_item(self):
        if not auth_manager.can_add(self.session):
            messagebox.showerror("Access Denied", "Your role does not allow adding items.")
            return
        if not self._check_lock():
            return

        def _save(data):
            try:
                new_row = self.client.add_item(data)
                new_item = {"_row": new_row, **data}
                self._items.append(new_item)
                values = [data.get(col, "") for col in COLUMNS]
                self.tree.insert("", "end", iid=str(new_row), values=values)
                self.status_var.set(
                    f"{len(self._items)} record(s) loaded.  •  {self.client.file_path}")
                self.status_var.set("Item added successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not add item:\n{e}")

        ItemForm(self, "Add New Item", None, _save)

    def edit_item(self):
        item = self._selected_item()
        if not item:
            return
        if not auth_manager.can_edit(self.session):
            messagebox.showerror("Access Denied", "Your role does not allow editing items.")
            return
        if not self._check_lock():
            return

        def _save(data):
            try:
                self.client.update_item(item["_row"], data)
                for i, existing in enumerate(self._items):
                    if existing["_row"] == item["_row"]:
                        self._items[i] = {**existing, **data}
                        break
                values = [data.get(col, "") for col in COLUMNS]
                self.tree.item(str(item["_row"]), values=values)
                self.status_var.set("Item updated successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not update item:\n{e}")

        ItemForm(self, "Edit Item", item, _save)

    def delete_item(self):
        item = self._selected_item()
        if not item:
            return

        if not auth_manager.can_delete(self.session):
            messagebox.showerror("Access Denied",
                                 "Only admins can delete records.")
            return

        if not self._check_lock():
            return

        name = (
            f"{item.get('FIRST NAME', '')} {item.get('LAST NAME', '')}".strip()
            or f"row {item['_row']}"
        )
        if not messagebox.askyesno("Confirm Delete",
                                   f"Permanently delete record for '{name}'?"):
            return

        try:
            deleted_row = item["_row"]
            self.client.delete_item(deleted_row)
            # Update in-memory state: remove item and shift rows below
            self._items = [i for i in self._items if i["_row"] != deleted_row]
            for i in self._items:
                if i["_row"] > deleted_row:
                    i["_row"] -= 1
            self._populate_table(self._items)
            self.status_var.set("Item deleted.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete item:\n{e}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    # ── Step 1: login ─────────────────────────
    temp_root = tk.Tk()
    temp_root.withdraw()

    session = auth_manager.login(parent=temp_root)

    if not session:
        # User closed/cancelled the login dialog → exit cleanly
        temp_root.destroy()
        return

    temp_root.destroy()

    # ── Step 2: find Excel file ───────────────
    file_path = find_file_path()

    if not file_path:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "File Not Found",
            "The inventory file could not be found.\n\n"
            "Please make sure:\n"
            "  1. OneDrive is running and synced\n"
            "  2. You have added the SharePoint folder shortcut to OneDrive\n"
            "  3. The file exists at:\n\n"
            "     OneDrive - a360inc \\ PTY Files - EQUIPOS \\\n"
            "     Formato_Inventario_TI.xlsx"
        )
        root.destroy()
        return

    # ── Step 3: load dynamic column names from Excel header ──
    from config import load_extra_columns
    load_extra_columns(file_path)

    # ── Step 4: launch the main app ───────────
    client = ExcelClient(file_path)
    app    = InventoryApp(client, session)      # ← pass session in
    app.mainloop()


if __name__ == "__main__":
    main()