#!/usr/bin/env python3
import requests
import json
import sys
import os
import subprocess
import re
import argparse
from time import sleep

VERBOSE_LEN = 20
YOUR_SITE_URL = ""
YOUR_APP_NAME = "shellai"

prefix_input: str
input_string: str
api_key: str

system_prompt = """
You are an AI assistant within a shell command 'ai'. You operate by reading the
users scrollback. You can not see interactive input. Here are your guidelines:

DO ensure you present one command per response at the end, in a code block:
  ```bash
  command
  ```

DO NOT use multiple code blocks. For multiple commands, join with semicolons:
  ```bash
  command1; command2
  ```

DO precede commands with brief explanations.

DO NOT rely on your own knowledge; use `command --help` or `man command | cat`
  so both you and the user understand what is happening.

DO give a command to gather information when needed.

Do NOT suggest interactive editors like nano or vim, or other interactive programs.

DO use commands like `sed` or `echo >>` for file edits, or other non-interactive commands where applicable.

DO NOT add anything after command

If no command seems necessary, gather info or give a command for the user to explore.

ONLY ONE COMMAND PER RESPONSE AT END OF RESPONSE
"""


def clean_command(c: str) -> str:
    subs = {
            '"': '\\"',
            "\n": "",
            "$": "\\$",
            "`": "\\`",
            "\\": "\\\\",
            }
    return "".join(subs.get(x, x) for x in c)


def get_response_debug(prompt: str) -> str:
    if args.verbose:
        print("raw input")
        print("------------------------------------------")
        print("\n".join("# "+l for l in prompt.splitlines()))
        print("------------------------------------------")
    response = ""
    response += "prompt len:".ljust(VERBOSE_LEN) + str(len(prompt)) + "\n"
    response += "prefix_input:".ljust(VERBOSE_LEN) + prompt.splitlines()[0:-1][0] + "\n"
    response += "test code block:\n"
    response += "```bash\n echo \"$(" + prefix_input + ")\"\n```\n"
    return response


def get_response_default(prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt }
    ]

    response = requests.post(
        url=provider["url"],
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": YOUR_SITE_URL,
            "X-Title": YOUR_APP_NAME,
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": args.model,
            "messages": messages,
            "temperature": 0,
            "frequency_penalty": 1.3
        })
    )

    if response.status_code == 200:
        response_data = response.json()
        try:
            response = response_data['choices'][0]['message']['content']
        except KeyError:
            print("unexpected output")
            print(response_data)
            quit()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        quit()
    return response


def get_response_gemini(prompt: str) -> str:
    try:
        import google.generativeai as genai
    except ModuleNotFoundError:
        print("run pip install google-generativeai")
        quit()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
            args.model,
            system_instruction=system_prompt
            )
    response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0,
                )
            )
    return response.text


def get_response_anthropic(prompt: str) -> str:
    try:
        import anthropic
    except ModuleNotFoundError:
        print("run pip install anthropic")
        quit()

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
            model=args.model,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user",
                 "content": prompt}
            ]
    )
    text_content = []
    for content_block in response.content:
        if isinstance(content_block, dict) and content_block.get('type') == 'text':
            text_content.append(content_block.get('text', ''))
    return ' '.join(text_content)


providers = {
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key": "OPENROUTER_API_KEY",
        "default_model": "nousresearch/hermes-3-llama-3.1-405b:free",
        "wrapper": get_response_default,
    },
    "xai": {
        "url": "https://api.x.ai/v1/chat/completions",
        "api_key": "XAI_API_KEY",
        "default_model": "grok-beta",
        "wrapper": get_response_default,
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/",
        "api_key": "GEMINI_API_KEY",
        "default_model": "gemini-1.5-flash-002",
        "wrapper": get_response_gemini,
    },
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "api_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-3-5-sonnet-20240620",
        "wrapper": get_response_anthropic,
    },
    "together": {
        "url": "https://api.together.xyz/v1/chat/completions",
        "api_key": "TOGETHER_API_KEY",
        "default_model": "meta-llama/Llama-Vision-Free",
        "wrapper": get_response_default,
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "api_key": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
        "wrapper": get_response_default,
    }

}

