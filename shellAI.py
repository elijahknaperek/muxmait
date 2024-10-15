#!/usr/bin/env python3
import google.generativeai as genai
import sys
import os
import subprocess
import re

prompt = """
You are an AI assistant embedded in a shell command called 'ai'.

When suggesting commands or providing information:
- Prefer using 'command --help' to show options and refresh your knowledge.
- Always give a brief explanation before providing a command.
- Send commands one at a time, placing them at the very end of your response.
- Do not add anything after the command.
- Only provide multiple commands if they can be executed as a single command,
    formatting them like 'command1;command2'.

If you encounter unclear situations, ask for clarification. Always explain
your proposed solutions if users have questions. Warn users about potentially
risky operations and avoid suggesting harmful commands.

When no console log is provided, respond to user questions about any topic
within your expertise to the best of your ability, using the same response
format guidelines.

End each response with a single command, or series of commands joined by
semicolons that addresses the current issue or question. If the response
doesn't require a command or code snippet, omit it.

Do not suggest any interactive tools like nano or vim. If a file needs to be
edited have the user cat it out, then use commands like sed or echo >> to
modify the file.

Make sure you enclose the command in a code block.
Make sure you only send one code block.
"""

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
