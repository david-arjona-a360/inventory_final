import json
import os
import hashlib

from core.auth.utils import hash_password as _hash_password
from core.auth.utils import get_windows_username
from config.settings import USERS_FILE


class UserService:

    def __init__(self):
        self._users_file = USERS_FILE
        self._current_user = None
        self._last_content_hash = None
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self._users_file), exist_ok=True)
        if not os.path.exists(self._users_file):
            default_users = [
                {"username": "admin", "password": _hash_password("admin"), "role": "admin", "type": "local"},
            ]
            self._save_users(default_users)

    def _load_users(self):
        with open(self._users_file, "r") as f:
            content = f.read()
        self._last_content_hash = hashlib.md5(content.encode()).hexdigest()
        return json.loads(content)

    def _save_users(self, users):
        if os.path.exists(self._users_file) and self._last_content_hash is not None:
            with open(self._users_file, "r") as f:
                current_content = f.read()
            current_hash = hashlib.md5(current_content.encode()).hexdigest()
            if current_hash != self._last_content_hash:
                print("Warning: users.json was modified by another user. Overwriting.")
        with open(self._users_file, "w") as f:
            json.dump(users, f, indent=2)
        with open(self._users_file, "r") as f:
            self._last_content_hash = hashlib.md5(f.read().encode()).hexdigest()

    def find_by_username(self, username):
        users = self._load_users()
        username = username.lower()
        for user in users:
            if user["username"].lower() == username:
                return user
        return None

    def try_windows_sso(self):
        win_user = get_windows_username()
        if not win_user:
            return None
        users = self._load_users()
        for user in users:
            if user["username"].lower() == win_user \
                    and user.get("type", "local") == "windows":
                self._current_user = user
                return user
        return None

    def authenticate(self, username, password):
        users = self._load_users()
        for user in users:
            if user["username"] != username:
                continue
            user_type = user.get("type", "local")
            if user_type == "windows":
                if username.lower() == get_windows_username():
                    self._current_user = user
                    return user
                return None
            if user.get("password") == _hash_password(password):
                self._current_user = user
                return user
        return None

    def get_current_user(self):
        return self._current_user

    def logout(self):
        self._current_user = None

    def get_all_users(self):
        return self._load_users()

    def create_user(self, username, password, role, user_type="local", created_by=None):
        users = self._load_users()
        if any(u["username"] == username for u in users):
            raise ValueError(f"User '{username}' already exists")
        if role not in ("admin", "editor", "viewer"):
            raise ValueError(f"Invalid role: {role}")
        user = {
            "username": username,
            "role": role,
            "type": user_type,
        }
        if user_type == "local":
            if not password:
                raise ValueError("Password is required for local users")
            user["password"] = _hash_password(password)
        else:
            user["password"] = ""
        users.append(user)
        self._save_users(users)

    def update_user(self, username, password=None, role=None, user_type=None):
        users = self._load_users()
        for user in users:
            if user["username"] == username:
                if role:
                    if role not in ("admin", "editor", "viewer"):
                        raise ValueError(f"Invalid role: {role}")
                    user["role"] = role
                if user_type is not None:
                    user["type"] = user_type
                    if user_type == "windows":
                        user["password"] = ""
                if password:
                    if user.get("type", "local") == "local":
                        user["password"] = _hash_password(password)
                self._save_users(users)
                return
        raise ValueError(f"User '{username}' not found")

    def delete_user(self, username):
        users = self._load_users()
        users = [u for u in users if u["username"] != username]
        self._save_users(users)

    def is_admin(self):
        return self._current_user and self._current_user.get("role") == "admin"

    def can_edit(self):
        if not self._current_user:
            return False
        return self._current_user.get("role") in ("admin", "editor")

    def can_view(self):
        return self._current_user is not None
