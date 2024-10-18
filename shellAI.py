#!/usr/bin/env python3
import google.generativeai as genai
import sys
import os
import subprocess
import re
import argparse
from time import sleep

VERBOSELEN = 20

parser = argparse.ArgumentParser(
    prog="ai",
    description="ai terminal assistant",
    epilog="eschaton",
)

parser.add_argument(
    "-A", "--auto", help="automatically run command. be weary", action="store_true"
)
parser.add_argument(
    "-r", "--recursive", help="add ;ai to the end of the ai suggested command", action="store_true"
)
parser.add_argument(
    "-p", "--pro", help="use gemini pro model instead", action="store_true"
)
parser.add_argument(
    "-t", "--terse", help="only return command no explanation", action="store_true"
)
parser.add_argument(
    "-v", "--verbose", help="verbose mode", action="store_true"
)

flag_thing, arg_input = parser.parse_known_args()
flags = {x: y for x, y in vars(flag_thing).items() if y is True}.keys()
if "verbose" in flags:
    print("Flags: ".ljust(VERBOSELEN), end="")
    print(" ".join(flags))
    print("Prompt prefix: ".ljust(VERBOSELEN), end="")
    print(" ".join(arg_input))

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

system_info = subprocess.check_output("hostnamectl", shell=True).decode("utf-8")
prompt = prompt + "\nHere is the output of hostnamectl\n" + system_info


if "pro" in flags:
    model = "gemini-1.5-pro-002"
else:
    model = "gemini-1.5-flash-002"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(model_name=model, system_instruction=prompt)



input_string: str = ""
if not sys.stdin.isatty():
    input_string = "".join(sys.stdin)
elif os.getenv("TMUX") != "":
    ib = subprocess.check_output("tmux capture-pane -pS -600", shell=True)
    input_string = ib.decode("utf-8")
i = ""
if len(arg_input) > 0:
    i = " ".join(arg_input)
if i + input_string != "":
    if "verbose" in flags:
        print("Tokens:".ljust(VERBOSELEN), end="")
        print(model.count_tokens(i + ":\n" + input_string))

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

    if command is None:
        # just take last line as command if no code block
        resp = response.strip().splitlines()
        command = resp[-1]
        response = "\n".join(resp[0:-1])

    if not ("terse" in flags):
        print(re.sub(r"```.*?```", "", response, flags=re.DOTALL))

    if command:
        # Remove leading $ if present and replace " for input and remove enter
        command = command.lstrip("$").replace('"', "'").replace("\n", " ")
        enter = "ENTER" if "auto" in flags else ""
        if "recursive" in flags:
            command = command + ";ai " + " ".join(["--"+s for s in flags]) + " " + i
        subprocess.run(
            " ".join(["tmux send-keys", '"' + command + '"', enter]), shell=True
        )
        print("\n")
        if "auto" in flags:
            sleep(2)

else:
    print("no input")
