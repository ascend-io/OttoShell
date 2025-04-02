# imports
import os
import glob
import shlex
import pyperclip

from difflib import unified_diff

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.completion import Completer, Completion

from otto_shell.utils import get_otto_shell_dir


# classes
class PathCompleter(Completer):
    def get_completions(self, document, complete_event):
        # Only run autocompletion for commands starting with '!'
        full_text = document.text_before_cursor
        if not full_text.startswith("!"):
            return

        # Only show completions when explicitly requested (e.g., on Tab press)
        if not complete_event.completion_requested:
            return

        # If text ends with a space, assume the token is complete
        if full_text.endswith(" "):
            file_fragment = ""
        else:
            try:
                parts = shlex.split(full_text)
            except ValueError:
                parts = full_text.split()
            file_fragment = parts[-1] if parts else ""

        start_position = -len(file_fragment)
        expanded = os.path.expanduser(file_fragment)
        matches = glob.glob(expanded + "*")
        for match in matches:
            yield Completion(match, start_position=start_position)


# functions
def get_input(prompt_text: str, history: FileHistory | InMemoryHistory) -> str:
    session = PromptSession(history=history, completer=PathCompleter())
    return session.prompt(prompt_text)


def get_user_input(prompt_text: str) -> str:
    """Ask the user for input.

    Args:
        prompt_text (str): The text to prompt the user with.
    Returns:
        str: The user's input.
    """
    history = FileHistory(os.path.join(get_otto_shell_dir(), "bots.history"))
    return get_input(prompt_text, history)


def confirm(text: str, *args, **kwargs) -> bool:
    confirmed = get_input(f"{text} (y/n): ", InMemoryHistory())
    if confirmed.lower() in ["y", "yes"]:
        return True
    else:
        return False


def _copy_to_clipboard(text: str) -> None:
    pyperclip.copy(text)


def copy_to_clipboard(text: str) -> str:
    _copy_to_clipboard(text)
    return "Successfully copied text to to clipboard"


def git_diff(old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = unified_diff(old_lines, new_lines, lineterm="")

    return "\n".join(diff)
