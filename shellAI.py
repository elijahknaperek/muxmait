#!/usr/bin/env python3
import requests
import json
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
    "-A", "--auto", help="automatically run command. be weary",
    action="store_true"
)
parser.add_argument(
    "-r", "--recursive", help="add ;ai to the end of the ai suggested command",
    action="store_true"
)
parser.add_argument(
    "-p", "--pro", help="use a more advanced model",
    action="store_true"
)
parser.add_argument(
    "-t", "--terse", help="only return command no explanation",
    action="store_true"
)
parser.add_argument(
    "-v", "--verbose", help="verbose mode",
    action="store_true"
)
parser.add_argument(
    "--debug", help="skips api request and sets message to something mundane",
    action="store_true"
)

args, arg_input = parser.parse_known_args()

if args.verbose:
    print("Flags: ".ljust(VERBOSELEN), end="")
    print(args)
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

if args.pro:
    model = "openai/gpt-4-turbo-preview"
else:
    model = "nousresearch/hermes-3-llama-3.1-405b:free"

try:
    OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
    YOUR_SITE_URL = ""
    YOUR_APP_NAME = "shellai"
except KeyError:
    print("need OPENROUTER_API_KEY environment variable")
    quit()


def clean_command(c: str) -> str:
    subs = {
            '"': '\\"',
            "\n": "",
            "$": "\\$",
            "`": "\\`",
            "\\": "\\\\",
            }
    return "".join(subs.get(x, x) for x in c)


input_string: str = ""
if not sys.stdin.isatty():
    input_string = "".join(sys.stdin)
elif os.getenv("TMUX") != "":
    ib = subprocess.check_output("tmux capture-pane -pS -1000", shell=True)
    input_string = ib.decode("utf-8")

prefix_input = ""
if len(arg_input) > 0:
    prefix_input = " ".join(arg_input)

if prefix_input + input_string != "":
    if args.verbose:
        print("Using model:".ljust(VERBOSELEN), end="")
        print(model)

    if args.debug:
        response = """test msg \n echo test \n echo test \n"""
    else:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": prefix_input + ":\n" + input_string}
        ]

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_APP_NAME,
            },
            data=json.dumps({
                "model": model,
                "messages": messages
            })
        )

        if response.status_code == 200:
            response_data = response.json()
            response = response_data['choices'][0]['message']['content']
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            quit()

    # Extract a command from the response
    command = None
    # Look for the last code block
    code_blocks = re.findall(r"```(?:bash|shell)?\n(.+?)```", response, re.DOTALL)
    if code_blocks:
        # Get the last line from the last code block
        command = code_blocks[-1].strip().split("\n")[-1]
    else:
        # just take last line as command if no code block
        resp = response.strip().splitlines()
        command = resp[-1]
        response = "\n".join(resp[0:-1])

    if not args.terse:
        print(re.sub(r"```.*?```", "", response, flags=re.DOTALL))

    if command:
        command = clean_command(command)
        enter = "ENTER" if args.auto else ""
        if args.recursive:
            command = command + ";ai " + " ".join(sys.argv[1:])
        subprocess.run(
            " ".join(["tmux send-keys", '"' + command + '"', enter]), shell=True
        )
        print("\n")
        if args.auto:
            sleep(2)

else:
    print("no input")
