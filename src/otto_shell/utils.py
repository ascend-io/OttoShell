import os
import glob
import uuid
import tomllib
import textwrap

from dotenv import load_dotenv
from datetime import UTC, datetime


def now():
    return datetime.now(UTC)


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_otto_shell_dir() -> str:
    dirpath = os.path.join(os.path.expanduser("~"), ".otto_shell")
    os.makedirs(dirpath, exist_ok=True)
    return dirpath


def get_otto_shell_config() -> dict:
    filepath = os.path.join(get_otto_shell_dir(), "config.toml")
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "rb") as f:
        config = tomllib.load(f)
    return config


def get_otto_shell_model() -> str:
    config = get_otto_shell_config()
    model = config.get("ai", {}).get("model", "gpt-4o-mini")
    return model


def get_otto_shell_model_effort() -> str:
    config = get_otto_shell_config()
    effort = config.get("ai", {}).get("effort", "medium")
    return effort


def get_otto_shell_system_str() -> str:
    config = get_otto_shell_config()
    system = config.get("ai", {}).get("system", "You are OttoShell.")
    return system


def get_otto_shell_aliases() -> dict[str, str]:
    config = get_otto_shell_config()
    aliases = config.get("aliases", {})
    return aliases


def get_otto_shell_interactive_apps() -> list[str]:
    config = get_otto_shell_config()
    interactive_apps = config.get("interactive", {}).get("apps", [])
    return interactive_apps


def load_otto_shell_dotenv():
    load_dotenv(os.path.join(get_otto_shell_dir(), ".env"))


def estimate_tokens(text: str) -> int:
    return len(text) // 4


def dedent_and_unwrap(text: str) -> str:
    dedented = textwrap.dedent(text.strip())
    paragraphs = dedented.split("\n\n")
    unwrapped_paragraphs = [textwrap.fill(p.replace("\n", " ")) for p in paragraphs]
    result = "\n\n".join(unwrapped_paragraphs)
    return result


def glob_to_str(glob_pattern: str) -> str:
    files = glob.glob(glob_pattern, recursive=True)
    files = [f for f in files if os.path.isfile(f)]

    files_str = f"# files\n\nglob: {glob_pattern}\n\n"

    for file in files:
        files_str += f"## {file}\n\n"
        with open(file, "r") as f:
            files_str += f.read() + "\n\n"

    return files_str
