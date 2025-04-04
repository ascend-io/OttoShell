# imports
import os
import rich
import shutil
import subprocess

from rich.console import Console

from otto_shell.hci import get_input, copy_to_clipboard
from otto_shell.openai import question
from otto_shell.state import state, clear_state
from otto_shell.utils import get_otto_shell_model
from otto_shell.prompt import get_file_history
from otto_shell.commands import run_command
from otto_shell.flows.git import commit_flow

# console setup
console = Console()


def print_separator():
    width = shutil.get_terminal_size().columns
    console.print("-" * width, style="bold violet")


# functions
def display_splash():
    ascii_art = r"""
 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄         ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄            ▄            
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░▌          ▐░▌           
▐░█▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌       ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌          ▐░▌           
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌▐░▌          ▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌           
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌          ▐░▌           
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌▐░░░░░░░░░░▌▐░░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░▌          ▐░▌           
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌          ▐░▌           
▐░▌       ▐░▌     ▐░▌          ▐░▌     ▐░▌       ▐░▌          ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌          ▐░▌           
▐░█▄▄▄▄▄▄▄█░▌     ▐░▌          ▐░▌     ▐░█▄▄▄▄▄▄▄█░▌ ▄▄▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄▄▄  
▐░░░░░░░░░░░▌     ▐░▌          ▐░▌     ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌ 
 ▀▀▀▀▀▀▀▀▀▀▀       ▀            ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀
 """
    tagline = "(01001111 01110100 01110100 01101111 01010011 01101000 01100101 01101100 01101100)"
    console.print(ascii_art, style="violet")
    console.print(tagline, style="violet")


exit_commands = ["exit", "quit", "bye", "q", "x"]


def run_repl():
    display_splash()
    while True:
        try:
            user_input = get_input(
                f"{fish_style_cwd()} (os) > ", history=get_file_history()
            )
            if user_input in exit_commands:
                rich.print("exiting...")
                break
            decision_tree(user_input)
        except KeyboardInterrupt:
            continue
        except EOFError:
            rich.print("exiting...")
            break
        except Exception as e:
            rich.print(f"[red]{e}[/red]")
            continue


def decision_tree(user_input: str):
    if not user_input or user_input == "?":
        return
    elif user_input == "reset":
        clear_state()
        rich.print("reset state...")
    elif user_input.startswith("commit"):
        instructions = user_input.replace("commit", "").strip()
        commit_flow(instructions=instructions, all_files=True, confirm_commit=True)
    elif user_input == "model":
        rich.print(f"{get_otto_shell_model()}")
    elif user_input == "state":
        rich.print(state)
    elif user_input == "copy":
        if "last_otto_response" in state:
            copy_to_clipboard(state["last_otto_response"])
            rich.print("copied to clipboard")
        else:
            rich.print("nothing to copy")
    elif user_input.startswith("!"):
        subprocess.run(user_input[1:], shell=True, env=os.environ, cwd=os.getcwd())
    elif user_input.startswith("%"):
        try:
            exec(user_input[1:].strip())
        except Exception as e:
            rich.print(f"[red]{e}[/red]")
    elif user_input.startswith("?"):
        with console.status(
            f"asking Otto ({get_otto_shell_model()})...", spinner="dots"
        ):
            res = question(user_input[1:], history=state.get("shell_history", []))
        print_separator()
        rich.print(res) if res else None
        state["last_otto_response"] = res
        if "all_shell_history" not in state:
            state["all_shell_history"] = []
        state["all_shell_history"].extend(state.get("shell_history", []))
        state["shell_history"] = []

    else:
        res = run_command(user_input)
        rich.print(res) if res else None
        if "shell_history" not in state:
            state["shell_history"] = []
        state["shell_history"].append(f"{fish_style_cwd()} (OS) > {user_input}\n{res}")


def fish_style_cwd(path=None):
    """
    Convert a path to fish shell style abbreviated format.
    If no path is provided, uses the current working directory.
    - Uses ~ for paths in home directory
    - First letter abbreviation for intermediate directories
    - Preserves first and last components
    """

    if path is None:
        path = os.getcwd()

    # Special case for root directory
    if path == "/":
        return "/"

    # Handle home directory with ~
    home = os.path.expanduser("~")
    if path.startswith(home):
        path = "~" + path[len(home) :]

    # Split the path into components
    components = path.split(os.sep)
    # Filter out empty components that cause double slashes
    components = [c for c in components if c]

    # Handle empty components list (should only happen for root, which we handled above)
    if not components:
        return "/"

    # Handle absolute paths
    if path.startswith(os.sep):
        # For absolute paths outside of home, use / prefix
        result = ["/"]
        start_idx = 0
    elif path.startswith("~"):
        result = ["~"]
        start_idx = 1
    else:
        result = []
        start_idx = 0

    # Add first component (if we have more than one component and start_idx is valid)
    if len(components) > start_idx:
        if start_idx == 0 or len(components) > 1:
            result.append(components[start_idx])
            start_idx += 1

    # Abbreviate intermediate directories (keep just first letter)
    if len(components) > start_idx + 1:
        for component in components[start_idx:-1]:
            if component:  # Skip empty components
                result.append(component[0])

    # Keep the last component as is (if there are multiple components)
    if len(components) > start_idx and start_idx > 0:
        result.append(components[-1])

    # Join with the separator
    formatted_path = os.sep.join(result)

    # For special case of root subdirectories like /usr, avoid double slash
    if formatted_path.startswith("//"):
        formatted_path = formatted_path[1:]

    return formatted_path
