import os
import json
import httpx
import tiktoken

from pydantic import BaseModel

from otto_shell.utils import (
    dedent_and_unwrap,
    get_otto_shell_system_str,
    get_otto_shell_model,
    get_otto_shell_model_effort,
)
from otto_shell.state import state

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set, use `os -c -e`")

client = httpx.Client(
    base_url="https://api.openai.com/v1",
    timeout=90.0,
    headers={
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "OttoShell/1.0",
    },
    http2=True,
    limits=httpx.Limits(max_connections=1, max_keepalive_connections=1),
)


def str_to_tokens(text: str, model: str = "gpt-4o-mini") -> list[int]:
    enc = tiktoken.encoding_for_model(model)
    return enc.encode(text)


def tokens_to_str(tokens: list[int], model: str = "gpt-4o-mini") -> str:
    enc = tiktoken.encoding_for_model(model)
    return enc.decode(tokens)


def question(q: str, model: str | None = None, history: list[str] = []) -> str:
    model = model or get_otto_shell_model()
    effort = get_otto_shell_model_effort()
    messages = [{"role": "developer", "content": h} for h in history]
    messages += [{"role": "user", "content": q}]
    instructions = get_otto_shell_system_str()
    data = {
        "model": model,
        "instructions": instructions,
        "input": messages,
        "previous_response_id": state.get("last_request_id", None),
        "reasoning": {"effort": effort} if model.startswith("o") else None,
    }
    r = client.post("/responses", json=data)

    response_text = ""
    if r.status_code != 200:
        return f"Error: {r.status_code}\n\n{r.text}"
    j = r.json()
    state["last_request_id"] = j["id"]
    for output in j["output"]:
        if "content" in output:
            for c in output["content"]:
                if "text" in c:
                    response_text += c["text"]

    return response_text


def choose(
    message: str,
    model: str = "gpt-4o-mini",
    options: list = ["yes", "no"],
    n: int = 3,
) -> str:
    # TODO: responses API doesn't have logit_bias, that's curious
    choose_system_template = """
    You are a text-based tool used to choose between options. You will be given instructions by the user and relevant context.

    You MUST choose between ONLY the following options:

    {options}

    You MUST choose the corresponding option number. They are:

    {option_numbers}

    You MUST respond with ONE and ONLY ONE option number from the options above.

    DO NOT INCLUDE EXTRA TEXT. You should respond like "1", "2", "3", etc.

    {additional_context}
    """
    choose_system_template = dedent_and_unwrap(choose_system_template)

    logit_bias = {}
    for i, _ in enumerate(options, start=1):
        logit_bias[str_to_tokens(str(i), model=model)[0]] = 100.0
    option_numbers = "\n".join(
        [f"Option {i}: {option}" for i, option in enumerate(options, start=1)]
    )

    system_message = choose_system_template.format(
        options=options, option_numbers=option_numbers, additional_context=""
    )

    messages = [
        {"role": "developer", "content": system_message},
        {"role": "user", "content": message},
    ]

    votes = {}
    for _ in range(n):
        payload = {
            "messages": messages,
            "model": model,
            "logit_bias": logit_bias,
            "max_tokens": 1,
            "temperature": 1.0,
            "n": 1,
        }

        # r = client.post("/responses", json=payload).json()
        r = client.post("/chat/completions", json=payload).json()
        for i, choice in enumerate(r["choices"]):
            category = int(choice["message"]["content"])
            count = votes.get(category, 0)
            votes[category] = count + 1

    max_option = max(votes, key=votes.get)
    choice = options[max_option - 1]
    return choice


def cast(
    message: str,
    model_class: BaseModel,
    model: str = "gpt-4o-mini",
) -> str:
    # TODO: update to responses API (some differences)
    cast_system_template = """
    You are a text-based tool used to cast a string into a structured JSON object. You will be given instructions by the user and relevant context.

    You MUST respond with a JSON object with the specified schema:

    {schema}
    """
    cast_system_template = dedent_and_unwrap(cast_system_template)

    system_message = cast_system_template.format(schema=model_class.schema())

    messages = [
        {
            "role": "system",
            "content": system_message,
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    payload = {
        "messages": messages,
        "model": model,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "cast",
                    "description": "cast text into a JSON format",
                    "parameters": model_class.schema(),
                },
            }
        ],
        "tool_choice": {"type": "function", "function": {"name": "cast"}},
        "temperature": 1.0,
    }

    response = client.post("/chat/completions", json=payload).json()

    class_output = json.loads(
        response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]
    )

    casted = model_class(**class_output)

    return casted
