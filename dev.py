# ruff: noqa
# imports
import os
import json
import asyncio

import otto_shell

from rich import print

from openai import OpenAI
from agents import Agent, Runner

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
