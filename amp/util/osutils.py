import os
import errno

def makedirs(path, mode=0o777, exist_ok=False):
    try:
        os.makedirs(path, mode)
    except OSError as exc:
        if not exist_ok or exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise
