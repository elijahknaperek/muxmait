#!/usr/bin/env python3
import google.generativeai as genai
import sys
import os
import subprocess
import re

prompt = """
You are an AI assistant within a shell command 'ai'. You operate by reading the 
users scrollback. You can not see interactive input. Here are your guidelines:

- DO ensure you present one command per response at the end, in a code block:
  ```bash
  command
  ```

- DO NOT use multiple code blocks. For multiple commands, join with semicolons:
  ```bash
  command1; command2
  ```

- DO precede commands with brief explanations.

- DO NOT rely on your own knowledge; use `command --help` or `man command | cat`
  so both you and the user understand what is happening.

- DO give a command to gather information when needed.

- Do NOT suggest interactive editors like nano or vim, or other interactive programs.

- DO use commands like `sed` or `echo >>` for file edits, or other non-interactive commands where applicable.

- If no command seems necessary, gather info or give a command for the user to explore.
"""

system_info = subprocess.check_output("hostnamectl",shell=True).decode('utf-8')
prompt = prompt + "\nHere is the output of hostnamectl\n" + system_info

model = "gemini-1.5-flash-002"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(model_name=model, system_instruction=prompt)

input_string: str = ""
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
    print(re.sub(r"```.*?```", "", response, flags=re.DOTALL))

    if command:
        # Remove leading $ if present
        command = command.lstrip("$")
        command = command.replace('"', "'")
        session = (
            subprocess.check_output("tmux display-message -p '#S'", shell=True)
            .decode("utf-8")
            .strip()
        )
        subprocess.run(
            " ".join(["tmux send-keys", "-t", session, '"' + command + '"']), shell=True
        )
        print("\n")

else:
    print("no input")
