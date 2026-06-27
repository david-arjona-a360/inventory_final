import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# ── Base path (dev / PyInstaller) ──────────────────────────────────────────
def _get_base_dir():
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = _get_base_dir()

# ── App dispatch (PyInstaller multi-call) ──────────────────────────────────
if len(sys.argv) > 1:
    if sys.argv[1] == "--app-insumos":
        app_dir = os.path.join(BASE_DIR, "Insumos", "inventory_app")
        sys.path.insert(0, app_dir)
        os.chdir(os.path.join(BASE_DIR, "Insumos"))
        from main import main
        try:
            main()
        except SystemExit:
            pass
        sys.exit(0)
    elif sys.argv[1] == "--app-equipos-qt":
        app_dir = os.path.join(BASE_DIR, "equipos", "inventory_app_qt")
        sys.path.insert(0, app_dir)
        os.chdir(os.path.join(BASE_DIR, "equipos"))
        from main import main
        try:
            main()
        except SystemExit:
            pass
        sys.exit(0)
    elif sys.argv[1] == "--app-equipos":
        app_dir = os.path.join(BASE_DIR, "equipos")
        sys.path.insert(0, app_dir)
        os.chdir(app_dir)
        import inventory_app
        try:
            inventory_app.main()
        except SystemExit:
            pass
        sys.exit(0)

# ── First-run onboarding ───────────────────────────────────────────────────
import onboarding
onboarding.run()

# ── Theme ────────────────────────────────────────────────────────────────────
_theme_dir = os.path.join(BASE_DIR, "Theme")
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

try:
    from theme import (
        PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
        TEXT_DARK, TEXT_MUTED, BORDER, HOVER, LOGO_PATH,
    )
except ImportError:
    PRIMARY = "#df212b"; SECONDARY = "#796a6d"; ACCENT = "#8d3f44"
    LIGHT_BG = "#efe5e3"; WHITE = "#ffffff"; DARK_RED = "#b81a24"
    TEXT_DARK = "#3a3a3a"; TEXT_MUTED = "#796a6d"; BORDER = "#d9d0ce"
    HOVER = "#c91d26"; LOGO_PATH = ""

# ── App paths ────────────────────────────────────────────────────────────────

APPS = ["Insumos", "Equipos"]


class LauncherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Inventario - a360incPanama")
        self.root.resizable(False, False)
        self.root.configure(bg=WHITE)

        self._logo_img = None
        if LOGO_PATH and os.path.exists(LOGO_PATH):
            try:
                from PIL import Image, ImageTk
                img = Image.open(LOGO_PATH)
                img.thumbnail((100, 100))
                self._logo_img = ImageTk.PhotoImage(img)
            except ImportError:
                pass

        self._build_ui()
        self._center(520, 320)

    def _build_ui(self):
        if self._logo_img:
            lbl_logo = tk.Label(self.root, image=self._logo_img, bg=WHITE)
            lbl_logo.pack(pady=(30, 5))

        tk.Label(
            self.root,
            text="Sistema de Inventario",
            font=("Segoe UI", 18, "bold"),
            fg=TEXT_DARK, bg=WHITE,
        ).pack(pady=(5, 0))

        tk.Label(
            self.root,
            text="Seleccione el sistema que desea abrir",
            font=("Segoe UI", 11),
            fg=TEXT_MUTED, bg=WHITE,
        ).pack(pady=(0, 25))

        frm = tk.Frame(self.root, bg=WHITE)
        frm.pack(expand=True)

        for name in APPS:
            btn = tk.Button(
                frm,
                text=name,
                font=("Segoe UI", 14, "bold"),
                bg=PRIMARY, fg=WHITE,
                activebackground=DARK_RED, activeforeground=WHITE,
                relief="flat", padx=40, pady=14,
                cursor="hand2",
                command=lambda n=name: self._launch(n),
            )
            btn.pack(side="left", padx=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=DARK_RED))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=PRIMARY))

        tk.Label(self.root, text="", bg=WHITE).pack(pady=15)

    def _center(self, w, h):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _launch(self, name):
        flag = "--app-insumos" if name == "Insumos" else "--app-equipos"
        if hasattr(sys, '_MEIPASS'):
            exe = sys.executable
            workdir = os.path.dirname(sys.executable)
            cmd = [exe, flag]
        else:
            exe = sys.executable
            workdir = BASE_DIR
            cmd = [exe, os.path.abspath(__file__), flag]
        try:
            subprocess.Popen(cmd, cwd=workdir)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo iniciar {name}.\n\n{str(e)}"
            )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    LauncherApp().run()
