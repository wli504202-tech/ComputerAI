# Computer.AI

> A local-first bridge between a supported web AI chat and your own Windows workspace.

Computer.AI is a free, open-source **Manifest V3** browser extension plus a Python localhost server. After you explicitly start Computer Mode on a supported chat page, the extension can detect a valid Computer.AI command, send it to the local server, and return the real result to the same conversation.

It is designed for local project work such as creating folders, writing files, reading files, and running controlled Python or Node.js scripts inside a configured workspace.

> [!IMPORTANT]
> Computer.AI is not an AI provider, remote desktop product, quota-bypass tool, or a way to bypass logins, payments, CAPTCHA, platform limits, or terms of service.

## Current support

| Website | Status |
| --- | --- |
| ChatGPT | ✓ Enabled |
| Grok | ✓ Enabled |
| DeepSeek | × Shown as unavailable |
| Qwen | × Shown as unavailable |
| Gemini | × Shown as unavailable |
| Meta AI | × Shown as unavailable |
| Claude | × Shown as unavailable |

Unsupported sites still show the Computer.AI panel, but their button is grey and cannot be selected. Their adapters remain in the source tree for future compatibility work.

## Features

- Chrome and Microsoft Edge extension using Manifest V3.
- A small `computer.ai` panel injected near the supported chat UI.
- A real local-only HTTP server at `http://127.0.0.1:8765`.
- Automatic local-server handshake, command delivery, and result injection after Computer Mode is started.
- Workspace-sandboxed file operations with traversal protection.
- Duplicate command-ID protection, logs, file/request/output limits, and process timeouts.
- Default user confirmation for high-risk operations.
- No third-party Python packages required.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer, available as `python`
- Google Chrome or Microsoft Edge

## Installation

### 1. Get the project

Clone or download this repository. The folder containing this README is the project root.

### 2. Prepare the local workspace

Run:

```bat
scripts\install.bat
```

This creates `workspace/`. No unrelated software is installed.

### 3. Start the local server

Run:

```bat
scripts\start.bat
```

Keep that window open. A successful start shows:

```text
Computer.AI Local Server running at http://127.0.0.1:8765
```

### 4. Load the browser extension

**Chrome**

1. Open `chrome://extensions/`.
2. Turn on **Developer mode**.
3. Select **Load unpacked**.
4. Choose this repository's `extension` folder.

**Microsoft Edge**

1. Open `edge://extensions/`.
2. Turn on **Developer mode**.
3. Select **Load unpacked**.
4. Choose this repository's `extension` folder.

On first install, read and accept the local-operation disclosure page.

## Using Computer.AI

1. Start `scripts\start.bat`.
2. Open ChatGPT or Grok.
3. Click **Start to computer** in the `computer.ai` panel.
4. The extension sends the Computer.AI protocol instructions as a normal chat message.
5. Ask the AI to create or edit files in your project.
6. Valid Computer.AI commands are sent one at a time to the local server. The structured result is returned to the chat before the next command should be made.

The AI must receive a successful result before it should claim that a local operation is complete.

## Command protocol

Commands must be one JSON object in a fenced code block and include a unique ID:

```json
{
  "id": "cmd-001",
  "computer": "create_directory",
  "params": {
    "path": "123"
  }
}
```

Available commands:

```text
ping
get_status
get_workspace
list_files
read_file
write_file
append_file
create_directory
copy_file
move_file
delete_file
exists
run_python
run_node
run_command
```

All file paths must be relative to the configured workspace. For example, use `project/index.html`, not `C:\Windows\...` and never `..`.

## Security model

- The server binds to `127.0.0.1` only; it is not exposed on the network.
- Absolute paths and path traversal are rejected.
- The server does not collect browser history, passwords, cookies, saved cards, or files outside the workspace.
- Requests are limited to 1 MB, files to 10 MB, command output to 1 MB, and execution to 60 seconds by default.
- `run_command` is disabled by default. If enabled, it uses a limited command allow-list and does not invoke a shell.
- Python, Node, move, delete, and shell operations require a browser confirmation by default.
- Logs redact common secret-shaped values such as passwords, API keys, tokens, and cookies.

> [!WARNING]
> An AI can generate incorrect code. Read confirmation dialogs and review generated files before running them in a production environment.

## Settings

Open the extension popup and choose **Settings** to configure:

- Local server URL
- Workspace location
- Python / Node / restricted shell permissions
- High-risk command confirmation
- Command timeout and limits

## API

The local server exposes the following local-only endpoints:

```text
GET  /health
GET  /status
GET  /workspace
GET  /logs
POST /command
POST /extension/hello
POST /settings
```

Example health response:

```json
{
  "status": "ok",
  "computerAI": true,
  "version": "1.0.0",
  "protocol_version": 1
}
```

## Project structure

```text
ComputerAI/
├── extension/           # Manifest V3 browser extension
│   ├── content/         # UI, adapters, and command detection
│   ├── popup/           # Extension popup
│   └── options/         # Settings page
├── server/              # Local Python HTTP server
├── scripts/             # Windows install/start/stop helpers
├── protocol/            # JSON schemas
├── tests/               # Server and parser tests
└── workspace/           # Default sandboxed local workspace
```

## Tests

From the project root, run:

```bat
python -m unittest discover -s tests -v
node tests\test-command-detector.js
```

The tests cover file creation and reading, path-traversal rejection, invalid and duplicate commands, missing files, and process timeout handling. Reload the extension after changes and manually verify the browser handshake on ChatGPT or Grok.

## Troubleshooting

| Message | What to do |
| --- | --- |
| `ERROR 002` | Start `scripts\start.bat` and leave the server window open. |
| `ERROR 004` | Use a workspace-relative path; do not use `..` or an absolute path. |
| `ERROR 005` | Approve the operation if you understand it, or enable the needed permission in Settings. |
| `ERROR 010` | Refresh the AI chat after it finishes loading, then try again. |
| `ERROR_PROTOCOL_MISMATCH` | Reload the extension and restart the server so both sides use version 1.0.0. |

## Contributing

Issues and pull requests are welcome. Site integrations change frequently, so compatibility fixes should be isolated in `extension/content/sites/` and include a reproducible test or clear manual verification steps.

## License

Released under the [MIT License](LICENSE).
