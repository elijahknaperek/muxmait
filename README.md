# Shell AI Assistant

A command-line tool that integrates AI assistance directly into your terminal. It reads your tmux pane content and provides contextually aware command suggestions using various AI models through litellm.

## Features

- Reads your tmux pane content and sends it to your choice of AI model
- Automatically parses commands from AI responses and puts them into your prompt
- Optional Stack Exchange integration to provide additional context from relevant stack exchange google search.
- Terrible and poorly thought out features like auto-execution and recursive mode for automated system destruction.

## Prerequisites

- Python 3
- TMux
- litellm
- BeautifulSoup4 (for Stack Exchange integration)
- requests

## Installation

1. Install required Python packages:
   ```bash
   pip install shellai-tmux
   ```
2. Set up your API key for your chosen provider as an environment variable:
   The tool looks for API keys in environment variables based on the chosen model:
   ```bash
   # Example API key setup
   export OPENROUTER_API_KEY="your-key-here"
   export ANTHROPIC_API_KEY="your-key-here"
   export GEMINI_API_KEY="your-key-here"
   export TOGETHER_API_KEY="your-key-here"
   ```
   - And any others supported by litellm

## Usage

Basic usage:
```bash
shellai [options] [input]
```

### Options

- `-A`, `--auto`: Automatically execute the suggested command (use with caution)
- `-r`, `--recursive`: Add `;shellai` to the end of suggested commands for continuous operation
- `-m MODEL`, `--model MODEL`: Choose AI model (can use number 0-5 to select from model list)
- `-q`, `--quiet`: Only output the command without explanation
- `-v`, `--verbose`: Enable verbose mode with detailed output
- `--debug`: Run in debug mode (skips API request)
- `-t TARGET`, `--target TARGET`: Specify target TMux pane (default: current pane)
- `--log FILE`: Log all output to specified file
- `--log-commands FILE`: Log only commands to specified file
- `--file FILE`: Read additional input from specified file
- `-S LINES`, `--scrollback LINES`: Number of scrollback lines to include from tmux (default: 0)
- `--system-prompt FILE`: Use custom system prompt from file
- `--delay SECONDS`: Set delay before auto-execution (default: 2.0 seconds)
- `-c`, `--add-stackexchange`: Add relevant context from Stack Exchange
- `-M MODEL`, `--model-stackexchange MODEL`: Specify model for Stack Exchange search query generation (default: gemini/gemini-1.5-flash-latest)

### Examples

1. Basic command suggestion based on visible terminal content:
   ```bash
   shellai
   ```

2. Get a suggestion for a specific task:
   ```bash
   shellai how to find large files
   ```

3. Use a specific model by number or name:
   ```bash
   shellai -m 3 how do I automate these commands
   # or
   shellai -m anthropic/claude-3-5-sonnet-latest how do I automate these commands
   ```

4. Include Stack Exchange context with custom model:
   ```bash
   shellai -c -M gemini/gemini-1.5-pro-latest how to compress images in bulk
   ```

5. Auto-execute commands with auto and recursive mode(or don't):
   ```bash
   shellai -A -r process these files  # DO NOT DO THIS
   ```

6. Include more context from terminal history:
   ```bash
   shellai -S 100 why won't this compile
   ```

## Security Considerations

- **Review commands before execution**: Always review suggested commands before running them
- **Auto-execution risks**: The `-A` flag will execute commands without confirmation
- **Data privacy**: Be mindful that terminal content is sent to AI providers
- **API credentials**: Secure your API keys and avoid exposing them in scripts or logs
- **Recursive mode**: Use `-r` flag with extreme caution as it can create command loops

## Troubleshooting

- Enable verbose mode (-v) for detailed operation information
- Check API key environment variables if model requests fail

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## License

GPL 3
