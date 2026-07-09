import os


def is_file_locked(filepath):
    if not os.path.exists(filepath):
        return False
    folder = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    lock = os.path.join(folder, f"~${filename}")
    return os.path.exists(lock)
