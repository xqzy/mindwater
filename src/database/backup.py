import os
import shutil

def rotate_backups(db_path: str, max_backups: int = 9):
    """
    Rotates database backups in a round-robin fashion.
    Keeps max_backups versions (e.g., .1 through .9).
    """
    if not os.path.exists(db_path):
        return

    # 1. Remove the oldest backup if it exists
    oldest = f"{db_path}.{max_backups}"
    if os.path.exists(oldest):
        os.remove(oldest)

    # 2. Shift existing backups (8 -> 9, 7 -> 8, ..., 1 -> 2)
    for i in range(max_backups - 1, 0, -1):
        src = f"{db_path}.{i}"
        dst = f"{db_path}.{i+1}"
        if os.path.exists(src):
            os.rename(src, dst)

    # 3. Create the newest backup from the current live database
    newest = f"{db_path}.1"
    shutil.copy2(db_path, newest)
