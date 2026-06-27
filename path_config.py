import os
import glob
import sys
import logging
import tempfile

_DIAG_LOG = os.path.join(tempfile.gettempdir(), "inventory_diag.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(_DIAG_LOG, mode="a"),
        logging.StreamHandler(sys.stderr),
    ],
    force=True,
)
log = logging.getLogger("path_config")
log.info("=== DIAGNOSTIC: path_config loaded ===")
log.info("sys.executable: %s", sys.executable)
log.info("sys._MEIPASS present: %s", hasattr(sys, "_MEIPASS"))
if hasattr(sys, "_MEIPASS"):
    log.info("sys._MEIPASS: %s", sys._MEIPASS)
log.info("CWD: %s", os.getcwd())
log.info("USERNAME env: %s", os.environ.get("USERNAME", "NOT SET"))
log.info("USERPROFILE env: %s", os.environ.get("USERPROFILE", "NOT SET"))
log.info("HOME env: %s", os.environ.get("HOME", "NOT SET"))
log.info("expanduser(~): %s", os.path.expanduser("~"))

ONEDRIVE_ORG = "a360inc"


def get_windows_username():
    return os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"


def _try_find_onedrive_root():
    methods = []

    log.info("OneDrive env vars: OneDriveCommercial=%s OneDriveConsumer=%s",
             os.environ.get("OneDriveCommercial", "NOT SET"),
             os.environ.get("OneDriveConsumer", "NOT SET"))

    onedrive_env = os.environ.get("OneDriveCommercial") or os.environ.get("OneDriveConsumer")
    if onedrive_env:
        log.info("Method 0 (OneDrive env var): %s", onedrive_env)
        if os.path.isdir(onedrive_env):
            log.info("Method 0 directory exists: %s", onedrive_env)
            methods.append(("onedrive-env", onedrive_env))

    m1_home = os.path.expanduser("~")
    p1 = os.path.join(m1_home, f"OneDrive - {ONEDRIVE_ORG}*")
    matches1 = glob.glob(p1)
    log.info("Method 1 (expanduser ~ + glob): home=%s pattern=%s matches=%s", m1_home, p1, matches1)
    if matches1:
        methods.append(("expanduser+glob", matches1[0]))

    m2_profile = os.environ.get("USERPROFILE")
    if m2_profile:
        p2 = os.path.join(m2_profile, f"OneDrive - {ONEDRIVE_ORG}*")
        matches2 = glob.glob(p2)
        log.info("Method 2 (USERPROFILE + glob): profile=%s pattern=%s matches=%s", m2_profile, p2, matches2)
        if matches2:
            methods.append(("userprofile+glob", matches2[0]))

    m3_homedrive = os.environ.get("HOMEDRIVE", "")
    m3_homepath = os.environ.get("HOMEPATH", "")
    if m3_homedrive and m3_homepath:
        m3_base = os.path.join(m3_homedrive, m3_homepath.lstrip("\\"))
        p3 = os.path.join(m3_base, f"OneDrive - {ONEDRIVE_ORG}*")
        matches3 = glob.glob(p3)
        log.info("Method 3 (HOMEDRIVE+HOMEPATH + glob): base=%s pattern=%s matches=%s", m3_base, p3, matches3)
        if matches3:
            methods.append(("homepath+glob", matches3[0]))

    fallback_username = get_windows_username()
    fallback_path = rf"C:\Users\{fallback_username}\OneDrive - {ONEDRIVE_ORG}"
    log.info("Fallback candidate path: %s", fallback_path)
    if os.path.isdir(fallback_path):
        methods.append(("fallback-username", fallback_path))
    else:
        log.info("Fallback path does not exist as directory: %s", fallback_path)

    for method, path in methods:
        log.info("Candidate from %s: %s", method, path)
        if os.path.isdir(path):
            log.info("SELECTED method=%s path=%s", method, path)
            return path
        log.warning("Candidate path not directory: %s", path)

    log.error("ALL OneDrive discovery methods FAILED")
    return None


def find_onedrive_root():
    result = _try_find_onedrive_root()
    log.info("find_onedrive_root -> %s", result)
    return result


EQUIPOS_FOLDER = "PTY Files - EQUIPOS"
EQUIPOS_FILE = "Formato_Inventario_TI.xlsx"


def get_equipos_path():
    root = find_onedrive_root()
    if root:
        result = os.path.join(root, EQUIPOS_FOLDER)
        log.info("get_equipos_path -> %s (exists=%s)", result, os.path.isdir(result))
        return result
    log.warning("get_equipos_path -> None (root not found)")
    return None


def get_equipos_file_path():
    path = get_equipos_path()
    if path:
        result = os.path.join(path, EQUIPOS_FILE)
        log.info("get_equipos_file_path -> %s (exists=%s)", result, os.path.isfile(result))
        return result
    return None


INSUMOS_FOLDER = "PTY Files - INSUMOS"
INSUMOS_FILE = "Inventario_Insumos.xlsx"


def get_insumos_path():
    root = find_onedrive_root()
    if root:
        result = os.path.join(root, INSUMOS_FOLDER)
        log.info("get_insumos_path -> %s (exists=%s)", result, os.path.isdir(result))
        return result
    log.warning("get_insumos_path -> None (root not found)")
    return None


def get_insumos_file_path():
    path = get_insumos_path()
    if path:
        result = os.path.join(path, INSUMOS_FILE)
        log.info("get_insumos_file_path -> %s (exists=%s)", result, os.path.isfile(result))
        return result
    return None
