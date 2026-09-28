# Computer.AI

**Computer.AI** is a free, open-source, local-first Chrome / Microsoft Edge extension and Python localhost server. It lets supported web AI chats request controlled operations in a user-selected local workspace. It is not an AI provider, a remote desktop service, or a way to bypass platform limits.

## Features

- Manifest V3 browser extension for ChatGPT, DeepSeek, Qwen, Gemini, Meta AI, Claude, and Grok.
- Small, dark/light-aware `computer.ai` panel with **Start to computer**.
- Real `127.0.0.1:8765` local server, health handshake, reconnect checks, logging, command IDs, and result injection.
- Sandboxed file commands, output/file/request limits, process timeouts, duplicate-command protection, and confirmation for high-risk commands.
- No third-party Python dependency.

## Installation

1. Open a terminal in this project and run `scripts\\install.bat` once.
2. Run `scripts\\start.bat` and leave its window open. The server listens only at `http://127.0.0.1:8765`.
3. In Chrome, open `chrome://extensions/`; in Edge, open `edge://extensions/`.
4. Enable **Developer mode**, choose **Load unpacked**, then select the `ComputerAI\\extension` folder.
5. Read and accept the first-run disclosure page.

## First run

Open one supported AI site. Near the chat input, choose **Start to computer**. Computer.AI checks the server and chat input, registers the extension, then sends the protocol instructions as a normal chat message. The extension observes only Computer.AI JSON code blocks, sends one command at a time to localhost, and injects the structured result into the current chat.

## Supported AI

ChatGPT (`chatgpt.com`), DeepSeek, Qwen, Gemini, Meta AI, Claude, and Grok. Each has its own adapter registration file under `extension/content/sites`. The base adapter deliberately uses semantic input fallbacks (`textarea`, `contenteditable`, and `role=textbox`) instead of brittle positional selectors.

## Command protocol

Commands must be one JSON code block, for example:

```json
{"id":"cmd-001","computer":"create_directory","params":{"path":"123"}}
```

Supported commands are `ping`, `get_status`, `get_workspace`, `list_files`, `read_file`, `write_file`, `append_file`, `create_directory`, `copy_file`, `move_file`, `delete_file`, `exists`, `run_python`, `run_node`, and `run_command`.

Paths are always relative to the configured workspace. `run_command` is disabled by default and, if enabled, runs without a shell through a short allow-list. Python, Node, moving/deleting files, and shell commands request confirmation by default.

## Security

The server binds to `127.0.0.1`, rejects absolute paths and traversal, does not inspect browser history/cookies/passwords, and redacts common secret-shaped values in logs. It bounds request size (1 MB), file size (10 MB), command output (1 MB), and command time (60 seconds). Configuration changes are made in the extension Settings page and saved to `server/config.json`.

## Troubleshooting

- **ERROR 002:** start `scripts\\start.bat`; do not close its window.
- **ERROR 010:** refresh the chat page after it finishes loading, then try again.
- **ERROR PROTOCOL_MISMATCH:** reload the unpacked extension and restart the server so both are 1.0.0.
- **ERROR 004:** use a workspace-relative path, never `..` or `C:\\Windows`.
- **ERROR 005:** approve the browser confirmation or adjust Settings only when you understand the operation.

## Tests

Run `python -m unittest discover -s tests -v` from the project root. Tests cover server commands, directory/file creation, read, traversal rejection, invalid commands, missing files, duplicate IDs, and process timeout. Browser handshake, UI, unsupported-site invisibility, reconnect, and result injection are implemented by the extension and should be verified manually using the first-run flow above.

## License

MIT. See [LICENSE](LICENSE).
