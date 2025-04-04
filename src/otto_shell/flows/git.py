from otto_shell.hci import confirm
from otto_shell.openai import client
from otto_shell.commands import run_command


def commit_flow(
    instructions: str = "", all_files: bool = False, confirm_commit: bool = True
):
    diff = run_command("git diff")
    instructions = "Write a git commit for the user. Respond ONLY with the commit message. Do not include any other text."
    instructions += f"\n{instructions}" if instructions else ""
    message = ai_commit_message(diff, instructions)
    if confirm_commit:
        confirmed = confirm(f"Commit message:\n{message}\n\nProceed?")
        if not confirmed:
            return
    run_command("git add .") if not all else run_command("git add -A")
    run_command("git commit -m '{message}'")

    breakpoint()


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
