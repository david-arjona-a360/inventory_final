import sys
import os
import logging
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_DIAG_LOG_MAIN = os.path.join(tempfile.gettempdir(), "inventory_diag.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(_DIAG_LOG_MAIN, mode="a"),
        logging.StreamHandler(sys.stderr),
    ],
    force=True,
)
log = logging.getLogger("main")

log.info("=== DIAGNOSTIC: main.py loaded ===")
log.info("sys.executable: %s", sys.executable)
log.info("sys._MEIPASS present: %s", hasattr(sys, "_MEIPASS"))
if hasattr(sys, "_MEIPASS"):
    log.info("sys._MEIPASS: %s", sys._MEIPASS)
log.info("CWD: %s", os.getcwd())
log.info("__file__: %s", __file__)
log.info("sys.argv: %s", sys.argv)
log.info("USERNAME: %s", os.environ.get("USERNAME", "NOT SET"))
log.info("USERPROFILE: %s", os.environ.get("USERPROFILE", "NOT SET"))
log.info("HOME: %s", os.environ.get("HOME", "NOT SET"))
log.info("HOMEDRIVE: %s", os.environ.get("HOMEDRIVE", "NOT SET"))
log.info("HOMEPATH: %s", os.environ.get("HOMEPATH", "NOT SET"))

_theme_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Theme")
)
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

from theme import (
    PRIMARY, SECONDARY, ACCENT, LIGHT_BG, WHITE, DARK_RED,
    TEXT_DARK, TEXT_MUTED, BORDER, HOVER,
)
from qss import build_stylesheet

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from config.settings import APP_NAME, get_excel_path
from services.user_service import UserService
from services.excel_service import ExcelService
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


APP_STYLESHEET = build_stylesheet({
    "PRIMARY": PRIMARY, "SECONDARY": SECONDARY, "ACCENT": ACCENT,
    "LIGHT_BG": LIGHT_BG, "WHITE": WHITE, "DARK_RED": DARK_RED,
    "TEXT_DARK": TEXT_DARK, "TEXT_MUTED": TEXT_MUTED, "BORDER": BORDER,
    "HOVER": HOVER,
})


def main():
    log.info("=== MAIN() STARTED ===")
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)

    excel_path = get_excel_path()
    log.info("main(): resolved excel_path=%s exists=%s", excel_path, os.path.exists(excel_path))
    if not os.path.exists(excel_path):
        log.critical("main(): Excel file NOT FOUND at %s", excel_path)
        QMessageBox.critical(
            None, "Archivo no encontrado",
            f"Excel file not found at expected location\n\n{excel_path}"
        )
        sys.exit(1)

    log.info("main(): file exists, proceeding")

    user_service = UserService()
    excel_service = ExcelService()

    try:
        log.info("main(): calling excel_service.ensure_structure()")
        excel_service.ensure_structure()
    except PermissionError as e:
        log.critical("main(): PermissionError: %s", e)
        QMessageBox.critical(None, "Archivo bloqueado", str(e))
        sys.exit(1)
    except Exception as e:
        log.critical("main(): Exception during ensure_structure: %s", e, exc_info=True)
        QMessageBox.critical(None, "Error de inicialización",
                             f"Error al inicializar el archivo Excel:\n{str(e)}\n\n"
                             f"Asegúrese de que la ruta existe:\n{excel_path}")
        sys.exit(1)

    # ── Try Windows SSO auto-login ──────────────────────────────
    sso_user = user_service.try_windows_sso()
    if sso_user:
        print(f"[Auth] Windows SSO auto-login: {sso_user['username']} ({sso_user.get('role')})")
    else:
        print("[Auth] No Windows SSO match, showing login dialog")
        login = LoginDialog(user_service)
        if login.exec_() != LoginDialog.Accepted:
            sys.exit(0)

    log.info("main(): Opening main window for user: %s", user_service.get_current_user())
    window = MainWindow(user_service, excel_service)
    window.show()
    log.info("main(): entering event loop")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
