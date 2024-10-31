# Shell AI Assistant

A command-line tool that integrates AI assistance directly into your terminal. It reads your shell history and provides contextually aware command suggestions using various AI models through litellm.

## Features

- Reads your tmux pane directly and sends content to your choice of AI model (Currently openrouter/nousresearch/hermes-3-llama-3.1-405b:free by default)
- Automatically parses commands out of AI responses and puts them into your prompt for easy execution
- Optional Stack Exchange integration to provide additional context from relevant Q&A
- Embrace the danger with --auto and --recursive flags to make shellai automatically execute AI suggested commands and then call itself again in a loop

## Prerequisites

- Python 3
- TMux
- litellm
- BeautifulSoup4 (for Stack Exchange integration)

## Installation

1. Save the script as `shellai` in your PATH
2. Make it executable:
   ```bash
   chmod +x shellai
   ```
3. Set up your API key for your chosen provider as an environment variable:
   - `OPENROUTER_API_KEY`
   - `GEMINI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `TOGETHER_API_KEY`
   - And any others supported by litellm

## Usage

Basic usage:
```bash
shellai [options] [input]
```

### Options

- `-A`, `--auto`: Automatically execute the suggested command
- `-r`, `--recursive`: Add `;shellai` to the end of suggested commands
- `-m MODEL`, `--model MODEL`: Specify the AI model to use (default: openrouter/nousresearch/hermes-3-llama-3.1-405b:free)
- `-q`, `--quiet`: Only output the command, no explanation
- `-v`, `--verbose`: Enable verbose mode
- `--debug`: Run in debug mode (skips API request)
- `-t TARGET`, `--target TARGET`: Specify target TMux pane
- `--log FILE`: Log all output to specified file
- `--log-commands FILE`: Log only commands to specified file
- `--file FILE`: Read additional input from file
- `-S LINES`, `--scrollback LINES`: Number of scrollback lines to include
- `--system-prompt FILE`: Use custom system prompt from file
- `--delay SECONDS`: Set delay for auto-execution (default: 2.0)
- `-c`, `--add-stackexchange`: Add relevant context from Stack Exchange

### Examples

1. Get a command suggestion based on visible terminal content:
   ```bash
   shellai
   ```

2. Get a suggestion for a specific task:
   ```bash
   shellai how to find large files
   ```

3. Use a specific AI model:
   ```bash
   shellai -m anthropic/claude-3-5-sonnet-latest how do I automate these commands
   ```

4. Include Stack Exchange context:
   ```bash
   shellai -c how to compress images in bulk
   ```

## Security Notes

- Be cautious with `--auto` flag as it executes commands without confirmation
- Review suggested commands before execution
- Be mindful of sending terminal content to AI providers

## Limitations

- Requires TMux for full functionality
- API rate limits apply based on provider

## Contributing

Feel free to submit issues and enhancement requests!

## License

GPL 3
