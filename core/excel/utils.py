import os
import shutil
import tempfile


def is_file_locked(filepath):
    if not os.path.exists(filepath):
        return False
    folder = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    lock = os.path.join(folder, f"~${filename}")
    return os.path.exists(lock)


def safe_copy_for_reading(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    shutil.copy2(filepath, tmp.name)
    return tmp.name
