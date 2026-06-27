# ─────────────────────────────────────────────
#  auth_manager.py  –  Authentication, user
#  management, login / logout for Inventory App
# ─────────────────────────────────────────────

import os
import json
import hashlib
import subprocess
import sys
import shutil
import logging
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("auth_manager")

# ── SHARED USER DATABASE (ONEDRIVE) ──────────
from config import find_shared_dir, USERS_JSON_PATH

_theme_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Theme"))
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)
from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER, ROLE_COLORS,
)

shared_dir = find_shared_dir()
if shared_dir:
    USERS_FILE = os.path.join(shared_dir, "users.json")
    log.info("USERS_FILE set to OneDrive shared path: %s", USERS_FILE)

    if not os.path.exists(USERS_FILE):
        try:
            shutil.copy2(USERS_JSON_PATH, USERS_FILE)
            log.info("Copied bundled users.json to shared location: %s", USERS_FILE)
        except Exception as e:
            log.warning("Could not copy bundled users.json to shared location: %s", e)
else:
    USERS_FILE = USERS_JSON_PATH
    log.warning(
        "OneDrive shared folder NOT FOUND — falling back to LOCAL users.json: %s",
        USERS_FILE
    )
# ─────────────────────────────────────────────

LOCAL_ADMIN_USERNAME   = "localadmin"
LOCAL_ADMIN_DEFAULT_PW = "Admin@1234"   # ← Change via Manage Users after first login

# ── Roles ─────────────────────────────────────
ROLES = ("admin", "editor", "viewer")


# ──────────────────────────────────────────────
#  Internal helpers
# ──────────────────────────────────────────────

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        _bootstrap_users()
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        _bootstrap_users()
        with open(USERS_FILE, "r") as f:
            return json.load(f)


def _save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def _bootstrap_users():
    """Create users.json with localadmin on first run."""
    default = {
        LOCAL_ADMIN_USERNAME: {
            "password": _hash(LOCAL_ADMIN_DEFAULT_PW),
            "role":     "admin",
            "type":     "local",
        }
    }
    _save_users(default)


def _windows_username() -> str:
    """Return the current Windows login username, lowercase."""
    return (os.environ.get("USERNAME") or os.environ.get("USER") or "").lower().strip()


# ──────────────────────────────────────────────
#  Login
# ──────────────────────────────────────────────

def _show_first_run_instructions():
    """Shows the INSTRUCTIONS.txt content in a popup if it's the first time."""
    flag_file = os.path.join(os.path.dirname(USERS_FILE), ".first_run_done")
    if not os.path.exists(flag_file):
        try:
            # Try to read the instructions file we bundled
            instr_path = USERS_JSON_PATH.replace("users.json", "INSTRUCTIONS.txt")
            if os.path.exists(instr_path):
                with open(instr_path, "r") as f:
                    content = f.read()
                
                # Create a simple scrollable instruction window
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("First Run Instructions", content)
                root.destroy()
                
                # Mark as done so it doesn't show again
                with open(flag_file, "w") as f:
                    f.write("done")
        except:
            pass

def login(parent=None) -> dict | None:
    """
    Try Windows SSO first. If the Windows username is registered
    as a 'windows' type user → silent auto-login.
    Otherwise → show manual login dialog.
    """
    # Show instructions to new users
    _show_first_run_instructions()
    
    users       = _load_users()
    win_user    = _windows_username()

    if win_user and win_user in users and users[win_user]["type"] == "windows":
        return {
            "username": win_user,
            "role":     users[win_user]["role"],
            "type":     "windows",
        }

    return _login_dialog(parent)


def _login_dialog(parent=None) -> dict | None:
    """Modal login window — returns session dict or None."""
    dlg = tk.Toplevel(parent) if parent else tk.Tk()
    dlg.title("Equipos — Login")
    dlg.resizable(False, False)
    dlg.grab_set()

    dlg.update_idletasks()
    w, h = 360, 260
    x = (dlg.winfo_screenwidth()  - w) // 2
    y = (dlg.winfo_screenheight() - h) // 2
    dlg.geometry(f"{w}x{h}+{x}+{y}")

    result = {"session": None}

    tk.Label(dlg, text="🔐  Equipos",
             font=("Segoe UI", 13, "bold"), fg=TEXT_DARK).pack(pady=(24, 4))
    tk.Label(dlg, text="Please log in to continue",
             font=("Segoe UI", 9), fg=TEXT_MUTED).pack(pady=(0, 16))

    form = tk.Frame(dlg, padx=32)
    form.pack(fill="x")

    tk.Label(form, text="Username:", anchor="w").grid(row=0, column=0, sticky="w", pady=4)
    uname_var = tk.StringVar()
    tk.Entry(form, textvariable=uname_var, width=24).grid(row=0, column=1, sticky="w", pady=4)

    tk.Label(form, text="Password:", anchor="w").grid(row=1, column=0, sticky="w", pady=4)
    pwd_var = tk.StringVar()
    tk.Entry(form, textvariable=pwd_var, show="*", width=24).grid(row=1, column=1, sticky="w", pady=4)

    def _attempt():
        users = _load_users()
        uname = uname_var.get().strip().lower()
        pwd   = pwd_var.get()

        if not uname or not pwd:
            messagebox.showwarning("Missing fields", "Please enter username and password.", parent=dlg)
            return

        if uname in users and users[uname]["type"] == "local" \
                and users[uname]["password"] == _hash(pwd):
            result["session"] = {
                "username": uname,
                "role":     users[uname]["role"],
                "type":     "local",
            }
            dlg.destroy()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.", parent=dlg)

    def _cancel():
        dlg.destroy()

    tk.Button(dlg, text="Login", width=16, bg=PRIMARY, fg=WHITE,
              activebackground=DARK_RED, activeforeground=WHITE,
              command=_attempt).pack(pady=(20, 4))
    tk.Button(dlg, text="Cancel", width=16, command=_cancel,
              fg=TEXT_MUTED).pack()

    dlg.bind("<Return>", lambda e: _attempt())
    dlg.protocol("WM_DELETE_WINDOW", _cancel)
    dlg.wait_window()
    return result["session"]


