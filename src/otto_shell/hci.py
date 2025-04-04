# imports
import os
import pyperclip

from typing import Iterable, List, Optional
from difflib import unified_diff

from prompt_toolkit import PromptSession
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.history import FileHistory, InMemoryHistory
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings


# keybindings
kb = KeyBindings()


@kb.add("enter")
def submit(event):
    event.current_buffer.validate_and_handle()


@kb.add("right")
def newline(event):
    event.current_buffer.insert_text("\n")


# prompt continuation
def prompt_continuation(width, line_number, is_soft_wrap):
    return "█" * width


# classes
class PathCompleter(Completer):
    def __init__(
        self,
        only_directories: bool = False,
        expanduser: bool = True,
        file_filter: Optional[callable] = None,
    ):
        self.only_directories = only_directories
        self.expanduser = expanduser
        self.file_filter = file_filter
        self._executable_cache = None

        # Commands that should only complete directories
        self.directory_commands = {"cd", "pushd", "rmdir", "mkdir"}

        # Commands that commonly use file/path arguments
        self.file_commands = {
            "rm",
            "cp",
            "mv",
            "cat",
            "less",
            "more",
            "vim",
            "grep",
            "head",
            "tail",
            "touch",
            "chmod",
            "chown",
            "ln",
            "wc",
            "diff",
            "find",
            "tar",
            "zip",
            "unzip",
            "gzip",
        }

    def get_completions(
        self, document: Document, complete_event
    ) -> Iterable[Completion]:
        # Only provide completions when tab is pressed
        if not complete_event.completion_requested:
            return

        text = document.text_before_cursor

        # If no text, nothing to complete
        if not text.strip():
            return

        # Parse the command line
        parts = self._parse_command_line(text)
        command = parts["command"]
        current_word = parts["current_word"]
        is_option = parts["is_option"]
        expecting_path = parts["expecting_path"]

        # Complete executables at the beginning of the line
        if len(parts["words"]) == 1 and not text.endswith(" "):
            yield from self._get_executables_completions(current_word)
            return

        # If the current word starts with '-' and not at path position, don't complete
        if is_option and not expecting_path:
            return

        # Determine if we should only complete directories
        only_dirs = self.only_directories or command in self.directory_commands

        # Complete paths
        if expecting_path or not is_option:
            yield from self._get_path_completions(current_word, only_dirs=only_dirs)

    def _parse_command_line(self, text: str) -> dict:
        """Parse the command line to extract command, options, and current word."""
        # Split the text into words
        words = []
        current_word = ""

        # Handle multi-word commands with spaces, respecting quotes
        in_quotes = False
        quote_char = None
        escaped = False

        for char in text:
            if escaped:
                current_word += char
                escaped = False
            elif char == "\\":
                escaped = True
            elif char in ('"', "'"):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current_word += char
            elif char.isspace() and not in_quotes:
                if current_word:
                    words.append(current_word)
                    current_word = ""
            else:
                current_word += char

        # If we have a current word, add it
        if current_word:
            words.append(current_word)

        # Default values
        result = {
            "words": words,
            "command": words[0] if words else "",
            "current_word": words[-1] if words else "",
            "is_option": False,
            "expecting_path": False,
        }

        # If text ends with space, we're expecting a new word
        if text.endswith(" "):
            result["current_word"] = ""
            result["expecting_path"] = True
        else:
            result["is_option"] = result["current_word"].startswith("-")

            # Check if we're in a position to expect a path
            # For commands that take file args, we expect a path after any flag
            if (
                result["command"] in self.file_commands
                or result["command"] in self.directory_commands
            ):
                # After a flag with = (like --file=path)
                if "=" in result["current_word"] and result["is_option"]:
                    prefix_parts = result["current_word"].split("=", 1)
                    result["current_word"] = prefix_parts[1]
                    result["is_option"] = False
                    result["expecting_path"] = True
                # Or after a space following any word
                elif len(words) > 1:
                    result["expecting_path"] = True

        return result

    def _get_executables_completions(self, prefix: str) -> Iterable[Completion]:
        if not prefix:
            return

        # Lazy load the executable list
        if self._executable_cache is None:
            self._executable_cache = self._get_executables()

        for executable in self._executable_cache:
            if executable.startswith(prefix):
                yield Completion(executable, start_position=-len(prefix))

    def _get_executables(self) -> List[str]:
        executables = set()

        for path_dir in os.environ.get("PATH", "").split(os.pathsep):
            if not path_dir:
                continue

            path_dir = os.path.expanduser(path_dir)

            if not os.path.isdir(path_dir):
                continue

            try:
                for filename in os.listdir(path_dir):
                    full_path = os.path.join(path_dir, filename)

                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        executables.add(filename)
            except OSError:
                # Handle cases where we don't have permission to list the directory
                continue

        return sorted(executables)

    def _get_path_completions(
        self, prefix: str, only_dirs: bool = False
    ) -> Iterable[Completion]:
        # Handle empty prefix
        if not prefix:
            directory = "."
            partial = ""  # This should be empty, not "."
        # Handle root directory specially
        elif prefix == "/":
            directory = "/"
            partial = ""
        else:
            # Expand ~ to user's home directory
            if self.expanduser and prefix.startswith("~"):
                prefix = os.path.expanduser(prefix)

            # Handle absolute paths that might be just the root
            if os.path.isabs(prefix) and os.path.dirname(prefix) == "":
                directory = "/"
                partial = ""
            else:
                # Split into directory and partial name
                directory = os.path.dirname(prefix) or "."
                partial = os.path.basename(prefix)

                # Special handling for absolute paths
                if os.path.isabs(prefix) and directory == "":
                    directory = "/"

        # Get all files/directories in that directory
        try:
            filenames = os.listdir(directory)
        except OSError:
            return

        # Filter and sort results
        filenames = [f for f in filenames if f.startswith(partial)]

        for filename in sorted(
            filenames,
            key=lambda name: (
                not os.path.isdir(os.path.join(directory, name)),
                name.lower(),
            ),
        ):
            full_path = os.path.join(directory, filename)

            # Skip files if only_directories is True or we're in cd context
            if only_dirs and not os.path.isdir(full_path):
                continue

            # Apply custom file_filter if provided
            if self.file_filter is not None and not self.file_filter(full_path):
                continue

            # Add directory separator for directories
            display = filename
            if os.path.isdir(full_path):
                display = filename + os.path.sep

            # Calculate the correct completion text
            if directory == "/":
                # For root directory, we need to ensure the path starts with /
                completion_text = "/" + display if os.path.isabs(prefix) else display
            else:
                completion_text = display

            yield Completion(completion_text, start_position=-len(partial))


# functions
def get_input(prompt_text: str, history: FileHistory | InMemoryHistory) -> str:
    session = PromptSession(
        history=history,
        completer=PathCompleter(),
        editing_mode=EditingMode.VI,
        key_bindings=kb,
        multiline=True,
        prompt_continuation=prompt_continuation,
    )
    return session.prompt(prompt_text).strip()


def confirm(text: str) -> bool:
    confirmed = get_input(f"{text} (y/n): ", InMemoryHistory())
    if confirmed.lower() in ["y", "yes"]:
        return True
    else:
        return False


def copy_to_clipboard(text: str) -> None:
    pyperclip.copy(text)


def git_diff(old_text: str, new_text: str) -> str:
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = unified_diff(old_lines, new_lines, lineterm="")

    return "\n".join(diff)
