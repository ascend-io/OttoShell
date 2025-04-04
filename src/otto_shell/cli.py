# imports
import os
import rich
import typer
import subprocess

from typing import List, Optional

from otto_shell.repl import run_repl
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
    # configuration
    config: bool = typer.Option(False, "--config", "-c", help="configure OttoShell"),
    vim: bool = typer.Option(
        False, "--vim", "-v", help="configure with vim (overrides $EDITOR)"
    ),
    env: bool = typer.Option(
        False, "--env", "-e", help="configure the .env file (secrets)"
    ),
    # arguments
    args: Optional[List[str]] = typer.Argument(None, help="input text"),
):
    if config:
        program = "vim" if vim else os.environ.get("EDITOR", "vim")
        filename = ".env" if env else "config.toml"
        filename = os.path.join(get_otto_shell_dir(), filename)
        rich.print(f"opening {filename} with {program}...")
        subprocess.call(f"{program} {filename}", shell=True)
    elif args is None:
        run_repl()
    else:
        text = " ".join(args)
        if text.strip():
            rich.print(text)
        else:
            rich.print("no text provided")