def logout(session: dict, restart_callback=None):
    session.clear()
    if restart_callback:
        restart_callback()


# ──────────────────────────────────────────────
#  Manage Users  (admin only)
# ──────────────────────────────────────────────

def open_manage_users(session: dict, parent=None):
    """Full user-management window. Only admins may open it."""
    if session.get("role") != "admin":
        messagebox.showerror("Access Denied",
                             "Only administrators can manage users.", parent=parent)
        return

    win = tk.Toplevel(parent)
    win.title("Manage Users")
    win.resizable(False, False)
    win.grab_set()

    win.update_idletasks()
    w, h = 580, 420
    x = (win.winfo_screenwidth()  - w) // 2
    y = (win.winfo_screenheight() - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(win, text="👥  User Management",
             font=("Segoe UI", 12, "bold"), fg=TEXT_DARK).pack(pady=(16, 4))

    frame = tk.Frame(win, padx=16)
    frame.pack(fill="both", expand=True)

    cols = ("Username", "Role", "Type")
    tree = ttk.Treeview(frame, columns=cols, show="headings",
                            height=10, selectmode="browse")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=160, anchor="w")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    frame.columnconfigure(0, weight=1)

    def _refresh():
        tree.delete(*tree.get_children())
        for uname, info in _load_users().items():
            tree.insert("", "end", iid=uname,
                        values=(uname, info["role"], info["type"]))

    _refresh()

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=12)

    def _selected_username() -> str | None:
        sel = tree.selection()
        return sel[0] if sel else None

    def _add():
        add_win = tk.Toplevel(win)
        add_win.title("Add User")
        add_win.resizable(False, False)
        add_win.grab_set()
        add_win.geometry("360x320")

        tk.Label(add_win, text="Add New User",
                 font=("Segoe UI", 11, "bold")).pack(pady=(16, 8))

        f = tk.Frame(add_win, padx=28)
        f.pack(fill="x")

        fields = {}

        def _row(label, key, show=None, row=0):
            tk.Label(f, text=label, anchor="w").grid(
                row=row, column=0, sticky="w", pady=5)
            var = tk.StringVar()
            e   = tk.Entry(f, textvariable=var, width=22, show=show or "")
            e.grid(row=row, column=1, sticky="w", pady=5)
            fields[key] = var

        _row("Username:",  "uname", row=0)

        tk.Label(f, text="Type:", anchor="w").grid(row=1, column=0, sticky="w", pady=5)
        type_var = tk.StringVar(value="windows")
        rb_frame = tk.Frame(f)
        rb_frame.grid(row=1, column=1, sticky="w")
        tk.Radiobutton(rb_frame, text="Windows SSO", variable=type_var,
                       value="windows").pack(side="left")
        tk.Radiobutton(rb_frame, text="Local",       variable=type_var,
                       value="local").pack(side="left")

        pwd_label = tk.Label(f, text="Password:", anchor="w")
        pwd_label.grid(row=2, column=0, sticky="w", pady=5)
        pwd_var_field = tk.StringVar()
        pwd_entry = tk.Entry(f, textvariable=pwd_var_field, show="*", width=22)
        pwd_entry.grid(row=2, column=1, sticky="w", pady=5)

        def _toggle_pwd(*_):
            state = "normal" if type_var.get() == "local" else "disabled"
            pwd_entry.config(state=state)
        type_var.trace_add("write", _toggle_pwd)
        _toggle_pwd()

        tk.Label(f, text="Role:", anchor="w").grid(row=3, column=0, sticky="w", pady=5)
        role_var = tk.StringVar(value="viewer")
        tk.OptionMenu(f, role_var, *ROLES).grid(row=3, column=1, sticky="w")

        def _save_new():
            uname = fields["uname"].get().strip().lower()
            utype = type_var.get()
            role  = role_var.get()
            pwd   = pwd_var_field.get()

            if not uname:
                messagebox.showwarning("Missing", "Username is required.", parent=add_win)
                return
            users = _load_users()
            if uname in users:
                messagebox.showerror("Exists",
                                     f"User '{uname}' already exists.", parent=add_win)
                return
            if utype == "local" and not pwd:
                messagebox.showwarning("Missing", "Password required for local users.", parent=add_win)
                return

            users[uname] = {
                "password": _hash(pwd) if utype == "local" else "",
                "role":     role,
                "type":     utype,
            }
            _save_users(users)
            _refresh()
            add_win.destroy()
            messagebox.showinfo("Added", f"User '{uname}' added successfully.", parent=win)

        tk.Button(add_win, text="Add User", width=16, bg=PRIMARY, fg=WHITE,
                  activebackground=DARK_RED, activeforeground=WHITE,
                  command=_save_new).pack(pady=(16, 4))
        tk.Button(add_win, text="Cancel",   width=16, fg=TEXT_MUTED,
                  command=add_win.destroy).pack()

    def _remove():
        uname = _selected_username()
        if not uname:
            messagebox.showwarning("No selection", "Select a user to remove.", parent=win)
            return
        if uname == LOCAL_ADMIN_USERNAME:
            messagebox.showerror("Protected",
                                 "The localadmin account cannot be removed.", parent=win)
            return
        if uname == session.get("username"):
            messagebox.showerror("Error",
                                 "You cannot remove your own account.", parent=win)
            return
        if messagebox.askyesno("Confirm", f"Remove user '{uname}'?", parent=win):
            users = _load_users()
            users.pop(uname, None)
            _save_users(users)
            _refresh()

    def _change_pwd():
        uname = _selected_username()
        if not uname:
            messagebox.showwarning("No selection", "Select a user to change password.", parent=win)
            return
        users = _load_users()
        if users[uname]["type"] == "windows":
            messagebox.showinfo("Windows User",
                                f"'{uname}' uses Windows domain authentication.\n"
                                "Change their password in Active Directory / Microsoft 365.",
                                parent=win)
            return
        new_pwd = simpledialog.askstring("Change Password",
                                         f"New password for '{uname}':",
                                         show="*", parent=win)
        if new_pwd:
            users[uname]["password"] = _hash(new_pwd)
            _save_users(users)
            messagebox.showinfo("Updated", "Password changed successfully.", parent=win)

    def _change_role():
        uname = _selected_username()
        if not uname:
            messagebox.showwarning("No selection", "Select a user to change role.", parent=win)
            return
        if uname == LOCAL_ADMIN_USERNAME:
            messagebox.showerror("Protected",
                                 "The localadmin role cannot be changed.", parent=win)
            return

        role_win = tk.Toplevel(win)
        role_win.title("Change Role")
        role_win.resizable(False, False)
        role_win.grab_set()
        role_win.geometry("280x180")

        tk.Label(role_win, text=f"Change role for '{uname}'",
                 font=("Segoe UI", 10, "bold")).pack(pady=(20, 8))

        users    = _load_users()
        role_var = tk.StringVar(value=users[uname]["role"])
        tk.OptionMenu(role_win, role_var, *ROLES).pack(pady=8)

        def _save_role():
            users = _load_users()
            users[uname]["role"] = role_var.get()
            _save_users(users)
            _refresh()
            role_win.destroy()

        tk.Button(role_win, text="Save", width=14, bg=PRIMARY, fg=WHITE,
                  activebackground=DARK_RED, activeforeground=WHITE,
                  command=_save_role).pack(pady=6)
        tk.Button(role_win, text="Cancel", width=14, fg=TEXT_MUTED,
                  command=role_win.destroy).pack()

    tk.Button(btn_frame, text="➕  Add User",        width=16,
              fg=WHITE, bg=PRIMARY, activeforeground=WHITE, activebackground=DARK_RED,
              command=_add).grid(row=0, column=0, padx=6)
    tk.Button(btn_frame, text="🗑  Remove User",     width=16,
              fg=WHITE, bg=PRIMARY, activeforeground=WHITE, activebackground=DARK_RED,
              command=_remove).grid(row=0, column=1, padx=6)
    tk.Button(btn_frame, text="🔑  Change Password", width=16,
              fg=WHITE, bg=PRIMARY, activeforeground=WHITE, activebackground=DARK_RED,
              command=_change_pwd).grid(row=0, column=2, padx=6)
    tk.Button(btn_frame, text="🔒  Change Role",     width=16,
              fg=WHITE, bg=PRIMARY, activeforeground=WHITE, activebackground=DARK_RED,
              command=_change_role).grid(row=1, column=0, padx=6, pady=6, columnspan=3)

    win.wait_window()


# ──────────────────────────────────────────────
#  Role-based permission helpers
# ──────────────────────────────────────────────

def can_add(session: dict)    -> bool: return session.get("role") in ("admin", "editor")
def can_edit(session: dict)   -> bool: return session.get("role") in ("admin", "editor")
def can_delete(session: dict) -> bool: return session.get("role") == "admin"
def can_manage(session: dict) -> bool: return session.get("role") == "admin"