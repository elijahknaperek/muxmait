#!/usr/bin/env python3
import google.generativeai as genai
import sys
import os
import subprocess
import tomllib
from pathlib import Path
import re
import pty

config_path = Path.home() / ".config/shellAI/shellAI.toml"
if os.path.exists(config_path):
    with open(Path.home() / ".config/shellAI/shellAI.toml", "rb") as f:
        config = tomllib.load(f)
else:
    print("config not present")
    quit()

prompt_path = Path.home() / ".config/shellAI/" / config["PROMPT"]
if os.path.exists(prompt_path):
    with open(prompt_path) as f:
        prompt = f.read()
else:
    prompt = "read the shell output and awnser"


genai.configure(api_key=config["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    model_name=config["MAIN_MODEL"], system_instruction=prompt
)

input_string: str = ""
# this is a comment
if not sys.stdin.isatty():
    input_string = "".join(sys.stdin)
elif os.getenv("TMUX") != "":
    ib = subprocess.check_output("tmux capture-pane -pS -1000", shell=True)
    input_string = ib.decode("utf-8")
i = ""
if len(sys.argv) > 1:
    i = " ".join(sys.argv[1:])
if i + input_string != "":
    r = model.generate_content(i + ":\n" + input_string)
    response = r.text
    print(response)

    # Extract a command from the response
    command = None
    # Look for the last code block
    code_blocks = re.findall(r"```(?:bash|shell)?\n(.+?)```", response, re.DOTALL)
    if code_blocks:
        # Get the last line from the last code block
        command = code_blocks[-1].strip().split("\n")[-1]
    else:
        # If no code blocks, look for the last line starting with $
        dollar_lines = re.findall(r"^\$\s*(.+)$", response, re.MULTILINE)
        if dollar_lines:
            command = dollar_lines[-1]

    if command:
        # Remove leading $ if present
        command = command.lstrip("$").strip()
        session = (
            subprocess.check_output("tmux display-message -p '#S'", shell=True)
            .decode("utf-8")
            .strip()
        )
        pty.spawn(["tmux", "send-keys", "-t", session, command])
else:
    print("no input")
