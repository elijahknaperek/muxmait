# Shell AI Assistant

A command-line tool that integrates AI assistance directly into your terminal. It reads your shell history and provides contextually aware command suggestions using various AI providers.

## Features

- Reads your tmux pane directly and then sends it to the AI of you choice (Currently openrouters nousresearch/hermes-3-llama-3.1-405b:free by default).
- Automaticly parses command out of AI responses and puts it into your prompt for easy exacution.
- Embrace the danger by using --auto and --recursive flags to make shellai automaticly exacute AI sugessted command and then call itself again in a loop.

## Prerequisites

- Python 3
- TMux
- Required Python packages (based on chosen provider):
  - `requests`
  - `anthropic` (for Claude)
  - `google-generativeai` (for Gemini)

## Installation

1. Save the script as `shellai` in your PATH
2. Make it executable:
   ```bash
   chmod +x shellai
   ```
3. Set up your API key for your chosen provider as an environment variable:
   - `OPENROUTER_API_KEY`
   - `XAI_API_KEY`
   - `GEMINI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `TOGETHER_API_KEY`
   - `OPENAI_API_KEY`

## Usage

Basic usage:
```bash
shellai [options] [input]
```

### Options

- `-A`, `--auto`: Automatically execute the suggested command
- `-r`, `--recursive`: Add `;shellai` to the end of suggested commands
- `-m MODEL`, `--model MODEL`: Specify the AI model to use
- `-q`, `--quiet`: Only output the command, no explanation
- `-v`, `--verbose`: Enable verbose mode
- `--debug`: Run in debug mode (skips API request)
- `-t TARGET`, `--target TARGET`: Specify target TMux pane
- `-p PROVIDER`, `--provider PROVIDER`: Select AI provider
- `--log FILE`: Log all output to specified file
- `--log-commands FILE`: Log only commands to specified file
- `--file FILE`: Read additional input from file
- `-S LINES`, `--scrollback LINES`: Number of scrollback lines to include
- `--custom-system FILE`: Use custom system prompt from file
- `--delay SECONDS`: Set delay for auto-execution (default: 2.0)

### Examples

1. Get a command suggestion based on visible terminal content:
   ```bash
   shellai
   ```

2. Get a suggestion for a specific task:
   ```bash
   shellai how to find large files
   ```

3. Auto-execute the suggested command:
   ```bash
   shellai -A create a backup of my home directory
   ```

4. Use a specific AI provider:
   ```bash
   shellai -p anthropic how do I automate these commands.
   ```


## Security Notes

- Be cautious with `--auto` flag as it executes commands without confirmation
- API keys should be stored securely
- Review suggested commands before execution
- Be mindful of sending sensitive terminal content to AI providers

## Limitations

- Requires TMux for full functionality
- Cannot handle interactive programs (vim, nano, etc.)
- API rate limits apply based on provider
- May require specific Python packages based on chosen provider

## Contributing

Feel free to submit issues and enhancement requests!

## License

[License information not provided in source code]
