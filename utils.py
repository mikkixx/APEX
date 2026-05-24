import sys
import os


def resource_path(relative: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath('.'), relative)


def reports_dir() -> str:
    if hasattr(sys, '_MEIPASS'):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath('.')
    path = os.path.join(base, 'reports')
    os.makedirs(path, exist_ok=True)
    return path
