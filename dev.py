# ruff: noqa
# imports
import os
import json
import httpx
import subprocess

from rich import print
from pydantic import BaseModel, Field

from otto_shell.openai import client, question, str_to_tokens, choose, cast
from otto_shell.state import state, clear_state
