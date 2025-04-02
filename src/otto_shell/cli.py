# imports
import os
import typer
import subprocess

from rich import print
from typing import List

from otto_shell.utils import get_otto_shell_dir

# typer config
## main app
app_kwargs = {
    "no_args_is_help": False,
    "add_completion": False,
    "context_settings": {"help_option_names": ["-h", "--help"]},
}
app = typer.Typer(help="otto_shell", **app_kwargs)


# command
@app.command()
def shell(
    text: List[str] = typer.Argument(None, help="input text"),
    config: bool = typer.Option(False, "--config", "-c", help="configure OttoShell"),
    vim: bool = typer.Option(
        False, "--vim", "-v", help="configure with vim (overrides $EDITOR)"
    ),
    env: bool = typer.Option(False, "--env", "-e", help="configure the .env file"),
):
    if config:
        program = "vim" if vim else os.environ.get("EDITOR", "vim")
        filename = ".env" if env else "system.md"
        filename = os.path.join(get_otto_shell_dir(), filename)
        print(f"opening {filename} with {program}...")
        subprocess.call([program, f"{filename}"])
    elif text is None:
        print("shelling...")
    else:
        text = " ".join(text)
        if text.strip():
            print(text)
        else:
            print("no text provided")
