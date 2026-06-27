import os
import json
import hashlib
import shutil
import logging

log = logging.getLogger("auth_service")

from config import find_shared_dir, USERS_JSON_PATH

_theme_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "Theme"))
if _theme_dir not in os.sys.path:
    os.sys.path.insert(0, _theme_dir)

shared_dir = find_shared_dir()
if shared_dir:
    USERS_FILE = os.path.join(shared_dir, "users.json")
    if not os.path.exists(USERS_FILE):
        try:
            shutil.copy2(USERS_JSON_PATH, USERS_FILE)
        except Exception:
            pass
else:
    USERS_FILE = USERS_JSON_PATH

LOCAL_ADMIN_USERNAME = "localadmin"
LOCAL_ADMIN_DEFAULT_PW = "Admin@1234"

ROLES = ("admin", "editor", "viewer")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        _bootstrap_users()
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        _bootstrap_users()
        with open(USERS_FILE, "r") as f:
            return json.load(f)


def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def _bootstrap_users():
    default = {
        LOCAL_ADMIN_USERNAME: {
            "password": hash_password(LOCAL_ADMIN_DEFAULT_PW),
            "role": "admin",
            "type": "local",
        }
    }
    save_users(default)


def users_to_list(users_dict: dict) -> list:
    result = []
    for idx, (username, info) in enumerate(users_dict.items()):
        result.append({
            "id": idx + 1,
            "username": username,
            "password": info.get("password", ""),
            "role": info.get("role", "viewer"),
            "status": info.get("status", "active"),
            "type": info.get("type", "local"),
        })
    return result


def users_from_list(users_list: list) -> dict:
    result = {}
    for user in users_list:
        username = user.get("username", "").strip()
        if not username:
            continue
        result[username] = {
            "password": user.get("password", ""),
            "role": user.get("role", "viewer"),
            "type": user.get("type", "local"),
            "status": user.get("status", "active"),
        }
    return result


def get_windows_username() -> str:
    return (os.environ.get("USERNAME") or os.environ.get("USER") or "").lower().strip()


def login() -> dict | None:
    users = load_users()
    win_user = get_windows_username()
    if win_user and win_user in users and users[win_user]["type"] == "windows":
        return {
            "username": win_user,
            "role": users[win_user]["role"],
            "type": "windows",
        }
    return None


def authenticate(username: str, password: str) -> dict | None:
    users = load_users()
    username = username.strip().lower()
    if username in users:
        user = users[username]
        if user["type"] == "windows":
            if username == get_windows_username():
                return {"username": username, "role": user["role"], "type": "windows"}
            return None
        if user["password"] == hash_password(password):
            return {"username": username, "role": user["role"], "type": "local"}
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
