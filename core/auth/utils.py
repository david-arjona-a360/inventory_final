import os
import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_windows_username() -> str:
    return (os.environ.get("USERNAME") or os.environ.get("USER") or "").lower().strip()