default_tmux_target = (
            subprocess
            .check_output("tmux display-message -p '#S:#I.#P'", shell=True)
            .decode("utf-8")
            .strip()
        )

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
    "-m", "--model", help="change model.",
    default="",
)
parser.add_argument(
    "-q", "--quiet", help="only return command no explanation",
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
parser.add_argument(
    "-t", "--target", help="give target tmux pane to send commands to",
    default=default_tmux_target,
)
parser.add_argument(
    "-p", "--provider", help="set the api provider (openrouter, xai, etc...)",
    default="openrouter",
)
parser.add_argument(
    "--log", help="log output to given file"
)
parser.add_argument(
    "--log-commands", help="log only commands to file"
)
parser.add_argument(
    "--file", help="read input from file and append to prefix prompt"
)
parser.add_argument(
    "-S", "--scrollback", help="Scrollback lines to include in prompt. Without this only visable pane contents are included",
    default=0, type=int
)

args, arg_input = parser.parse_known_args()
provider = providers[args.provider]
args.model = provider["default_model"]

# get input from stdin or tmux scrollback
input_string: str = ""
if not sys.stdin.isatty():
    input_string = "".join(sys.stdin)
elif os.getenv("TMUX") != "":
    ib = subprocess.check_output(f"tmux capture-pane -p -t {args.target} -S -{args.scrollback}", shell=True)
    input_string = ib.decode("utf-8")
# remove shellai invocation from prompt (hopefully)
input_string = "\n".join(input_string.strip().splitlines()[0:-1])


if args.verbose:
    print("Flags: ".ljust(VERBOSE_LEN), end="")
    print(",\n".ljust(VERBOSE_LEN+2).join(str(vars(args)).split(",")))
    print("Prompt prefix: ".ljust(VERBOSE_LEN), end="")
    print(" ".join(arg_input))
    print("Provider:".ljust(VERBOSE_LEN), end="")
    print(",\n".ljust(VERBOSE_LEN+2).join(str(provider).split(",")))
    print("Using model:".ljust(VERBOSE_LEN), end="")
    print(args.model)
    print("Target:".ljust(VERBOSE_LEN), end="")
    print(args.target)
    print("\n")


# Add system info to prompt
with open("/etc/os-release") as f:
    system_info = {f: v for f, v in
                   (x.strip().split("=") for x in f.readlines())
                   }
system_prompt = system_prompt + f"user os: {system_info.get('NAME', 'linux')}"


# Get key
try:
    api_key = os.environ[provider["api_key"]]

except KeyError:
    print(f"need {provider["api_key"]} environment variable")
    quit()


# add input from command invocation
prefix_input = ""
if len(arg_input) > 0:
    prefix_input = " ".join(arg_input)
if args.file is not None:
    with open(args.file) as f:
        prefix_input += f.read()

# start processing input
prompt = prefix_input + ":\n" + input_string
if prefix_input + input_string != "":
    if args.verbose:
        print("getting response")
    response: str
    if args.debug:
        response = get_response_debug(prompt)
    else:
        response = provider["wrapper"](prompt)
    if args.verbose:
        print("raw response")
        print("------------------------------------------")
        print(response)
        print("------------------------------------------")

    if args.log is not None:
        with open(args.log, 'a') as log:
            log.write(response)

    # Extract a command from the response
    command = None
    # Look for the last code block
    code_blocks = re.findall(r"```(?:bash|shell)?\n(.+?)```", response, re.DOTALL)
    if args.verbose:
        print("code_blocks:".ljust(VERBOSE_LEN) + ":".join(code_blocks))
    if code_blocks:
        # Get the last line from the last code block
        command = code_blocks[-1].strip().split("\n")[-1]
    else:
        # just take last line as command if no code block
        resp = response.strip().splitlines()
        command = resp[-1]
        response = "\n".join(resp[0:-1])

    if not args.quiet:
        if len(code_blocks) == 1 and args.target == default_tmux_target:
            """ if printing msg remove code block as command will be printed
             by send-keys if sending to remote target cmd will not be printed
             by tmux so we skip this. """
            print(re.sub(r"```.*?```", "", response, flags=re.DOTALL))
        else:
            # if ai sends wrong number of commands just print whole msg
            print(response)

    # add command to Shell Prompt
    if command:
        command = clean_command(command)

        if args.log_commands is not None:
            with open(args.log_commands, 'a') as f:
                f.write(command)

        # presses enter on target tmux pane
        enter = "ENTER" if args.auto else ""
        # allows user to repeatedly call ai with the same options
        if args.recursive:
            if args.target == default_tmux_target:
                command = command + ";ai " + " ".join(sys.argv[1:])
            else:
                subprocess.run(
                    f'tmux send-keys "ai {" ".join(sys.argv[1:])}" {enter}', shell=True
                    )
                print("\n")

        # a little delay when using auto so user can hopefully C-c out
        if args.auto:
            sleep(2)
        # send command to shell prompt
        subprocess.run(
            f'tmux send-keys -t {args.target} "{command}" {enter}', shell=True
        )
        """ tmux send-keys on own pane will put output in front of ps and
        on prompt this keeps that output from moving the ps. If we are sending
        remote we do not need to worry about this. """
        if args.target == default_tmux_target:
            print("\n")

else:
    print("no input")
