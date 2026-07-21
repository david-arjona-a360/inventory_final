import os
import sys
import json
import shutil
import logging

from core.auth.utils import hash_password, get_windows_username

log = logging.getLogger("auth_service")

from config.settings import USERS_FILE, USERS_JSON_PATH

_theme_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "Theme"))
if _theme_dir not in sys.path:
    sys.path.insert(0, _theme_dir)

_shared_dir = os.path.dirname(USERS_FILE)
if _shared_dir and os.path.isdir(_shared_dir):
    if not os.path.exists(USERS_FILE):
        try:
            shutil.copy2(USERS_JSON_PATH, USERS_FILE)
        except Exception:
            pass

LOCAL_ADMIN_USERNAME = "localadmin"
LOCAL_ADMIN_DEFAULT_PW = "Admin@1234"

ROLES = ("admin", "editor", "viewer")


def _migrate_dict_to_list(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        result = []
        for username, info in data.items():
            result.append({
                "username": username,
                "password": info.get("password", ""),
                "role": info.get("role", "viewer"),
                "type": info.get("type", "local"),
                "status": info.get("status", "active"),
            })
        return result
    return []


def load_users() -> list:
    if not os.path.exists(USERS_FILE):
        _bootstrap_users()
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        _bootstrap_users()
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
    users = _migrate_dict_to_list(data)
    if isinstance(data, dict):
        save_users(users)
    return users


def save_users(users: list):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _bootstrap_users():
    default = [
        {
            "username": LOCAL_ADMIN_USERNAME,
            "password": hash_password(LOCAL_ADMIN_DEFAULT_PW),
            "role": "admin",
            "type": "local",
            "status": "active",
        }
    ]
    save_users(default)


def _find_user(users, username):
    username = username.lower()
    for u in users:
        if u.get("username", "").lower() == username:
            return u
    return None


def login() -> dict | None:
    users = load_users()
    win_user = get_windows_username()
    user = _find_user(users, win_user)
    if user and user.get("type") == "windows":
        return {
            "username": user["username"],
            "role": user["role"],
            "type": "windows",
        }
    return None


def authenticate(username: str, password: str) -> dict | None:
    users = load_users()
    user = _find_user(users, username)
    if user:
        if user.get("type") == "windows":
            if user["username"].lower() == get_windows_username():
                return {"username": user["username"], "role": user["role"], "type": "windows"}
            return None
        if user.get("password") == hash_password(password):
            return {"username": user["username"], "role": user["role"], "type": "local"}
    return None


def logout(session: dict):
    session.clear()


def can_add(session: dict) -> bool:
    return session.get("role") in ("admin", "editor")


def can_edit(session: dict) -> bool:
    return session.get("role") in ("admin", "editor")


def can_delete(session: dict) -> bool:
    return session.get("role") == "admin"


def can_manage(session: dict) -> bool:
    return session.get("role") == "admin"
