# imports
import os
import subprocess

from otto_shell.utils import get_otto_shell_aliases

# Define interactive apps once
INTERACTIVE_APPS = [
    "vim",
    "nvim",
    "nano",
    "less",
    "more",
    "top",
    "htop",
    "btop",
    "vi",
    "v",
]
COMMANDS_OVERRIDES = get_otto_shell_aliases()


def run_command(cmd: str, verbose: bool = False) -> str:
    """Run a command and return its output"""
    if cmd.strip() in COMMANDS_OVERRIDES:
        cmd = COMMANDS_OVERRIDES[cmd.strip()]

    if cmd.strip() == "os":
        raise ValueError("no os recursion allowed!")
    elif cmd.strip() == "cd":
        os.chdir(os.path.expanduser("~"))
        return ""
    elif cmd.strip().startswith("cd "):
        os.chdir(os.path.expanduser(cmd.strip().split(" ")[1]))
        return ""
    elif cmd.strip() == "clear":
        # os.system("clear")
        subprocess.run("clear", shell=True)
        return ""

    full_cmd = f"zsh -c 'source ~/.bash_aliases && {cmd}'"

    actual_cmd = cmd.strip().split()[0] if cmd.strip().split() else ""
    if actual_cmd in INTERACTIVE_APPS:
        subprocess.run(full_cmd, shell=True, env=os.environ, cwd=os.getcwd())
        return ""

    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=os.environ,
            cwd=os.getcwd(),
        )

        if verbose:
            return "\n".join(
                filter(
                    None,
                    [
                        f"command: {cmd}",
                        f"return code: {result.returncode}",
                        f"stdout:\n{result.stdout}" if result.stdout else "",
                        f"stderr:\n{result.stderr}" if result.stderr else "",
                    ],
                )
            )
        else:
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += result.stderr
            return output.strip()

    except Exception as e:
        return f"Error: {str(e)}"
