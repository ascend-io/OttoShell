import os
import tempfile

from rich.console import Console

from otto_shell.hci import confirm
from otto_shell.utils import get_otto_shell_model
from otto_shell.openai import client
from otto_shell.commands import run_command

# console setup
console = Console()


def commit_flow(
    instructions: str = "", all_files: bool = False, confirm_commit: bool = True
) -> None:
    diff = run_command("git diff origin/main")
    additional_instructions = f"\n\n{instructions}" if instructions else ""
    instructions = f"Write a Git commit for the user. Respond ONLY with the commit message. Do not include any other text like backticks or anything. Include all relevant changes from the code diff worth mentioning. Write in normal sentence casing.{additional_instructions}".strip()
    with console.status(f"asking Otto ({get_otto_shell_model()})...", spinner="dots"):
        message = ai_commit_message(diff, instructions)
    if confirm_commit:
        confirmed = confirm(f"Commit message:\n{message}\n\nProceed?")
        if not confirmed:
            return
    run_command("git add .") if not all_files else run_command("git add -A")

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as commit_file:
        commit_file.write(message)
        commit_file_path = commit_file.name

    run_command(f"git commit -F {commit_file_path}")
    os.remove(commit_file_path)


def ai_commit_message(diff: str, instructions: str) -> str:
    model = "gpt-4o-mini"
    messages = [{"role": "developer", "content": f"> git diff\n{diff}"}]
    messages += [
        {"role": "user", "content": "Can you write a good git commit message for me?"}
    ]
    data = {
        "model": model,
        "instructions": instructions,
        "input": messages,
    }
    r = client.post("/responses", json=data)

    response_text = ""
    j = r.json()
    for output in j["output"]:
        if "content" in output:
            for c in output["content"]:
                if "text" in c:
                    response_text += c["text"]

    return response_text
