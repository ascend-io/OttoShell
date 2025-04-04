import os

from prompt_toolkit.history import FileHistory

from otto_shell.utils import get_otto_shell_dir


def get_file_history():
    history_file = os.path.join(get_otto_shell_dir(), "os.history")
    if not os.path.exists(history_file):
        return FileHistory(history_file)
    return FileHistory(history_file)
